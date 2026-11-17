<!-- Poster card layout shared by SearchCard and DiscoverCard. -->
<script lang="ts">
	import type { Snippet } from 'svelte';
	import { ImageOff, Star } from 'lucide-svelte';
	import { imdbUrl } from '$lib/config';

	let {
		imdb,
		title,
		year,
		image,
		score,
		showScore,
		vertical = false,
		details,
		action
	}: {
		/** Links the title to IMDb when known. */
		imdb: string | null;
		title: string;
		year: string | null;
		image: string | null;
		score: number | null;
		/** Show the score row ("No score" when `score` is null). */
		showScore: boolean;
		/** Always poster-on-top (carousels); otherwise a row on phones, a column from sm up. */
		vertical?: boolean;
		/** Small text line under the score. */
		details: Snippet;
		/** The add button. */
		action: Snippet;
	} = $props();

	const label = $derived(year ? `${title} (${year})` : title);
</script>

<article class="card h-full bg-base-200 shadow-sm {vertical ? '' : 'flex-row sm:flex-col'}">
	<figure class="aspect-[2/3] shrink-0 bg-base-300 {vertical ? 'w-full' : 'w-24 sm:w-full'}">
		{#if image}
			<img src={image} alt="" loading="lazy" class="h-full w-full object-cover" />
		{:else}
			<ImageOff size={32} class="opacity-40" />
		{/if}
	</figure>

	<div class="card-body min-w-0 gap-2 p-3 {vertical ? '' : 'sm:p-4'}">
		<h2 class="card-title text-base leading-snug">
			{#if imdb}
				<a href={imdbUrl(imdb)} target="_blank" rel="noopener noreferrer" class="link link-hover">
					{label}
				</a>
			{:else}
				{label}
			{/if}
		</h2>

		{#if showScore}
			<div class="flex items-center gap-1 text-sm">
				<Star size={14} class="text-warning" />
				{score === null ? 'No score' : score.toFixed(1)}
			</div>
		{/if}
		<div class="text-xs text-base-content/60">{@render details()}</div>

		<div class="mt-auto card-actions justify-end">{@render action()}</div>
	</div>
</article>
