/**
 * Discover (TMDB popular titles): one store per media type, filled page by page.
 *
 * Deliberately in memory only (never localStorage): a full page load starts empty and
 * refills from the backend, which is the only cache. Within one visit, moving between
 * /, /discover/tv and /discover/movies reuses what is already loaded.
 */
import { get, writable, type Readable } from 'svelte/store';
import { api } from '$lib/api/client';
import type { DiscoverItem, DiscoverPage, MediaType } from '$lib/api/types';
import { addMovieEntry, addTvEntry } from './lists';
import { addStatus } from './search';

export interface DiscoverState {
	items: DiscoverItem[];
	/** Last page loaded; 0 before the first one. */
	page: number;
	/** Known after the first page loads. */
	totalPages: number | null;
	loading: boolean;
}

export interface DiscoverStore extends Readable<DiscoverState> {
	readonly type: MediaType;
	/** Load page 1 unless something is already loaded. */
	ensureFirstPage(): Promise<void>;
	/** Append the next page (no-op while loading or after the last page). */
	loadNextPage(): Promise<void>;
	hasMore(): boolean;
	/** Remember the IMDb id of an item once it has been added, so its card shows "Added". */
	markAdded(tmdbId: number, imdb: string): void;
}

function createDiscoverStore(type: MediaType, fetchPage: (page: number) => Promise<DiscoverPage>) {
	const state = writable<DiscoverState>({ items: [], page: 0, totalPages: null, loading: false });
	let inFlight: Promise<void> | null = null;

	function load(page: number): Promise<void> {
		inFlight ??= (async () => {
			state.update((s) => ({ ...s, loading: true }));
			try {
				const result = await fetchPage(page);
				state.update((s) => {
					const seen = new Set(s.items.map((item) => item.tmdb_id));
					const fresh = result.results.filter((item) => !seen.has(item.tmdb_id));
					return {
						items: [...s.items, ...fresh],
						page: result.page,
						totalPages: result.total_pages,
						loading: false
					};
				});
			} catch (error) {
				state.update((s) => ({ ...s, loading: false }));
				throw error;
			} finally {
				inFlight = null;
			}
		})();
		return inFlight;
	}

	const hasMore = () => {
		const s = get(state);
		return s.totalPages === null || s.page < s.totalPages;
	};

	const store: DiscoverStore = {
		type,
		subscribe: state.subscribe,
		ensureFirstPage: () => (get(state).page > 0 ? Promise.resolve() : load(1)),
		loadNextPage: () => (inFlight ?? (hasMore() ? load(get(state).page + 1) : Promise.resolve())),
		hasMore,
		markAdded(tmdbId, imdb) {
			state.update((s) => ({
				...s,
				items: s.items.map((item) => (item.tmdb_id === tmdbId ? { ...item, imdb } : item))
			}));
		}
	};
	return store;
}

export const discoverTv = createDiscoverStore('tv', api.discoverTv);
export const discoverMovies = createDiscoverStore('movie', api.discoverMovies);

export const discoverStore = (type: MediaType): DiscoverStore =>
	type === 'tv' ? discoverTv : discoverMovies;

/**
 * Add a Discover title with the status chosen in the shared "Add as" dropdown. The backend
 * resolves it (TMDB -> IMDb id -> TVmaze / OMDb) and runs the same add as the search page.
 */
export async function addDiscoverItem(type: MediaType, item: DiscoverItem): Promise<void> {
	const body = { tmdb_id: item.tmdb_id, status: get(addStatus) };
	if (type === 'tv') {
		const entry = await api.addDiscoverTv(body);
		addTvEntry(entry);
		discoverTv.markAdded(item.tmdb_id, entry.show.imdb);
	} else {
		const entry = await api.addDiscoverMovie(body);
		addMovieEntry(entry);
		discoverMovies.markAdded(item.tmdb_id, entry.movie.imdb);
	}
}
