<!-- Shared layout behind SearchTVCard and SearchMovieCard. -->
<script lang="ts">
	import { Check, ImageOff, LogIn, Plus, Star } from 'lucide-svelte';
	import { imdbUrl } from '$lib/config';

	let {
		imdb,
		title,
		year,
		image,
		score,
		showScore,
		inList,
		adding,
		loggedIn,
		onadd
	}: {
		imdb: string | null;
		title: string;
		year: string | null;
		image: string | null;
		score: number | null;
		showScore: boolean;
		inList: boolean;
		adding: boolean;
		loggedIn: boolean;
		onadd: () => void;
	} = $props();

	const label = $derived(year ? `${title} (${year})` : title);
</script>

<article class="card h-full flex-row bg-base-200 shadow-sm sm:flex-col">
	<figure class="aspect-[2/3] w-24 shrink-0 bg-base-300 sm:w-full">
		{#if image}
			<img src={image} alt="" loading="lazy" class="h-full w-full object-cover" />
		{:else}
			<ImageOff size={32} class="opacity-40" />
		{/if}
	</figure>

	<div class="card-body min-w-0 gap-2 p-3 sm:p-4">
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
		<div class="text-xs text-base-content/60">IMDb: {imdb ?? 'unknown'}</div>

		<div class="mt-auto card-actions justify-end">
			{#if !loggedIn}
				<a href="/login" class="btn btn-sm btn-primary" aria-label="Log in to add">
					<LogIn size={16} />
					<span class="hidden sm:inline">Add</span>
				</a>
			{:else if inList}
				<button class="btn btn-sm" disabled aria-label="Already in your list">
					<Check size={16} />
					<span class="hidden sm:inline">Added</span>
				</button>
			{:else}
				<button
					class="btn btn-sm btn-primary"
					disabled={adding || !imdb}
					title={imdb ? undefined : 'No IMDb id, so this title cannot be added'}
					aria-label="Add"
					onclick={onadd}
				>
					{#if adding}
						<span class="loading loading-xs loading-spinner"></span>
					{:else}
						<Plus size={16} />
					{/if}
					<span class="hidden sm:inline">Add</span>
				</button>
			{/if}
		</div>
	</div>
</article>
