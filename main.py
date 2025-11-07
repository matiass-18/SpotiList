import os
from dotenv import load_dotenv 
from setlist_api import obtener_mbid_artista
from setlist_scraper import obtener_setlist_promedio
from spotify_manager import SpotifyManager
import urllib.parse

# Cargar las variables de entorno del archivo .env
load_dotenv() 

def ejecutar_proceso(artista, año):
    """Ejecuta el flujo completo: Scraping Setlist -> Spotify."""
    print(f"\n⚙️ Iniciando el proceso para generar un setlist de {artista} del año {año}.\n")
    
    # Obtener MBID y código único
    mbid, unique_code = obtener_mbid_artista(artista)
    if not mbid or not unique_code:
        print("\n🛑 Proceso detenido: No se pudo obtener el MBID o el código único.")
        return

    # Construir la URL exactamente con el formato requerido
    url_setlist = f"https://www.setlist.fm/stats/average-setlist/{artista.lower().replace(' ', '-')}-{unique_code}.html?year={año}"
    print(f"URL generada: {url_setlist}")
    
    # 1. Obtener el Setlist Promedio usando web scraping
    setlist = obtener_setlist_promedio(url_setlist)
    
    if not setlist:
        print("\n🛑 Proceso detenido: No se pudo obtener el setlist.")
        return

    # 2. Iniciar el Administrador de Spotify (maneja la autenticación)
    try:
        manager = SpotifyManager(artist_name=artista)
    except Exception:
        print("\n🛑 Proceso detenido: Falló la inicialización de SpotifyManager.")
        return
    
    # 3. Buscar URIs de Spotify para las canciones
    track_uris = manager.buscar_canciones(setlist)
    
    if not track_uris:
        print("\n🛑 Proceso detenido: No se encontraron URIs de Spotify para las canciones.")
        return
        
    # 4. Crear la Playlist
    playlist_url = manager.crear_playlist(track_uris, year=año)
    
    if playlist_url:
        print(f"\n🎉 ¡Éxito! Tu playlist está lista aquí: {playlist_url}")
    else:
        print("\n⚠️ El proceso finalizó con errores en la creación de la playlist.")

if __name__ == '__main__':
    # Comprobación de variables de entorno
    if not os.getenv("SPOTIPY_CLIENT_ID"):
        print("🚨 ERROR: Las variables de entorno de Spotify no están configuradas.")
        print("Necesitas configurar: SPOTIPY_CLIENT_ID, SPOTIPY_CLIENT_SECRET y SPOTIPY_REDIRECT_URI.")
    elif not os.getenv("SETLIST_API_KEY"):
        print("🚨 ERROR: La clave de la API de Setlist.fm (SETLIST_API_KEY) no está configurada en .env.")
    else:
        # Solicitar al usuario el nombre del artista y el año
        artista = input("Introduce el nombre del artista: ")
        año = input("Introduce el año: ")
        ejecutar_proceso(artista, año)