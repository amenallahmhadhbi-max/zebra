
# Zebra Label Printer - Visteon Tunisia

Label generation and printing application for a Zebra printer, developed as part of an internship at Visteon Tunisia.

## Features

- Generation of unique codes encoded as Data Matrix on each label
- Three code generation modes:
  - **Sequential**: `PN_NUMBER_DATE_LINE_STATION`, incremental serial number
  - **Date/Time**: `PN_YYMMDDHHMMSS`, unique timestamp
  - **Custom**: `PN_field1_field2_...`, up to 5 free-text fields defined by the user
- Real connection to the printer via serial port (RS-232)
- Printer status check before each print (paper, ribbon, head, pause)
- Visual preview of the Data Matrix in the interface
- Externalized ZPL template, editable without touching the code

## Requirements

- Python 3.12
- A Zebra printer connected via serial port (RS-232), e.g. model 105SL

## Installation

1. Clone the repository:
git clone https://github.com/amenallahmhadhbi-max/zebra.git
cd zebra


2. Create and activate the virtual environment:
python -m venv venv
venv\Scripts\activate


3. Install the dependencies:
pip install -r requirement.txt


## Configuration

Before the first launch, configure the printer connection settings in `config/printer_config.ini`:

```ini
[PrinterSettings]
port = COM7
baud_rate = 9600
data_bits = 8
parity = N
stop_bits = 1
flow_control = XONXOFF
```

Adjust `port` according to the COM port assigned by Windows (visible in Device Manager).

The label's ZPL template can be adjusted in `templates/label_mask.txt`.

## Launch
python app/main.py


## Project Structure
zebra/
├── app/
│ ├── main.py # Entry point
│ ├── ui.py # Graphical interface (Tkinter)
│ ├── serial_number.py # Code generation (3 modes)
│ ├── label_template.py # ZPL construction from the template
│ ├── printer.py # Printer communication (send + status)
│ └── datamatrix_preview.py # Visual Data Matrix preview generation
├── templates/
│ └── label_mask.txt # Label ZPL template
├── config/
│ └── printer_config.ini # Printer connection settings
├── assets/
│ └── visteon_logo.png
└── requirement.txt


## Author

Amenallah Mhadhbi — Visteon Tunisia Internship

