/** Watch status, matching the backend's `WatchStatus` enum values. */
export enum WatchStatus {
	Watching = 'watching',
	Completed = 'completed',
	Planned = 'planned',
	Dropped = 'dropped'
}

export const WATCH_STATUSES: readonly WatchStatus[] = [
	WatchStatus.Watching,
	WatchStatus.Completed,
	WatchStatus.Planned,
	WatchStatus.Dropped
];

/** Theme variables (not hex values), so colors follow the active daisyUI theme. */
export const STATUS_COLORS: Record<WatchStatus, string> = {
	[WatchStatus.Watching]: 'var(--color-success)',
	[WatchStatus.Completed]: 'var(--color-primary)',
	[WatchStatus.Planned]: 'var(--color-neutral)',
	[WatchStatus.Dropped]: 'var(--color-error)'
};

export const STATUS_LABELS: Record<WatchStatus, string> = {
	[WatchStatus.Watching]: 'Watching',
	[WatchStatus.Completed]: 'Completed',
	[WatchStatus.Planned]: 'Planned',
	[WatchStatus.Dropped]: 'Dropped'
};

/** A list filter: one status, or every status. */
export type StatusFilter = WatchStatus | 'all';
