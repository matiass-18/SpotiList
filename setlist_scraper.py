# setlist_scraper.py

import requests
from bs4 import BeautifulSoup

def obtener_setlist_promedio(url_setlist):
    """
    Extrae los títulos de las canciones de la página de setlist.fm usando Web Scraping.
    """
    print("🚀 Iniciando el scraping de setlist.fm...")
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    setlist = []
    try:
        response = requests.get(url_setlist, headers=headers)
        response.raise_for_status()

        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Selector CSS basado en la inspección: ol.songsList > li.song
        song_containers = soup.select('ol.songsList > li.song')

        print(f"✅ Encontradas {len(song_containers)} posibles canciones.")
        
        for container in song_containers:
            # Intenta encontrar el enlace del título de la canción si tiene una clase específica.
            # (A menudo el título de la canción es un enlace a otra página dentro de setlist.fm)
            title_element = container.find('a', href=True) # Buscamos cualquier <a> con un href

            if title_element and title_element.text.strip():
                title = title_element.text.strip()
                setlist.append(title)
            else:
                # Caso de reserva: limpiar el texto del contenedor
                title = container.text.strip().split('\n')[0].strip()
                if title and not title.isdigit():
                    setlist.append(title)
        
        print(f"🎶 Setlist final extraído con {len(setlist)} canciones.")
        return setlist
    
    except requests.exceptions.RequestException as e:
        print(f"❌ Error HTTP/Conexión: {e}")
        return []
    except Exception as e:
        print(f"❌ Error inesperado en el scraping: {e}")
        return []

if __name__ == '__main__':
    # Ejemplo de prueba local para este módulo (puedes reemplazar la URL)
    url_test = "https://www.setlist.fm/stats/average-setlist/katatonia-73d6e253.html?year=2025"
    setlist_prueba = obtener_setlist_promedio(url_test)
    if setlist_prueba:
        print("\nPrueba de Setlist:")
        for i, song in enumerate(setlist_prueba, 1):
            print(f"{i}. {song}")