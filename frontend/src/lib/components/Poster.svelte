<script lang="ts">
	import { ImageOff } from 'lucide-svelte';
	import { imdbUrl } from '$lib/config';

	let {
		src,
		imdb,
		alt,
		wide = false
	}: {
		src: string | null | undefined;
		imdb: string;
		alt: string;
		/** Episode stills are landscape; posters are portrait. */
		wide?: boolean;
	} = $props();
</script>

<a
	href={imdbUrl(imdb)}
	target="_blank"
	rel="noopener noreferrer"
	class="mx-auto block shrink-0 overflow-hidden rounded bg-base-300 {wide
		? 'h-14 w-24'
		: 'h-16 w-11'}"
	title="Open on IMDb"
>
	{#if src}
		<img {src} {alt} loading="lazy" class="h-full w-full object-cover object-center" />
	{:else}
		<span class="flex h-full w-full items-center justify-center opacity-50">
			<ImageOff size={18} />
		</span>
	{/if}
</a>
