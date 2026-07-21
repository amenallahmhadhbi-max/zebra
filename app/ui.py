import tkinter as tk
from tkinter import messagebox
import threading
from PIL import Image, ImageTk
from paths import resource_path
from serial_number import (
    generate_serial_number_sequential,
    generate_serial_number_datetime,
    generate_serial_number_custom,
)
from label_template import build_zpl_label
from printer import send_to_printer, get_printer_status, SERIAL_PORT, BAUD_RATE, DATA_BITS, PARITY, STOP_BITS, FLOW_CONTROL
from datamatrix_preview import generate_datamatrix_image

# --- Visteon palette ---
COLOR_ORANGE = "#F4901E"
COLOR_DARK = "#313131"
COLOR_MEDIUM_GRAY = "#5A5A5A"
COLOR_WHITE = "#FFFFFF"
COLOR_LIGHT_BG = "#F5F5F5"

FONT_TITLE = ("Segoe UI", 16, "bold")
FONT_LABEL = ("Segoe UI", 10)
FONT_ENTRY = ("Segoe UI", 10)

MAX_CUSTOM_FIELDS = 5


def main():
    root = tk.Tk()
    root.title("Zebra Label Printer - Visteon")
    root.geometry("760x720")
    root.configure(bg=COLOR_LIGHT_BG)

    # --- Validation helper for numeric-only entries (used by "Sequence" fields) ---
    def _validate_numeric(value):
        return value == "" or value.isdigit()

    vcmd = (root.register(_validate_numeric), '%P')

    # --- Header ---
    header = tk.Frame(root, bg=COLOR_MEDIUM_GRAY, height=60)
    header.pack(fill="x")

    header_label = tk.Label(
        header, text="Visteon — Zebra Label Printer",
        bg=COLOR_MEDIUM_GRAY, fg=COLOR_WHITE, font=FONT_TITLE
    )
    header_label.pack(side="left", padx=20, pady=15)

    logo_img = Image.open(resource_path("assets/visteon_logo.png"))
    logo_img = logo_img.resize((100, 45))
    logo_tk = ImageTk.PhotoImage(logo_img)

    logo_label = tk.Label(header, image=logo_tk, bg=COLOR_MEDIUM_GRAY)
    logo_label.image = logo_tk
    logo_label.pack(side="right", padx=15, pady=8)

    # --- Top zone: PN, Starting SN, Quantity ---
    top_frame = tk.Frame(root, bg=COLOR_LIGHT_BG)
    top_frame.pack(pady=8)

    pn_label = tk.Label(top_frame, text="Product Number:", bg=COLOR_LIGHT_BG, fg=COLOR_DARK, font=FONT_LABEL)
    pn_label.grid(row=0, column=0, padx=5, pady=5, sticky="e")

    pn_entry = tk.Entry(top_frame, width=20, font=FONT_ENTRY)
    pn_entry.grid(row=0, column=1, padx=5, pady=5)

    sn_start_label = tk.Label(top_frame, text="Starting Serial Number:", bg=COLOR_LIGHT_BG, fg=COLOR_DARK, font=FONT_LABEL)
    sn_start_label.grid(row=1, column=0, padx=5, pady=5, sticky="e")

    sn_start_entry = tk.Entry(top_frame, width=20, font=FONT_ENTRY)
    sn_start_entry.grid(row=1, column=1, padx=5, pady=5)

    qty_label = tk.Label(top_frame, text="Quantity:", bg=COLOR_LIGHT_BG, fg=COLOR_DARK, font=FONT_LABEL)
    qty_label.grid(row=2, column=0, padx=5, pady=5, sticky="e")

    qty_entry = tk.Entry(top_frame, width=20, font=FONT_ENTRY)
    qty_entry.grid(row=2, column=1, padx=5, pady=5)

    # --- Custom fields zone (built dynamically) ---
    custom_frame = tk.Frame(top_frame, bg=COLOR_LIGHT_BG)
    custom_entries = []  # list of dicts: one per field row
    sequential_field = {"row": None}  # tracks which field (if any) is sequential

    custom_counter_label = tk.Label(
        custom_frame, text=f"Fields: 0/{MAX_CUSTOM_FIELDS}", bg=COLOR_LIGHT_BG, fg=COLOR_DARK, font=FONT_LABEL
    )

    def apply_field_display(field_row):
        """Configure the entry widget according to its sequential/type state."""
        entry = field_row["entry"]

        if field_row["seq_var"].get() == 1:
            if field_row["type_var"].get() == "Date/Time":
                # Read-only, shows a placeholder text, no numeric validation
                entry.config(state="normal", validate="none")
                entry.delete(0, tk.END)
                entry.insert(0, "date/time")
                entry.config(state="readonly", readonlybackground=COLOR_LIGHT_BG, fg=COLOR_MEDIUM_GRAY)
            else:  # Sequence
                # Editable, numeric only, used as the starting value
                entry.config(state="normal", fg=COLOR_DARK)
                entry.delete(0, tk.END)
                entry.config(validate="key", validatecommand=vcmd)
        else:
            # Free text field
            entry.config(state="normal", validate="none", fg=COLOR_DARK)
            entry.delete(0, tk.END)

    def on_seq_toggle(field_row):
        if field_row["seq_var"].get() == 1:
            # Uncheck any other field currently marked sequential
            if sequential_field["row"] is not None and sequential_field["row"] is not field_row:
                old = sequential_field["row"]
                old["seq_var"].set(0)
                old["type_menu"].grid_remove()
                apply_field_display(old)

            sequential_field["row"] = field_row
            field_row["type_menu"].grid(row=0, column=3, padx=3)
            apply_field_display(field_row)
        else:
            if sequential_field["row"] is field_row:
                sequential_field["row"] = None
            field_row["type_menu"].grid_remove()
            apply_field_display(field_row)

    def on_seq_type_change(field_row):
        apply_field_display(field_row)

    def refresh_custom_layout():
        for i, field_row in enumerate(custom_entries):
            row_frame = field_row["row_frame"]
            row_frame.grid(row=i, column=0, columnspan=2, pady=3, sticky="w")

        custom_counter_label.config(text=f"Fields: {len(custom_entries)}/{MAX_CUSTOM_FIELDS}")
        custom_counter_label.grid(row=MAX_CUSTOM_FIELDS, column=0, columnspan=2, pady=5)

        if len(custom_entries) >= MAX_CUSTOM_FIELDS:
            add_field_button.config(state="disabled")
        else:
            add_field_button.config(state="normal")

    def remove_custom_field(field_row):
        field_row["row_frame"].destroy()
        custom_entries.remove(field_row)
        if sequential_field["row"] is field_row:
            sequential_field["row"] = None
        refresh_custom_layout()

    def add_custom_field():
        if len(custom_entries) >= MAX_CUSTOM_FIELDS:
            return

        row_frame = tk.Frame(custom_frame, bg=COLOR_LIGHT_BG)

        entry = tk.Entry(row_frame, width=14, font=FONT_ENTRY)
        entry.grid(row=0, column=0, padx=3)

        field_row = {"row_frame": row_frame, "entry": entry}

        seq_var = tk.IntVar(value=0)
        seq_checkbox = tk.Checkbutton(
            row_frame, text="Sequential", variable=seq_var,
            bg=COLOR_LIGHT_BG, fg=COLOR_DARK, font=FONT_LABEL,
            activebackground=COLOR_LIGHT_BG, command=lambda: on_seq_toggle(field_row)
        )
        seq_checkbox.grid(row=0, column=1, padx=3)

        type_var = tk.StringVar(value="Date/Time")
        type_menu = tk.OptionMenu(row_frame, type_var, "Date/Time", "Sequence",
                                   command=lambda _: on_seq_type_change(field_row))
        type_menu.config(font=FONT_LABEL, bg=COLOR_WHITE)

        remove_button = tk.Button(
            row_frame, text="✕", font=FONT_LABEL,
            bg=COLOR_LIGHT_BG, fg=COLOR_DARK, relief="flat",
            cursor="hand2", command=lambda: remove_custom_field(field_row)
        )
        remove_button.grid(row=0, column=6, padx=3)

        field_row["seq_var"] = seq_var
        field_row["type_var"] = type_var
        field_row["type_menu"] = type_menu

        custom_entries.append(field_row)
        refresh_custom_layout()

    add_field_button = tk.Button(
        custom_frame, text="+ Add Field", command=add_custom_field,
        bg=COLOR_ORANGE, fg=COLOR_WHITE, font=FONT_LABEL,
        relief="flat", activebackground=COLOR_DARK, activeforeground=COLOR_WHITE,
        cursor="hand2"
    )

    # --- Mode selection ---
    mode_var = tk.StringVar(value="sequential")

    def on_mode_change():
        mode = mode_var.get()

        pn_label.grid_remove()
        pn_entry.grid_remove()
        sn_start_label.grid_remove()
        sn_start_entry.grid_remove()
        custom_frame.grid_remove()

        if mode == "sequential":
            pn_label.grid(row=0, column=0, padx=5, pady=5, sticky="e")
            pn_entry.grid(row=0, column=1, padx=5, pady=5)
            sn_start_label.grid(row=1, column=0, padx=5, pady=5, sticky="e")
            sn_start_entry.grid(row=1, column=1, padx=5, pady=5)
        elif mode == "datetime":
            pn_label.grid(row=0, column=0, padx=5, pady=5, sticky="e")
            pn_entry.grid(row=0, column=1, padx=5, pady=5)
        else:  # custom
            custom_frame.grid(row=1, column=0, columnspan=2, pady=5)
            if len(custom_entries) == 0:
                add_custom_field()
            else:
                refresh_custom_layout()
            add_field_button.grid(row=MAX_CUSTOM_FIELDS + 1, column=0, columnspan=2, pady=5)

    mode_frame = tk.Frame(top_frame, bg=COLOR_LIGHT_BG)
    mode_frame.grid(row=3, column=0, columnspan=2, pady=4)

    tk.Radiobutton(
        mode_frame, text="Sequential", variable=mode_var, value="sequential",
        command=on_mode_change, bg=COLOR_LIGHT_BG, fg=COLOR_DARK,
        font=FONT_LABEL, selectcolor=COLOR_WHITE, activebackground=COLOR_LIGHT_BG
    ).pack(side="left", padx=8)

    tk.Radiobutton(
        mode_frame, text="Date/Time", variable=mode_var, value="datetime",
        command=on_mode_change, bg=COLOR_LIGHT_BG, fg=COLOR_DARK,
        font=FONT_LABEL, selectcolor=COLOR_WHITE, activebackground=COLOR_LIGHT_BG
    ).pack(side="left", padx=8)

    tk.Radiobutton(
        mode_frame, text="Custom", variable=mode_var, value="custom",
        command=on_mode_change, bg=COLOR_LIGHT_BG, fg=COLOR_DARK,
        font=FONT_LABEL, selectcolor=COLOR_WHITE, activebackground=COLOR_LIGHT_BG
    ).pack(side="left", padx=8)

    custom_frame.grid(row=4, column=0, columnspan=2, pady=5)
    custom_frame.grid_remove()

    # --- Bottom zone: toggleable view (left) + Printed codes list (right) ---
    bottom_frame = tk.Frame(root, bg=COLOR_LIGHT_BG)
    bottom_frame.pack(pady=8, fill="both", expand=True, padx=20)

    left_frame = tk.Frame(bottom_frame, bg=COLOR_WHITE, highlightbackground=COLOR_ORANGE, highlightthickness=1)
    left_frame.pack(side="left", padx=(0, 10), fill="both", expand=True)

    nav_frame = tk.Frame(left_frame, bg=COLOR_ORANGE)
    nav_frame.pack(fill="x")

    view_title = tk.Label(nav_frame, text="Printer Configuration", font=("Segoe UI", 10, "bold"), bg=COLOR_ORANGE, fg=COLOR_WHITE)
    view_title.pack(side="left", expand=True, pady=6)

    config_frame = tk.Frame(left_frame, bg=COLOR_WHITE)

    config_lines = [
        f"Port: {SERIAL_PORT}",
        f"Baud rate: {BAUD_RATE}",
        f"Data bits: {DATA_BITS}",
        f"Parity: {PARITY}",
        f"Stop bits: {STOP_BITS}",
        f"Flow control: {FLOW_CONTROL}",
    ]

    for line in config_lines:
        tk.Label(config_frame, text=line, anchor="w", bg=COLOR_WHITE, fg=COLOR_DARK, font=FONT_LABEL).pack(fill="x", padx=10, pady=2)

    datamatrix_frame = tk.Frame(left_frame, bg=COLOR_WHITE)

    datamatrix_display = tk.Label(datamatrix_frame, bg=COLOR_WHITE)
    datamatrix_display.pack(pady=10)

    current_view = {"index": 0}

    def show_view(index):
        config_frame.pack_forget()
        datamatrix_frame.pack_forget()

        if index == 0:
            config_frame.pack(fill="both", expand=True)
            view_title.config(text="Printer Configuration")
        else:
            datamatrix_frame.pack(fill="both", expand=True)
            view_title.config(text="Data Matrix Preview")

        current_view["index"] = index

    def show_previous():
        show_view((current_view["index"] - 1) % 2)

    def show_next():
        show_view((current_view["index"] + 1) % 2)

    prev_button = tk.Button(
        nav_frame, text="◀", command=show_previous,
        bg=COLOR_ORANGE, fg=COLOR_WHITE, font=FONT_LABEL,
        relief="flat", activebackground=COLOR_DARK, activeforeground=COLOR_WHITE
    )
    prev_button.pack(side="left", padx=8)

    next_button = tk.Button(
        nav_frame, text="▶", command=show_next,
        bg=COLOR_ORANGE, fg=COLOR_WHITE, font=FONT_LABEL,
        relief="flat", activebackground=COLOR_DARK, activeforeground=COLOR_WHITE
    )
    next_button.pack(side="right", padx=8)

    show_view(0)

    right_frame = tk.Frame(bottom_frame, bg=COLOR_WHITE, highlightbackground=COLOR_ORANGE, highlightthickness=1)
    right_frame.pack(side="left", fill="both", expand=True)

    sn_label = tk.Label(right_frame, text="Printed Codes", bg=COLOR_ORANGE, fg=COLOR_WHITE, font=("Segoe UI", 10, "bold"))
    sn_label.pack(fill="x", ipady=6)

    sn_listbox = tk.Listbox(
        right_frame, width=40, height=10, font=FONT_ENTRY,
        bg=COLOR_WHITE, fg=COLOR_DARK, selectbackground=COLOR_ORANGE,
        relief="flat", highlightthickness=0
    )
    sn_listbox.pack(pady=10, padx=10, fill="both", expand=True)

    # --- UI update function (called ONLY via root.after) ---
    def update_ui_after_print(code):
        sn_listbox.insert(tk.END, code)

        pil_image = generate_datamatrix_image(code)
        pil_image = pil_image.resize((150, 150))
        tk_image = ImageTk.PhotoImage(pil_image)

        datamatrix_display.configure(image=tk_image)
        datamatrix_display.image = tk_image

    def show_error(message):
        messagebox.showerror("Printer Error", message)
        print_button.config(state="normal")

    # --- Print loop, run in a separate thread ---
    def print_loop(mode, pn, sn_start, qty, fields_config):
        for i in range(qty):
            status = get_printer_status()

            if status is None:
                root.after(0, show_error, "Unable to reach the printer.")
                return
            if status.get("paper_out"):
                root.after(0, show_error, "Printer is out of paper!")
                return
            if status.get("ribbon_out"):
                root.after(0, show_error, "Printer is out of ribbon!")
                return
            if status.get("head_open"):
                root.after(0, show_error, "Print head is open!")
                return
            if status.get("paused"):
                root.after(0, show_error, "Printer is paused.")
                return

            if mode == "sequential":
                code = generate_serial_number_sequential(pn, sn_start, i)
            elif mode == "datetime":
                code = generate_serial_number_datetime(pn)
            else:
                code = generate_serial_number_custom(fields_config, i)

            zpl_code = build_zpl_label(pn, code)
            success = send_to_printer(zpl_code)

            if success:
                root.after(0, update_ui_after_print, code)
                print(f"Label {i + 1}/{qty} printed. Code: {code}")
            else:
                root.after(0, show_error, f"Failed to print label {i + 1}/{qty}.")
                return

        root.after(0, lambda: print_button.config(state="normal"))

    # --- Called on Print button click ---
    def on_print_click():
        mode = mode_var.get()
        qty_text = qty_entry.get().strip()

        if not qty_text.isdigit():
            messagebox.showerror("Error", "Quantity must be a whole number.")
            return

        qty = int(qty_text)
        pn = ""
        sn_start = 0
        fields_config = []

        if mode == "sequential":
            pn = pn_entry.get().strip()
            if not pn:
                messagebox.showerror("Error", "Product Number is empty.")
                return
            sn_start_text = sn_start_entry.get().strip()
            if not sn_start_text.isdigit():
                messagebox.showerror("Error", "Starting serial number must be a whole number.")
                return
            sn_start = int(sn_start_text)

        elif mode == "datetime":
            pn = pn_entry.get().strip()
            if not pn:
                messagebox.showerror("Error", "Product Number is empty.")
                return

        else:  # custom
            if len(custom_entries) == 0:
                messagebox.showerror("Error", "Add at least one field for Custom mode.")
                return

            for field_row in custom_entries:
                is_seq = field_row["seq_var"].get() == 1
                entry_text = field_row["entry"].get().strip()
                field_data = {"sequential": is_seq}

                if is_seq:
                    seq_type = field_row["type_var"].get()
                    if seq_type == "Sequence":
                        if not entry_text.isdigit():
                            messagebox.showerror("Error", "Sequence start must be a whole number.")
                            return
                        field_data["seq_type"] = "sequence"
                        field_data["start"] = int(entry_text)
                        field_data["value"] = ""
                    else:
                        field_data["seq_type"] = "datetime"
                        field_data["value"] = ""
                else:
                    field_data["value"] = entry_text

                fields_config.append(field_data)

        print_button.config(state="disabled")
        thread = threading.Thread(target=print_loop, args=(mode, pn, sn_start, qty, fields_config))
        thread.start()

    # --- Print button ---
    print_button = tk.Button(
        top_frame, text="PRINT", command=on_print_click,
        bg=COLOR_ORANGE, fg=COLOR_WHITE, font=("Segoe UI", 11, "bold"),
        relief="flat", activebackground=COLOR_DARK, activeforeground=COLOR_WHITE,
        padx=20, pady=8, cursor="hand2"
    )
    print_button.grid(row=5, column=0, columnspan=2, pady=8)

    on_mode_change()

    root.mainloop()


if __name__ == "__main__":
    main()