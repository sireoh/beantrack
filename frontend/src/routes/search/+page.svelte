<script lang="ts">
	import { SearchX } from 'lucide-svelte';
	import { SvelteSet } from 'svelte/reactivity';
	import { page } from '$app/state';
	import { ApiError } from '$lib/api/client';
	import LandingPage from '$lib/components/LandingPage.svelte';
	import SearchBar from '$lib/components/SearchBar.svelte';
	import SearchMovieCard from '$lib/components/SearchMovieCard.svelte';
	import SearchTVCard from '$lib/components/SearchTVCard.svelte';
	import { ensureMovieList, ensureTvList, movieList, tvList } from '$lib/stores/lists';
	import { addSearchResult, fetchSearch, searchMode, searchResults } from '$lib/stores/search';
	import { showError, showToast } from '$lib/stores/toasts';
	import { user, userLoaded } from '$lib/stores/user';

	const query = $derived((page.url.searchParams.get('q') ?? '').trim());

	let loading = $state(false);
	let error = $state<string | null>(null);
	const adding = new SvelteSet<string>();
	let requestId = 0;

	// Re-run whenever the query, the TV/Movie toggle or the login state changes.
	$effect(() => {
		const q = query;
		const mode = $searchMode;
		if (!$userLoaded || !$user || !q) return;

		const id = ++requestId;
		loading = true;
		error = null;
		fetchSearch(mode, q)
			.then((results) => {
				if (id === requestId) searchResults.set(results);
			})
			.catch((e: unknown) => {
				if (id !== requestId) return;
				error = e instanceof ApiError ? e.message : 'Search failed';
				searchResults.set(null);
			})
			.finally(() => {
				if (id === requestId) loading = false;
			});

		// Needed to mark results that are already in the user's list.
		(mode === 'tv' ? ensureTvList() : ensureMovieList()).catch(showError);
	});

	const results = $derived(
		$searchResults && $searchResults.query === query && $searchResults.type === $searchMode
			? $searchResults
			: null
	);

	const inList = $derived(
		new Set(
			results?.type === 'tv'
				? ($tvList?.entries.map((e) => e.show.imdb) ?? [])
				: ($movieList?.entries.map((e) => e.movie.imdb) ?? [])
		)
	);

	async function add(index: number, imdb: string | null, title: string) {
		if (!imdb) return;
		adding.add(imdb);
		try {
			await addSearchResult(index);
			showToast(`Added ${title}`, 'success', 2500);
		} catch (e) {
			showError(e);
		} finally {
			adding.delete(imdb);
		}
	}
</script>

<svelte:head><title>{query ? `${query} · ` : ''}Search · BeanTrack</title></svelte:head>

<div class="mb-6"><SearchBar /></div>

{#if !$userLoaded}
	<div class="flex justify-center py-24"><span class="loading loading-lg loading-spinner"></span></div>
{:else if !$user}
	<LandingPage message="Log in to search for shows and movies." />
{:else if !query}
	<p class="py-16 text-center text-base-content/60">
		Type a title above to search {$searchMode === 'tv' ? 'TV shows' : 'movies'}.
	</p>
{:else if loading && !results}
	<div class="flex justify-center py-24"><span class="loading loading-lg loading-spinner"></span></div>
{:else if error}
	<div role="alert" class="alert alert-error">{error}</div>
{:else if results && results.items.length === 0}
	<div class="flex flex-col items-center gap-2 py-16 text-base-content/60">
		<SearchX size={40} />
		<p>No {results.type === 'tv' ? 'shows' : 'movies'} found for "{query}".</p>
	</div>
{:else if results}
	<h1 class="mb-4 text-lg font-semibold">
		{results.type === 'tv' ? 'TV shows' : 'Movies'} matching "{query}"
		{#if loading}<span class="loading ml-2 loading-xs loading-spinner"></span>{/if}
	</h1>
	<div class="grid grid-cols-1 gap-3 sm:grid-cols-2 sm:gap-4 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5">
		{#if results.type === 'tv'}
			{#each results.items as card, index (card.tvmaze_id)}
				<SearchTVCard
					{card}
					loggedIn
					inList={card.imdb !== null && inList.has(card.imdb)}
					adding={card.imdb !== null && adding.has(card.imdb)}
					onadd={() => add(index, card.imdb, card.title)}
				/>
			{/each}
		{:else}
			{#each results.items as card, index (card.imdb)}
				<SearchMovieCard
					{card}
					loggedIn
					inList={inList.has(card.imdb)}
					adding={adding.has(card.imdb)}
					onadd={() => add(index, card.imdb, card.title)}
				/>
			{/each}
		{/if}
	</div>
{/if}
