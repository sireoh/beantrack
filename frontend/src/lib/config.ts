import * as publicEnv from '$env/static/public';

// Read through a plain record so a missing variable is `undefined` instead of a build error.
const env = publicEnv as Record<string, string | undefined>;

/** API origin, without a trailing slash. Empty means "same origin as the frontend". */
export const API_URL = (env.PUBLIC_API_URL ?? '').replace(/\/+$/, '');

/** daisyUI theme used until the user picks one. */
export const DEFAULT_THEME = env.PUBLIC_DAISYUI_THEME?.trim() || 'dark';

/** Starts the backend's Discord OAuth flow (a full-page navigation, not a fetch). */
export const LOGIN_URL = `${API_URL}/api/auth/login`;

/** LOGIN_URL that brings the user back to app path `next` (e.g. "/discover/tv") afterwards. */
export const loginUrl = (next?: string | null): string =>
	next && next.startsWith('/') && !next.startsWith('//')
		? `${LOGIN_URL}?next=${encodeURIComponent(next)}`
		: LOGIN_URL;

/** TMDB poster for a `poster_path`, or null when there is none. */
export const tmdbPosterUrl = (posterPath: string | null): string | null =>
	posterPath ? `https://image.tmdb.org/t/p/w500${posterPath}` : null;

export const imdbUrl = (imdb: string): string => `https://www.imdb.com/title/${imdb}/`;
