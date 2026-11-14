<script lang="ts">
	import { Pencil, Star } from 'lucide-svelte';
	import type { TvListEntry } from '$lib/api/types';
	import { episodeCode } from '$lib/list-edit';
	import {
		filterEntries,
		nextSort,
		sortEntries,
		type EntryAccessors,
		type SortKey,
		type SortState
	} from '$lib/list-view';
	import { tvFilter, tvList } from '$lib/stores/lists';
	import EditMobileModal from './EditMobileModal.svelte';
	import EpisodeEditDropdown from './EpisodeEditDropdown.svelte';
	import Poster from './Poster.svelte';
	import SortHeader from './SortHeader.svelte';
	import StatusSliver from './StatusSliver.svelte';
	import TvEditPanel from './TvEditPanel.svelte';

	const accessors: EntryAccessors<TvListEntry> = {
		status: (e) => e.status,
		title: (e) => e.show.title,
		score: (e) => e.show.score
	};

	let sort = $state<SortState | null>(null);
	const rows = $derived(
		sortEntries(filterEntries($tvList?.entries ?? [], $tvFilter, accessors), sort, accessors)
	);

	function onsort(key: SortKey) {
		sort = nextSort(sort, key);
	}

	/** Episodes watched so far: the 1-based position of the current episode, 0 if not started. */
	const progress = (e: TvListEntry) => (e.current_episode_metadata ? e.current_episode + 1 : 0);

	// Mobile/tablet: a single modal, pointed at the row being edited.
	let editingImdb = $state<string | null>(null);
	let modalOpen = $state(false);
	const editing = $derived($tvList?.entries.find((e) => e.show.imdb === editingImdb) ?? null);

	function openModal(imdb: string) {
		editingImdb = imdb;
		modalOpen = true;
	}
</script>

{#if rows.length === 0}
	<p class="py-12 text-center text-base-content/60">No shows match this filter.</p>
{:else}
	<!-- Desktop -->
	<div class="hidden lg:block">
		<table class="table">
			<thead>
				<tr>
					<th class="w-2 pr-0"><span class="sr-only">Status</span></th>
					<th class="w-28">Image</th>
					<SortHeader label="Title" key="title" {sort} {onsort} />
					<SortHeader label="Score" key="score" {sort} {onsort} />
					<th>Progress</th>
					<th class="w-12">Edit</th>
				</tr>
			</thead>
			<tbody>
				{#each rows as entry (entry.show.imdb)}
					{@const meta = entry.current_episode_metadata}
					<tr class="hover:bg-base-200/60">
						<td class="pr-0"><StatusSliver status={entry.status} /></td>
						<td>
							<Poster
								src={meta?.image ?? entry.show.image}
								wide={Boolean(meta?.image)}
								imdb={entry.show.imdb}
								alt={entry.show.title}
							/>
						</td>
						<td class="w-full">
							<div class="font-semibold">{entry.show.title}</div>
							{#if meta}
								<div class="text-sm text-base-content/70">{meta.title} - {episodeCode(meta)}</div>
							{/if}
						</td>
						<td class="whitespace-nowrap">
							{#if entry.show.score !== null}
								<span class="flex items-center gap-1">
									<Star size={14} class="text-warning" />
									{entry.show.score.toFixed(1)}
								</span>
							{:else}
								<span class="text-base-content/40">—</span>
							{/if}
						</td>
						<td class="whitespace-nowrap tabular-nums">
							{progress(entry)} / {entry.show.episodes_count}
						</td>
						<td><EpisodeEditDropdown {entry} /></td>
					</tr>
				{/each}
			</tbody>
		</table>
	</div>

	<!-- Mobile / tablet: default poster and title only -->
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
				{#each rows as entry (entry.show.imdb)}
					<tr>
						<td class="pr-0"><StatusSliver status={entry.status} /></td>
						<td><Poster src={entry.show.image} imdb={entry.show.imdb} alt={entry.show.title} /></td>
						<td class="w-full font-semibold">{entry.show.title}</td>
						<td>
							<button
								type="button"
								class="btn btn-square btn-ghost btn-sm"
								aria-label="Edit {entry.show.title}"
								onclick={() => openModal(entry.show.imdb)}
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

<EditMobileModal bind:open={modalOpen} title={editing?.show.title ?? ''}>
	{#if editing}<TvEditPanel entry={editing} />{/if}
</EditMobileModal>
