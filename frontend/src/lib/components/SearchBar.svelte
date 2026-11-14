<script lang="ts">
	import { Film, Search, Tv } from 'lucide-svelte';
	import { goto } from '$app/navigation';
	import { page } from '$app/state';
	import { searchMode } from '$lib/stores/search';

	let { size = 'md' }: { size?: 'sm' | 'md' } = $props();

	let query = $state('');

	// Mirror the URL's ?q= while on /search, so both search bars show the active query.
	$effect(() => {
		if (page.url.pathname === '/search') query = page.url.searchParams.get('q') ?? '';
	});

	const btnSize = $derived(size === 'sm' ? 'btn-sm' : '');
	const inputSize = $derived(size === 'sm' ? 'input-sm' : '');

	function submit(event: SubmitEvent) {
		event.preventDefault();
		const q = query.trim();
		if (q) goto(`/search?q=${encodeURIComponent(q)}`);
	}
</script>

<form class="join w-full" role="search" onsubmit={submit}>
	<button
		type="button"
		class="btn join-item {btnSize} {$searchMode === 'tv' ? 'btn-primary' : ''}"
		aria-pressed={$searchMode === 'tv'}
		title="Search TV shows"
		onclick={() => searchMode.set('tv')}
	>
		<Tv size={16} />
		<span class="hidden sm:inline">TV</span>
	</button>
	<button
		type="button"
		class="btn join-item {btnSize} {$searchMode === 'movie' ? 'btn-primary' : ''}"
		aria-pressed={$searchMode === 'movie'}
		title="Search movies"
		onclick={() => searchMode.set('movie')}
	>
		<Film size={16} />
		<span class="hidden sm:inline">Movie</span>
	</button>
	<label class="input join-item {inputSize} w-full min-w-0">
		<Search size={16} class="opacity-60" />
		<input
			type="search"
			class="grow"
			placeholder={$searchMode === 'tv' ? 'Search TV shows…' : 'Search movies…'}
			aria-label="Search"
			bind:value={query}
		/>
	</label>
	<button type="submit" class="btn btn-primary join-item {btnSize}" aria-label="Search">
		<Search size={16} />
	</button>
</form>
