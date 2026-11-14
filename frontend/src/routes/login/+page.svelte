<script lang="ts">
	import { CircleCheck, Film, Tv } from 'lucide-svelte';
	import LandingPage from '$lib/components/LandingPage.svelte';
	import { user, userLoaded } from '$lib/stores/user';
</script>

<svelte:head><title>Login · BeanTrack</title></svelte:head>

{#if !$userLoaded}
	<div class="flex justify-center py-24"><span class="loading loading-lg loading-spinner"></span></div>
{:else if $user}
	<section class="flex flex-col items-center gap-4 py-24 text-center">
		<CircleCheck size={48} class="text-success" />
		<h1 class="text-2xl font-bold">You're logged in as {$user.username}</h1>
		<div class="flex flex-wrap justify-center gap-2">
			<a href="/tvlist" class="btn"><Tv size={18} /> TV List</a>
			<a href="/movielist" class="btn"><Film size={18} /> Movie List</a>
		</div>
	</section>
{:else}
	<LandingPage />
{/if}
