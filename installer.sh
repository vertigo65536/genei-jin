#!/bin/bash

pipx install discord || pip3 install discord --user
pipx install wikipedia || pip3 install wikipedia --user
pipx install you || pip3 install you --user
pipx install pokedex.py || pip3 install pokedex.py --user
pipx install python-dotenv || pip3 install python-dotenv --user
pipx install currencyconverter || pip3 install currencyconverter --user

FILE=.env
if [ ! -f "$FILE" ]; then
    touch .env
    printf "DISCORD_TOKEN=\nADMIN_ID=\n" > .env
fi
