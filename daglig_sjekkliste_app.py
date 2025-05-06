#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed May  7 00:15:00 2025

@author: ludvikborgen
"""

import streamlit as st
from datetime import date

st.set_page_config(page_title="Daglig Sjekkliste", layout="centered")

st.title("✅ Daglig Sjekkliste – Operations")
st.subheader(f"Dato: {date.today()}")

checklist_items = [
    "Flippe paller / sjekke bats",
    "Ta med deploy fra lager",
    "Planlegge rute (godkjenne med skiftleder)",
    "Sjekke at bilene har alt / sikret",
    "Poste skiftplan, rute og «use car» før lading",
    "Skiftleder gå gjennom Nivel",
    "Ringrunde og skiftleder-gruppe oppdatering",
    "Sette paller på lading når man flipper",
    "Rydde ut av bilene og bruke «use car»",
    "Gjennomgang med neste skiftleder"
]

completed = []

for item in checklist_items:
    if st.checkbox(item):
        completed.append(item)

st.write(f"✔️ {len(completed)} av {len(checklist_items)} sjekkpunkter er ferdig.")

if st.button("Lagre (ikke permanent)"):
    st.success("Takk! (Denne versjonen lagrer ikke ennå – kun demo)")