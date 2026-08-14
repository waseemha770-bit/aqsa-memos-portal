self.addEventListener('install', (e) => {
  console.log('[Service Worker] Installed');
  self.skipWaiting();
});

self.addEventListener('fetch', (e) => {
  // تركناه فارغاً، يكفي فقط وجوده لكي يعترف المتصفح أن الموقع PWA
});
