import * as publicEnv from '$env/static/public';

// Read through a plain record so a missing variable is `undefined` instead of a build error.
const env = publicEnv as Record<string, string | undefined>;

/** API origin, without a trailing slash. Empty means "same origin as the frontend". */
export const API_URL = (env.PUBLIC_API_URL ?? '').replace(/\/+$/, '');

/** daisyUI theme used until the user picks one. */
export const DEFAULT_THEME = env.PUBLIC_DAISYUI_THEME?.trim() || 'dark';

/** Starts the backend's Discord OAuth flow (a full-page navigation, not a fetch). */
export const LOGIN_URL = `${API_URL}/api/auth/login`;

export const imdbUrl = (imdb: string): string => `https://www.imdb.com/title/${imdb}/`;
