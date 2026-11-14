<!-- A list entry's title, linking to its IMDb page (plain text when there is no IMDb id). -->
<script lang="ts">
	import { imdbUrl } from '$lib/config';

	let { imdb, title }: { imdb: string | null | undefined; title: string } = $props();
</script>

{#if imdb}
	<a href={imdbUrl(imdb)} target="_blank" rel="noopener noreferrer" class="link link-hover">
		{title}
	</a>
{:else}
	{title}
{/if}
