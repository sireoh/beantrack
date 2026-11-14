<script lang="ts">
	import { ArrowDown, ArrowUp, ArrowUpDown } from 'lucide-svelte';
	import type { SortKey, SortState } from '$lib/list-view';

	let {
		label,
		key,
		sort,
		onsort
	}: { label: string; key: SortKey; sort: SortState | null; onsort: (key: SortKey) => void } =
		$props();

	const active = $derived(sort?.key === key);
</script>

<th aria-sort={active ? (sort?.dir === 'asc' ? 'ascending' : 'descending') : 'none'}>
	<button type="button" class="flex items-center gap-1 uppercase" onclick={() => onsort(key)}>
		{label}
		{#if !active}
			<ArrowUpDown size={14} class="opacity-40" />
		{:else if sort?.dir === 'asc'}
			<ArrowUp size={14} />
		{:else}
			<ArrowDown size={14} />
		{/if}
	</button>
</th>
