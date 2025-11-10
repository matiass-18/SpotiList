import os
import sys
from dotenv import load_dotenv 
from setlist_api import obtener_mbid_artista
from setlist_scraper import obtener_setlist_promedio
from spotify_manager import SpotifyManager
import urllib.parse
import pyfiglet
from colorama import init, Fore, Style
init(autoreset=True) # Inicializa colorama para que los colores se reseteen automáticamente

def resource_path(relative_path):
    """ Obtiene la ruta absoluta al recurso, funciona para desarrollo y para PyInstaller """
    try:
        # PyInstaller crea una carpeta temporal y almacena la ruta en _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

# Cargar las variables de entorno desde la ruta correcta
dotenv_path = resource_path('.env')
load_dotenv(dotenv_path=dotenv_path)

def mostrar_banner():
    """Muestra el banner principal de la aplicación."""
    banner = pyfiglet.figlet_format("SPOTILIST", font="slant")
    print(Fore.GREEN + Style.BRIGHT + banner)
    print(Fore.GREEN + Style.BRIGHT + banner.rstrip())
    print(Fore.CYAN + Style.BRIGHT + "=" * 60)
    print(Fore.CYAN + " " * 12 + "Generador de Playlists desde Setlist.fm")
    print(Fore.CYAN + " " * 16 + "Hecho con <3 para melómanos")
    print(Fore.CYAN + Style.BRIGHT + "=" * 60 + "\n")

def ejecutar_proceso(artista, año):
    """Ejecuta el flujo completo: Scraping Setlist -> Spotify."""
    print(Fore.YELLOW + f"\n⚙️  Iniciando el proceso para '{artista}' ({año})...\n")
    
    # Obtener MBID y código único
    mbid, unique_code = obtener_mbid_artista(artista)
    if not mbid or not unique_code:
        print(Fore.RED + "\n🛑 Proceso detenido: No se pudo obtener el MBID o el código único del artista.")
        return

    # Construir la URL exactamente con el formato requerido
    url_setlist = f"https://www.setlist.fm/stats/average-setlist/{artista.lower().replace(' ', '-')}-{unique_code}.html?year={año}"
    print(f"URL generada: {url_setlist}")
    
    # 1. Obtener el Setlist Promedio usando web scraping
    setlist = obtener_setlist_promedio(url_setlist)
    
    if not setlist:
        print(Fore.RED + "\n🛑 Proceso detenido: No se pudo obtener el setlist desde la URL.")
        return

    # 2. Iniciar el Administrador de Spotify (maneja la autenticación)
    try:
        manager = SpotifyManager(artist_name=artista)
    except Exception:
        print(Fore.RED + "\n🛑 Proceso detenido: Falló la inicialización de SpotifyManager.")
        return
    
    # 3. Buscar URIs de Spotify para las canciones
    track_uris = manager.buscar_canciones(setlist)
    
    if not track_uris:
        print(Fore.RED + "\n🛑 Proceso detenido: No se encontraron URIs de Spotify para las canciones del setlist.")
        return
        
    # 4. Crear la Playlist
    playlist_url = manager.crear_playlist(track_uris, year=año)
    
    if playlist_url:
        print(Fore.GREEN + Style.BRIGHT + f"\n🎉 ¡Éxito! Tu playlist está lista aquí:")
        print(Fore.WHITE + Style.BRIGHT + playlist_url)
    else:
        print(Fore.RED + "\n⚠️ El proceso finalizó con errores en la creación de la playlist.")

if __name__ == '__main__':
    mostrar_banner()

    # Comprobación de variables de entorno
    if not os.getenv("SPOTIPY_CLIENT_ID"):
        print(Fore.RED + "🚨 ERROR: Las variables de entorno de Spotify no están configuradas.")
        print(Fore.YELLOW + "Necesitas configurar: SPOTIPY_CLIENT_ID, SPOTIPY_CLIENT_SECRET y SPOTIPY_REDIRECT_URI.")
    elif not os.getenv("SETLIST_API_KEY"):
        print(Fore.RED + "🚨 ERROR: La clave de la API de Setlist.fm (SETLIST_API_KEY) no está configurada en .env.")
    else:
        # Solicitar al usuario el nombre del artista y el año
        artista = input(Fore.MAGENTA + "Introduce el nombre del artista: " + Style.RESET_ALL)
        año = input(Fore.MAGENTA + "Introduce el año: " + Style.RESET_ALL)
        ejecutar_proceso(artista, año)