<!-- /discover/tv and /discover/movies: a grid that loads the next TMDB page near the bottom. -->
<script lang="ts">
	import type { MediaType } from '$lib/api/types';
	import { discoverStore } from '$lib/stores/discover';
	import { ensureMovieList, ensureTvList, movieImdbs, tvImdbs } from '$lib/stores/lists';
	import { addStatus } from '$lib/stores/search';
	import { showError } from '$lib/stores/toasts';
	import { user } from '$lib/stores/user';
	import DiscoverCard from './DiscoverCard.svelte';
	import StatusSelect from './StatusSelect.svelte';

	let { type, heading }: { type: MediaType; heading: string } = $props();

	const store = $derived(discoverStore(type));
	const listed = $derived(type === 'tv' ? tvImdbs : movieImdbs);

	let sentinel = $state<HTMLElement>();
	let failed = $state(false);
	// Start loading this far before the bottom is actually reached.
	const LOOKAHEAD_PX = 800;

	$effect(() => {
		if ($user) (type === 'tv' ? ensureTvList() : ensureMovieList()).catch(showError);
	});

	function sentinelIsNear(): boolean {
		return !!sentinel && sentinel.getBoundingClientRect().top < window.innerHeight + LOOKAHEAD_PX;
	}

	async function loadMore() {
		if (failed || $store.loading || !store.hasMore()) return;
		try {
			await ($store.page === 0 ? store.ensureFirstPage() : store.loadNextPage());
		} catch (e) {
			failed = true;
			showError(e);
			return;
		}
		// A tall screen can still show the bottom after a page: keep going until it doesn't.
		requestAnimationFrame(() => {
			if (sentinelIsNear()) loadMore();
		});
	}

	$effect(() => {
		if (!sentinel) return;
		const observer = new IntersectionObserver(
			(entries) => {
				if (entries.some((entry) => entry.isIntersecting)) loadMore();
			},
			{ rootMargin: `0px 0px ${LOOKAHEAD_PX}px 0px` }
		);
		observer.observe(sentinel);
		return () => observer.disconnect();
	});

	function retry() {
		failed = false;
		loadMore();
	}
</script>

<div class="mb-6 flex flex-col gap-2 sm:flex-row sm:items-center sm:justify-between">
	<h1 class="text-2xl font-bold">{heading}</h1>
	<StatusSelect label="Add as" value={$addStatus} onchange={(status) => addStatus.set(status)} />
</div>

<div class="grid grid-cols-1 gap-3 sm:grid-cols-2 sm:gap-4 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5">
	{#each $store.items as item (item.tmdb_id)}
		<DiscoverCard {type} {item} inList={item.imdb !== null && $listed.has(item.imdb)} />
	{/each}
</div>

{#if failed}
	<div class="flex justify-center py-8">
		<button type="button" class="btn" onclick={retry}>Try again</button>
	</div>
{:else if store.hasMore() || $store.loading}
	<div bind:this={sentinel} class="flex justify-center py-8">
		<span class="loading loading-lg loading-spinner"></span>
	</div>
{:else if $store.items.length === 0}
	<p class="py-16 text-center text-base-content/60">Nothing to show right now.</p>
{/if}
