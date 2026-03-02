import tailwindcss from '@tailwindcss/vite';
import { sveltekit } from '@sveltejs/kit/vite';
import { defineConfig } from 'vite';

export default defineConfig({
	plugins: [tailwindcss(), sveltekit()], ssr: {
		// This forces Vite to bundle these packages into the SSR build,
		// which fixes the "./utils/json" resolution issue.
		noExternal: ['better-auth', '@better-auth/core']
	}
});
