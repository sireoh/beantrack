<script lang="ts">
	import { ArrowDown, ArrowUp, ArrowUpDown } from 'lucide-svelte';
	import type { SortKey, SortState } from '$lib/list-view';

	let {
		label,
		key,
		sort,
		onsort,
		class: className = ''
	}: {
		label: string;
		key: SortKey;
		sort: SortState | null;
		onsort: (key: SortKey) => void;
		class?: string;
	} = $props();

	const active = $derived(sort?.key === key);
</script>

<th
	class={className}
	aria-sort={active ? (sort?.dir === 'asc' ? 'ascending' : 'descending') : 'none'}
>
	<button type="button" class="flex items-center gap-1" onclick={() => onsort(key)}>
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
