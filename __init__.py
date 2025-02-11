import importlib
import os
import json

def install_gcp_storage():
    print(f"Checking for google-cloud-storage installation..")
    try:
        importlib.import_module("google-cloud-storage")
    except ImportError:
        print("Error: google-cloud-storage not found. Installing..")
        import pip
        pip.main(["install", "google-cloud-storage"])

from .gcp_storage import NODE_CLASS_MAPPINGS
from .gcp_storage import NODE_DISPLAY_NAME_MAPPINGS
__all__ = ['NODE_CLASS_MAPPINGS', 'NODE_DISPLAY_NAME_MAPPINGS']