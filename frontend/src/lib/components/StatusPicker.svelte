<script lang="ts">
	import { Check } from 'lucide-svelte';
	import { STATUS_COLORS, STATUS_LABELS, WATCH_STATUSES, type WatchStatus } from '$lib/status';

	let {
		value,
		onchange,
		disabled = false
	}: {
		value: WatchStatus;
		onchange: (status: WatchStatus) => void;
		disabled?: boolean;
	} = $props();
</script>

<div class="grid grid-cols-2 gap-1" role="radiogroup" aria-label="Watch status">
	{#each WATCH_STATUSES as status (status)}
		{@const selected = status === value}
		<button
			type="button"
			role="radio"
			aria-checked={selected}
			class="btn btn-sm justify-start gap-2 font-normal {selected ? 'btn-outline' : 'btn-ghost'}"
			style:border-color={selected ? STATUS_COLORS[status] : undefined}
			{disabled}
			onclick={() => onchange(status)}
		>
			<span class="size-2.5 shrink-0 rounded-full" style:background-color={STATUS_COLORS[status]}
			></span>
			{STATUS_LABELS[status]}
			{#if selected}<Check size={14} class="ml-auto" />{/if}
		</button>
	{/each}
</div>
