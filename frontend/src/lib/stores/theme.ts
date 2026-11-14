import { writable } from 'svelte/store';
import { browser } from '$app/environment';
import { DEFAULT_THEME } from '$lib/config';

const STORAGE_KEY = 'beantrack.theme'; // also read by the inline script in app.html

/**
 * Active daisyUI theme. Starts from what app.html applied before first paint:
 * cached choice (localStorage) > system preference (prefers-color-scheme).
 * When logged in, the account's saved theme replaces it (see `stores/user.ts`).
 */
export const theme = writable<string>(
	(browser && document.documentElement.getAttribute('data-theme')) || DEFAULT_THEME
);

if (browser) {
	theme.subscribe((value) => document.documentElement.setAttribute('data-theme', value));
}

/** Apply a theme and cache it in this browser, so the next page load paints it right away. */
export function applyTheme(value: string): void {
	try {
		localStorage.setItem(STORAGE_KEY, value);
	} catch {
		// ignore
	}
	theme.set(value);
}
