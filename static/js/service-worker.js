const cacheName = 'dinoWeb-v1';
const filesToCache = [
  '/',
  '/static/icons/pwa192.png',
  '/static/icons/pwa500.png',
  '/static/manifest.json',
  // Agrega otros archivos que quieras cachear
];

self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(cacheName)
      .then((cache) => {
        return cache.addAll(filesToCache);
      })
  );
});

self.addEventListener('fetch', (event) => {
  event.respondWith(
    caches.match(event.request)
      .then((response) => {
        return response || fetch(event.request);
      })
  );
});