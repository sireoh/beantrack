/** Filtering and sorting for the list tables (pure functions over list entries). */
import type { WatchStatus } from '$lib/status';
import type { ListFilter } from '$lib/stores/lists';

export type SortKey = 'title' | 'score';
export type SortDirection = 'asc' | 'desc';
export interface SortState {
	key: SortKey;
	dir: SortDirection;
}

export interface EntryAccessors<T> {
	status: (entry: T) => WatchStatus;
	title: (entry: T) => string;
	score: (entry: T) => number | null;
}

export function filterEntries<T>(entries: T[], filter: ListFilter, get: EntryAccessors<T>): T[] {
	const q = filter.query.trim().toLowerCase();
	return entries.filter(
		(entry) =>
			(filter.status === 'all' || get.status(entry) === filter.status) &&
			(!q || get.title(entry).toLowerCase().includes(q))
	);
}

/** Sort a copy. Entries without a score always go last. `null` keeps the list's own order. */
export function sortEntries<T>(entries: T[], sort: SortState | null, get: EntryAccessors<T>): T[] {
	if (!sort) return entries;
	const sign = sort.dir === 'asc' ? 1 : -1;
	return [...entries].sort((a, b) => {
		if (sort.key === 'title') {
			return sign * get.title(a).localeCompare(get.title(b), undefined, { sensitivity: 'base' });
		}
		const sa = get.score(a);
		const sb = get.score(b);
		if (sa === null && sb === null) return 0;
		if (sa === null) return 1;
		if (sb === null) return -1;
		return sign * (sa - sb);
	});
}

/** Clicking a header: first click sorts ascending, the next one flips the direction. */
export function nextSort(current: SortState | null, key: SortKey): SortState {
	if (current?.key === key) return { key, dir: current.dir === 'asc' ? 'desc' : 'asc' };
	return { key, dir: 'asc' };
}

export function countByStatus<T>(entries: T[], status: (entry: T) => WatchStatus) {
	const counts: Record<string, number> = { all: entries.length };
	for (const entry of entries) counts[status(entry)] = (counts[status(entry)] ?? 0) + 1;
	return counts;
}

/** Blur the focused element: closes daisyUI focus-based dropdowns after a choice. */
export function closeDropdown(): void {
	(document.activeElement as HTMLElement | null)?.blur();
}
