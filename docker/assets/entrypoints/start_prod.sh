#!/bin/bash

# Avvia il servizio Nginx
service nginx start

# Avvia lo script run_main.sh
cd /app
/app/run_main_env.sh