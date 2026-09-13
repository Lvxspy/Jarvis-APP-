# Jarvis

## Estructura del proyecto

- `main.py` — modo consola original: Jarvis escucha por el micrófono del PC (igual que antes, con el bug de reconocimiento arreglado).
- `jarvis_core.py` — hablar y escuchar por el micrófono del PC.
- `comandos.py` — **aquí se agregan los comandos nuevos**. Es una lista de `(palabra_clave, función)`.
- `server.py` — servidor que conecta la app del celular con Jarvis.
- `static/` — la interfaz de celular (PWA).
- `Jarvis` — tu archivo original, sin tocar, por si quieres compararlo.

## 1. Instalar dependencias

Abre una terminal en esta carpeta y corre:

```
pip install -r requirements.txt
```

## 2. Modo consola (como antes)

```
python main.py
```

## 3. Modo app de celular

### a) Prende el servidor en el PC

```
python server.py
```

Debe quedar corriendo (no cierres la ventana).

### b) Encuentra la IP de tu PC

En una terminal de Windows (cmd):

```
ipconfig
```

Busca "Dirección IPv4", algo como `192.168.1.5`.

### c) Abre la app desde el celular

El celular tiene que estar en el **mismo wifi** que el PC. Abre Chrome en el celular y entra a:

```
http://TU_IP:5000
```

(reemplaza `TU_IP` por lo que viste en el paso b, ej: `http://192.168.1.5:5000`)

### d) Instálala como app

En Chrome del celular, toca el menú (⋮) → **"Agregar a pantalla de inicio"**. Te queda un ícono de Jarvis como cualquier otra app.

> **Nota honesta:** el reconocimiento de voz del navegador (lo que usa el botón del micrófono) funciona muy bien en Chrome para Android. En iPhone/Safari el soporte es más limitado — si falla, el campo de texto siempre funciona igual de bien.

## Cómo agregar un comando nuevo

Abre `comandos.py`, agrega una función y regístrala en la lista `COMANDOS`. Ejemplo:

```python
def cmd_saludo(texto):
    return "¡Qué más, todo bien!"

COMANDOS = [
    ("reproduce", cmd_reproducir),
    ("hora", cmd_hora),
    ("saludo", cmd_saludo),   # <- nuevo
]
```

Ese comando queda disponible automáticamente tanto en el modo consola como en la app del celular — no hay que tocar nada más.
