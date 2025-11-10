# spotify_manager.py

import os
import spotipy
from spotipy.oauth2 import SpotifyOAuth

# --- Configuración de Credenciales (Deben estar en el entorno) ---
# Necesitas: SPOTIPY_CLIENT_ID, SPOTIPY_CLIENT_SECRET, SPOTIPY_REDIRECT_URI

# Define los permisos (scopes) que necesita tu aplicación
SCOPE = "playlist-modify-public playlist-modify-private"

class SpotifyManager:
    def __init__(self, artist_name):
        self.artist_name = artist_name
        self.sp = self._authenticate()
        self.user_id = self.sp.current_user()['id']

    def _authenticate(self):
        """Inicializa y autentica el objeto Spotipy."""
        print("🔑 Autenticando con Spotify...")
        try:
            sp = spotipy.Spotify(auth_manager=SpotifyOAuth(scope=SCOPE))
            print("✅ Autenticación exitosa.")
            return sp
        except Exception as e:
            print(f"❌ Error de autenticación de Spotify: {e}")
            print("Asegúrate de que las variables de entorno (ID, Secret, URI) estén configuradas.")
            raise

    def buscar_canciones(self, setlist):
        """Busca el URI de cada canción en Spotify."""
        print(f"\n🔍 Buscando URIs para {len(setlist)} canciones...")
        track_uris = []
        for song_title in setlist:
            # Búsqueda combinada: canción y artista para mayor precisión
            query = f'track:{song_title} artist:{self.artist_name}'
            result = self.sp.search(q=query, type='track', limit=1)
            
            if result['tracks']['items']:
                uri = result['tracks']['items'][0]['uri']
                track_uris.append(uri)
                # print(f"   [ENCONTRADO] {song_title}") # Descomentar para ver el progreso
            else:
                print(f"   [NO ENCONTRADO] Saltando '{song_title}'")
        
        print(f"✅ URIs encontradas: {len(track_uris)}")
        return track_uris

    def crear_playlist(self, track_uris, year=None):
        """Crea una nueva playlist y añade las canciones."""
        year_str = f" ({year})" if year else ""
        playlist_name = f"Setlist Promedio: {self.artist_name}{year_str}"
        
        print(f"\n🎧 Creando playlist: '{playlist_name}'...")
        
        try:
            # 1. Crear la playlist
            playlist = self.sp.user_playlist_create(
                user=self.user_id, 
                name=playlist_name, 
                public=False, # Recomendado empezar como privada
                description=f'Setlist promedio de {self.artist_name} extraído de setlist.fm'
            )
            playlist_id = playlist['id']
            print(f"✅ Playlist creada: {playlist['external_urls']['spotify']}")

            # 2. Añadir las canciones (hasta 100 por solicitud)
            if track_uris:
                self.sp.playlist_add_items(playlist_id=playlist_id, items=track_uris)
                print(f"✅ {len(track_uris)} canciones añadidas con éxito.")
            else:
                print("⚠️ No hay URIs de canciones para añadir.")
                
            return playlist['external_urls']['spotify']
            
        except Exception as e:
            print(f"❌ Error al crear/modificar la playlist: {e}")
            return None