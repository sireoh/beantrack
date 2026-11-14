import { writable } from 'svelte/store';
import { browser } from '$app/environment';
import { DEFAULT_THEME } from '$lib/config';

const STORAGE_KEY = 'beantrack.theme'; // also read by the inline script in app.html

/** Active daisyUI theme. Starts from what app.html applied before first paint. */
export const theme = writable<string>(
	(browser && document.documentElement.getAttribute('data-theme')) || DEFAULT_THEME
);

if (browser) {
	theme.subscribe((value) => document.documentElement.setAttribute('data-theme', value));
}

/** Switch theme because the user asked to; the choice is remembered in this browser. */
export function chooseTheme(value: string): void {
	try {
		localStorage.setItem(STORAGE_KEY, value);
	} catch {
		// ignore
	}
	theme.set(value);
}
