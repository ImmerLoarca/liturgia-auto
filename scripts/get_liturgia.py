import requests
from bs4 import BeautifulSoup
from datetime import datetime
import json
import os
import time

USER_AGENT = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
              "(KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36")
REQUEST_TIMEOUT = 20
RETRY_DELAY = 3
MAX_RETRIES = 3

def get_formatted_date():
    # Ajusta aquí si necesitas desfase horario a tu zona
    hoy = datetime.utcnow()
    return {
        "url_format": hoy.strftime("%Y/%m/%d"),       # 2025/08/03
        "readable_format": hoy.strftime("%d de %B de %Y")  # 03 de agosto de 2025
    }

def scrape_liturgia():
    dates = get_formatted_date()
    url = f"https://www.vaticannews.va/es/evangelio-de-hoy/{dates['url_format']}.html"
    headers = {
        "User-Agent": USER_AGENT,
        "Accept": "text/html",
        "Accept-Language": "es-ES,es;q=0.8",
        "Referer": "https://www.vaticannews.va/"
    }

    for attempt in range(MAX_RETRIES):
        try:
            print(f"Intento {attempt + 1} de {MAX_RETRIES} - {url}")
            resp = requests.get(url, headers=headers, timeout=REQUEST_TIMEOUT)
            resp.raise_for_status()
            if "404" in resp.url or "Page not found" in resp.text:
                raise requests.RequestException("Página no encontrada (404)")
            soup = BeautifulSoup(resp.content, "html.parser")

            # Título del evangelio
            titulo = soup.find("h1")
            titulo_text = titulo.get_text(strip=True) if titulo else "Título no disponible"

            # Contenido del evangelio
            contenido = ""
            article = soup.find("article") or soup.find("div", class_=lambda x: x and "content" in x.lower())
            if article:
                for tag in article(["script", "style", "nav", "footer", "aside"]):
                    tag.decompose()
                contenido = article.get_text("\n", strip=True)
            else:
                contenido = "Contenido no disponible"

            # Palabra del Papa (si existe)
            papa_section = soup.find("section", id="word‑of‑the‑pope") or soup.find("blockquote")
            palabra_papa = papa_section.get_text("\n", strip=True) if papa_section else "No disponible hoy"

            return {
                "fecha": dates["readable_format"],
                "evangelio_titulo": titulo_text,
                "evangelio_contenido": contenido,
                "palabra_del_papa": palabra_papa,
                "fuente": url,
                "status": "success",
                "actualizado": datetime.now().isoformat()
            }

        except Exception as e:
            print(f"Error en intento {attempt + 1}: {e}", flush=True)
            if attempt < MAX_RETRIES - 1:
                time.sleep(RETRY_DELAY)
                continue
            return {
                "fecha": dates["readable_format"],
                "error": str(e),
                "evangelio_titulo": "Título no disponible",
                "evangelio_contenido": "Contenido no disponible",
                "palabra_del_papa": "No disponible hoy",
                "status": "error",
                "actualizado": datetime.now().isoformat()
            }

def main():
    data = scrape_liturgia()
    salida = os.path.join(os.path.dirname(__file__), "..", "liturgia.json")
    with open(salida, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    if data.get("status") == "error":
        raise RuntimeError("Scraping falló")

if __name__ == "__main__":
    main()
