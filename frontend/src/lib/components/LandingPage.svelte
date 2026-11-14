<script lang="ts">
	import { Bean } from 'lucide-svelte';
	import LoginButton from './LoginButton.svelte';

	let { message }: { message?: string } = $props();
</script>

<section class="hero py-16 sm:py-24">
	<div class="hero-content text-center">
		<div class="flex max-w-md flex-col items-center gap-4">
			<Bean size={56} class="text-primary" />
			<h1 class="text-4xl font-bold sm:text-5xl">BeanTrack</h1>
			<p class="text-base-content/70">
				Keep track of the TV shows and movies you're watching, finished, planning or dropped.
			</p>
			{#if message}<p class="text-sm text-base-content/60">{message}</p>{/if}
			<LoginButton />
		</div>
	</div>
</section>
