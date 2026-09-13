// Service worker minimo: solo cachea los archivos de la interfaz
// para que Chrome permita instalar esto como app. Los comandos
// siempre van directo al servidor, nunca se cachean.
const CACHE = 'jarvis-v1';
const ARCHIVOS = ['/', '/style.css', '/app.js', '/manifest.json'];

self.addEventListener('install', (evento) => {
  evento.waitUntil(
    caches.open(CACHE).then((cache) => cache.addAll(ARCHIVOS))
  );
});

self.addEventListener('fetch', (evento) => {
  if (evento.request.url.includes('/comando')) return;
  evento.respondWith(
    caches.match(evento.request).then((resp) => resp || fetch(evento.request))
  );
});
