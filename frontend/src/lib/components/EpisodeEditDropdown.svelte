<script lang="ts">
	import type { TvListEntry } from '$lib/api/types';
	import EditDropdown from './EditDropdown.svelte';
	import TvEditPanel from './TvEditPanel.svelte';

	let { entry }: { entry: TvListEntry } = $props();
</script>

<EditDropdown label="Edit {entry.show.title}">
	<TvEditPanel {entry} />
</EditDropdown>
