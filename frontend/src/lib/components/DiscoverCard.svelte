<!-- A TMDB Discover title: SearchCard's layout, with genres in place of the IMDb line. -->
<script lang="ts">
	import type { DiscoverItem, MediaType } from '$lib/api/types';
	import { tmdbPosterUrl } from '$lib/config';
	import { genreNames } from '$lib/genres';
	import DiscoverAdd from './DiscoverAdd.svelte';
	import MediaCard from './MediaCard.svelte';

	let {
		type,
		item,
		inList,
		vertical = false
	}: { type: MediaType; item: DiscoverItem; inList: boolean; vertical?: boolean } = $props();

	const genres = $derived(genreNames(type, item.genre_ids));
</script>

<MediaCard
	imdb={item.imdb}
	title={item.title}
	year={item.date?.slice(0, 4) || null}
	image={tmdbPosterUrl(item.poster_path)}
	score={item.score}
	showScore={item.score !== null}
	{vertical}
>
	{#snippet details()}{genres}{/snippet}
	{#snippet action()}<DiscoverAdd {type} {item} {inList} />{/snippet}
</MediaCard>
