"""
Registro de comandos de Jarvis.

Cada comando puede devolver dos cosas:
- Solo texto (str): Jarvis lo dice, y ya. (ej: la hora)
- Una tupla (texto, accion): Jarvis lo dice Y ADEMÁS le manda una
  instrucción al CELULAR para que la ejecute (abrir una app, poner
  una canción, mandar un WhatsApp). El PC no puede ejecutar esas
  acciones directamente porque pasan en el celular; por eso se las
  manda como un diccionario "accion" que la app de Android sabe
  interpretar.

Para agregar un comando nuevo que solo hable: sigue el patrón de
cmd_hora. Para uno que además controle el celular: sigue el patrón
de cmd_abrir_app.
"""
import datetime
import pywhatkit

import contactos
import spotify_client


def cmd_reproducir(texto):
    """Reproduce algo en YouTube EN EL PC. Ej: 'jarvis reproduce bad bunny'."""
    musica = texto.replace('reproduce', '', 1).strip()
    if not musica:
        return "¿Qué quieres que reproduzca?"
    pywhatkit.playonyt(musica)
    return f"Dale, reproduciendo {musica}"


def cmd_hora(texto):
    """Dice la hora actual."""
    hora = datetime.datetime.now().strftime('%H:%M')
    return f"Son las {hora}"


def cmd_abrir_app(texto):
    """Ej: 'jarvis abre instagram' -> abre esa app en el celular."""
    app_nombre = texto.replace('abre', '', 1).strip()
    if not app_nombre:
        return "¿Cuál app quieres que abra?"
    return (f"Abriendo {app_nombre}", {"tipo": "abrir_app", "app": app_nombre})


def cmd_spotify(texto):
    """Ej: 'jarvis pon bad bunny en spotify' -> la busca y la manda a reproducir en el celular."""
    cancion = texto.replace('en spotify', '').replace('pon', '', 1).strip()
    if not cancion:
        return "¿Qué canción quieres poner?"
    uri = spotify_client.buscar_uri_cancion(cancion)
    if uri is None:
        return "No encontré esa canción en Spotify (o falta configurar las credenciales en spotify_client.py)."
    return (f"Poniendo {cancion} en Spotify", {"tipo": "reproducir_spotify", "uri": uri})


def cmd_whatsapp(texto):
    """Ej: 'jarvis mandale a julieth por whatsapp ya voy para la casa'"""
    resto = texto.replace('mandale a', '', 1).strip()
    if ' por whatsapp ' not in resto:
        return "Dime: mándale a [contacto] por whatsapp [mensaje]"
    contacto_str, mensaje = resto.split(' por whatsapp ', 1)
    contacto_str = contacto_str.strip()
    mensaje = mensaje.strip()
    telefono = contactos.CONTACTOS.get(contacto_str)
    if telefono is None:
        return f"No tengo el número de {contacto_str} guardado. Agrégalo en contactos.py."
    if not mensaje:
        return f"¿Qué le digo a {contacto_str}?"
    return (f"Enviando WhatsApp a {contacto_str}", {"tipo": "enviar_whatsapp", "telefono": telefono, "mensaje": mensaje})


# El orden importa: se revisa de arriba hacia abajo, y se ejecuta el
# PRIMER comando cuya palabra clave esté contenida en el texto. Por
# eso las frases más específicas van primero (si "pon" estuviera antes
# que "en spotify", cualquier frase con "pon" activaría el comando
# equivocado).
COMANDOS = [
    ("por whatsapp", cmd_whatsapp),
    ("en spotify", cmd_spotify),
    ("abre", cmd_abrir_app),
    ("reproduce", cmd_reproducir),
    ("hora", cmd_hora),
]


def ejecutar_comando(texto):
    """
    Busca el primer comando cuya palabra clave esté en el texto y lo
    ejecuta. Siempre devuelve un diccionario {"respuesta": ..., "accion": ...}
    para que tanto la app web (PC) como la app de Android sepan qué hacer.
    """
    texto = texto.lower().strip()
    # Desde el celular el texto llega completo ("jarvis abre instagram"),
    # asi que quitamos el nombre aqui para que los comandos no lo vean
    # (si no, se intentaria abrir una app llamada "jarvis instagram").
    texto = texto.replace("jarvis", "", 1).strip()
    for palabra_clave, funcion in COMANDOS:
        if palabra_clave in texto:
            try:
                resultado = funcion(texto)
            except Exception as e:
                return {"respuesta": f"Se me dañó algo tratando de hacer eso: {e}", "accion": None}
            if isinstance(resultado, tuple):
                respuesta, accion = resultado
            else:
                respuesta, accion = resultado, None
            return {"respuesta": respuesta, "accion": accion}
    return {"respuesta": "No entendí ese comando todavía.", "accion": None}
