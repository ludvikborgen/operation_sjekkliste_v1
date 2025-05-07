#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed May  7 01:58:29 2025

@author: ludvikborgen
"""

import streamlit as st
from datetime import date
import json
import os

# --- Konfigurasjon ---
FILENAME = "sjekkliste_status.json"

# --- Sjekklisteinnhold ---
SJEKLISTE = {
    "Morgenskift": [
        "Flippe paller / sjekke bats",
        "Ta med deploy fra lager",
        "Planlegge rute (godkjenne med skiftleder)",
        "Sjekke at bilene har alt / sikret",
        "Poste skiftplan, rute og «use car» før lading"
        "Skiftleder gå gjennom Nivel",
        "Ringrunde og skiftleder-gruppe oppdatering",
        "Sette paller på lading når man flipper",
        "Rydde ut av bilene og bruke «use car»",
        "Gjennomgang med neste skiftleder"
    ],
    "Kveldsskift": [
        "Flippe paller / sjekke bats",
        "Ta med deploy fra lager",
        "Planlegge rute (godkjenne med skiftleder)",
        "Sjekke at bilene har alt / sikret",
        "Poste skiftplan, rute og «use car» før lading"
        "Skiftleder gå gjennom Nivel",
        "Ringrunde og skiftleder-gruppe oppdatering",
        "Sette paller på lading når man flipper",
        "Rydde ut av bilene og bruke «use car»",
        "Gjennomgang med neste skiftleder"
    ]
}

# --- Last eller lagre JSON-status ---
def load_status():
    if not os.path.exists(FILENAME):
        return {}
    with open(FILENAME, "r") as f:
        return json.load(f)

def save_status(data):
    with open(FILENAME, "w") as f:
        json.dump(data, f)

# --- App start ---
st.set_page_config("Daglig Sjekkliste", layout="centered")
st.title("✅ Daglig Sjekkliste – Operations")

# Velg skift
skiftvalg = st.selectbox("Velg skift", ["Morgenskift", "Kveldsskift"])
dagens_dato = str(date.today())

# Last lagret status
status_data = load_status()
dagens_status = status_data.get(dagens_dato, {}).get(skiftvalg, {})

# Vis sjekkliste
st.subheader(f"Dato: {dagens_dato} – {skiftvalg}")

checkboxes = []
for punkt in SJEKLISTE[skiftvalg]:
    checked = dagens_status.get(punkt, False)
    val = st.checkbox(punkt, value=checked)
    checkboxes.append((punkt, val))

# Lagre status
if st.button("💾 Lagre status"):
    # Oppdater statusdata
    if dagens_dato not in status_data:
        status_data[dagens_dato] = {}
    status_data[dagens_dato][skiftvalg] = {punkt: val for punkt, val in checkboxes}
    save_status(status_data)
    st.success("Status lagret!")