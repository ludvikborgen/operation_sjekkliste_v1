#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed May  7 03:13:30 2025

@author: ludvikborgen
"""

import gspread
from oauth2client.service_account import ServiceAccountCredentials

# Oppsett
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name("service-account-sjekkliste.json", scope)
client = gspread.authorize(creds)

# Test: Åpne ark og legg inn en rad
sheet = client.open("operation_sjekkliste_logg").sheet1  # <- må matche navnet ditt nøyaktig
sheet.append_row(["TEST", "Morgenskift", "Testpunkt", "Utført"])