import { get, writable } from 'svelte/store';
import { api, ApiError, setUnauthorizedHandler } from '$lib/api/client';
import type { ThemeName, User } from '$lib/api/types';
import { resetLists } from './lists';
import { applyTheme } from './theme';
import { showError } from './toasts';

/** The logged-in Discord user, or null when logged out. */
export const user = writable<User | null>(null);

/** False until the first `/api/auth/me` check finishes (avoids flashing the landing page). */
export const userLoaded = writable(false);

function clearSession(): void {
	user.set(null);
	resetLists();
}

setUnauthorizedHandler(clearSession);

export async function loadUser(): Promise<void> {
	try {
		const me = await api.me();
		user.set(me);
		// The account's theme wins over this browser's cached one, so every device matches.
		if (me.theme) applyTheme(me.theme);
	} catch (error) {
		if (!(error instanceof ApiError && error.status === 401)) showError(error);
		user.set(null);
	} finally {
		userLoaded.set(true);
	}
}

/** The theme toggle: apply now, cache locally, and save on the account when logged in. */
export async function setThemePreference(value: ThemeName): Promise<void> {
	applyTheme(value);
	if (!get(user)) return;
	try {
		user.set(await api.setTheme(value));
	} catch (error) {
		showError(error);
	}
}

export async function logout(): Promise<void> {
	try {
		await api.logout();
	} catch (error) {
		showError(error);
	} finally {
		clearSession();
	}
}
