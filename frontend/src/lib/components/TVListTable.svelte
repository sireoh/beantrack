<script lang="ts">
	import { Pencil, Star } from 'lucide-svelte';
	import type { TvListEntry } from '$lib/api/types';
	import { deleteTvEntry, episodeCode } from '$lib/list-edit';
	import {
		closeDropdown,
		filterEntries,
		nextSort,
		sortEntries,
		type EntryAccessors,
		type SortKey,
		type SortState
	} from '$lib/list-view';
	import { tvFilter, tvList } from '$lib/stores/lists';
	import { showError, showToast } from '$lib/stores/toasts';
	import ConfirmModal from './ConfirmModal.svelte';
	import EditMobileModal from './EditMobileModal.svelte';
	import EpisodeEditDropdown from './EpisodeEditDropdown.svelte';
	import Poster from './Poster.svelte';
	import SortHeader from './SortHeader.svelte';
	import StatusSliver from './StatusSliver.svelte';
	import TitleLink from './TitleLink.svelte';
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

	// Delete confirmation (shared by every layout).
	let deleting = $state<{ imdb: string; title: string } | null>(null);
	let confirmOpen = $state(false);

	function askDelete(entry: TvListEntry) {
		closeDropdown();
		modalOpen = false;
		deleting = { imdb: entry.show.imdb, title: entry.show.title };
		confirmOpen = true;
	}

	async function confirmDelete() {
		if (!deleting) return;
		try {
			await deleteTvEntry(deleting.imdb);
			showToast(`Removed ${deleting.title}`, 'success', 2500);
		} catch (e) {
			showError(e);
		}
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
					<SortHeader label="" key="status" {sort} {onsort} class="w-24" />
					<th class="w-28 text-center">Image</th>
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
						<td><StatusSliver status={entry.status} /></td>
						<td>
							<Poster
								src={meta?.image ?? entry.show.image}
								wide={Boolean(meta?.image)}
								imdb={entry.show.imdb}
								alt={entry.show.title}
							/>
						</td>
						<td class="w-full">
							<div class="font-semibold"><TitleLink imdb={entry.show.imdb} title={entry.show.title} /></div>
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
						<td><EpisodeEditDropdown {entry} ondelete={() => askDelete(entry)} /></td>
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
					<SortHeader label="" key="status" {sort} {onsort} class="w-16" />
					<th class="w-14 text-center">Image</th>
					<SortHeader label="Title" key="title" {sort} {onsort} />
					<th class="w-12">Edit</th>
				</tr>
			</thead>
			<tbody>
				{#each rows as entry (entry.show.imdb)}
					<tr>
						<td><StatusSliver status={entry.status} /></td>
						<td><Poster src={entry.show.image} imdb={entry.show.imdb} alt={entry.show.title} /></td>
						<td class="w-full font-semibold">
							<TitleLink imdb={entry.show.imdb} title={entry.show.title} />
						</td>
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
	{#if editing}
		{@const entry = editing}
		<TvEditPanel {entry} ondelete={() => askDelete(entry)} />
	{/if}
</EditMobileModal>

<ConfirmModal
	bind:open={confirmOpen}
	title="Remove {deleting?.title ?? 'this show'} from your list?"
	message="Your progress for this show will be deleted."
	confirmLabel="Delete"
	danger
	onconfirm={confirmDelete}
/>
