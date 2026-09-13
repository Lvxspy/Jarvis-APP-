"""
Servidor de Jarvis: corre en tu PC y es el puente con la app del
celular.

Como funciona:
1. El celular abre esta pagina en su navegador (ej: http://192.168.1.5:5000)
   y usa el reconocimiento de voz del NAVEGADOR (no del PC) para
   convertir lo que dices en texto.
2. Ese texto se manda por una peticion HTTP a /comando.
3. El servidor ejecuta el comando con el mismo comandos.py que usa el
   modo consola, y devuelve la respuesta en texto.
4. El celular lee la respuesta en voz alta con su propio altavoz.

Para saber la IP de tu PC en la red local: abre "cmd" y escribe
"ipconfig", busca "Direccion IPv4" (algo como 192.168.1.5). El
celular tiene que estar conectado al MISMO wifi que el PC.

Uso: python server.py
"""
from flask import Flask, request, jsonify, send_from_directory
from comandos import ejecutar_comando

app = Flask(__name__, static_folder="static", static_url_path="")


@app.route("/")
def index():
    return send_from_directory("static", "index.html")


@app.route("/comando", methods=["POST"])
def comando():
    datos = request.get_json(force=True, silent=True) or {}
    texto = datos.get("texto", "")
    if not texto:
        return jsonify({"respuesta": "No me llegó ningún texto.", "accion": None}), 400
    # ejecutar_comando ya devuelve {"respuesta": ..., "accion": ...}.
    # "accion" viaja tal cual hasta la app de Android, que es la
    # única que sabe ejecutarla (abrir apps, Spotify, WhatsApp). La
    # app web del navegador simplemente la ignora.
    resultado = ejecutar_comando(texto)
    return jsonify(resultado)


@app.route("/estado")
def estado():
    return jsonify({"ok": True})


if __name__ == "__main__":
    # host="0.0.0.0" para que el celular (otro dispositivo en la red)
    # pueda alcanzar el servidor, no solo el propio PC.
    app.run(host="0.0.0.0", port=5000, debug=True)
