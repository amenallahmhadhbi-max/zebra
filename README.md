# Zebra Label Printer - Visteon Tunisia

Label generation and printing application for a Zebra printer, developed as part of an internship at Visteon Tunisia.

## Features

- Generation of unique codes encoded as Data Matrix on each label
- Three code generation modes:
  - **Sequential**: `PN_NUMBER_DATE_LINE_STATION`, incremental serial number
  - **Date/Time**: `PN_YYMMDDHHMMSS`, unique timestamp
  - **Custom**: up to 5 free-text fields defined by the user, with an optional sequential field (Date/Time or Sequence)
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
Set-ExecutionPolicy -ExecutionPolicy Bypass -Scope Process
venv\Scripts\activate



   > `Set-ExecutionPolicy -ExecutionPolicy Bypass -Scope Process` is needed on Windows/PowerShell if activating the venv fails with a "running scripts is disabled on this system" error. It only changes the policy for the current terminal session, not system-wide.

3. Install the dependencies:

pip install -r requirement.txt


## Simulation Mode

Before a real Zebra printer is connected, the app can run in **simulation mode**: instead of sending data to a physical printer over serial, it prints the ZPL output to the console and simulates a short delay, without needing any hardware.

To enable it, open `app/printer.py` and set:

```python
SIMULATION_MODE = True
```

Set it back to `False` once the real printer is connected and configured (see the Configuration section below), so that `send_to_printer` and `get_printer_status` communicate with the actual serial port instead of simulating.

## Building the executable (.exe)

This project uses PyInstaller to build a standalone Windows executable.
A `.spec` file is already included in the repo, so it's recommended to build from it directly — this ensures consistent build settings (name, icon, included data files, etc.) every time.

1. Make sure your venv is activated and dependencies are installed (see above).

2. If a previous build exists, remove the old `dist` folder first so PyInstaller regenerates it cleanly:

Remove-Item -Recurse -Force dist


3. Build using the existing spec file and Copy the required data folders into the build output (the spec file's `datas` may already include these, but re-copy manually if needed after a clean rebuild):

pyinstaller ZebraLabelPrinter.spec
Copy-Item -Recurse config dist/config -Force
Copy-Item -Recurse templates dist/templates -Force


4. The generated executable will be located at:

dist/ZebraLabelPrinter.exe


## Troubleshooting the executable

### Missing DLL errors on the target machine

If the `.exe` fails to start on another computer with an error like:

The code execution cannot proceed because VCRUNTIME140.dll was not found


This means the **Microsoft Visual C++ Redistributable** is not installed on that machine. This is common on older or industrial Windows PCs.

**Fix:** Download and install it from Microsoft:
👉 https://aka.ms/vs/17/release/vc_redist.x64.exe

### pywin32 / DLL load failed errors

If you see a `DLL load failed` or `pywintypesXX.dll` related error when running the built `.exe`, it usually means PyInstaller didn't bundle a required `pywin32` module. Rebuild with the hidden imports explicitly included:

pyinstaller --hidden-import=win32timezone --hidden-import=win32com main.py


Alternatively, add them directly to the `hiddenimports` list in `ZebraLabelPrinter.spec`.

### Printer-specific DLLs

If the app communicates with the Zebra printer through a vendor SDK or driver DLL, make sure those files are included in the `.spec` file's `datas` list so they get bundled into the executable. Missing printer DLLs will cause connection/communication failures even if the app itself launches correctly.

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