import tkinter as tk
import threading
from PIL import Image, ImageTk
from serial_number import generate_serial_number_sequential, generate_serial_number_datetime
from label_template import build_zpl_label
from printer import send_to_printer, SERIAL_PORT, BAUD_RATE, DATA_BITS, PARITY, STOP_BITS, FLOW_CONTROL
from datamatrix_preview import generate_datamatrix_image

# --- Palette Visteon ---
COLOR_ORANGE = "#F4901E"
COLOR_DARK = "#313131"
COLOR_WHITE = "#FFFFFF"
COLOR_LIGHT_BG = "#F5F5F5"
COLOR_MEDIUM_GRAY = "#5A5A5A"

FONT_TITLE = ("Segoe UI", 16, "bold")
FONT_LABEL = ("Segoe UI", 10)
FONT_ENTRY = ("Segoe UI", 10)


def main():
    root = tk.Tk()
    root.title("Zebra Label Printer - Visteon")
    root.geometry("720x600")
    root.configure(bg=COLOR_LIGHT_BG)

    # --- En-tête ---
    header = tk.Frame(root, bg=COLOR_MEDIUM_GRAY, height=60)
    header.pack(fill="x")

    header_label = tk.Label(
        header, text="Visteon — Zebra Label Printer",
        bg=COLOR_MEDIUM_GRAY, fg=COLOR_WHITE, font=FONT_TITLE
    )
    header_label.pack(side="left", padx=20, pady=15)

    logo_img = Image.open("assets/visteon_logo.png")
    logo_img = logo_img.resize((100, 45))
    logo_tk = ImageTk.PhotoImage(logo_img)

    logo_label = tk.Label(header, image=logo_tk, bg=COLOR_MEDIUM_GRAY)
    logo_label.image = logo_tk
    logo_label.pack(side="right", padx=15, pady=8)

    # --- Zone du haut : PN, SN de départ et Quantité ---
    top_frame = tk.Frame(root, bg=COLOR_LIGHT_BG)
    top_frame.pack(pady=8)

    pn_label = tk.Label(top_frame, text="Product Number:", bg=COLOR_LIGHT_BG, fg=COLOR_DARK, font=FONT_LABEL)
    pn_label.grid(row=0, column=0, padx=5, pady=5, sticky="e")

    pn_entry = tk.Entry(top_frame, width=20, font=FONT_ENTRY)
    pn_entry.grid(row=0, column=1, padx=5, pady=5)

    sn_start_label = tk.Label(top_frame, text="N° de série de départ:", bg=COLOR_LIGHT_BG, fg=COLOR_DARK, font=FONT_LABEL)
    sn_start_label.grid(row=1, column=0, padx=5, pady=5, sticky="e")

    sn_start_entry = tk.Entry(top_frame, width=20, font=FONT_ENTRY)
    sn_start_entry.grid(row=1, column=1, padx=5, pady=5)

    qty_label = tk.Label(top_frame, text="Quantité:", bg=COLOR_LIGHT_BG, fg=COLOR_DARK, font=FONT_LABEL)
    qty_label.grid(row=2, column=0, padx=5, pady=5, sticky="e")

    qty_entry = tk.Entry(top_frame, width=20, font=FONT_ENTRY)
    qty_entry.grid(row=2, column=1, padx=5, pady=5)

    # --- Sélection du mode de génération ---
    mode_var = tk.StringVar(value="sequential")

    def on_mode_change():
        if mode_var.get() == "sequential":
            sn_start_label.grid(row=1, column=0, padx=5, pady=5, sticky="e")
            sn_start_entry.grid(row=1, column=1, padx=5, pady=5)
        else:
            sn_start_label.grid_remove()
            sn_start_entry.grid_remove()

    mode_frame = tk.Frame(top_frame, bg=COLOR_LIGHT_BG)
    mode_frame.grid(row=4, column=0, columnspan=2, pady=4)

    tk.Radiobutton(
        mode_frame, text="Séquentiel", variable=mode_var, value="sequential",
        command=on_mode_change, bg=COLOR_LIGHT_BG, fg=COLOR_DARK,
        font=FONT_LABEL, selectcolor=COLOR_WHITE, activebackground=COLOR_LIGHT_BG
    ).pack(side="left", padx=10)

    tk.Radiobutton(
        mode_frame, text="Date/Heure", variable=mode_var, value="datetime",
        command=on_mode_change, bg=COLOR_LIGHT_BG, fg=COLOR_DARK,
        font=FONT_LABEL, selectcolor=COLOR_WHITE, activebackground=COLOR_LIGHT_BG
    ).pack(side="left", padx=10)

    # --- Zone du bas : Vue basculable (gauche) + Liste des codes (droite) ---
    bottom_frame = tk.Frame(root, bg=COLOR_LIGHT_BG)
    bottom_frame.pack(pady=8, fill="both", expand=True, padx=20)

    left_frame = tk.Frame(bottom_frame, bg=COLOR_WHITE, highlightbackground=COLOR_ORANGE, highlightthickness=1)
    left_frame.pack(side="left", padx=(0, 10), fill="both", expand=True)

    nav_frame = tk.Frame(left_frame, bg=COLOR_ORANGE)
    nav_frame.pack(fill="x")

    view_title = tk.Label(nav_frame, text="Configuration Imprimante", font=("Segoe UI", 10, "bold"), bg=COLOR_ORANGE, fg=COLOR_WHITE)
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
            view_title.config(text="Configuration Imprimante")
        else:
            datamatrix_frame.pack(fill="both", expand=True)
            view_title.config(text="Aperçu Data Matrix")

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

    sn_label = tk.Label(right_frame, text="Codes imprimés", bg=COLOR_ORANGE, fg=COLOR_WHITE, font=("Segoe UI", 10, "bold"))
    sn_label.pack(fill="x", ipady=6)

    sn_listbox = tk.Listbox(
        right_frame, width=40, height=10, font=FONT_ENTRY,
        bg=COLOR_WHITE, fg=COLOR_DARK, selectbackground=COLOR_ORANGE,
        relief="flat", highlightthickness=0
    )
    sn_listbox.pack(pady=10, padx=10, fill="both", expand=True)

    # --- Fonction qui met à jour l'interface (appelée UNIQUEMENT via root.after) ---
    def update_ui_after_print(code):
        sn_listbox.insert(tk.END, code)

        pil_image = generate_datamatrix_image(code)
        pil_image = pil_image.resize((150, 150))
        tk_image = ImageTk.PhotoImage(pil_image)

        datamatrix_display.configure(image=tk_image)
        datamatrix_display.image = tk_image

    # --- La boucle d'impression, exécutée dans un thread séparé ---
    def print_loop(mode, pn, sn_start, qty):
        for i in range(qty):
            if mode == "sequential":
                code = generate_serial_number_sequential(pn, sn_start, i)
            else:
                code = generate_serial_number_datetime(pn)

            zpl_code = build_zpl_label(pn, code)
            success = send_to_printer(zpl_code)

            if success:
                root.after(0, update_ui_after_print, code)
                print(f"Étiquette {i + 1}/{qty} imprimée. Code: {code}")
            else:
                print(f"Échec de l'impression de l'étiquette {i + 1}/{qty}.")

    # --- Fonction appelée au clic du bouton ---
    def on_print_click():
        mode = mode_var.get()
        pn = pn_entry.get().strip()
        qty_text = qty_entry.get().strip()

        if not pn:
            print("Erreur : Product Number vide.")
            return

        if not qty_text.isdigit():
            print("Erreur : la quantité doit être un nombre entier.")
            return

        qty = int(qty_text)
        sn_start = 0

        if mode == "sequential":
            sn_start_text = sn_start_entry.get().strip()
            if not sn_start_text.isdigit():
                print("Erreur : le numéro de série de départ doit être un nombre entier.")
                return
            sn_start = int(sn_start_text)

        thread = threading.Thread(target=print_loop, args=(mode, pn, sn_start, qty))
        thread.start()

    # --- Bouton Imprimer ---
    print_button = tk.Button(
        top_frame, text="IMPRIMER", command=on_print_click,
        bg=COLOR_ORANGE, fg=COLOR_WHITE, font=("Segoe UI", 11, "bold"),
        relief="flat", activebackground=COLOR_DARK, activeforeground=COLOR_WHITE,
        padx=20, pady=8, cursor="hand2"
    )
    print_button.grid(row=5, column=0, columnspan=2, pady=8)

    root.mainloop()


if __name__ == "__main__":
    main()