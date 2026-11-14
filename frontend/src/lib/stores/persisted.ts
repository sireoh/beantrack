import { writable, type Writable } from 'svelte/store';
import { browser } from '$app/environment';

/** A writable store mirrored to localStorage (silently in-memory if storage is unavailable). */
export function persisted<T extends string>(
	key: string,
	initial: T,
	isValid: (value: string) => value is T
): Writable<T> {
	let start = initial;
	if (!browser) return writable<T>(start);
	try {
		const saved = localStorage.getItem(key);
		if (saved !== null && isValid(saved)) start = saved;
	} catch {
		// private mode / blocked storage
	}

	const store = writable<T>(start);
	store.subscribe((value) => {
		try {
			localStorage.setItem(key, value);
		} catch {
			// ignore
		}
	});
	return store;
}
