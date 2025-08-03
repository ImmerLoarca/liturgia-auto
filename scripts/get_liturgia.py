import requests
from bs4 import BeautifulSoup
from datetime import datetime
import json

hoy = datetime.now()
fecha_str = hoy.strftime('%Y/%m/%d')
fecha_legible = hoy.strftime('%d de %B de %Y')

url = f"https://www.vaticannews.va/es/evangelio-de-hoy/{fecha_str}.html"

try:
    resp = requests.get(url, timeout=10)
    resp.raise_for_status()  # Lanza error si la respuesta no es 200
    
    soup = BeautifulSoup(resp.content, "html.parser")
    
    # Elementos con manejo de errores
    titulo_element = soup.find("h1", class_="vv-article__title")
    titulo = titulo_element.get_text(strip=True) if titulo_element else "Título no disponible"
    
    cuerpo_element = soup.find("div", class_="vv-article__body")
    cuerpo = cuerpo_element.get_text("\n", strip=True) if cuerpo_element else "Contenido no disponible"
    
    papa_seccion = soup.find("section", {"id": "word-of-the-pope"})
    palabra_papa = papa_seccion.get_text("\n", strip=True) if papa_seccion else "No disponible hoy."

    liturgia = {
        "fecha": fecha_legible,
        "evangelio_titulo": titulo,
        "evangelio_contenido": cuerpo,
        "palabra_del_papa": palabra_papa
    }

    with open("liturgia.json", "w", encoding="utf-8") as f:
        json.dump(liturgia, f, ensure_ascii=False, indent=2)
        
except Exception as e:
    print(f"Error al obtener la liturgia: {str(e)}")
    # Crear un JSON con mensaje de error
    with open("liturgia.json", "w", encoding="utf-8") as f:
        json.dump({"error": str(e), "fecha": fecha_legible}, f, ensure_ascii=False, indent=2)
    raise  # Re-lanza el error para que GitHub Actions lo detecte
