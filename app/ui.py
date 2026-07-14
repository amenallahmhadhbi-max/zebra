import tkinter as tk
from PIL import ImageTk
from serial_number import generate_serial_number
from label_template import build_zpl_label
from printer import send_to_printer
from datamatrix_preview import generate_datamatrix_image


def main():
    root = tk.Tk()
    root.title("Zebra Label Printer - Visteon")
    root.geometry("700x450")

    # Zone du haut
    top_frame = tk.Frame(root)
    top_frame.pack(pady=10)

    pn_label = tk.Label(top_frame, text="Product Number:")
    pn_label.grid(row=0, column=0, padx=5, pady=5, sticky="e")

    pn_entry = tk.Entry(top_frame, width=20)
    pn_entry.grid(row=0, column=1, padx=5, pady=5)

    qty_label = tk.Label(top_frame, text="Quantité:")
    qty_label.grid(row=1, column=0, padx=5, pady=5, sticky="e")

    qty_entry = tk.Entry(top_frame, width=20)
    qty_entry.grid(row=1, column=1, padx=5, pady=5)

    # Zone du bas 
    bottom_frame = tk.Frame(root)
    bottom_frame.pack(pady=10, fill="both", expand=True)

    # Sous-zone gauche 
    left_frame = tk.Frame(bottom_frame)
    left_frame.pack(side="left", padx=10, fill="both", expand=True)

    datamatrix_title = tk.Label(left_frame, text="Aperçu Data Matrix :")
    datamatrix_title.pack(anchor="w")

    datamatrix_display = tk.Label(left_frame)
    datamatrix_display.pack(pady=5)

    # Sous-zone droite 
    right_frame = tk.Frame(bottom_frame)
    right_frame.pack(side="left", padx=10, fill="both", expand=True)

    sn_label = tk.Label(right_frame, text="Numéros de série imprimés :")
    sn_label.pack(anchor="w")

    sn_listbox = tk.Listbox(right_frame, width=40, height=10)
    sn_listbox.pack(pady=5, fill="both", expand=True)

    # Fonction clic du bouton
    def on_print_click():
        pn = pn_entry.get()
        qty_text = qty_entry.get()

        if not pn:
            print("Erreur : Product Number vide.")
            return

        if not qty_text.isdigit():
            print("Erreur : la quantité doit être un nombre entier.")
            return

        qty = int(qty_text)

        for i in range(qty):
            sn = generate_serial_number(pn)
            zpl_code = build_zpl_label(pn, sn)
            success = send_to_printer(zpl_code)

            if success:
                sn_listbox.insert(tk.END, sn)

                # Génère et affiche l'aperçu Data Matrix du dernier SN imprimé
                pil_image = generate_datamatrix_image(sn)
                pil_image = pil_image.resize((150, 150))
                tk_image = ImageTk.PhotoImage(pil_image)

                datamatrix_display.configure(image=tk_image)
                datamatrix_display.image = tk_image 

                print(f"Étiquette {i + 1}/{qty} imprimée. SN: {sn}")
            else:
                print(f"Échec de l'impression de l'étiquette {i + 1}/{qty}.")

    # Bouton Imprimer
    print_button = tk.Button(top_frame, text="Imprimer", command=on_print_click)
    print_button.grid(row=2, column=0, columnspan=2, pady=10)

    root.mainloop()


if __name__ == "__main__":
    main()