<!-- Compact status dropdown (daisyUI dropdown, colored dots), e.g. "add as" on /search. -->
<script lang="ts">
	import { Check, ChevronDown } from 'lucide-svelte';
	import { closeDropdown } from '$lib/list-view';
	import { STATUS_COLORS, STATUS_LABELS, WATCH_STATUSES, type WatchStatus } from '$lib/status';

	let {
		value,
		onchange,
		label = 'Status'
	}: { value: WatchStatus; onchange: (status: WatchStatus) => void; label?: string } = $props();
</script>

<div class="dropdown dropdown-end">
	<div
		tabindex="0"
		role="button"
		class="btn w-full justify-between gap-2 sm:w-40"
		aria-label="{label}: {STATUS_LABELS[value]}"
		title={label}
	>
		<span class="flex items-center gap-2">
			<span class="size-2.5 rounded-full" style:background-color={STATUS_COLORS[value]}></span>
			{STATUS_LABELS[value]}
		</span>
		<ChevronDown size={16} />
	</div>
	<ul tabindex="-1" class="dropdown-content menu z-30 mt-1 w-48 rounded-box bg-base-100 p-2 shadow-lg">
		<li class="menu-title">{label}</li>
		{#each WATCH_STATUSES as status (status)}
			<li>
				<button
					type="button"
					class={status === value ? 'menu-active' : ''}
					onclick={() => {
						onchange(status);
						closeDropdown();
					}}
				>
					<span class="size-2.5 rounded-full" style:background-color={STATUS_COLORS[status]}
					></span>
					{STATUS_LABELS[status]}
					{#if status === value}<Check size={14} class="ml-auto" />{/if}
				</button>
			</li>
		{/each}
	</ul>
</div>
