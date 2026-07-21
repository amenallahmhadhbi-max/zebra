# Zebra Label Printer - Visteon Tunisie

Application de génération et d'impression d'étiquettes pour imprimante Zebra, développée dans le cadre d'un stage chez Visteon Tunisie.

## Fonctionnalités

- Génération de codes uniques encodés en Data Matrix sur chaque étiquette
- Trois modes de génération de code :
  - **Séquentiel** : `PN_NUMERO_DATE_LIGNE_STATION`, numéro de série incrémental
  - **Date/Heure** : `PN_AAMMJJHHMMSS`, horodatage unique
  - **Custom** : `PN_champ1_champ2_...`, jusqu'à 5 champs texte libres définis par l'utilisateur
- Connexion réelle à l'imprimante via port série (RS-232)
- Vérification de l'état de l'imprimante avant chaque impression (papier, ruban, tête, pause)
- Aperçu visuel du Data Matrix dans l'interface
- Masque ZPL externalisé, modifiable sans toucher au code

## Prérequis

- Python 3.12
- Une imprimante Zebra connectée via port série (RS-232), ex: modèle 105SL

## Installation

1. Cloner le dépôt :git clone https://github.com/amenallahmhadhbi-max/zebra.git
cd zebra

2. Créer et activer l'environnement virtuel :python -m venv venv
venv\Scripts\activate


3. Installer les dépendances :pip install -r requirement.txt
4. ## Configuration

Avant le premier lancement, configurer les paramètres de connexion imprimante dans `config/printer_config.ini` :

```ini
[PrinterSettings]
port = COM7
baud_rate = 9600
data_bits = 8
parity = N
stop_bits = 1
flow_control = XONXOFF
```

Ajuster `port` selon le port COM attribué par Windows (visible dans le Gestionnaire de périphériques).

Le masque ZPL de l'étiquette peut être ajusté dans `templates/label_mask.txt`.

## Lancement
python app/main.py

## Structure du projet
zbra/
├── app/
│ ├── main.py # Point d'entrée
│ ├── ui.py # Interface graphique (Tkinter)
│ ├── serial_number.py # Génération des codes (3 modes)
│ ├── label_template.py # Construction du ZPL à partir du masque
│ ├── printer.py # Communication avec l'imprimante (envoi + statut)
│ └── datamatrix_preview.py # Génération de l'aperçu visuel du Data Matrix
├── templates/
│ └── label_mask.txt # Masque ZPL de l'étiquette
├── config/
│ └── printer_config.ini # Paramètres de connexion imprimante
├── assets/
│ └── visteon_logo.png
└── requirement.txt

## Auteur

Amenallah Mhadhbi — Stage Visteon Tunisie