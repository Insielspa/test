import logging
from configparser import ConfigParser


class ConfigExecutor:
    def apply_logging_config(self, config: ConfigParser):
        # Verificare se la sezione esiste nel file di configurazione
        if config.has_section("logging"):
            # Recuperare tutti i parametri della sezione
            parametri_della_sezione = config.items("logging")

            # Stampare i parametri
            for parametro, valore in parametri_della_sezione:
                # Configura il logger per il pacchetto "azure.iot" e sotto-pacchetti
                logging.getLogger(parametro).setLevel(valore)
