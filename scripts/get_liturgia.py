import requests
from bs4 import BeautifulSoup
from datetime import datetime
import json

hoy = datetime.now()
fecha_str = hoy.strftime('%Y/%m/%d')
fecha_legible = hoy.strftime('%d de %B de %Y')

url = f"https://www.vaticannews.va/es/evangelio-de-hoy/{fecha_str}.html"
resp = requests.get(url)
soup = BeautifulSoup(resp.content, "html.parser")

titulo = soup.find("h1", class_="vv-article__title").get_text(strip=True)
cuerpo = soup.find("div", class_="vv-article__body").get_text("\n", strip=True)
papa_seccion = soup.find("section", {"id": "word-of-the-pope"})
palabra_papa = papa_seccion.get_text("\n", strip=True) if papa_seccion else "No disponible hoy."

liturgia = {
    "fecha": fecha_legible,
    "evangelio_titulo": titulo,
    "evangelio_contenido": cuerpo,
    "palabra_del_papa": palabra_papa
}

with open("liturgia.json", "w", encoding="utf-8") as f:
    json.dump(liturgia, f, ensure_ascii=False, indent=4)