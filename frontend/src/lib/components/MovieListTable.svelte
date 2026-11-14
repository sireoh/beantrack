<script lang="ts">
	import { Pencil, Star } from 'lucide-svelte';
	import type { MovieListEntry } from '$lib/api/types';
	import { setMovieStatus } from '$lib/list-edit';
	import {
		filterEntries,
		nextSort,
		sortEntries,
		type EntryAccessors,
		type SortKey,
		type SortState
	} from '$lib/list-view';
	import type { WatchStatus } from '$lib/status';
	import { movieFilter, movieList } from '$lib/stores/lists';
	import { showError } from '$lib/stores/toasts';
	import EditDropdown from './EditDropdown.svelte';
	import EditMobileModal from './EditMobileModal.svelte';
	import Poster from './Poster.svelte';
	import SortHeader from './SortHeader.svelte';
	import StatusPicker from './StatusPicker.svelte';
	import StatusSliver from './StatusSliver.svelte';

	const accessors: EntryAccessors<MovieListEntry> = {
		status: (e) => e.status,
		title: (e) => e.movie.title,
		score: (e) => e.movie.score
	};

	let sort = $state<SortState | null>(null);
	const rows = $derived(
		sortEntries(filterEntries($movieList?.entries ?? [], $movieFilter, accessors), sort, accessors)
	);

	function onsort(key: SortKey) {
		sort = nextSort(sort, key);
	}

	let busy = $state(false);
	async function changeStatus(entry: MovieListEntry, status: WatchStatus) {
		if (busy) return; // not disabled: that would blur the button and close the dropdown
		busy = true;
		try {
			await setMovieStatus(entry, status);
		} catch (e) {
			showError(e);
		} finally {
			busy = false;
		}
	}

	let editingImdb = $state<string | null>(null);
	let modalOpen = $state(false);
	const editing = $derived($movieList?.entries.find((e) => e.movie.imdb === editingImdb) ?? null);
</script>

{#if rows.length === 0}
	<p class="py-12 text-center text-base-content/60">No movies match this filter.</p>
{:else}
	<!-- Desktop -->
	<div class="hidden lg:block">
		<table class="table">
			<thead>
				<tr>
					<th class="w-2 pr-0"><span class="sr-only">Status</span></th>
					<th class="w-20">Image</th>
					<SortHeader label="Title" key="title" {sort} {onsort} />
					<SortHeader label="Score" key="score" {sort} {onsort} />
					<th class="w-12">Edit</th>
				</tr>
			</thead>
			<tbody>
				{#each rows as entry (entry.movie.imdb)}
					<tr class="hover:bg-base-200/60">
						<td class="pr-0"><StatusSliver status={entry.status} /></td>
						<td><Poster src={entry.movie.image} imdb={entry.movie.imdb} alt={entry.movie.title} /></td>
						<td class="w-full font-semibold">{entry.movie.title}</td>
						<td class="whitespace-nowrap">
							{#if entry.movie.score !== null}
								<span class="flex items-center gap-1">
									<Star size={14} class="text-warning" />
									{entry.movie.score.toFixed(1)}
								</span>
							{:else}
								<span class="text-base-content/40">—</span>
							{/if}
						</td>
						<td>
							<EditDropdown label="Edit {entry.movie.title}">
								<div class="mb-1 text-xs font-semibold uppercase text-base-content/60">Status</div>
								<StatusPicker
									value={entry.status}
									onchange={(s) => changeStatus(entry, s)}
								/>
							</EditDropdown>
						</td>
					</tr>
				{/each}
			</tbody>
		</table>
	</div>

	<!-- Mobile / tablet -->
	<div class="lg:hidden">
		<table class="table table-sm">
			<thead>
				<tr>
					<th class="w-2 pr-0"><span class="sr-only">Status</span></th>
					<th class="w-14">Image</th>
					<SortHeader label="Title" key="title" {sort} {onsort} />
					<th class="w-12">Edit</th>
				</tr>
			</thead>
			<tbody>
				{#each rows as entry (entry.movie.imdb)}
					<tr>
						<td class="pr-0"><StatusSliver status={entry.status} /></td>
						<td><Poster src={entry.movie.image} imdb={entry.movie.imdb} alt={entry.movie.title} /></td>
						<td class="w-full font-semibold">{entry.movie.title}</td>
						<td>
							<button
								type="button"
								class="btn btn-square btn-ghost btn-sm"
								aria-label="Edit {entry.movie.title}"
								onclick={() => {
									editingImdb = entry.movie.imdb;
									modalOpen = true;
								}}
							>
								<Pencil size={16} />
							</button>
						</td>
					</tr>
				{/each}
			</tbody>
		</table>
	</div>
{/if}

<EditMobileModal bind:open={modalOpen} title={editing?.movie.title ?? ''}>
	{#if editing}
		{@const entry = editing}
		<div class="mb-1 text-xs font-semibold uppercase text-base-content/60">Status</div>
		<StatusPicker value={entry.status} onchange={(s) => changeStatus(entry, s)} />
	{/if}
</EditMobileModal>
