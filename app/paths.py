import sys
import os


def resource_path(relative_path):
    """Fichiers embarqués en lecture seule dans l'exe (ex: logo)."""
    if hasattr(sys, "_MEIPASS"):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)


def external_path(relative_path):
    """Fichiers éditables, à côté de l'exe (config, templates)."""
    if getattr(sys, "frozen", False):
        base = os.path.dirname(sys.executable)
    else:
        base = os.path.abspath(".")
    return os.path.join(base, relative_path)