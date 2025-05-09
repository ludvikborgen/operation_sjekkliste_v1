#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri May  9 17:00:50 2025

@author: ludvikborgen
"""

import streamlit as st
from datetime import date, datetime
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from gspread_formatting import *

# --- Google Sheets-oppsett ---
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name("service-account-sjekkliste.json", scope)
client = gspread.authorize(creds)
spreadsheet = client.open("operation_sjekkliste_logg")

# --- Sjekklisteinnhold ---
SJEKLISTE = {
    "Morgenskift": [
        "Flippe ALLE paller / sjekke bats",
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
        "Flippe ALLE paller / sjekke bats",
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

# --- Dato og ark-tittel ---
sheet_title = datetime.now().strftime("%A %d.%m").capitalize()
sheet_title = sheet_title.replace('Monday', 'Mandag').replace('Tuesday', 'Tirsdag') \
    .replace('Wednesday', 'Onsdag').replace('Thursday', 'Torsdag') \
    .replace('Friday', 'Fredag').replace('Saturday', 'Lørdag').replace('Sunday', 'Søndag')

# --- Hent eller opprett ark ---
try:
    sheet = spreadsheet.worksheet(sheet_title)
except gspread.exceptions.WorksheetNotFound:
    sheet = spreadsheet.add_worksheet(title=sheet_title, rows="100", cols="10")
    sheet.insert_row(["Dato", "Tidspunkt", "Skift", "Punkt", "Status", "Navn"], index=1)

    tidspunkt = datetime.now().strftime("%H:%M:%S")
    dagens_dato = str(date.today())

    # --- Morgenskift ---
    sheet.insert_row(["--- Morgenskift ---"], index=2)
    morgen_rader = [
        [dagens_dato, tidspunkt, "Morgenskift", punkt, "Ikke utført", ""] for punkt in SJEKLISTE["Morgenskift"]
    ]
    for i, rad in enumerate(reversed(morgen_rader)):
        sheet.insert_row(rad, index=3)

    # --- Kveldsskift ---
    antall_morgen = len(SJEKLISTE["Morgenskift"])
    kveld_start = 3 + antall_morgen + 1
    sheet.insert_row([""], index=kveld_start)
    sheet.insert_row(["--- Kveldsskift ---"], index=kveld_start + 1)
    kveld_rader = [
        [dagens_dato, tidspunkt, "Kveldsskift", punkt, "Ikke utført", ""] for punkt in SJEKLISTE["Kveldsskift"]
    ]
    for i, rad in enumerate(reversed(kveld_rader)):
        sheet.insert_row(rad, index=kveld_start + 2)

    bold_fmt = cellFormat(
        textFormat=textFormat(bold=True),
        backgroundColor=color(0.9, 0.9, 0.9)
    )
    format_cell_range(sheet, "A1:F1", bold_fmt)
    format_cell_range(sheet, f"A2", bold_fmt)
    format_cell_range(sheet, f"A{kveld_start + 1}", bold_fmt)

# --- Streamlit-grensesnitt ---
st.set_page_config("Daglig Sjekkliste", layout="centered")
st.title("✅ Daglig Sjekkliste – Operations")

skiftvalg = st.selectbox("Velg skift", ["Morgenskift", "Kveldsskift"])
brukernavn = st.text_input("Navn på skiftleder:")
dagens_dato = str(date.today())
st.subheader(f"{dagens_dato} – {skiftvalg}")
checkboxes = {punkt: st.checkbox(punkt) for punkt in SJEKLISTE[skiftvalg]}

# --- Hjelpefunksjon ---
def finn_rad_indeks(rader, dato, skift, punkt, navn):
    navn = navn.strip().lower()
    punkt = punkt.strip().lower()
    for i, rad in enumerate(rader):
        try:
            rad_dato = rad[0].strip()
            rad_skift = rad[2].strip()
            rad_punkt = rad[3].strip().lower()
            rad_navn = rad[5].strip().lower()
            if (
                rad_dato == dato and
                rad_skift == skift and
                rad_punkt == punkt and
                (rad_navn == navn or rad_navn == "")
            ):
                return i
        except:
            continue
    return None

# --- Lagre-knappen ---
if st.button("💾 Lagre"):
    if not brukernavn.strip():
        st.error("Vennligst skriv inn navn før du lagrer.")
    else:
        tidspunkt = datetime.now().strftime("%H:%M:%S")

        try:
            eksisterende_rader = sheet.get_all_values()
        except Exception as e:
            st.error(f"Kunne ikke hente data fra Google Sheet: {e}")
            st.stop()

        lagret = False

        for punkt in SJEKLISTE[skiftvalg]:
            status = "Utført" if checkboxes[punkt] else "Ikke utført"
            rad_indeks = finn_rad_indeks(eksisterende_rader, dagens_dato, skiftvalg, punkt, brukernavn)

            if rad_indeks is not None:
                try:
                    sheet.update(f"E{rad_indeks+1}", [[status]])
                    if eksisterende_rader[rad_indeks][5].strip() == "":
                        sheet.update(f"F{rad_indeks+1}", [[brukernavn]])
                    lagret = True
                except Exception as e:
                    st.error(f"Kunne ikke oppdatere rad: {e}")
                    st.stop()
            else:
                st.warning(f"Punktet '{punkt}' ble ikke funnet og ble ikke lagt til på nytt.")

        if lagret:
            st.success("✅ Oppdatering lagret!")
        else:
            st.info("Ingen endringer ble gjort.")