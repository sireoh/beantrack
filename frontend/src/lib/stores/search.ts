import { get, writable } from 'svelte/store';
import { api } from '$lib/api/client';
import type { MediaType, SearchMovieCard, SearchTVCard } from '$lib/api/types';
import { WATCH_STATUSES, WatchStatus } from '$lib/status';
import { persisted } from './persisted';
import { addMovieEntry, addTvEntry } from './lists';

/** TV or movie search; the last choice is remembered. */
export const searchMode = persisted<MediaType>(
	'beantrack.searchMode',
	'tv',
	(v): v is MediaType => v === 'tv' || v === 'movie'
);

/** Status that "Add" uses on /search; remembered across reloads. */
export const addStatus = persisted<WatchStatus>(
	'beantrack.addStatus',
	WatchStatus.Planned,
	(v): v is WatchStatus => (WATCH_STATUSES as readonly string[]).includes(v)
);

/** Results of the latest search, tagged with the type they were searched as. */
export type SearchResults =
	| { type: 'tv'; query: string; items: SearchTVCard[] }
	| { type: 'movie'; query: string; items: SearchMovieCard[] };

export const searchResults = writable<SearchResults | null>(null);

/** Call the search endpoint. The caller stores the result (so stale responses can be dropped). */
export async function fetchSearch(type: MediaType, query: string): Promise<SearchResults> {
	return type === 'tv'
		? { type, query, items: (await api.searchTv(query)).results }
		: { type, query, items: (await api.searchMovies(query)).results };
}

/** Add the search result at `index` to the matching list, with the chosen `addStatus`. */
export async function addSearchResult(index: number): Promise<void> {
	const results = get(searchResults);
	if (!results) return;
	const status = get(addStatus);

	if (results.type === 'tv') {
		const card = results.items[index];
		if (!card?.imdb) return;
		const entry = await api.addTv({
			show: {
				imdb: card.imdb,
				tvmaze_id: card.tvmaze_id,
				title: card.title,
				image: card.image,
				score: card.score
			},
			status
		});
		addTvEntry(entry);
	} else {
		const card = results.items[index];
		if (!card) return;
		const entry = await api.addMovie({
			movie: { imdb: card.imdb, title: card.title, image: card.image },
			status
		});
		addMovieEntry(entry);
	}
}
