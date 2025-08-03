import requests
from bs4 import BeautifulSoup
from datetime import datetime
import json
import os

# Fecha de hoy en dos formatos: para URL y para mostrar
hoy = datetime.now()
fecha_url = hoy.strftime('%Y/%m/%d')
fecha_legible = hoy.strftime('%d de %B de %Y')

# URL de Vatican News con formato de fecha
url = f"https://www.vaticannews.va/es/evangelio-de-hoy/{fecha_url}.html"

# Encabezado para simular un navegador real
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"
}

# Asegurar que el JSON se guarda en la raíz del proyecto
ruta_salida = os.path.join(os.path.dirname(__file__), "..", "liturgia.json")

try:
    # Obtener la página
    resp = requests.get(url, headers=headers, timeout=10)
    resp.raise_for_status()  # Si no responde 200, lanza error

    # Analizar HTML
    soup = BeautifulSoup(resp.content, "html.parser")

    # Extraer título del evangelio
    titulo_element = soup.find("h1", class_="vv-article__title")
    titulo = titulo_element.get_text(strip=True) if titulo_element else "Título no disponible"

    # Extraer cuerpo del evangelio
    cuerpo_element = soup.find("div", class_="vv-article__body")
    cuerpo = cuerpo_element.get_text("\n", strip=True) if cuerpo_element else "Contenido no disponible"

    # Extraer palabra del Papa (si existe)
    papa_seccion = soup.find("section", {"id": "word-of-the-pope"})
    palabra_papa = papa_seccion.get_text("\n", strip=True) if papa_seccion else "No disponible hoy."

    # Estructura del JSON
    liturgia = {
        "fecha": fecha_legible,
        "evangelio_titulo": titulo,
        "evangelio_contenido": cuerpo,
        "palabra_del_papa": palabra_papa
    }

    # Guardar JSON en la raíz
    with open(ruta_salida, "w", encoding="utf-8") as f:
        json.dump(liturgia, f, ensure_ascii=False, indent=2)

except Exception as e:
    print(f"❌ Error al obtener la liturgia: {str(e)}")
    # Guardar archivo de error
    with open(ruta_salida, "w", encoding="utf-8") as f:
        json.dump({
            "fecha": fecha_legible,
            "error": str(e),
            "evangelio_titulo": "Título no disponible",
            "evangelio_contenido": "Contenido no disponible",
            "palabra_del_papa": "No disponible hoy."
        }, f, ensure_ascii=False, indent=2)
    raise
