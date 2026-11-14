/**
 * Typed wrapper around the BeanTrack API. Every request sends the session cookie.
 */
import { API_URL } from '$lib/config';
import type { WatchStatus } from '$lib/status';
import type {
	Backup,
	Episode,
	MovieAddRequest,
	MovieList,
	MovieListEntry,
	ProfileExport,
	ProfileImportResult,
	RestoreResult,
	SearchMovieCard,
	SearchResponse,
	SearchTVCard,
	TvAddRequest,
	TvList,
	TvListEntry,
	TvProgressRequest,
	User
} from './types';

export class ApiError extends Error {
	constructor(
		readonly status: number,
		message: string
	) {
		super(message);
		this.name = 'ApiError';
	}
}

let onUnauthorized: (() => void) | null = null;

/** Called whenever the API answers 401 (session missing or expired). */
export function setUnauthorizedHandler(handler: () => void): void {
	onUnauthorized = handler;
}

async function request<T>(method: string, path: string, body?: unknown): Promise<T> {
	let response: Response;
	try {
		response = await fetch(`${API_URL}${path}`, {
			method,
			credentials: 'include',
			headers: body === undefined ? undefined : { 'Content-Type': 'application/json' },
			body: body === undefined ? undefined : JSON.stringify(body)
		});
	} catch {
		throw new ApiError(0, 'Could not reach the BeanTrack server');
	}

	if (!response.ok) {
		if (response.status === 401) onUnauthorized?.();
		throw new ApiError(response.status, await errorMessage(response));
	}
	if (response.status === 204) return undefined as T;
	return (await response.json()) as T;
}

async function errorMessage(response: Response): Promise<string> {
	try {
		const data: unknown = await response.json();
		const detail = (data as { detail?: unknown }).detail;
		if (typeof detail === 'string') return detail;
		// FastAPI validation errors: [{ msg: "..." }, ...]
		if (Array.isArray(detail) && typeof detail[0]?.msg === 'string') return detail[0].msg;
	} catch {
		// not JSON
	}
	return response.statusText || `Request failed (${response.status})`;
}

const enc = encodeURIComponent;

export const api = {
	// Auth
	me: () => request<User>('GET', '/api/auth/me'),
	logout: () => request<void>('POST', '/api/auth/logout'),

	// Search
	searchTv: (q: string) =>
		request<SearchResponse<SearchTVCard>>('GET', `/api/search?type=tv&q=${enc(q)}`),
	searchMovies: (q: string) =>
		request<SearchResponse<SearchMovieCard>>('GET', `/api/search?type=movie&q=${enc(q)}`),

	// TV list
	getTvList: () => request<TvList>('GET', '/api/tvlist'),
	addTv: (body: TvAddRequest) => request<TvListEntry>('POST', '/api/tvlist/add', body),
	getEpisodes: (imdb: string) => request<Episode[]>('GET', `/api/tvlist/${enc(imdb)}/episodes`),
	updateTvProgress: (imdb: string, body: TvProgressRequest) =>
		request<TvListEntry>('PATCH', `/api/tvlist/${enc(imdb)}/progress`, body),
	updateTvStatus: (imdb: string, status: WatchStatus) =>
		request<TvListEntry>('PATCH', `/api/tvlist/${enc(imdb)}/status`, { status }),
	deleteTv: (imdb: string) => request<void>('DELETE', `/api/tvlist/${enc(imdb)}`),

	// Movie list
	getMovieList: () => request<MovieList>('GET', '/api/movielist'),
	addMovie: (body: MovieAddRequest) => request<MovieListEntry>('POST', '/api/movielist/add', body),
	updateMovieStatus: (imdb: string, status: WatchStatus) =>
		request<MovieListEntry>('PATCH', `/api/movielist/${enc(imdb)}/status`, { status }),
	deleteMovie: (imdb: string) => request<void>('DELETE', `/api/movielist/${enc(imdb)}`),

	// Profile (watchlist export / import)
	exportProfile: () => request<ProfileExport>('GET', '/api/auth/profile/export'),
	importProfile: (data: unknown) =>
		request<ProfileImportResult>('POST', '/api/auth/profile/import', data),

	// Admin (role checked by the backend too)
	createBackup: () => request<Backup>('POST', '/api/admin/backup'),
	listBackups: () => request<Backup[]>('GET', '/api/admin/backups'),
	restoreBackup: (name: string) => request<RestoreResult>('POST', '/api/admin/restore', { name })
};
