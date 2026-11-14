<!--
  Everything you can edit on a TV list entry: +/- episode, jump to an episode, status.
  Shared by EpisodeEditDropdown (desktop) and EditMobileModal (mobile/tablet); the
  logic itself lives in $lib/list-edit.
-->
<script lang="ts">
	import { Minus, Plus, Search } from 'lucide-svelte';
	import { ApiError } from '$lib/api/client';
	import type { TvListEntry } from '$lib/api/types';
	import {
		canStep,
		episodeCode,
		filterEpisodes,
		jumpToEpisode,
		loadEpisodes,
		setTvStatus,
		stepProgress
	} from '$lib/list-edit';
	import { episodes } from '$lib/stores/episodes';
	import { showError } from '$lib/stores/toasts';
	import DeleteEntryButton from './DeleteEntryButton.svelte';
	import StatusPicker from './StatusPicker.svelte';

	let { entry, ondelete }: { entry: TvListEntry; ondelete: () => void } = $props();

	let query = $state('');
	let busy = $state(false);
	let loadError = $state<string | null>(null);

	const list = $derived($episodes[entry.show.imdb]);
	const current = $derived(entry.current_episode_metadata);
	const currentIndex = $derived(current ? entry.current_episode : -1);
	const matches = $derived(list ? filterEpisodes(list, query) : []);

	// Fetch (or reuse cached) episodes when the panel opens.
	$effect(() => {
		loadError = null;
		loadEpisodes(entry.show.imdb).catch((e: unknown) => {
			loadError = e instanceof ApiError ? e.message : 'Could not load episodes';
		});
	});

	// Buttons stay enabled while a request runs: disabling the focused button would blur it
	// and close the desktop dropdown. Extra clicks are ignored instead.
	async function run(action: () => Promise<void>) {
		if (busy) return;
		busy = true;
		try {
			await action();
		} catch (e) {
			showError(e);
		} finally {
			busy = false;
		}
	}
</script>

<div class="flex flex-col gap-3" aria-busy={busy}>
	<div class="flex items-center gap-2">
		<button
			type="button"
			class="btn btn-square btn-sm"
			aria-label="Previous episode"
			disabled={!list || !canStep(entry, list, -1)}
			onclick={() => run(() => stepProgress(entry, -1))}
		>
			<Minus size={16} />
		</button>
		<div class="min-w-0 flex-1 text-center text-sm">
			{#if current}
				<div class="font-semibold">
					{episodeCode(current)}
					{#if busy}<span class="loading ml-1 loading-xs loading-spinner"></span>{/if}
				</div>
				<div class="truncate text-base-content/70" title={current.title}>{current.title}</div>
			{:else}
				<span class="text-base-content/60">Not started</span>
			{/if}
		</div>
		<button
			type="button"
			class="btn btn-square btn-sm"
			aria-label="Next episode"
			disabled={!list || !canStep(entry, list, 1)}
			onclick={() => run(() => stepProgress(entry, 1))}
		>
			<Plus size={16} />
		</button>
	</div>

	<label class="input input-sm w-full">
		<Search size={14} class="opacity-60" />
		<input
			type="search"
			class="grow"
			placeholder="Episode title or 2.5"
			aria-label="Find episode"
			bind:value={query}
		/>
	</label>

	<ul class="menu max-h-60 w-full flex-nowrap overflow-y-auto rounded-box bg-base-200 menu-sm">
		{#if loadError}
			<li class="disabled"><span class="text-error">{loadError}</span></li>
		{:else if !list}
			<li class="disabled"><span><span class="loading loading-xs loading-spinner"></span> Loading episodes…</span></li>
		{:else if list.length === 0}
			<li class="disabled"><span>No episodes yet</span></li>
		{:else if matches.length === 0}
			<li class="disabled"><span>No episodes match "{query}"</span></li>
		{:else}
			{#each matches as { episode, index } (episode.id)}
				<li>
					<button
						type="button"
						class={index === currentIndex ? 'menu-active' : ''}
						onclick={() => run(() => jumpToEpisode(entry, index))}
					>
						<span class="w-16 shrink-0 font-mono text-xs opacity-70">{episodeCode(episode)}</span>
						<span class="truncate">{episode.title}</span>
					</button>
				</li>
			{/each}
		{/if}
	</ul>

	<div>
		<div class="mb-1 text-xs font-semibold uppercase text-base-content/60">Status</div>
		<StatusPicker
			value={entry.status}
			onchange={(status) => run(() => setTvStatus(entry, status))}
		/>
	</div>

	<DeleteEntryButton {ondelete} />
</div>
