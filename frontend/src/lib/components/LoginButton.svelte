<script lang="ts">
	import { LogIn } from 'lucide-svelte';
	import { page } from '$app/state';
	import { loginUrl } from '$lib/config';

	// On /login, return to `?next=` (set by Discover's Add); elsewhere, to the current page.
	const next = $derived(
		page.url.pathname === '/login'
			? page.url.searchParams.get('next')
			: page.url.pathname + page.url.search
	);
</script>

<!-- A plain link: the backend redirects to Discord, then back to the app with the session cookie. -->
<a href={loginUrl(next)} class="btn btn-primary" data-sveltekit-reload>
	<LogIn size={18} />
	Login with Discord
</a>
