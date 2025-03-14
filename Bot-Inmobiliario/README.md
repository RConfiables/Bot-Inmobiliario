# Bot Inmobiliario

## Descripción
El Bot Inmobiliario es una herramienta diseñada para gestionar inmuebles y documentos escaneados. Utiliza Google Drive para almacenar archivos y Google Sheets para registrar y organizar la información de los inmuebles. El bot interactúa con los usuarios a través de Telegram, permitiendo registrar, buscar, actualizar y eliminar inmuebles mediante comandos y botones.

## Funcionalidades

### Gestión de Inmuebles
- **Registrar Inmueble**: Permite registrar un nuevo inmueble en la hoja de cálculo correspondiente y crear una carpeta en Google Drive para almacenar los documentos relacionados.
- **Buscar Inmueble**: Permite buscar un inmueble en la hoja de cálculo correspondiente y obtener la información registrada.
- **Actualizar Inmueble**: Permite actualizar la información de un inmueble en la hoja de cálculo correspondiente.
- **Eliminar Inmueble**: Permite eliminar un inmueble de la hoja de cálculo correspondiente y eliminar la carpeta en Google Drive.

### Gestión de Documentos Escaneados
- **Escanear Documento**: Permite escanear un documento utilizando la cámara del celular y almacenarlo en la carpeta correspondiente en Google Drive.

## Comandos de Telegram

### Comandos de Gestión de Inmuebles
- `/new_property`: Registra un nuevo inmueble.
- `/search_property`: Busca un inmueble.
- `/update_property`: Actualiza un inmueble.
- `/delete_property`: Elimina un inmueble.

### Comandos de Gestión de Documentos Escaneados
- `/scan`: Escanea un documento y lo almacena en Google Drive.

## Botones de Telegram
El bot utiliza botones para facilitar la interacción con los usuarios. Los botones disponibles son:
- **Registrar Inmueble**
- **Buscar Inmueble**
- **Actualizar Inmueble**
- **Eliminar Inmueble**

## Configuración

### Requisitos
- Python 3.7 o superior
- Credenciales de Google (archivo `credentials.json`)
- Token de Telegram Bot

### Instalación
1. Clona el repositorio del bot en tu máquina local.
2. Instala las dependencias necesarias:
    ```bash
    pip install -r requirements.txt
    ```
3. Coloca el archivo `credentials.json` en la carpeta del proyecto.
4. Configura el token del bot de Telegram en el archivo `Bot-Inmobiliario.py`:
    ```python
    TELEGRAM_BOT_TOKEN = 'TU_TOKEN_DE_TELEGRAM'
    ```

### Ejecución
Para ejecutar el bot, utiliza el siguiente comando:
```bash
python [Bot-Inmobiliario.py](http://_vscodecontentref_/0)
```

## Interacción con n8n
El bot puede interactuar con n8n para automatizar flujos de trabajo. Puedes configurar n8n para recibir notificaciones del bot y realizar acciones adicionales, como enviar correos electrónicos o actualizar bases de datos.

## Sincronización de la Cámara del Celular
Para escanear documentos utilizando la cámara del celular, sigue estos pasos:

1. Abre la aplicación de Telegram en tu celular.
2. Envía el comando /scan al bot.
3. El bot te pedirá que tomes una foto del documento.
4. Toma la foto y envíala al bot.
5. El bot almacenará el documento escaneado en la carpeta correspondiente en Google Drive.

## Tipos de Solicitudes Soportadas
El bot soporta las siguientes solicitudes:

- Registro de nuevos inmuebles
- Búsqueda de inmuebles
- Actualización de inmuebles
- Eliminación de inmuebles
- Escaneo de documentos

## Ejemplos de Uso

### Registrar un Nuevo Inmueble
1. Envía el comando /new_property al bot.
2. El bot te pedirá la información del inmueble (tipo de anuncio, tipo de inmueble, ubicación, moneda, precio).
3. Proporciona la información solicitada.
4. El bot registrará el inmueble en la hoja de cálculo correspondiente y creará una carpeta en Google Drive.

### Buscar un Inmueble
1. Envía el comando /search_property al bot.
2. El bot te pedirá el ID del inmueble.
3. Proporciona el ID del inmueble.
4. El bot buscará el inmueble en la hoja de cálculo correspondiente y te enviará la información registrada.

### Actualizar un Inmueble
1. Envía el comando /update_property al bot.
2. El bot te pedirá el ID del inmueble y la información a actualizar.
3. Proporciona el ID del inmueble y la información a actualizar.
4. El bot actualizará la información del inmueble en la hoja de cálculo correspondiente.

### Eliminar un Inmueble
1. Envía el comando /delete_property al bot.
2. El bot te pedirá el ID del inmueble.
3. Proporciona el ID del inmueble.
4. El bot eliminará el inmueble de la hoja de cálculo correspondiente y eliminará la carpeta en Google Drive.

### Escanear un Documento
1. Envía el comando /scan al bot.
2. El bot te pedirá que tomes una foto del documento.
3. Toma la foto y envíala al bot.
4. El bot almacenará el documento escaneado en la carpeta correspondiente en Google Drive.

## Notas
- Asegúrate de tener permisos adecuados en Google Drive y Google Sheets para que el bot pueda acceder y modificar los archivos.
- Mantén el archivo credentials.json seguro y no lo compartas con terceros.

## Contacto
Para cualquier consulta o soporte, puedes contactar al desarrollador del bot a través de [correo electrónico] o [Telegram].

