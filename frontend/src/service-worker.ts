/// <reference no-default-lib="true"/>
/// <reference lib="esnext" />
/// <reference lib="webworker" />
/// <reference types="@sveltejs/kit" />
/**
 * Minimal service worker: makes the app installable and caches the app shell (built JS/CSS,
 * static files, icons) so it starts fast. API responses are never cached: list and Discover
 * data always come from the backend. SvelteKit registers this file automatically.
 */
import { build, files, version } from '$service-worker';

const sw = self as unknown as ServiceWorkerGlobalScope;
const CACHE = `beantrack-shell-${version}`;
const SHELL = '/'; // index.html: every route renders from it (single-page app)
const PRECACHE = [...build, ...files, SHELL];
const PRECACHED = new Set(PRECACHE);

sw.addEventListener('install', (event) => {
	event.waitUntil(
		caches
			.open(CACHE)
			.then((cache) => cache.addAll(PRECACHE))
			.then(() => sw.skipWaiting())
	);
});

// A new deploy has a new `version`: drop the old caches.
sw.addEventListener('activate', (event) => {
	event.waitUntil(
		caches
			.keys()
			.then((keys) => Promise.all(keys.filter((key) => key !== CACHE).map((key) => caches.delete(key))))
			.then(() => sw.clients.claim())
	);
});

sw.addEventListener('fetch', (event) => {
	const request = event.request;
	if (request.method !== 'GET') return;
	const url = new URL(request.url);
	// Other origins (posters, Discord avatars) and the API go straight to the network.
	if (url.origin !== sw.location.origin || url.pathname.startsWith('/api/')) return;

	if (request.mode === 'navigate') {
		// Pages: always the latest index.html; the cached shell only when offline.
		event.respondWith(fetch(request).catch(() => caches.match(SHELL).then((r) => r ?? Response.error())));
		return;
	}

	if (PRECACHED.has(url.pathname)) {
		event.respondWith(caches.match(url.pathname).then((cached) => cached ?? fetch(request)));
	}
});
