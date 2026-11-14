<script lang="ts">
	import LandingPage from '$lib/components/LandingPage.svelte';
	import MovieListTable from '$lib/components/MovieListTable.svelte';
	import SearchFilter from '$lib/components/SearchFilter.svelte';
	import { ensureMovieList, movieList } from '$lib/stores/lists';
	import { showError } from '$lib/stores/toasts';
	import { user, userLoaded } from '$lib/stores/user';

	// Loads once; later visits reuse the store.
	$effect(() => {
		if ($user) ensureMovieList().catch(showError);
	});
</script>

<svelte:head><title>Movie List · BeanTrack</title></svelte:head>

{#if !$userLoaded}
	<div class="flex justify-center py-24"><span class="loading loading-lg loading-spinner"></span></div>
{:else if !$user}
	<LandingPage />
{:else}
	<h1 class="mb-4 text-2xl font-bold">Movie List</h1>
	<SearchFilter kind="movie" />
	{#if $movieList === null}
		<div class="flex justify-center py-16"><span class="loading loading-lg loading-spinner"></span></div>
	{:else if $movieList.entries.length === 0}
		<p class="py-16 text-center text-base-content/60">
			Your movie list is empty. Switch the search bar to Movie and search for a title.
		</p>
	{:else}
		<MovieListTable />
	{/if}
{/if}
