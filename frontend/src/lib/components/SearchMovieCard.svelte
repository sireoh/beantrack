<script lang="ts">
	import type { SearchMovieCard } from '$lib/api/types';
	import SearchCard from './SearchCard.svelte';

	let {
		card,
		inList,
		adding,
		loggedIn,
		onadd
	}: {
		card: SearchMovieCard;
		inList: boolean;
		adding: boolean;
		loggedIn: boolean;
		onadd: () => void;
	} = $props();
</script>

<SearchCard
	imdb={card.imdb}
	title={card.title}
	year={card.year}
	image={card.image}
	score={null}
	showScore={false}
	{inList}
	{adding}
	{loggedIn}
	{onadd}
/>
