<script lang="ts">
	import DiscoverCarousel from '$lib/components/DiscoverCarousel.svelte';
	import StatusSelect from '$lib/components/StatusSelect.svelte';
	import { addStatus } from '$lib/stores/search';
</script>

<svelte:head><title>BeanTrack</title></svelte:head>

<div class="flex flex-col gap-8">
	<div class="flex flex-col gap-2 sm:flex-row sm:items-center sm:justify-between">
		<h1 class="text-2xl font-bold">Discover</h1>
		<StatusSelect label="Add as" value={$addStatus} onchange={(status) => addStatus.set(status)} />
	</div>
	<DiscoverCarousel type="tv" heading="Discover TV" href="/discover/tv" />
	<DiscoverCarousel type="movie" heading="Discover Movies" href="/discover/movies" />
</div>
