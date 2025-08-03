import requests
from bs4 import BeautifulSoup
from datetime import datetime
import json

# Fecha en el formato requerido por el URL
hoy = datetime.now()
fecha_str = hoy.strftime('%Y/%m/%d')
fecha_legible = hoy.strftime('%d de %B de %Y')

url = f"https://www.vaticannews.va/es/evangelio-de-hoy/{fecha_str}.html"

try:
    resp = requests.get(url, timeout=10)
    resp.raise_for_status()

    soup = BeautifulSoup(resp.content, "html.parser")

    # Obtener el título del evangelio
    titulo_element = soup.select_one("div.vv-article__content h1")
    titulo = titulo_element.get_text(strip=True) if titulo_element else "Título no disponible"

    # Obtener el cuerpo del evangelio
    cuerpo_element = soup.select_one("div.vv-article__body")
    cuerpo = cuerpo_element.get_text("\n", strip=True) if cuerpo_element else "Contenido no disponible"

    # Buscar "Palabra del Papa" si está disponible (como subtítulo o sección posterior)
    palabra_papa = "No disponible hoy."
    for h2 in soup.select("div.vv-article__body h2"):
        if "Palabra del Papa" in h2.get_text(strip=True):
            parrafo = h2.find_next_sibling("p")
            palabra_papa = parrafo.get_text(strip=True) if parrafo else "No disponible hoy."
            break

    # Crear el JSON
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
    with open("liturgia.json", "w", encoding="utf-8") as f:
        json.dump({"error": str(e), "fecha": fecha_legible}, f, ensure_ascii=False, indent=2)
    raise
