/** Human-readable formatting for the settings page. */

const dateTime = new Intl.DateTimeFormat(undefined, {
	month: 'short',
	day: 'numeric',
	year: 'numeric',
	hour: 'numeric',
	minute: '2-digit'
});

/** e.g. "Nov 14, 2026, 3:42 AM" in the viewer's locale and time zone. */
export function formatDateTime(iso: string): string {
	return dateTime.format(new Date(iso));
}

/** e.g. "2.1 MB". */
export function formatBytes(bytes: number): string {
	if (bytes < 1024) return `${bytes} B`;
	const units = ['KB', 'MB', 'GB'];
	let value = bytes / 1024;
	let unit = 0;
	while (value >= 1024 && unit < units.length - 1) {
		value /= 1024;
		unit++;
	}
	return `${value.toFixed(value < 10 ? 1 : 0)} ${units[unit]}`;
}
