// Offline support for the checklist and the citizenship test practice.
// Network first: while you are online you always get the current page and the current officials.
// The saved copy is used only when the network fails or takes longer than 4 seconds.
var CACHE = 'gc-v1';
var CORE = ['./', 'civics.html', 'questions.json', 'why.json', 'officials.json', 'interview.json', 'steps.json', 'zip.json', 'news.json',
            'civics.webmanifest', 'icon-192.png', 'icon-512.png'];

self.addEventListener('install', function(e){
  e.waitUntil(caches.open(CACHE).then(function(c){ return c.addAll(CORE); }).then(function(){ return self.skipWaiting(); }));
});
self.addEventListener('activate', function(e){
  e.waitUntil(caches.keys().then(function(keys){
    return Promise.all(keys.filter(function(k){ return k !== CACHE; }).map(function(k){ return caches.delete(k); }));
  }).then(function(){ return self.clients.claim(); }));
});
self.addEventListener('fetch', function(e){
  var req = e.request, url = new URL(req.url);
  if (req.method !== 'GET' || url.origin !== location.origin) return;   // the visit counter and outside links are left alone
  var key = url.origin + url.pathname;                                  // one saved copy per page, whatever the ?query
  var fresh = fetch(req).then(function(res){
    if (res.ok) { var copy = res.clone(); caches.open(CACHE).then(function(c){ c.put(key, copy); }); }
    return res;
  });
  var slow = new Promise(function(_, no){ setTimeout(no, 4000); });
  e.respondWith(Promise.race([fresh, slow]).catch(function(){
    return caches.match(key).then(function(hit){ return hit || fresh; });
  }));
});
