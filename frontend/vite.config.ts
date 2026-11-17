import tailwindcss from '@tailwindcss/vite';
import { sveltekit } from '@sveltejs/kit/vite';
import { defineConfig, loadEnv } from 'vite';

export default defineConfig(({ mode }) => {
	// '' loads every variable from .env (not only PUBLIC_*); they stay in this config file.
	const env = loadEnv(mode, process.cwd(), '');

	// The browser calls /api on the dev server itself and Vite forwards it to the backend.
	// So the site works from any device on the network (e.g. a phone at http://<LAN-IP>:5173)
	// and the session cookie is first-party, with no CORS or localhost/127.0.0.1 mix-ups.
	const apiTarget = env.API_PROXY_TARGET || 'http://127.0.0.1:8000';
	// xfwd: send X-Forwarded-For, so the backend records the real client IP at login
	// (it trusts that header from 127.0.0.1, see FORWARDED_ALLOW_IPS).
	const apiProxy = { '/api': { target: apiTarget, xfwd: true } };

	return {
		plugins: [tailwindcss(), sveltekit()],
		server: {
			host: '0.0.0.0', // reachable from other devices on the LAN
			port: 5173,
			strictPort: true,
			proxy: apiProxy
		},
		preview: {
			host: '0.0.0.0',
			proxy: apiProxy
		}
	};
});
