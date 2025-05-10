#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri May  9 19:30:31 2025

@author: ludvikborgen
"""

import streamlit as st
from datetime import date, datetime
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from gspread_formatting import *

# --- Google Sheets-oppsett ---
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
import json
service_account_info = json.loads(st.secrets["service_account_json"])
creds = ServiceAccountCredentials.from_json_keyfile_dict(service_account_info, scope)
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
    ],
}

st.title("✅ Ops Sjekkliste")

# --- Innholdsboks
st.markdown("""
    <div style="background-color: rgba(255, 255, 255, 0.95); padding: 20px 25px 30px 25px; border-radius: 16px;">
""", unsafe_allow_html=True)


norsk_dager = ["Mandag", "Tirsdag", "Onsdag", "Torsdag", "Fredag", "Lørdag", "Søndag"]
today = datetime.now()
sheet_name = today.strftime("%d.%m") + f" {norsk_dager[today.weekday()]}"

try:
    sheet = spreadsheet.worksheet(sheet_name)
except:
    sheet = spreadsheet.add_worksheet(title=sheet_name, rows="100", cols="10")

valgt_skift = st.radio("Velg skift", list(SJEKLISTE.keys()))

st.markdown(f"## Sjekkliste – {valgt_skift}")
st.markdown("<style>div.row-widget.stCheckbox{margin-bottom: 10px;} .stTextArea{margin-top: 40px;} .punkt-label{font-weight: bold;}</style>", unsafe_allow_html=True)

checkboxes = []
for i, punkt in enumerate(SJEKLISTE[valgt_skift]):
    cols = st.columns([0.1, 0.9])
    with cols[0]:
        checked = st.checkbox("", key=f"{valgt_skift}_{i}")
    with cols[1]:
        farge = "green" if checked else "red"
        st.markdown(f"<span style='color:{farge}'>{punkt}</span>", unsafe_allow_html=True)
    checkboxes.append((punkt, checked))

st.markdown("---")
kommentar = st.text_area("Kommentar og navn", placeholder="Skriv inn navn på skiftleder og eventuelle kommentarer her...")

if st.button("Lagre til Google Sheets", disabled=not kommentar.strip()):
    from gspread_formatting import CellFormat, Color, format_cell_range, TextFormat

    existing = sheet.get_all_values()
    first_time = not any(cell for row in existing for cell in row)

    new_data = []

    if first_time:
        for skift in ["Morgenskift", "Kveldsskift"]:
            new_data.append([])
            new_data.append([skift])
            new_data.append(["Punkt", "Status"])
            if skift == valgt_skift:
                for punkt, avhuket in checkboxes:
                    status = "Utført" if avhuket else "Ikke utført"
                    new_data.append([punkt, status])
                new_data.append([])
                new_data.append([f"Kommentar {valgt_skift}", kommentar])
            else:
                for punkt in SJEKLISTE[skift]:
                    new_data.append([punkt, "Ikke utført"])
    else:
        temp = []
        skip = False
        for row in existing:
            if row and row[0] == valgt_skift:
                skip = True
            elif skip and row == ["Punkt", "Status"]:
                continue
            elif skip and (not row or row == [""]):
                skip = False
                continue
            if not skip:
                temp.append(row)
        new_data = temp

        new_data.append([])
        new_data.append([valgt_skift])
        new_data.append(["Punkt", "Status"])
        for punkt, avhuket in checkboxes:
            status = "Utført" if avhuket else "Ikke utført"
            new_data.append([punkt, status])

        new_data.append([])
        new_data.append([f"Kommentar {valgt_skift}", kommentar])

    sheet.resize(rows=len(new_data))
    sheet.update("A1", new_data)

    # Formatering
    large_bold = CellFormat(textFormat=TextFormat(bold=True, fontSize=14))
    header_bold = CellFormat(textFormat=TextFormat(bold=True, fontSize=10))
    normal_text = CellFormat(textFormat=TextFormat(bold=False, fontSize=10))
    green_fmt = CellFormat(backgroundColor=Color(0.8, 1, 0.8))
    red_fmt = CellFormat(backgroundColor=Color(1, 0.8, 0.8))

    for i, row in enumerate(new_data):
        if row and row[0] in ("Morgenskift", "Kveldsskift"):
            format_cell_range(sheet, f"A{i+1}", large_bold)
        elif row and row == ["Punkt", "Status"]:
            format_cell_range(sheet, f"A{i+1}:B{i+1}", header_bold)
        elif len(row) >= 2:
            format_cell_range(sheet, f"A{i+1}:B{i+1}", normal_text)
            if row[1] == "Utført":
                format_cell_range(sheet, f"B{i+1}", green_fmt)
            elif row[1] == "Ikke utført":
                format_cell_range(sheet, f"B{i+1}", red_fmt)

    st.success(f"Sjekklisten for {valgt_skift} er lagret med kommentar.")




