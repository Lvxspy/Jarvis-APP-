"""
Modo consola: Jarvis sigue escuchando por el microfono del PC, igual
que en la version original, pero ahora con el bug de reconocimiento
arreglado y los comandos organizados en comandos.py.

Uso: python main.py
"""
from jarvis_core import hablar, escuchar_microfono
from comandos import ejecutar_comando


def run():
    hablar("Jarvis activado")
    while True:
        texto = escuchar_microfono()
        if texto is None:
            continue
        resultado = ejecutar_comando(texto)
        hablar(resultado["respuesta"])
        # Nota: si el comando trae una "accion" (abrir app, spotify,
        # whatsapp), aquí en modo consola se ignora, porque esas
        # acciones pasan en el CELULAR, no en el PC. Para usarlas,
        # habla con Jarvis desde la app del celular (server.py).


if __name__ == "__main__":
    run()
