import adapter from '@sveltejs/adapter-static';
import { vitePreprocess } from '@sveltejs/vite-plugin-svelte';

/** @type {import('@sveltejs/kit').Config} */
const config = {
	preprocess: vitePreprocess(),
	kit: {
		// Single-page app: every page is rendered in the browser, which talks to the API
		// directly with the session cookie. `index.html` serves all routes.
		adapter: adapter({ fallback: 'index.html' })
	}
};

export default config;
