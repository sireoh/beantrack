<script lang="ts">
	import { LogIn } from 'lucide-svelte';
	import { LOGIN_URL } from '$lib/config';
</script>

<!-- A plain link: the backend redirects to Discord, then back to the app with the session cookie. -->
<a href={LOGIN_URL} class="btn btn-primary" data-sveltekit-reload>
	<LogIn size={18} />
	Login with Discord
</a>
