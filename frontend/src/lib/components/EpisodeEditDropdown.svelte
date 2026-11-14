<script lang="ts">
	import type { TvListEntry } from '$lib/api/types';
	import EditDropdown from './EditDropdown.svelte';
	import TvEditPanel from './TvEditPanel.svelte';

	let { entry, ondelete }: { entry: TvListEntry; ondelete: () => void } = $props();
</script>

<EditDropdown label="Edit {entry.show.title}">
	<TvEditPanel {entry} {ondelete} />
</EditDropdown>
