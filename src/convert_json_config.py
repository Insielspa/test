from fvgvisionai.config.json_converter.convert_config_json_2_env import convert_config_json_2_env

if __name__ == "__main__":
    # Percorso del file di configurazione
    CONFIG_WEB_JSON_FILENAME = './config-web.json'
    ENV_WEB_FILENAME = './.env-main-web'
    convert_config_json_2_env(CONFIG_WEB_JSON_FILENAME, ENV_WEB_FILENAME)