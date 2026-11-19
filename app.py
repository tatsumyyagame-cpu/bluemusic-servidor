from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import yt_dlp
import os
import uuid

app = Flask(__name__)
CORS(app)

PASTA_TEMP = "/tmp/musicas"
os.makedirs(PASTA_TEMP, exist_ok=True)

@app.route("/")
def inicio():
    return "Servidor BlueMusic Online!"

@app.route("/buscar")
def buscar():
    termo = request.args.get("q", "")
    if not termo:
        return jsonify([])

    opcoes = {
        "quiet": True,
        "extract_flat": True,
        "default_search": "ytsearch5",
        "noplaylist": True
    }
    with yt_dlp.YoutubeDL(opcoes) as ydl:
        info = ydl.extract_info(termo, download=False)
        entradas = info.get("entries", [info]) if "entries" in info else [info]
        resultados = []
        for item in entradas:
            if item:
                resultados.append({
                    "titulo": item.get("title", "Sem título"),
                    "url": item.get("url") or f"https://youtube.com{item.get('id')}",
                    "duracao": item.get("duration_string", "MP3")
                })
        return jsonify(resultados)

@app.route("/baixar")
def baixar():
    url = request.args.get("url", "")
    if not url:
        return "URL faltando", 400

    arquivo_id = str(uuid.uuid4())
    caminho_saida = os.path.join(PASTA_TEMP, f"{arquivo_id}.%(ext)s")

    opcoes = {
        "format": "bestaudio/best",
        "outtmpl": caminho_saida,
        "writethumbnail": True,
        "postprocessors": [
            {
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": "192",
            },
            {"key": "EmbedThumbnail"},
            {"key": "FFmpegMetadata"},
        ],
    }

    with yt_dlp.YoutubeDL(opcoes) as ydl:
        info = ydl.extract_info(url, download=True)
        titulo_limpo = "".join(c for c in info.get("title", "musica") if c.isalnum() or c in " -_").strip()

    arquivo_mp3 = os.path.join(PASTA_TEMP, f"{arquivo_id}.mp3")
    return send_file(arquivo_mp3, as_attachment=True, download_name=f"{titulo_limpo}.mp3")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
  
