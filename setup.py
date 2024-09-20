import configparser
import os
import requests
import argparse
from tqdm import tqdm
from urllib.parse import urlparse


# Funzione per scaricare un file da un URL e salvarlo in un percorso locale con una barra di avanzamento
def download_file(url, local_path, platform_name):
    # Estrai il nome del file dall'URL
    file_name = os.path.basename(urlparse(url).path)

    # Costruisci il percorso completo dove salvare il file
    full_local_path = os.path.join(local_path, file_name)

    # Crea la directory in modo ricorsivo se non esiste
    os.makedirs(os.path.dirname(full_local_path), exist_ok=True)

    # Scarica il file con una barra di avanzamento
    response = requests.get(url, stream=True)
    response.raise_for_status()  # Verifica se la richiesta ha avuto successo
    total_size = int(response.headers.get('content-length', 0))  # Ottieni la dimensione del file

    # Scarica il file con una barra di avanzamento
    with open(full_local_path, 'wb') as file, tqdm(
            desc=f"Downloading {file_name}",
            total=total_size,
            unit='B',
            unit_scale=True,
            unit_divisor=1024,
            ncols=100,
            leave=False,
    ) as bar:
        for chunk in response.iter_content(chunk_size=1024):
            file.write(chunk)
            bar.update(len(chunk))

    # Una volta completato il download, mostra un messaggio finale
    print(f"Downloaded {file_name} to {full_local_path}")

    # Crea il file {platform_name}_assets.txt nella directory del file scaricato
    assets_file_path = os.path.join(os.path.dirname(full_local_path), f"{platform_name}_assets.txt")
    with open(assets_file_path, 'a') as assets_file:  # Usa 'a' per creare il file se non esiste
        pass  # Il comando 'pass' serve solo per creare il file senza scrivere nulla
    print(f"Created assets file: {assets_file_path}")


# Funzione per verificare se la piattaforma ha già gli asset scaricati
def check_assets_exists(platform_name, config):
    i = 1
    while True:
        file_path = config.get(platform_name, f'file{i}_path', fallback=None)
        if not file_path:
            break

        # Percorso del file assets per il controllo
        assets_file_path = os.path.join(file_path, f"{platform_name}_assets.txt")

        # Controlla se il file assets esiste
        if os.path.exists(assets_file_path):
            print(f"Skipping download for {platform_name}. Assets file already exists: {assets_file_path}")
            return True

        i += 1

    return False


# Funzione principale
def main(selected_platform=None):
    # Leggi il file di configurazione
    config = configparser.ConfigParser()
    config.read('setup.ini')  # Modificato per usare setup.ini

    # Lista delle piattaforme disponibili
    platforms = config.sections()
    if not platforms:
        print("No platforms found in the configuration file.")
        return

    # Se la piattaforma non è stata specificata da CLI, chiedi all'utente di selezionarla
    if not selected_platform:
        print("Available platforms:")
        for idx, platform in enumerate(platforms, start=1):
            print(f"{idx}. {platform}")

        # Chiedi all'utente di selezionare una piattaforma
        choice = int(input("Select a platform (number): ")) - 1
        if choice < 0 or choice >= len(platforms):
            print("Invalid choice.")
            return
        selected_platform = platforms[choice]
    else:
        # Verifica che la piattaforma specificata da CLI esista nel file di configurazione
        if selected_platform not in platforms:
            print(f"Platform '{selected_platform}' not found in the configuration file.")
            return

    print(f"Selected platform: {selected_platform}")

    # Controlla se il file assets esiste, se sì, salta il download
    if check_assets_exists(selected_platform, config):
        return

    # Procedi con il download dei file per la piattaforma selezionata
    i = 1
    while True:
        file_url = config.get(selected_platform, f'file{i}_url', fallback=None)
        file_path = config.get(selected_platform, f'file{i}_path', fallback=None)

        if not file_url or not file_path:
            break  # Esce dal ciclo se non ci sono più file

        try:
            download_file(file_url, file_path, selected_platform)
        except Exception as e:
            print(f"Error downloading from {file_url}: {e}")

        i += 1


if __name__ == "__main__":
    # Configura l'argomento opzionale per la piattaforma
    parser = argparse.ArgumentParser(description="Download assets for specified platform.")
    parser.add_argument('--platform', type=str, help="Specify the platform to download assets for.")

    # Parsare gli argomenti da linea di comando
    args = parser.parse_args()

    # Avvia il programma passando l'argomento della piattaforma se fornito
    main(args.platform)
