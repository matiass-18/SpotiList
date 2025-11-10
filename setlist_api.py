from collections import Counter
from dotenv import load_dotenv
import os
import requests
import time
import urllib.parse

# Asegurarse de cargar las variables de entorno
load_dotenv()

# Base de la API: Incluye la versión 1.0 (para que la concatenación sea limpia)
BASE_URL = "https://api.setlist.fm/rest/1.0/"

# Modificar cómo se configuran los headers
def get_headers():
    """Obtiene los headers con la API key actualizada."""
    return {
        'Accept': 'application/json',
        'x-api-key': os.getenv('SETLIST_API_KEY'),
        'User-Agent': 'SetlistFMScript/1.0'
    }

def verificar_api_key():
    """Verifica que la clave API esté configurada."""
    api_key = os.getenv("SETLIST_API_KEY")
    if not api_key:
        print("❌ Error: SETLIST_API_KEY no está configurada en el archivo .env")
        return False
    print(f"API Key configurada: {api_key[:8]}...")
    return True

def _extract_songs_from_setlist_item(item):
    """Extrae nombres de canciones de un objeto 'setlist' retornado por la API."""
    songs = []
    sets = item.get('sets') or {}
    sets_list = sets.get('set') or []
    # 'set' puede ser dict o lista
    if isinstance(sets_list, dict):
        sets_list = [sets_list]
    for s in sets_list:
        song_entries = s.get('song') or []
        if isinstance(song_entries, dict):
            song_entries = [song_entries]
        for song in song_entries:
            name = song.get('name')
            if name:
                songs.append(name.strip())
    return songs

def obtener_mbid_artista(artist_name, max_retries=3):
    """Busca el MBID y el código único de setlist.fm del artista."""
    if not verificar_api_key():
        return None, None

    encoded_name = urllib.parse.quote(artist_name)
    url = f"{BASE_URL}search/artists?artistName={encoded_name}"

    print(f"Buscando MBID para: {artist_name}...")
    print(f"URL de búsqueda: {url}")

    retries = 0
    while retries <= max_retries:
        try:
            resp = requests.get(url, headers=get_headers(), timeout=10)
            if resp.status_code == 429:
                wait = int(resp.headers.get('Retry-After', '2'))
                print(f"429 recibida. Esperando {wait} s antes de reintentar...")
                time.sleep(wait)
                retries += 1
                continue
            resp.raise_for_status()
            data = resp.json()
            
            artists = data.get('artist', [])
            if not artists:
                print("⚠️ No se encontraron artistas en la respuesta.")
                return None, None

            # Buscar el artista que coincida exactamente con el nombre
            for artist in artists:
                if artist.get('name') == artist_name:
                    mbid = artist.get('mbid')
                    url = artist.get('url', '')
                    # Extraer el código único de la URL (ejemplo: .../setlists/interpol-2bd6982e.html)
                    if '/setlists/' in url:
                        # Extrae el código después del último guión y antes del .html
                        unique_code = url.split('/')[-1].split('.')[0].split('-')[-1]
                        if mbid and unique_code:
                            print(f"✅ MBID encontrado: {mbid}")
                            print(f"✅ Código único encontrado: {unique_code}")
                            return mbid, unique_code

            print("⚠️ No se encontró MBID o código único en los resultados.")
            return None, None

        except requests.exceptions.RequestException as e:
            print(f"❌ Error en la llamada a la API de Setlist.fm: {e}")
            retries += 1
            time.sleep(2 ** retries)
    return None, None

def calcular_setlist_promedio(artist_name, year=None, num_songs=15, max_pages=5):
    """
    Obtiene los setlists de un artista usando el MBID y calcula las canciones más frecuentes.
    """
    # Get MBID and unique code
    mbid, unique_code = obtener_mbid_artista(artist_name)
    if not mbid:
        return []

    # Use only the MBID, not the tuple
    base_url = f"{BASE_URL}artist/{mbid}/setlists"
    url = f"{base_url}?year={year}" if year else base_url
    encoded_name = urllib.parse.quote(artist_name)

    # Pre-check primera página para detectar 404/429 (con reintentos cortos)
    def _safe_get(u, retries=3):
        attempt = 0
        while attempt <= retries:
            try:
                resp = requests.get(u, headers=get_headers(), timeout=10)
                if resp.status_code == 429:
                    wait = int(resp.headers.get('Retry-After', '2'))
                    print(f"429 recibida en pre-check. Esperando {wait}s...")
                    time.sleep(wait)
                    attempt += 1
                    continue
                return resp
            except requests.exceptions.RequestException:
                attempt += 1
                time.sleep(1 + attempt)
        return None

    pre_check_url = f"{url}{'&' if '?' in url else '?'}p=1"
    pre_resp = _safe_get(pre_check_url)
    if pre_resp is None:
        print("⚠️ No se pudo completar el pre-check (errores de red). Continuando al loop principal.")
    else:
        if pre_resp.status_code == 404:
            if year:
                print(f"⚠️ No se encontraron setlists para {artist_name} en {year}. Intentando sin filtrar por año...")
                url = base_url
                pre_resp2 = _safe_get(f"{url}?p=1")
                if pre_resp2 is None or pre_resp2.status_code == 404:
                    print("⚠️ No hay setlists por MBID (con/sin año). Intentando fallback por nombre...")
                    search_setlists_url = f"{BASE_URL}search/setlists?artistName={encoded_name}"
                    sresp = _safe_get(search_setlists_url)
                    if sresp and sresp.status_code == 200:
                        print("✅ Fallback por nombre devolvió resultados; usaremos ese endpoint.")
                        url = search_setlists_url
                    else:
                        print("⚠️ Fallback por nombre no devolvió resultados. Abortando.")
                        return []
            else:
                # sin year y recibimos 404: intentar fallback por nombre
                print("⚠️ 404 por MBID sin año. Intentando fallback por nombre...")
                search_setlists_url = f"{BASE_URL}search/setlists?artistName={encoded_name}"
                sresp = _safe_get(search_setlists_url)
                if sresp and sresp.status_code == 200:
                    print("✅ Fallback por nombre devolvió resultados; usaremos ese endpoint.")
                    url = search_setlists_url
                else:
                    print("⚠️ Fallback por nombre no devolvió resultados. Abortando.")
                    return []

    # --- resto del proceso (paginación, extracción) ---
    canciones_totales = []
    pagina = 1
    total_paginas = 1  # se actualizará si la respuesta lo indica

    while pagina <= total_paginas and pagina <= max_pages:
        paginated_url = f"{url}{'&' if '?' in url else '?'}p={pagina}"
        print(f"Buscando setlists (pág. {pagina})...")
        retries = 0
        data = None
        while retries < 4:
            try:
                resp = requests.get(paginated_url, headers=get_headers(), timeout=10)
                if resp.status_code == 429:
                    wait = int(resp.headers.get('Retry-After', '2'))
                    print(f"429 Too Many Requests. Esperando {wait}s...")
                    time.sleep(wait)
                    retries += 1
                    continue
                if resp.status_code == 404:
                    print(f"❌ 404 Not Found en {paginated_url}")
                    data = None
                    break
                resp.raise_for_status()
                data = resp.json()
                break
            except requests.exceptions.RequestException as e:
                print(f"❌ Error al buscar la página {pagina} de setlists: {e}")
                retries += 1
                time.sleep(2 ** retries)
        if data is None:
            print("❌ No se pudo obtener datos de setlists para la página, deteniendo búsqueda.")
            break

        # normalizar bloque de setlists y extraer canciones
        setlists_block = data.get('setlist') or data.get('setlists') or []
        if isinstance(setlists_block, dict) and 'setlist' in setlists_block:
            setlists = setlists_block.get('setlist', [])
        elif isinstance(setlists_block, list):
            setlists = setlists_block
        else:
            setlists = []

        for s in setlists:
            canciones_totales.extend(_extract_songs_from_setlist_item(s))

        # actualizar total_paginas si está disponible
        try:
            items_per_page = int(data.get('itemsPerPage', 0))
            total_items = int(data.get('total', 0))
            if items_per_page and total_items:
                total_paginas = max(1, (total_items + items_per_page - 1) // items_per_page)
        except Exception:
            pass

        pagina += 1
        time.sleep(0.5)

    if not canciones_totales:
        print("⚠️ No se encontraron canciones en los setlists consultados.")
        return []

    frecuencias = Counter(canciones_totales)
    if num_songs is None:
        result = [song for song, _ in frecuencias.most_common()]
    else:
        result = [song for song, _ in frecuencias.most_common(num_songs)]

    print(f"✅ Setlist promedio generado ({len(result)} canciones).")
    return result