import os
import logging
import pytesseract
import pandas as pd
import gspread
from datetime import datetime
from pdf2image import convert_from_path
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.oauth2.service_account import Credentials
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackQueryHandler, ContextTypes
from docx import Document

# Configuración de logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Configuraciones
TELEGRAM_BOT_TOKEN = 'TU_TOKEN_DE_TELEGRAM'
GOOGLE_CREDENTIALS_FILE = 'credentials.json'  # Archivo de credenciales de Google
BOT_INMOBILIRIO_ID = '1xJVpeyldBBFZeV6Uh-XlNDYEgP3QyG0U'  # ID de la carpeta principal del bot
GESTION_SCANNER_ID = "1lMZjqc5XWUuJqHperY1uXQTqUuCCilEw"  # ID de la carpeta Principal de Gestión de Scanner de Datos
GESTION_DE_INMUEBLES_EN_PROCESO_DE_ENTRADA_ID = "1cZQGYXx6Md_3PWKvrO8_83bZHaQ9OTQa"  # ID de la carpeta Principal de Gestión de Inmuebles en Proceso de Entrada

# IDs de las subcarpetas de Gestión de Inmuebles en Proceso de Entrada
TIPO_DE_ANUNCIO_ID = "1HwlP89dicq_1Z42OuW1oB1igMIVL9W6P"
AIRBNB_ID = "12VPMEe0bY8r-4k0AZSTcZPJCQ8aFDOZc"
TIPO_DE_INMUEBLE_ID = "1y09TABJeA8bR0KJe7PkkdQJ2CYq2uuMd"
APARTAMENTOS_ID = "1pV7j72C28NPg232jFd02r3RCs5iHF6sE"
CASA_DE_PLAYA_ID = "1SkXAgVfCZ2agjkUG8Erj2lMa2x6v8W_U"
CASAS_ID = "1BERysfRNNyjPQ20ui1MxXFG-pkifBw-X"
CASAS_DE_LUJOS_ID = "15YND7e6nVixeP67J46lggfLTtBN57kTz"
CLUB_ID = "1MSN2OUhuk52gbd5ppbYUPuAdlbqMkFGl"
EDIFICIOS_ID = "1SeFPPZUfGkFdxwkn5r13YZrDb1WswTU6"
FINCA_ID = "126EL_RcuOdw1Jm1z0YmZrv0jKleXpGbx"
LOCAL_COMERCIAL_ID = "1vkDbzwSZjpnlTisM3zEV0xiHAG6w-K-x"
OFICINAS_ID = "1u0w7WKqD1_Bpfuni51oaSSyD8HJux1KA"
PENTH_HOUSE_ID = "1vzdZ3mC8F0ZioDl3YOD1gTPmLzc0gnSQ"
SIN_CATEGORIAS_ID = "1XLMD4IOkAL8xeye8SbyuKOBAyPNzjXZq"
SOLARES_ID = "1gSYtNzK2DezpV2Tu6wIUPxOVMS376ADI"
VILLAS_ID = "1V9j99jdKFCfIyhvrNx5uSuUrA34CrPIc"

SE_ALQUILA_ID = "1eFWKxoHlE9a_R80Wx7RJtAWYG2cKYBL-"
SE_VENDE_ID = "1XXayfiqKf01nUveR3v_AO5pVmav79FRO"

# Inicializar servicios de Google Drive y Sheets
creds = Credentials.from_service_account_file(GOOGLE_CREDENTIALS_FILE, scopes=[
    "https://www.googleapis.com/auth/drive",
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/documents"
])
drive_service = build("drive", "v3", credentials=creds)
gc = gspread.authorize(creds)

# Configuración de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_or_create_folder(folder_name, parent_id):
    """Busca una carpeta en Google Drive, si no existe la crea."""
    query = f"name='{folder_name}' and mimeType='application/vnd.google-apps.folder' and '{parent_id}' in parents"
    results = drive_service.files().list(q=query, fields="files(id)").execute()
    folders = results.get("files", [])

    if folders:
        return folders[0]['id']  # La carpeta ya existe, devolver su ID

    # Si no existe, crearla
    file_metadata = {
        "name": folder_name,
        "mimeType": "application/vnd.google-apps.folder",
        "parents": [parent_id]
    }
    folder = drive_service.files().create(body=file_metadata, fields="id").execute()
    return folder.get("id")  # Devolver la nueva carpeta creada

def create_property_folder(property_name, tipo_anuncio, tipo_inmueble):
    """Crea una nueva carpeta para un inmueble siguiendo la jerarquía establecida."""
    tipo_anuncio_id = get_or_create_folder(tipo_anuncio, GESTION_DE_INMUEBLES_EN_PROCESO_DE_ENTRADA_ID)
    tipo_inmueble_id = get_or_create_folder(tipo_inmueble, tipo_anuncio_id)
    property_folder_id = get_or_create_folder(property_name, tipo_inmueble_id)
    return property_folder_id

def create_entry_folder(year, month, category, property_name):
    """Crea una carpeta para la gestión de entrada de inmuebles (Año > Mes > Categoría > Inmueble)."""
    year_id = get_or_create_folder(year, GESTION_SCANNER_ID)
    month_id = get_or_create_folder(month, year_id)
    category_id = get_or_create_folder(category, month_id)
    property_folder_id = get_or_create_folder(property_name, category_id)
    return property_folder_id

def add_property_to_sheet(sheet_url, worksheet_name, property_data):
    """Agrega un nuevo registro a la hoja de cálculo especificada."""
    sheet = gc.open_by_url(sheet_url)
    worksheet = sheet.worksheet(worksheet_name)
    worksheet.append_row(property_data)

async def handle_new_property(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Maneja la creación de un nuevo inmueble."""
    text = update.message.text
    # Identificar palabras clave
    tipo_anuncio = "SE VENDE"  # Extraído del mensaje
    tipo_inmueble = "CASA"  # Extraído del mensaje
    ubicacion = "Santo Domingo"  # Ejemplo de ubicación
    moneda = "USD$"  # Ejemplo de moneda
    precio = "200000"  # Ejemplo de precio

    today = datetime.today()
    year = str(today.year)
    month = today.strftime("%B")

    property_name = f"Casa en Santo Domingo - {year}"
    property_folder_id = create_entry_folder(year, month, "Sin Categorizar", property_name)
    property_folder_link = f"https://drive.google.com/drive/folders/{property_folder_id}"

    # Datos del inmueble a agregar a la hoja de cálculo
    property_data = [
        tipo_anuncio, property_name, tipo_inmueble, ubicacion, moneda, precio, property_folder_link,
        # URLs de imágenes y otros datos
    ]

    add_property_to_sheet("https://docs.google.com/spreadsheets/d/16xkF68bzC0Qc6WNajTpN2B6WgJVKWvZwsJM7bGbKMS0/edit?usp=sharing", "CASAS", property_data)

    await update.message.reply_text(
        f"✅ Inmueble registrado:\n📂 {property_name}\n"
        f"🔗 [Ver en Drive]({property_folder_link})",
        disable_web_page_preview=True
    )

async def handle_delete_property(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Maneja la eliminación de un inmueble."""
    text = update.message.text
    # Identificar palabras clave y buscar el ID del inmueble
    property_id = "ID_DEL_INMUEBLE"  # Extraído del mensaje
    worksheet = gc.open_by_url("https://docs.google.com/spreadsheets/d/16xkF68bzC0Qc6WNajTpN2B6WgJVKWvZwsJM7bGbKMS0/edit?usp=sharing").worksheet("SOLARES")
    cell = worksheet.find(property_id)
    if cell:
        worksheet.delete_row(cell.row)
        await update.message.reply_text(f"✅ Inmueble eliminado: {property_id}")
    else:
        await update.message.reply_text(f"❌ Inmueble no encontrado: {property_id}")

async def handle_search_property(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Maneja la búsqueda de un inmueble."""
    text = update.message.text
    # Identificar palabras clave y buscar el ID del inmueble
    property_id = "ID_DEL_INMUEBLE"  # Extraído del mensaje
    worksheet = gc.open_by_url("https://docs.google.com/spreadsheets/d/16xkF68bzC0Qc6WNajTpN2B6WgJVKWvZwsJM7bGbKMS0/edit?usp=sharing").worksheet("CASAS DE LUJO")
    cell = worksheet.find(property_id)
    if cell:
        property_data = worksheet.row_values(cell.row)
        await update.message.reply_text(f"✅ Inmueble encontrado: {property_data}")
    else:
        await update.message.reply_text(f"❌ Inmueble no encontrado: {property_id}")

async def handle_update_property(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Maneja la actualización de un inmueble."""
    text = update.message.text
    # Identificar palabras clave y buscar el ID del inmueble
    property_id = "ID_DEL_INMUEBLE"  # Extraído del mensaje
    worksheet = gc.open_by_url("https://docs.google.com/spreadsheets/d/16xkF68bzC0Qc6WNajTpN2B6WgJVKWvZwsJM7bGbKMS0/edit?usp=sharing").worksheet("SOLARES")
    cell = worksheet.find(property_id)
    if cell:
        # Actualizar los datos del inmueble
        worksheet.update_cell(cell.row, 2, "Nuevo Valor")  # Ejemplo de actualización
        await update.message.reply_text(f"✅ Inmueble actualizado: {property_id}")
    else:
        await update.message.reply_text(f"❌ Inmueble no encontrado: {property_id}")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Maneja mensajes sin una solicitud clara."""
    text = update.message.text
    keyboard = [
        [InlineKeyboardButton("Registrar Inmueble", callback_data='new_property')],
        [InlineKeyboardButton("Eliminar Inmueble", callback_data='delete_property')],
        [InlineKeyboardButton("Buscar Inmueble", callback_data='search_property')],
        [InlineKeyboardButton("Actualizar Inmueble", callback_data='update_property')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text('Seleccione una acción:', reply_markup=reply_markup)

async def button(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Maneja las acciones de los botones."""
    query = update.callback_query
    await query.answer()
    if query.data == 'new_property':
        await handle_new_property(update, context)
    elif query.data == 'delete_property':
        await handle_delete_property(update, context)
    elif query.data == 'search_property':
        await handle_search_property(update, context)
    elif query.data == 'update_property':
        await handle_update_property(update, context)

def main() -> None:
    """Inicia el bot."""
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    application.add_handler(CallbackQueryHandler(button))
    application.add_handler(CommandHandler("new_property", handle_new_property))
    application.add_handler(CommandHandler("delete_property", handle_delete_property))
    application.add_handler(CommandHandler("search_property", handle_search_property))
    application.add_handler(CommandHandler("update_property", handle_update_property))
    application.run_polling()

if __name__ == "__main__":
    main()