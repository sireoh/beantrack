/**
 * Shapes of the BeanTrack API (see backend/app/schemas). Field names match the JSON exactly.
 */
import type { WatchStatus } from '$lib/status';

export type MediaType = 'tv' | 'movie';

export type UserRole = 'user' | 'admin';

export type ThemeName = 'light' | 'dark';

export interface User {
	discord_id: string;
	username: string;
	avatar: string | null;
	avatar_url: string | null;
	created_at: string;
	last_login: string;
	role: UserRole;
	/** Saved light/dark preference; null until the user picks one. */
	theme: ThemeName | null;
}

// --- Search (GET /api/search) ---------------------------------------------------

/** TV search result. `imdb` is null when TVmaze has no IMDb id (such shows can't be added). */
export interface SearchTVCard {
	imdb: string | null;
	tvmaze_id: number; // not displayed; needed to add the show
	title: string;
	year: string | null;
	image: string | null;
	score: number | null;
}

/** Movie search result. OMDb search has no rating, and movies have no TVmaze id. */
export interface SearchMovieCard {
	imdb: string;
	title: string;
	year: string | null;
	image: string | null;
}

export interface SearchResponse<T> {
	type: MediaType;
	query: string;
	results: T[];
}

// --- TV list ---------------------------------------------------------------------

export interface TvShow {
	imdb: string;
	title: string;
	image: string | null;
	score: number | null;
	episodes_count: number;
}

export interface Episode {
	id: number;
	season: number;
	number: number | null; // null for specials
	title: string;
	image: string | null;
}

export interface TvListEntry {
	show: TvShow;
	status: WatchStatus;
	/** Zero-based index into the show's episode list (GET /api/tvlist/{imdb}/episodes). */
	current_episode: number;
	/** Cached copy of that episode; null until progress is first changed. */
	current_episode_metadata: Episode | null;
	added_at: string;
	updated_at: string;
}

export interface TvList {
	tvlist_id: string;
	entries: TvListEntry[];
}

export interface TvAddRequest {
	show: { imdb: string; tvmaze_id: number; title: string; image: string | null; score: number | null };
	status?: WatchStatus;
	current_episode?: number;
}

/** PATCH /api/tvlist/{imdb}/progress: exactly one of `delta` / `set_to`. */
export type TvProgressRequest =
	| { delta: number; current_episode_metadata: Episode }
	| { set_to: number; current_episode_metadata: Episode };

// --- Movie list ------------------------------------------------------------------

export interface Movie {
	imdb: string;
	title: string;
	image: string | null;
	score: number | null;
}

export interface MovieListEntry {
	movie: Movie;
	status: WatchStatus;
	added_at: string;
	updated_at: string;
}

export interface MovieList {
	movielist_id: string;
	entries: MovieListEntry[];
}

export interface MovieAddRequest {
	movie: { imdb: string; title: string; image: string | null };
	status?: WatchStatus;
}

// --- Profile export / import -----------------------------------------------------

/** The export file: list data only (no show/movie/episode metadata). */
export interface ProfileExport {
	format: 'beantrack-export';
	version: number;
	exported_at: string;
	tvlist: {
		imdb: string;
		tvmaze_id: number | null;
		status: WatchStatus;
		current_episode: number;
		current_episode_id: number | null;
		added_at: string | null;
		updated_at: string | null;
	}[];
	movielist: { imdb: string; status: WatchStatus; added_at: string | null; updated_at: string | null }[];
}

export interface ProfileImportResult {
	imported: number;
	skipped: number; // already in the list
	failed: number;
	failures: { kind: MediaType; imdb: string | null; reason: string }[];
}

// --- Admin backups ---------------------------------------------------------------

export interface Backup {
	id: string; // B2 file id
	name: string;
	size: number; // bytes
	created_at: string;
}

export interface RestoreResult {
	restored: Backup;
	safety_backup: Backup;
}
