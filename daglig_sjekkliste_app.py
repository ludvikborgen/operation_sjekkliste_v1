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
import json

# --- Google Sheets-oppsett ---
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
service_account_info = json.loads(st.secrets["service_account_json"])
creds = ServiceAccountCredentials.from_json_keyfile_dict(service_account_info, scope)
client = gspread.authorize(creds)
spreadsheet = client.open("operation_sjekkliste_logg")

# --- Sjekklisteinnhold ---
SJEKLISTE = {
    "Morgenskift": [
        "Pass på at ALLE paller er flippet",
        "Sørge for at Depolys blir tatt med",
        "Godkjenne ruter",
        "Sjekke at bilene har alt / sikret og at propper i batteri er plugget i",
        "Skrive skiftplan og følge opp at ruter og «use car» blir sendt",
        "Skiftleder gå gjennom Nivel",
        "Ringrunde og skiftleder-gruppe oppdatering",
        "Sette paller på lading når man flipper",
        "Rydde ut av bilene",
        "Gjennomgang med neste skiftleder",
    ],
    "Kveldsskift": [
        "Pass på at ALLE paller er flippet",
        "Sørge for at Depolys blir tatt med",
        "Godkjenne ruter",
        "Sjekke at bilene har alt / sikret og at propper i batteri er plugget i",
        "Skrive skiftplan og følge opp at ruter og «use car» blir sendt",
        "Skiftleder gå gjennom Nivel",
        "Ringrunde og skiftleder-gruppe oppdatering",
        "Sette paller på lading når man flipper",
        "Rydde ut av bilene",
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

sjekkliste = SJEKLISTE[valgt_skift]
checkboxes = []

# --- Hent eksisterende status fra Google Sheets hvis tilgjengelig
existing_data = sheet.get_all_values()
start_index = None
status_dict = {}

for i, row in enumerate(existing_data):
    if row and row[0] == valgt_skift:
        start_index = i
        break

if start_index is not None:
    for row in existing_data[start_index+2:]:
        if not row or row[0] == "" or row[0].startswith("Kommentar"):
            break
        punkt = row[0]
        status = row[1] if len(row) > 1 else "Ikke utført"
        status_dict[punkt] = status

# --- Vis sjekkbokser basert på tidligere status
for punkt in sjekkliste:
    default_checked = status_dict.get(punkt, "Ikke utført") == "Utført"
    checked = st.checkbox(punkt, key=punkt, value=default_checked)
    farge = "green" if checked else "red"
    checkboxes.append((punkt, checked))

    st.markdown(f"""
        <style>
        label[for=\"{punkt}\"] > div:first-child {{
            display: flex;
            align-items: center;
            gap: 12px;
        }}
        label[for=\"{punkt}\"] span {{
            color: {farge} !important;
            font-size: 18px;
        }}
        </style>
    """, unsafe_allow_html=True)

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

# --- Lukk innholdsboksen
st.markdown("</div>", unsafe_allow_html=True)






