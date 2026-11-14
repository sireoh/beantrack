/**
 * The user's TV and movie lists. Fetched once, then patched in place after every change,
 * so navigating between pages never refetches.
 */
import { get, writable } from 'svelte/store';
import { api } from '$lib/api/client';
import type { MovieList, MovieListEntry, TvList, TvListEntry } from '$lib/api/types';
import type { StatusFilter } from '$lib/status';
import { episodes } from './episodes';

export const tvList = writable<TvList | null>(null);
export const movieList = writable<MovieList | null>(null);

/** Text + status filter for each list page (kept while navigating away and back). */
export interface ListFilter {
	query: string;
	status: StatusFilter;
}
export const tvFilter = writable<ListFilter>({ query: '', status: 'all' });
export const movieFilter = writable<ListFilter>({ query: '', status: 'all' });

let tvLoading: Promise<TvList> | null = null;
let movieLoading: Promise<MovieList> | null = null;

/** Fetch the TV list unless it is already loaded (concurrent callers share one request). */
export function ensureTvList(): Promise<TvList> {
	const current = get(tvList);
	if (current) return Promise.resolve(current);
	tvLoading ??= api
		.getTvList()
		.then((list) => {
			tvList.set(list);
			return list;
		})
		.finally(() => {
			tvLoading = null;
		});
	return tvLoading;
}

export function ensureMovieList(): Promise<MovieList> {
	const current = get(movieList);
	if (current) return Promise.resolve(current);
	movieLoading ??= api
		.getMovieList()
		.then((list) => {
			movieList.set(list);
			return list;
		})
		.finally(() => {
			movieLoading = null;
		});
	return movieLoading;
}

export function addTvEntry(entry: TvListEntry): void {
	tvList.update((list) => (list ? { ...list, entries: [...list.entries, entry] } : list));
}

export function addMovieEntry(entry: MovieListEntry): void {
	movieList.update((list) => (list ? { ...list, entries: [...list.entries, entry] } : list));
}

/** Replace one row with the server's updated copy (keeps its position). */
export function replaceTvEntry(entry: TvListEntry): void {
	tvList.update((list) =>
		list
			? {
					...list,
					entries: list.entries.map((e) => (e.show.imdb === entry.show.imdb ? entry : e))
				}
			: list
	);
}

export function replaceMovieEntry(entry: MovieListEntry): void {
	movieList.update((list) =>
		list
			? {
					...list,
					entries: list.entries.map((e) => (e.movie.imdb === entry.movie.imdb ? entry : e))
				}
			: list
	);
}

export function removeTvEntry(imdb: string): void {
	tvList.update((list) =>
		list ? { ...list, entries: list.entries.filter((e) => e.show.imdb !== imdb) } : list
	);
}

export function removeMovieEntry(imdb: string): void {
	movieList.update((list) =>
		list ? { ...list, entries: list.entries.filter((e) => e.movie.imdb !== imdb) } : list
	);
}

/** Drop the cached lists so the next page that needs them refetches (e.g. after an import). */
export function invalidateLists(): void {
	tvList.set(null);
	movieList.set(null);
}

/** Forget everything user-specific (logout / expired session). */
export function resetLists(): void {
	tvList.set(null);
	movieList.set(null);
	episodes.set({});
	tvFilter.set({ query: '', status: 'all' });
	movieFilter.set({ query: '', status: 'all' });
}
