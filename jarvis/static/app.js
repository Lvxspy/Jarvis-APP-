const estadoEl = document.getElementById('estado');
const respuestaEl = document.getElementById('respuesta');
const btnHablar = document.getElementById('btnHablar');
const campoTexto = document.getElementById('campoTexto');
const btnEnviar = document.getElementById('btnEnviar');

async function enviarComando(texto) {
  estadoEl.textContent = 'Pensando...';
  try {
    const resp = await fetch('/comando', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ texto })
    });
    const datos = await resp.json();
    mostrarRespuesta(datos.respuesta || 'No hubo respuesta.');
  } catch (err) {
    mostrarRespuesta('No pude conectarme al servidor de Jarvis. ¿Está corriendo server.py en el PC y estás en el mismo wifi?');
  }
}

function mostrarRespuesta(texto) {
  respuestaEl.textContent = texto;
  estadoEl.textContent = 'Listo';
  hablarEnVozAlta(texto);
}

function hablarEnVozAlta(texto) {
  if (!('speechSynthesis' in window)) return;
  const utter = new SpeechSynthesisUtterance(texto);
  utter.lang = 'es-ES';
  speechSynthesis.speak(utter);
}

// Reconocimiento de voz del navegador (no del PC).
const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
let reconocimiento = null;

if (SpeechRecognition) {
  reconocimiento = new SpeechRecognition();
  reconocimiento.lang = 'es-ES';
  reconocimiento.interimResults = false;

  reconocimiento.onstart = () => { estadoEl.textContent = 'Escuchando...'; };
  reconocimiento.onerror = () => { estadoEl.textContent = 'No te escuché bien, intenta otra vez.'; };
  reconocimiento.onresult = (evento) => {
    const texto = evento.results[0][0].transcript;
    respuestaEl.textContent = `Dijiste: "${texto}"`;
    enviarComando(texto);
  };

  btnHablar.addEventListener('click', () => reconocimiento.start());
} else {
  btnHablar.disabled = true;
  estadoEl.textContent = 'Este navegador no tiene reconocimiento de voz. Usa el campo de texto.';
}

btnEnviar.addEventListener('click', () => {
  const texto = campoTexto.value.trim();
  if (texto) {
    enviarComando(texto);
    campoTexto.value = '';
  }
});

campoTexto.addEventListener('keydown', (e) => {
  if (e.key === 'Enter') btnEnviar.click();
});

// Registrar el service worker para que Chrome deje instalar esto
// como app ("Agregar a pantalla de inicio").
if ('serviceWorker' in navigator) {
  navigator.serviceWorker.register('sw.js').catch(() => {});
}
