# Spotilist - Generador de Playlists desde Setlist.fm

## 📝 Descripción
Una aplicación Python que crea playlists de Spotify basadas en los setlists promedio de artistas obtenidos desde Setlist.fm.

## 🚀 Características

- **Setlists Automáticos**: Obtiene el setlist promedio de un artista para un año específico
- **Integración con Spotify**: Crea automáticamente playlists personalizadas
- **Autenticación Segura**: Maneja tokens y claves API de forma segura
- **Interfaz Simple**: Línea de comandos intuitiva y fácil de usar

## 📋 Requisitos Previos

| Requisito | Versión/Detalle |
|-----------|----------------|
| Python | 3.8 o superior |
| Cuenta Spotify | Premium recomendado |
| API Key Setlist.fm | [Obtener aquí](https://www.setlist.fm/api) |
| Credenciales Spotify | Client ID y Secret |

## 🛠️ Instalación

1. **Clona el repositorio:**
   ```bash
   git clone https://github.com/tu-usuario/spotilist.git
   cd spotilist

2. **Crea el entorno virtual**
python -m venv venv_spoti
.\venv_spoti\Scripts\activate
pip install -r requirements.txt

3. **Configura el archivo .env**
SETLIST_API_KEY=tu_clave_api_de_setlist_fm
SPOTIPY_CLIENT_ID=tu_client_id_de_spotify
SPOTIPY_CLIENT_SECRET=tu_client_secret_de_spotify
SPOTIPY_REDIRECT_URI=http://localhost:8888/callback

## 📖 Uso

1. **Activa el entorno virtual**
.\venv_spoti\Scripts\activate

2. **Ejecuta la aplicación**
python main.py

3. **Sigue las instrucciones en pantalla**

Ingresa el nombre del artista
Selecciona el año deseado

## 🔧 Estructura del Proyecto
spotilist/
├── 📄 [main.py](http://_vscodecontentref_/0)              # Punto de entrada principal
├── 📄 [setlist_api.py](http://_vscodecontentref_/1)       # Manejo de API Setlist.fm
├── 📄 [setlist_scraper.py](http://_vscodecontentref_/2)   # Web scraping
├── 📄 [spotify_manager.py](http://_vscodecontentref_/3)   # Manejo de API Spotify
├── 📄 requirements.txt     # Dependencias
└── 📄 .env                 # Variables de entorno

## 📦 Dependencias Principales

Librería	    Versión	    Uso\
spotipy	        ^2.19.0	    Cliente Spotify\
requests	    ^2.26.0	    Llamadas HTTP\
beautifulsoup4	^4.9.3	    Web Scraping\
python-dotenv	^0.19.0	    Variables de entorno