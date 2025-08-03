import requests
from bs4 import BeautifulSoup
from datetime import datetime
import json
import time

# Configuración
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
REQUEST_TIMEOUT = 20
RETRY_DELAY = 3
MAX_RETRIES = 3

def get_formatted_date():
    hoy = datetime.now()
    return {
        'url_format': hoy.strftime('%Y/%m/%d'),  # 2025/08/03 (con ceros)
        'readable_format': hoy.strftime('%d de %B de %Y')  # 03 de agosto de 2025
    }

def scrape_liturgia():
    dates = get_formatted_date()
    url = f"https://www.vaticannews.va/es/evangelio-de-hoy/{dates['url_format']}.html"
    
    headers = {
        'User-Agent': USER_AGENT,
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'es-ES,es;q=0.8',
        'Referer': 'https://www.vaticannews.va/'
    }

    for attempt in range(MAX_RETRIES):
        try:
            print(f"Intento {attempt + 1} de {MAX_RETRIES} - URL: {url}")
            resp = requests.get(url, headers=headers, timeout=REQUEST_TIMEOUT)
            
            # Verificar si la respuesta es exitosa y no es una página genérica de error
            resp.raise_for_status()
            if "404" in resp.url or "Page not found" in resp.text:
                raise requests.exceptions.RequestException("Página no encontrada (404)")
            
            soup = BeautifulSoup(resp.content, 'html.parser')
            
            # Extracción robusta con múltiples selectores posibles
            titulo = soup.find('h1').get_text(strip=True) if soup.find('h1') else f"Evangelio del día - {dates['readable_format']}"
            
            # Contenido principal - buscamos en article o div.main-content
            article = soup.find('article') or soup.find('div', class_=lambda x: x and 'content' in x.lower())
            if article:
                # Limpieza de elementos no deseados
                for element in article(['script', 'style', 'iframe', 'nav', 'footer', 'aside']):
                    element.decompose()
                contenido = article.get_text('\n', strip=True)
            else:
                contenido = "No se pudo encontrar el contenido principal."
            
            # Palabra del Papa - buscamos por ID o clases comunes
            papa_section = (soup.find('section', id='word-of-the-pope') or 
                           soup.find('div', class_=lambda x: x and 'pope' in x.lower()) or
                           soup.find('blockquote'))
            papa = papa_section.get_text('\n', strip=True) if papa_section else "No disponible hoy"
            
            return {
                "fecha": dates['readable_format'],
                "titulo": titulo,
                "contenido": contenido,
                "palabra_papa": papa,
                "fuente": url,
                "actualizado": datetime.now().isoformat(),
                "status": "success"
            }
            
        except requests.exceptions.RequestException as e:
            print(f"Error en la solicitud (Intento {attempt + 1}): {str(e)}")
            if attempt < MAX_RETRIES - 1:
                time.sleep(RETRY_DELAY)
                continue
            return {
                "error": f"No se pudo obtener los datos: {str(e)}",
                "fecha": dates['readable_format'],
                "actualizado": datetime.now().isoformat(),
                "status": "error"
            }
        except Exception as e:
            print(f"Error inesperado (Intento {attempt + 1}): {str(e)}")
            if attempt < MAX_RETRIES - 1:
                time.sleep(RETRY_DELAY)
                continue
            return {
                "error": f"Error inesperado: {str(e)}",
                "fecha": dates['readable_format'],
                "actualizado": datetime.now().isoformat(),
                "status": "error"
            }

def main():
    data = scrape_liturgia()
    
    # Guardar resultados
    with open("liturgia.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    # Terminar con error si falló
    if data.get("status") == "error":
        exit(1)

if __name__ == "__main__":
    main()
