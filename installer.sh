#!/bin/bash

pip install discord --user || pip3 install discord --user
pip install wikipedia --user || pip3 install wikipedia --user
pip install you --user || pip3 install you --user
pip install pokedex.py --user || pip3 install pokedex.py --user
pip install python-dotenv --user || pip3 install python-dotenv --user
pip install --user currencyconverter || pip3 install currencyconverter --user
pip instal --user brickfront || pip3 install --user brickfront

FILE=.env
if [ ! -f "$FILE" ]; then
    touch .env
    printf "DISCORD_TOKEN=\nADMIN_ID=\n" > .env
fi
