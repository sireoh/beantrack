<script lang="ts">
	import type { SearchTVCard } from '$lib/api/types';
	import SearchCard from './SearchCard.svelte';

	let {
		card,
		inList,
		adding,
		loggedIn,
		onadd
	}: {
		card: SearchTVCard;
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
	score={card.score}
	showScore
	{inList}
	{adding}
	{loggedIn}
	{onadd}
/>
