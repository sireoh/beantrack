<!-- Shared layout behind SearchTVCard and SearchMovieCard. -->
<script lang="ts">
	import AddButton from './AddButton.svelte';
	import MediaCard from './MediaCard.svelte';

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
</script>

<MediaCard {imdb} {title} {year} {image} {score} {showScore}>
	{#snippet details()}IMDb: {imdb ?? 'unknown'}{/snippet}
	{#snippet action()}
		<AddButton
			{loggedIn}
			{inList}
			{adding}
			disabledReason={imdb ? null : 'No IMDb id, so this title cannot be added'}
			{onadd}
		/>
	{/snippet}
</MediaCard>
