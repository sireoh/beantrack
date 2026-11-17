<!-- Home page row of Discover cards. "Next" on the last card loads the following TMDB page. -->
<script lang="ts">
	import { tick } from 'svelte';
	import { ArrowRight, ChevronLeft, ChevronRight } from 'lucide-svelte';
	import type { MediaType } from '$lib/api/types';
	import { discoverStore } from '$lib/stores/discover';
	import { ensureMovieList, ensureTvList, movieImdbs, tvImdbs } from '$lib/stores/lists';
	import { showError } from '$lib/stores/toasts';
	import { user } from '$lib/stores/user';
	import DiscoverCard from './DiscoverCard.svelte';

	let { type, heading, href }: { type: MediaType; heading: string; href: string } = $props();

	const store = $derived(discoverStore(type));
	const listed = $derived(type === 'tv' ? tvImdbs : movieImdbs);

	let track = $state<HTMLDivElement>();
	let canPrev = $state(false);
	let atEnd = $state(false);

	$effect(() => {
		store.ensureFirstPage().catch(showError);
	});

	// Needed to mark titles that are already in the user's list.
	$effect(() => {
		if ($user) (type === 'tv' ? ensureTvList() : ensureMovieList()).catch(showError);
	});

	function updateEdges() {
		if (!track) return;
		canPrev = track.scrollLeft > 4;
		atEnd = track.scrollLeft + track.clientWidth >= track.scrollWidth - 8;
	}

	// Re-check the edges whenever cards are added.
	$effect(() => {
		void $store.items.length;
		tick().then(updateEdges);
	});

	function scrollPage(direction: 1 | -1) {
		track?.scrollBy({ left: direction * track.clientWidth * 0.9, behavior: 'smooth' });
	}

	async function next() {
		if (atEnd && store.hasMore()) {
			try {
				await store.loadNextPage();
			} catch (e) {
				showError(e);
				return;
			}
			await tick();
		}
		scrollPage(1);
	}
</script>

<section class="flex flex-col gap-3">
	<div class="flex items-center justify-between gap-2">
		<a {href} class="group flex items-center gap-2 text-xl font-bold hover:text-primary">
			{heading}
			<ArrowRight size={20} class="transition-transform group-hover:translate-x-1" />
		</a>
		<div class="flex gap-1">
			<button
				type="button"
				class="btn btn-circle btn-sm"
				aria-label="Previous"
				disabled={!canPrev}
				onclick={() => scrollPage(-1)}
			>
				<ChevronLeft size={18} />
			</button>
			<button
				type="button"
				class="btn btn-circle btn-sm"
				aria-label="Next"
				disabled={$store.loading || (atEnd && !store.hasMore())}
				onclick={next}
			>
				{#if $store.loading && $store.items.length > 0}
					<span class="loading loading-xs loading-spinner"></span>
				{:else}
					<ChevronRight size={18} />
				{/if}
			</button>
		</div>
	</div>

	{#if $store.items.length === 0}
		<div class="flex h-72 items-center justify-center rounded-box bg-base-200">
			{#if $store.loading}
				<span class="loading loading-lg loading-spinner"></span>
			{:else}
				<p class="text-base-content/60">Nothing to show right now.</p>
			{/if}
		</div>
	{:else}
		<div
			bind:this={track}
			onscroll={updateEdges}
			class="carousel carousel-start w-full gap-3 rounded-box pb-1"
		>
			{#each $store.items as item (item.tmdb_id)}
				<div class="carousel-item w-36 sm:w-44">
					<DiscoverCard
						{type}
						{item}
						vertical
						inList={item.imdb !== null && $listed.has(item.imdb)}
					/>
				</div>
			{/each}
		</div>
	{/if}
</section>

<svelte:window onresize={updateEdges} />
