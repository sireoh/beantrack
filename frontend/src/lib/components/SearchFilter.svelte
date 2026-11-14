<!-- Title search + status filter for a list page. Reads the list store; no extra fetch. -->
<script lang="ts">
	import { ChevronDown, Search } from 'lucide-svelte';
	import { closeDropdown, countByStatus } from '$lib/list-view';
	import { STATUS_COLORS, STATUS_LABELS, WATCH_STATUSES, type StatusFilter } from '$lib/status';
	import { movieFilter, movieList, tvFilter, tvList } from '$lib/stores/lists';

	let { kind }: { kind: 'tv' | 'movie' } = $props();

	const filter = kind === 'tv' ? tvFilter : movieFilter;

	const counts = $derived(
		kind === 'tv'
			? countByStatus($tvList?.entries ?? [], (e) => e.status)
			: countByStatus($movieList?.entries ?? [], (e) => e.status)
	);

	const options: { value: StatusFilter; label: string; color: string | undefined }[] = [
		{ value: 'all', label: 'All', color: undefined },
		...WATCH_STATUSES.map((s) => ({ value: s, label: STATUS_LABELS[s], color: STATUS_COLORS[s] }))
	];
	const selected = $derived(options.find((o) => o.value === $filter.status) ?? options[0]);

	function setStatus(value: StatusFilter) {
		filter.update((f) => ({ ...f, status: value }));
	}
</script>

<div class="mb-4 flex flex-col gap-3">
	<label class="input w-full">
		<Search size={16} class="opacity-60" />
		<input
			type="search"
			class="grow"
			placeholder="Filter by title…"
			aria-label="Filter by title"
			value={$filter.query}
			oninput={(e) => filter.update((f) => ({ ...f, query: e.currentTarget.value }))}
		/>
	</label>

	<!-- Desktop: tabs -->
	<div role="tablist" class="tabs-border tabs hidden lg:flex">
		{#each options as option (option.value)}
			{@const active = option.value === $filter.status}
			<button
				type="button"
				role="tab"
				aria-selected={active}
				class="tab gap-2 {active ? 'tab-active' : ''}"
				style:border-color={active ? (option.color ?? 'currentColor') : undefined}
				onclick={() => setStatus(option.value)}
			>
				{#if option.color}
					<span class="size-2.5 rounded-full" style:background-color={option.color}></span>
				{/if}
				{option.label}
				<span class="badge badge-ghost badge-sm">{counts[option.value] ?? 0}</span>
			</button>
		{/each}
	</div>

	<!-- Mobile / tablet: dropdown -->
	<div class="dropdown w-full lg:hidden">
		<div tabindex="0" role="button" class="btn w-full justify-between">
			<span class="flex items-center gap-2">
				{#if selected.color}
					<span class="size-2.5 rounded-full" style:background-color={selected.color}></span>
				{/if}
				{selected.label}
				<span class="badge badge-ghost badge-sm">{counts[selected.value] ?? 0}</span>
			</span>
			<ChevronDown size={16} />
		</div>
		<ul tabindex="-1" class="dropdown-content menu z-30 mt-1 w-full rounded-box bg-base-100 p-2 shadow-lg">
			{#each options as option (option.value)}
				<li>
					<button
						type="button"
						class={option.value === $filter.status ? 'menu-active' : ''}
						onclick={() => {
							setStatus(option.value);
							closeDropdown();
						}}
					>
						<span
							class="size-2.5 rounded-full {option.color ? '' : 'border border-base-content/40'}"
							style:background-color={option.color}
						></span>
						{option.label}
						<span class="ml-auto badge badge-ghost badge-sm">{counts[option.value] ?? 0}</span>
					</button>
				</li>
			{/each}
		</ul>
	</div>
</div>
