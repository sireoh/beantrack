<script lang="ts">
	import LandingPage from '$lib/components/LandingPage.svelte';
	import SearchFilter from '$lib/components/SearchFilter.svelte';
	import TVListTable from '$lib/components/TVListTable.svelte';
	import { ensureTvList, tvList } from '$lib/stores/lists';
	import { showError } from '$lib/stores/toasts';
	import { user, userLoaded } from '$lib/stores/user';

	// Loads once; later visits reuse the store.
	$effect(() => {
		if ($user) ensureTvList().catch(showError);
	});
</script>

<svelte:head><title>TV List · BeanTrack</title></svelte:head>

{#if !$userLoaded}
	<div class="flex justify-center py-24"><span class="loading loading-lg loading-spinner"></span></div>
{:else if !$user}
	<LandingPage />
{:else}
	<h1 class="mb-4 text-2xl font-bold">TV List</h1>
	<SearchFilter kind="tv" />
	{#if $tvList === null}
		<div class="flex justify-center py-16"><span class="loading loading-lg loading-spinner"></span></div>
	{:else if $tvList.entries.length === 0}
		<p class="py-16 text-center text-base-content/60">
			Your TV list is empty. Switch the search bar to TV and search for a show.
		</p>
	{:else}
		<TVListTable />
	{/if}
{/if}
