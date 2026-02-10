const CACHE_NAME = 'pokemon-card-search-v1';
const RUNTIME_CACHE = 'pokemon-card-runtime-v1';

// キャッシュするファイル（アプリシェル）
const PRECACHE_URLS = [
  '/app/index.html',
  '/app/manifest.json',
  '/app/icons/icon-192x192.png',
  '/app/icons/icon-512x512.png'
];

// インストール時：アプリシェルをキャッシュ
self.addEventListener('install', (event) => {
  console.log('[Service Worker] Installing...');

  event.waitUntil(
    caches.open(CACHE_NAME)
      .then((cache) => {
        console.log('[Service Worker] Precaching app shell');
        return cache.addAll(PRECACHE_URLS);
      })
      .then(() => self.skipWaiting())
  );
});

// アクティベーション時：古いキャッシュを削除
self.addEventListener('activate', (event) => {
  console.log('[Service Worker] Activating...');

  event.waitUntil(
    caches.keys().then((cacheNames) => {
      return Promise.all(
        cacheNames.map((cacheName) => {
          if (cacheName !== CACHE_NAME && cacheName !== RUNTIME_CACHE) {
            console.log('[Service Worker] Deleting old cache:', cacheName);
            return caches.delete(cacheName);
          }
        })
      );
    }).then(() => self.clients.claim())
  );
});

// フェッチ時：キャッシュ戦略
self.addEventListener('fetch', (event) => {
  const url = new URL(event.request.url);

  // HTMLファイル：ネットワーク優先、フォールバックでキャッシュ
  if (event.request.mode === 'navigate') {
    event.respondWith(
      fetch(event.request)
        .catch(() => {
          return caches.match('/app/index.html');
        })
    );
    return;
  }

  // JSONデータ：ネットワーク優先、フォールバックでキャッシュ
  if (url.pathname.endsWith('.json')) {
    event.respondWith(
      caches.open(RUNTIME_CACHE).then((cache) => {
        return fetch(event.request)
          .then((response) => {
            // 成功したレスポンスをキャッシュに保存
            cache.put(event.request, response.clone());
            return response;
          })
          .catch(() => {
            // ネットワークエラー時はキャッシュから返す
            return cache.match(event.request);
          });
      })
    );
    return;
  }

  // 画像：キャッシュ優先、なければネットワーク
  if (event.request.destination === 'image') {
    event.respondWith(
      caches.open(RUNTIME_CACHE).then((cache) => {
        return cache.match(event.request).then((cachedResponse) => {
          if (cachedResponse) {
            return cachedResponse;
          }

          return fetch(event.request).then((response) => {
            // 成功したレスポンスをキャッシュに保存
            if (response.status === 200) {
              cache.put(event.request, response.clone());
            }
            return response;
          });
        });
      })
    );
    return;
  }

  // その他：ネットワーク優先
  event.respondWith(
    fetch(event.request).catch(() => {
      return caches.match(event.request);
    })
  );
});

// バックグラウンド同期（将来の拡張用）
self.addEventListener('sync', (event) => {
  if (event.tag === 'sync-cards') {
    event.waitUntil(syncCards());
  }
});

async function syncCards() {
  try {
    const response = await fetch('/card_data/all_cards_local.json');
    const data = await response.json();

    const cache = await caches.open(RUNTIME_CACHE);
    await cache.put('/card_data/all_cards_local.json', new Response(JSON.stringify(data)));

    console.log('[Service Worker] Cards synced successfully');
  } catch (error) {
    console.error('[Service Worker] Sync failed:', error);
  }
}

// プッシュ通知（将来の拡張用）
self.addEventListener('push', (event) => {
  const data = event.data ? event.data.json() : {};
  const title = data.title || 'ポケモンカード検索';
  const options = {
    body: data.body || '新しいカード情報が追加されました',
    icon: '/app/icons/icon-192x192.png',
    badge: '/app/icons/icon-72x72.png'
  };

  event.waitUntil(
    self.registration.showNotification(title, options)
  );
});
