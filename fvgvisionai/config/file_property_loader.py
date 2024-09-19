from typing import Dict


def load_properties_from_file(file_name: str) -> Dict[str, str]:
    """
     Carica le proprietà da un file e imposta le variabili d'ambiente corrispondenti.

     Args:
         file_name (str): Il nome del file da cui caricare le proprietà.
     """
    properties: Dict[str, str] = {}
    with open(file_name, "r") as file:
        for line in file:
            # Ignora le righe vuote o quelle che iniziano con #
            line = line.strip()
            if not line or line.startswith("#"):
                continue

            key, value = line.strip().split("=", 1)
            properties[key.strip()] = value.strip()

    return properties
