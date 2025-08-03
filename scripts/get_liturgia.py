import requests
from bs4 import BeautifulSoup
from datetime import datetime, timezone
import pytz
import json

# Configurar zona horaria
tz = pytz.timezone('Europe/Rome')
hoy = datetime.now(timezone.utc).astimezone(tz)
fecha_str = hoy.strftime('%Y/%m/%d')
fecha_legible = hoy.strftime('%d de %B de %Y')

url = f"https://www.vaticannews.va/es/evangelio-de-hoy/{fecha_str}.html"

try:
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    print(f"Intentando acceder a: {url}")  # Log para debugging
    
    resp = requests.get(url, headers=headers, timeout=10)
    resp.raise_for_status()
    
    # Verificar si la página contiene el mensaje de "no disponible"
    if "no disponible" in resp.text.lower():
        raise ValueError("La liturgia no está disponible para esta fecha")
    
    soup = BeautifulSoup(resp.content, "html.parser")
    
    # Búsqueda más flexible del título
    titulo_element = soup.find("h1") or soup.find(class_="vv-article__title")
    titulo = titulo_element.get_text(strip=True) if titulo_element else "Título no disponible"
    
    # Búsqueda del contenido
    cuerpo_element = soup.find(class_="vv-article__body") or soup.find("article") or soup.find("div", class_="content")
    cuerpo = cuerpo_element.get_text("\n", strip=True) if cuerpo_element else "Contenido no disponible"
    
    # Búsqueda de la sección del Papa
    papa_seccion = soup.find("section", id="word-of-the-pope") or soup.find(id="pope") or soup.find(string=lambda text: "papa" in str(text).lower())
    palabra_papa = papa_seccion.get_text("\n", strip=True) if papa_seccion else "No disponible hoy."

    liturgia = {
        "fecha": fecha_legible,
        "url": url,
        "evangelio_titulo": titulo,
        "evangelio_contenido": cuerpo,
        "palabra_del_papa": palabra_papa
    }

    with open("liturgia.json", "w", encoding="utf-8") as f:
        json.dump(liturgia, f, ensure_ascii=False, indent=2)
        
except Exception as e:
    print(f"Error al obtener la liturgia: {str(e)}")
    # Crear un JSON con mensaje de error detallado
    with open("liturgia.json", "w", encoding="utf-8") as f:
        json.dump({
            "error": str(e),
            "fecha": fecha_legible,
            "url_intentada": url,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }, f, ensure_ascii=False, indent=2)
    raise  # Re-lanza el error para que GitHub Actions lo detecte
