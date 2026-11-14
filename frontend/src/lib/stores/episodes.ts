import { get, writable } from 'svelte/store';
import { api } from '$lib/api/client';
import type { Episode } from '$lib/api/types';

/** Episode lists by show IMDb id, fetched the first time an edit menu opens for that show. */
export const episodes = writable<Record<string, Episode[]>>({});

const loading = new Map<string, Promise<Episode[]>>();

export function ensureEpisodes(imdb: string): Promise<Episode[]> {
	const cached = get(episodes)[imdb];
	if (cached) return Promise.resolve(cached);

	let pending = loading.get(imdb);
	if (!pending) {
		pending = api
			.getEpisodes(imdb)
			.then((list) => {
				episodes.update((all) => ({ ...all, [imdb]: list }));
				return list;
			})
			.finally(() => loading.delete(imdb));
		loading.set(imdb, pending);
	}
	return pending;
}
