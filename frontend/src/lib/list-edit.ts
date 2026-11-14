/**
 * Edit actions shared by the desktop edit dropdown and the mobile edit modal:
 * episode loading, +/- progress, jump to an episode, status changes and episode search.
 * Every action updates the list stores with the server's response.
 */
import { api } from '$lib/api/client';
import type { Episode, MovieListEntry, TvListEntry } from '$lib/api/types';
import type { WatchStatus } from '$lib/status';
import { ensureEpisodes } from '$lib/stores/episodes';
import {
	removeMovieEntry,
	removeTvEntry,
	replaceMovieEntry,
	replaceTvEntry
} from '$lib/stores/lists';

export { ensureEpisodes as loadEpisodes };

export const clampIndex = (index: number, episodeCount: number): number =>
	Math.min(Math.max(index, 0), Math.max(episodeCount - 1, 0));

/** The episode the index points at, after clamping into range. */
export function episodeAt(episodes: Episode[], index: number): Episode | undefined {
	return episodes[clampIndex(index, episodes.length)];
}

/** Whether +/- would actually change anything (always true until progress is first saved). */
export function canStep(entry: TvListEntry, episodes: Episode[], delta: 1 | -1): boolean {
	if (episodes.length === 0) return false;
	if (entry.current_episode_metadata === null) return true;
	return clampIndex(entry.current_episode + delta, episodes.length) !== entry.current_episode;
}

/** Move progress by one episode (`delta`), sending the episode at the new index. */
export async function stepProgress(entry: TvListEntry, delta: 1 | -1): Promise<void> {
	const list = await ensureEpisodes(entry.show.imdb);
	const next = episodeAt(list, entry.current_episode + delta);
	if (!next) return;
	const updated = await api.updateTvProgress(entry.show.imdb, {
		delta,
		current_episode_metadata: next
	});
	replaceTvEntry(updated);
}

/** Jump straight to the episode at `index` (`set_to`). */
export async function jumpToEpisode(entry: TvListEntry, index: number): Promise<void> {
	const list = await ensureEpisodes(entry.show.imdb);
	const target = list[index];
	if (!target) return;
	const updated = await api.updateTvProgress(entry.show.imdb, {
		set_to: index,
		current_episode_metadata: target
	});
	replaceTvEntry(updated);
}

export async function setTvStatus(entry: TvListEntry, status: WatchStatus): Promise<void> {
	if (status === entry.status) return;
	replaceTvEntry(await api.updateTvStatus(entry.show.imdb, status));
}

export async function setMovieStatus(entry: MovieListEntry, status: WatchStatus): Promise<void> {
	if (status === entry.status) return;
	replaceMovieEntry(await api.updateMovieStatus(entry.movie.imdb, status));
}

export async function deleteTvEntry(imdb: string): Promise<void> {
	await api.deleteTv(imdb);
	removeTvEntry(imdb);
}

export async function deleteMovieEntry(imdb: string): Promise<void> {
	await api.deleteMovie(imdb);
	removeMovieEntry(imdb);
}

/** `S1.E2`, or `S1 Special` for episodes without a number. */
export function episodeCode(episode: Pick<Episode, 'season' | 'number'>): string {
	return episode.number === null
		? `S${episode.season} Special`
		: `S${episode.season}.E${episode.number}`;
}

export interface IndexedEpisode {
	episode: Episode;
	/** Position in the full episode list: the value for `set_to`. */
	index: number;
}

/**
 * Filter episodes by title, or by `season.episode` notation:
 * `2.5` -> S2E5, `2.` -> all of season 2, `s2e5` also works.
 */
export function filterEpisodes(episodes: Episode[], query: string): IndexedEpisode[] {
	const all = episodes.map((episode, index) => ({ episode, index }));
	const q = query.trim().toLowerCase();
	if (!q) return all;

	const code = q.match(/^s?(\d+)\s*(?:[.x]|e)\s*(\d*)$/);
	if (code) {
		const season = Number(code[1]);
		const number = code[2] ? Number(code[2]) : null;
		return all.filter(
			({ episode }) =>
				episode.season === season && (number === null || episode.number === number)
		);
	}
	return all.filter(({ episode }) => episode.title.toLowerCase().includes(q));
}
