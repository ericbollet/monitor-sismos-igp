import requests
import os
import sys
from datetime import datetime

NTFY_TOPIC = "sismo-midagri-coes-7k29x"
MAGNITUD_MINIMA = 3.0
IGP_URL = "https://ultimosismo.igp.gob.pe/api/ultimo-sismo"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/149.0.0.0 Safari/537.36",
    "Accept": "application/json",
    "Referer": "https://ultimosismo.igp.gob.pe/ultimo-sismo"
}

def enviar_ntfy(titulo, mensaje, prioridad="default"):
    url = f"https://ntfy.sh/{NTFY_TOPIC}"
    try:
        r = requests.post(
            url,
            data=mensaje.encode("utf-8"),
            headers={"Title": titulo.encode("utf-8"), "Priority": prioridad, "Tags": "warning"},
            timeout=10
        )
        print(f"Notificación enviada: {r.status_code}")
    except Exception as e:
        print(f"Error enviando notificación: {e}")

def obtener_ultimo_sismo_igp():
    r = requests.get(IGP_URL, headers=HEADERS, timeout=15)
    r.raise_for_status()
    return r.json()

def formatear_mensaje(sismo):
    magnitud = float(sismo.get("magnitud", 0))
    profundidad = sismo.get("profundidad", "N/D")
    referencia = sismo.get("referencia", "N/D")
    intensidades = sismo.get("intensidades", "N/D")
    codigo = sismo.get("codigo", "N/D")
    lat = sismo.get("latitud", "N/D")
    lon = sismo.get("longitud", "N/D")
    fecha_raw = sismo.get("fecha_hora", "")
    try:
        fecha_dt = datetime.fromisoformat(fecha_raw.replace("Z", "+00:00"))
        fecha_hora = fecha_dt.strftime("%d/%m/%Y %H:%M UTC")
    except Exception:
        fecha_hora = fecha_raw

    titulo = f"🌍 SISMO M{magnitud} - {referencia.split(',')[-1].strip() if ',' in referencia else 'Perú'}"
    cuerpo = (
        f"Reporte IGP: {codigo}\nMagnitud: {magnitud} Mw\nProfundidad: {profundidad} km\n"
        f"Referencia: {referencia}\nIntensidad: {intensidades}\nFecha/Hora: {fecha_hora}\nLat/Lon: {lat}, {lon}"
    )
    if magnitud >= 6.0:
        prioridad = "urgent"
    elif magnitud >= 4.5:
        prioridad = "high"
    else:
        prioridad = "default"
    return titulo, cuerpo, prioridad

def main():
    # Leemos el último ID enviado desde un archivo (para no repetir alertas)
    ultimo_id_archivo = "ultimo_id.txt"
    ultimo_id_enviado = None
    if os.path.exists(ultimo_id_archivo):
        with open(ultimo_id_archivo, "r") as f:
            contenido = f.read().strip()
            if contenido:
                ultimo_id_enviado = int(contenido)

    sismo = obtener_ultimo_sismo_igp()
    sismo_id = sismo.get("id")
    magnitud = float(sismo.get("magnitud", 0))

    if sismo_id != ultimo_id_enviado:
        if magnitud >= MAGNITUD_MINIMA:
            titulo, cuerpo, prioridad = formatear_mensaje(sismo)
            print(f"Nuevo sismo: {titulo}")
            enviar_ntfy(titulo, cuerpo, prioridad)
        else:
            print(f"Sismo nuevo pero bajo el umbral (M{magnitud})")

        with open(ultimo_id_archivo, "w") as f:
            f.write(str(sismo_id))
    else:
        print("Sin cambios respecto al último sismo enviado.")

if __name__ == "__main__":
    main()

if __name__ == "__main__":
    main()
