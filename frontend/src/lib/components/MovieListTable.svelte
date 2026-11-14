<script lang="ts">
	import { Pencil, Star } from 'lucide-svelte';
	import type { MovieListEntry } from '$lib/api/types';
	import { deleteMovieEntry } from '$lib/list-edit';
	import {
		closeDropdown,
		filterEntries,
		nextSort,
		sortEntries,
		type EntryAccessors,
		type SortKey,
		type SortState
	} from '$lib/list-view';
	import { movieFilter, movieList } from '$lib/stores/lists';
	import { showError, showToast } from '$lib/stores/toasts';
	import ConfirmModal from './ConfirmModal.svelte';
	import EditDropdown from './EditDropdown.svelte';
	import EditMobileModal from './EditMobileModal.svelte';
	import MovieEditPanel from './MovieEditPanel.svelte';
	import Poster from './Poster.svelte';
	import SortHeader from './SortHeader.svelte';
	import StatusSliver from './StatusSliver.svelte';
	import TitleLink from './TitleLink.svelte';

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

	let editingImdb = $state<string | null>(null);
	let modalOpen = $state(false);
	const editing = $derived($movieList?.entries.find((e) => e.movie.imdb === editingImdb) ?? null);

	// Delete confirmation (shared by every layout).
	let deleting = $state<{ imdb: string; title: string } | null>(null);
	let confirmOpen = $state(false);

	function askDelete(entry: MovieListEntry) {
		closeDropdown();
		modalOpen = false;
		deleting = { imdb: entry.movie.imdb, title: entry.movie.title };
		confirmOpen = true;
	}

	async function confirmDelete() {
		if (!deleting) return;
		try {
			await deleteMovieEntry(deleting.imdb);
			showToast(`Removed ${deleting.title}`, 'success', 2500);
		} catch (e) {
			showError(e);
		}
	}
</script>

{#if rows.length === 0}
	<p class="py-12 text-center text-base-content/60">No movies match this filter.</p>
{:else}
	<!-- Desktop -->
	<div class="hidden lg:block">
		<table class="table">
			<thead>
				<tr>
					<SortHeader label="" key="status" {sort} {onsort} class="w-24" />
					<th class="w-20 text-center">Image</th>
					<SortHeader label="Title" key="title" {sort} {onsort} />
					<SortHeader label="Score" key="score" {sort} {onsort} />
					<th class="w-12">Edit</th>
				</tr>
			</thead>
			<tbody>
				{#each rows as entry (entry.movie.imdb)}
					<tr class="hover:bg-base-200/60">
						<td><StatusSliver status={entry.status} /></td>
						<td><Poster src={entry.movie.image} imdb={entry.movie.imdb} alt={entry.movie.title} /></td>
						<td class="w-full font-semibold">
							<TitleLink imdb={entry.movie.imdb} title={entry.movie.title} />
						</td>
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
								<MovieEditPanel {entry} ondelete={() => askDelete(entry)} />
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
					<SortHeader label="" key="status" {sort} {onsort} class="w-16" />
					<th class="w-14 text-center">Image</th>
					<SortHeader label="Title" key="title" {sort} {onsort} />
					<th class="w-12">Edit</th>
				</tr>
			</thead>
			<tbody>
				{#each rows as entry (entry.movie.imdb)}
					<tr>
						<td><StatusSliver status={entry.status} /></td>
						<td><Poster src={entry.movie.image} imdb={entry.movie.imdb} alt={entry.movie.title} /></td>
						<td class="w-full font-semibold">
							<TitleLink imdb={entry.movie.imdb} title={entry.movie.title} />
						</td>
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
		<MovieEditPanel {entry} ondelete={() => askDelete(entry)} />
	{/if}
</EditMobileModal>

<ConfirmModal
	bind:open={confirmOpen}
	title="Remove {deleting?.title ?? 'this movie'} from your list?"
	confirmLabel="Delete"
	danger
	onconfirm={confirmDelete}
/>
