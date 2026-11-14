<!-- What you can edit on a movie: its status, or delete it. Shared by dropdown and modal. -->
<script lang="ts">
	import type { MovieListEntry } from '$lib/api/types';
	import { setMovieStatus } from '$lib/list-edit';
	import type { WatchStatus } from '$lib/status';
	import { showError } from '$lib/stores/toasts';
	import DeleteEntryButton from './DeleteEntryButton.svelte';
	import StatusPicker from './StatusPicker.svelte';

	let { entry, ondelete }: { entry: MovieListEntry; ondelete: () => void } = $props();

	let busy = $state(false);

	// Not `disabled` while busy: that would blur the button and close the desktop dropdown.
	async function changeStatus(status: WatchStatus) {
		if (busy) return;
		busy = true;
		try {
			await setMovieStatus(entry, status);
		} catch (e) {
			showError(e);
		} finally {
			busy = false;
		}
	}
</script>

<div class="flex flex-col gap-3" aria-busy={busy}>
	<div>
		<div class="mb-1 text-xs font-semibold text-base-content/60 uppercase">Status</div>
		<StatusPicker value={entry.status} onchange={changeStatus} />
	</div>
	<DeleteEntryButton {ondelete} />
</div>
