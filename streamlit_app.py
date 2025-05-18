import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload
from datetime import date
import pandas as pd
import io

st.set_page_config(page_title="Formulario Streamlit Cloud", layout="centered")

SCOPES = ['https://www.googleapis.com/auth/spreadsheets',
          'https://www.googleapis.com/auth/drive']

# Cargar credenciales desde st.secrets
creds = Credentials.from_service_account_info(st.secrets["gcp_service_account"], scopes=SCOPES)
client = gspread.authorize(creds)
sheet = client.open("hola_prueba").sheet1
drive_service = build('drive', 'v3', credentials=creds)

st.title("📝 Formulario Web con Drive y Sheets")

nombre = st.text_input("Nombre")
edad = st.text_input("Edad")
ciudad = st.text_input("Ciudad")
profesion = st.selectbox("Profesión", ["Ingeniero", "Doctor", "Profesor"])
genero = st.selectbox("Género", ["Masculino", "Femenino", "Otro"])
solicitud = st.selectbox("Tipo de Solicitud", ["Ingreso", "Actualización", "Baja"])
fecha = st.date_input("Fecha", value=date.today())
observaciones = st.text_area("Observaciones")
archivos = st.file_uploader("📎 Adjuntar archivos", type=None, accept_multiple_files=True)

if st.button("Enviar"):
    if not edad.isdigit():
        st.error("Edad debe ser un número")
    elif not all([nombre, edad, ciudad, profesion, genero, solicitud]):
        st.warning("Completa todos los campos obligatorios")
    else:
        row_count = len(sheet.get_all_values()) + 1
        registro_id = f"USR{row_count:04d}"

        # Crear carpeta y compartirla
        carpeta = drive_service.files().create(body={
            'name': registro_id,
            'mimeType': 'application/vnd.google-apps.folder'
        }, fields='id').execute()

        carpeta_id = carpeta['id']
        drive_service.permissions().create(
            SECRETS DISPONIBLES: ['gcp_service_account', 'destinatario']
            fileId=carpeta_id,
            body={'type': 'user', 'role': 'writer', 'emailAddress': st.secrets["destinatario"]},
            sendNotificationEmail=False
        ).execute()

        carpeta_link = f"https://drive.google.com/drive/folders/{carpeta_id}"

        for archivo in archivos:
            media = MediaIoBaseUpload(archivo, mimetype=archivo.type)
            file_metadata = {'name': archivo.name, 'parents': [carpeta_id]}
            drive_service.files().create(body=file_metadata, media_body=media, fields='id').execute()

        sheet.append_row([
            registro_id, str(fecha), nombre, edad, ciudad,
            profesion, genero, solicitud, observaciones, carpeta_link
        ])

        st.success("✅ Solicitud enviada correctamente")
        st.markdown(f"📂 [Ver carpeta]({carpeta_link})", unsafe_allow_html=True)
