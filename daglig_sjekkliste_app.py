#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed May  7 03:30:51 2025

@author: ludvikborgen
"""

import streamlit as st
from datetime import date, datetime
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# --- Google Sheets-oppsett ---
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name("service-account-sjekkliste.json", scope)
client = gspread.authorize(creds)
sheet = client.open("operation_sjekkliste_logg").sheet1  # <- må matche navnet på Google Sheet

# --- Sjekklisteinnhold ---
SJEKLISTE = {
    "Morgenskift": [
        "Flippe paller / sjekke bats",
        "Ta med deploy fra lager",
        "Planlegge rute (godkjenne med skiftleder)",
        "Sjekke at bilene har alt / sikret",
        "Poste skiftplan, rute og «use car» før lading",
        "Skiftleder gå gjennom Nivel",
        "Ringrunde og skiftleder-gruppe oppdatering",
        "Sette paller på lading når man flipper",
        "Rydde ut av bilene og bruke «use car»",
        "Gjennomgang med neste skiftleder",
    ],
    "Kveldsskift": [
        "Flippe paller / sjekke bats",
        "Ta med deploy fra lager",
        "Planlegge rute (godkjenne med skiftleder)",
        "Sjekke at bilene har alt / sikret",
        "Poste skiftplan, rute og «use car» før lading",
        "Skiftleder gå gjennom Nivel",
        "Ringrunde og skiftleder-gruppe oppdatering",
        "Sette paller på lading når man flipper",
        "Rydde ut av bilene og bruke «use car»",
        "Gjennomgang med neste skiftleder",
    ]
}

# --- Grensesnitt ---
st.set_page_config("Daglig Sjekkliste", layout="centered")
st.title("✅ Daglig Sjekkliste – Operations")

skiftvalg = st.selectbox("Velg skift", ["Morgenskift", "Kveldsskift"])
brukernavn = st.text_input("Navn på skiftleder:")
dagens_dato = str(date.today())

st.subheader(f"{dagens_dato} – {skiftvalg}")
checkboxes = {}

for punkt in SJEKLISTE[skiftvalg]:
    checkboxes[punkt] = st.checkbox(punkt)

# --- Lagre til Google Sheet ---
def finn_rad_indeks(rader, dato, skift, punkt, navn):
    for i, rad in enumerate(rader):
        try:
            if (
                len(rad) >= 6 and
                rad[0] == dato and
                rad[2] == skift and
                rad[3].strip() == punkt.strip() and
                rad[5].strip().lower() == navn.strip().lower()
            ):
                return i
        except:
            continue
    return None

# --- Lagre til Google Sheet ---
if st.button("💾 Lagre status"):
    if not brukernavn.strip():
        st.error("Vennligst skriv inn navn før du lagrer.")
    elif not any(checkboxes.values()):
        st.warning("Ingen punkter er huket av.")
    else:
        tidspunkt = datetime.now().strftime("%H:%M:%S")

        try:
            eksisterende_rader = sheet.get_all_values()
        except Exception as e:
            st.error(f"Kunne ikke hente data fra Google Sheet: {e}")
            st.stop()

        lagret = False

        for punkt, utført in checkboxes.items():
            rad_indeks = finn_rad_indeks(eksisterende_rader, dagens_dato, skiftvalg, punkt, brukernavn)

            if utført and rad_indeks is None:
                # Legg til ny rad
                try:
                    sheet.append_row([
                        dagens_dato,
                        tidspunkt,
                        skiftvalg,
                        punkt,
                        "Utført",
                        brukernavn
                    ])
                    lagret = True
                except Exception as e:
                    st.error(f"Kunne ikke lagre rad til Google Sheet: {e}")
                    st.stop()

            elif not utført and rad_indeks is not None:
                # Slett eksisterende rad
                try:
                    sheet.delete_rows(rad_indeks + 1)  # Google Sheets er 1-indeksert
                    lagret = True
                except Exception as e:
                    st.error(f"Kunne ikke slette rad fra Google Sheet: {e}")
                    st.stop()

        if lagret:
            st.success("✅ Endringer lagret i Google Sheet!")
        else:
            st.info("Ingen endringer ble gjort.")
            
            
            
            
            
            
            