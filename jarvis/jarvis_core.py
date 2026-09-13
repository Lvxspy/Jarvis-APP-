"""
Nucleo de Jarvis: hablar (texto -> voz) y escuchar (voz -> texto por
el microfono del PC). Lo usa el modo consola (main.py); el servidor
(server.py) no lo necesita porque el celular usa su propio microfono.
"""
import speech_recognition as sr
import pyttsx3

NOMBRE = 'jarvis'
VELOCIDAD_DE_VOZ = 130

_escuchar = sr.Recognizer()
_motor_voz = pyttsx3.init()
_motor_voz.setProperty('rate', VELOCIDAD_DE_VOZ)


def hablar(texto):
    print(f"Jarvis: {texto}")
    _motor_voz.say(texto)
    _motor_voz.runAndWait()


def escuchar_microfono():
    """
    Graba del microfono y devuelve el texto reconocido (sin el nombre
    "jarvis"), o None si no se entendio nada o hubo un error.

    Antes, si recognize_google fallaba, la funcion intentaba
    devolver una variable ("rec") que nunca se habia llegado a crear,
    y el programa se caia entero. Ahora cada tipo de falla se atrapa
    por separado y simplemente se devuelve None: quien llama decide
    que hacer (por lo general, volver a intentar).
    """
    try:
        with sr.Microphone() as fuente:
            print("Te escucho...")
            audio = _escuchar.listen(fuente)
            texto = _escuchar.recognize_google(audio, language="es")
            texto = texto.lower()
    except sr.UnknownValueError:
        print("No entendí lo que dijiste.")
        return None
    except sr.RequestError as e:
        print(f"No pude conectarme al reconocedor de voz: {e}")
        return None
    except Exception as e:
        print(f"Error inesperado escuchando: {e}")
        return None

    if NOMBRE in texto:
        return texto.replace(NOMBRE, '', 1).strip()
    return None
