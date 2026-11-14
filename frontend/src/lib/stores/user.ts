import { writable } from 'svelte/store';
import { api, ApiError, setUnauthorizedHandler } from '$lib/api/client';
import type { User } from '$lib/api/types';
import { resetLists } from './lists';
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
		user.set(await api.me());
	} catch (error) {
		if (!(error instanceof ApiError && error.status === 401)) showError(error);
		user.set(null);
	} finally {
		userLoaded.set(true);
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
