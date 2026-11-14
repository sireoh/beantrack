import tailwindcss from '@tailwindcss/vite';
import { sveltekit } from '@sveltejs/kit/vite';
import { defineConfig, loadEnv } from 'vite';

export default defineConfig(({ mode }) => {
	const env = loadEnv(mode, process.cwd(), 'PUBLIC_');

	// Serve the dev site on the same hostname as the API (e.g. 127.0.0.1 for both).
	// The session cookie is SameSite=Lax, so the browser only sends it to the API when
	// both run on the same site; localhost vs 127.0.0.1 counts as different sites.
	let host = '127.0.0.1';
	try {
		host = new URL(env.PUBLIC_API_URL).hostname;
	} catch {
		// PUBLIC_API_URL missing or relative: keep the default.
	}

	return {
		plugins: [tailwindcss(), sveltekit()],
		server: { host, port: 5173, strictPort: true }
	};
});
