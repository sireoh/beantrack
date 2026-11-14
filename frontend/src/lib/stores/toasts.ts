import { writable } from 'svelte/store';
import { ApiError } from '$lib/api/client';

export interface Toast {
	id: number;
	kind: 'error' | 'success';
	message: string;
}

export const toasts = writable<Toast[]>([]);

let nextId = 1;

export function showToast(message: string, kind: Toast['kind'] = 'error', ms = 4000): void {
	const id = nextId++;
	toasts.update((list) => [...list, { id, kind, message }]);
	setTimeout(() => toasts.update((list) => list.filter((t) => t.id !== id)), ms);
}

/** Toast an error from an API call. 401s are skipped: the UI already falls back to login. */
export function showError(error: unknown): void {
	if (error instanceof ApiError) {
		if (error.status !== 401) showToast(error.message);
		return;
	}
	showToast('Something went wrong');
	console.error(error);
}
