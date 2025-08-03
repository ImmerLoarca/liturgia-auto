import requests
from bs4 import BeautifulSoup
from datetime import datetime
import json

# Obtener fecha actual (sin zona horaria)
hoy = datetime.now()
fecha_str = hoy.strftime('%Y/%m/%d')
fecha_legible = hoy.strftime('%d de %B de %Y')

url = f"https://www.vaticannews.va/es/evangelio-de-hoy/{fecha_str}.html"

try:
    # Configurar headers para evitar bloqueos
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    
    resp = requests.get(url, headers=headers, timeout=10)
    resp.raise_for_status()  # Verificar que la respuesta sea exitosa
    
    soup = BeautifulSoup(resp.content, "html.parser")
    
    # Extracción de datos con búsqueda flexible
    titulo = soup.find("h1").get_text(strip=True) if soup.find("h1") else "Título no disponible"
    
    contenido = soup.find("article").get_text("\n", strip=True) if soup.find("article") else "Contenido no disponible"
    
    papa = soup.find("section", {"id": "word-of-the-pope"}).get_text("\n", strip=True) if soup.find("section", {"id": "word-of-the-pope"}) else "No disponible hoy"

    # Guardar datos
    data = {
        "fecha": fecha_legible,
        "titulo": titulo,
        "contenido": contenido,
        "palabra_papa": papa
    }

    with open("liturgia.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

except Exception as e:
    print(f"Error: {str(e)}")
    # Crear archivo con mensaje de error
    with open("liturgia.json", "w", encoding="utf-8") as f:
        json.dump({"error": str(e), "fecha": fecha_legible}, f, ensure_ascii=False, indent=2)
    raise  # Terminar con error para que aparezca en los logs
