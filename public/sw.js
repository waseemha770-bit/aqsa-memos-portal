// ملف sw.js لتمكين تثبيت التطبيق PWA
self.addEventListener('install', (e) => {
    console.log('[Service Worker] تم التثبيت بنجاح');
    self.skipWaiting();
});

self.addEventListener('activate', (e) => {
    console.log('[Service Worker] تم التفعيل');
    return self.clients.claim();
});

// جوجل كروم يشترط وجود دالة fetch حتى لو كانت فارغة ليسمح بالتثبيت
self.addEventListener('fetch', (e) => {
    // عدم تفعيل الكاش المعقد حالياً، فقط تمرير الطلب ليعمل النظام بشكل طبيعي
    e.respondWith(fetch(e.request).catch(() => new Response("يرجى التحقق من الاتصال بالإنترنت")));
});
