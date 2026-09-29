// Offline support for the checklist and the citizenship test practice.
// Network first: while you are online and the network answers within 4 seconds you get the current page and the current officials.
// The saved copy is used only when the network fails, the server has an error of its own (5xx), or it takes longer than 4 seconds.
var CACHE = 'gc-v1';
var CORE = ['./', 'civics.html', 'questions.json', 'why.json', 'officials.json', 'interview.json', 'steps.json', 'zip.json', 'zipcd.json', 'news.json',
            'civics.webmanifest', 'icon-192.png', 'icon-512.png'];

self.addEventListener('install', function(e){
  e.waitUntil(caches.open(CACHE).then(function(c){ return c.addAll(CORE); }).then(function(){ return self.skipWaiting(); }));
});
self.addEventListener('activate', function(e){
  e.waitUntil(caches.keys().then(function(keys){
    // every danpune.github.io site shares one Cache Storage: touch only our own caches
    return Promise.all(keys.filter(function(k){ return k.indexOf('gc-') === 0 && k !== CACHE; }).map(function(k){ return caches.delete(k); }));
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
  var good = fresh.then(function(res){ if (res.status >= 500) throw 0; return res; });   // a server error must not beat the saved copy; a 404 stays a 404
  var slow = new Promise(function(_, no){ setTimeout(no, 4000); });
  e.respondWith(Promise.race([good, slow]).catch(function(){
    return caches.match(key).then(function(hit){ return hit || fresh; });
  }));
});
