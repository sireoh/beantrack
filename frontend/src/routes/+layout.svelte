<script lang="ts">
	import '../app.css';
	import type { Snippet } from 'svelte';
	import { onMount } from 'svelte';
	import Navbar from '$lib/components/Navbar.svelte';
	import Toasts from '$lib/components/Toasts.svelte';
	import { loadUser } from '$lib/stores/user';

	let { children }: { children: Snippet } = $props();

	onMount(loadUser);
</script>

<div class="flex min-h-dvh flex-col bg-base-100 text-base-content">
	<Navbar />
	<main class="mx-auto w-full max-w-7xl flex-1 px-3 py-4 sm:px-6 sm:py-6">
		{@render children()}
	</main>
</div>
<Toasts />
