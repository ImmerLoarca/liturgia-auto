import requests
from bs4 import BeautifulSoup
from datetime import datetime
import json

# Formato de fecha para URL y para mostrar
hoy = datetime.now()
fecha_url = hoy.strftime('%Y/%m/%d')  # Para construir la URL
fecha_legible = hoy.strftime('%d de %B de %Y')  # Para mostrar

# URL del evangelio del día
url = f"https://www.vaticannews.va/es/evangelio-de-hoy/{fecha_url}.html"

# Encabezados para simular un navegador real (evita bloqueos por bot)
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"
}

try:
    # Obtener contenido de la página
    resp = requests.get(url, headers=headers, timeout=10)
    resp.raise_for_status()

    soup = BeautifulSoup(resp.content, "html.parser")

    # EXTRAER EL TÍTULO
    titulo_element = soup.select_one("div.vv-article__content h1")
    titulo = titulo_element.get_text(strip=True) if titulo_element else "Título no disponible"

    # EXTRAER EL CUERPO DEL EVANGELIO
    cuerpo_element = soup.select_one("div.vv-article__body")
    cuerpo = cuerpo_element.get_text("\n", strip=True) if cuerpo_element else "Contenido no disponible"

    # EXTRAER PALABRA DEL PAPA (si está)
    palabra_papa = "No disponible hoy."
    for h2 in soup.select("div.vv-article__body h2"):
        if "Palabra del Papa" in h2.get_text(strip=True):
            parrafo = h2.find_next_sibling("p")
            palabra_papa = parrafo.get_text(strip=True) if parrafo else "No disponible hoy."
            break

    # Crear diccionario final
    liturgia = {
        "fecha": fecha_legible,
        "evangelio_titulo": titulo,
        "evangelio_contenido": cuerpo,
        "palabra_del_papa": palabra_papa
    }

    # Escribir archivo JSON
    with open("liturgia.json", "w", encoding="utf-8") as f:
        json.dump(liturgia, f, ensure_ascii=False, indent=2)

except Exception as e:
    print(f"❌ Error al obtener la liturgia: {str(e)}")
    # Crear JSON de error
    with open("liturgia.json", "w", encoding="utf-8") as f:
        json.dump({
            "fecha": fecha_legible,
            "error": str(e),
            "evangelio_titulo": "Título no disponible",
            "evangelio_contenido": "Contenido no disponible",
            "palabra_del_papa": "No disponible hoy."
        }, f, ensure_ascii=False, indent=2)
    raise
