<!-- Add button for a Discover card. Logged out: goes to /login, then back to this page. -->
<script lang="ts">
	import { page } from '$app/state';
	import type { DiscoverItem, MediaType } from '$lib/api/types';
	import { addDiscoverItem } from '$lib/stores/discover';
	import { showError, showToast } from '$lib/stores/toasts';
	import { user } from '$lib/stores/user';
	import AddButton from './AddButton.svelte';

	let { type, item, inList }: { type: MediaType; item: DiscoverItem; inList: boolean } = $props();

	let adding = $state(false);

	const loginHref = $derived(`/login?next=${encodeURIComponent(page.url.pathname)}`);

	async function add() {
		adding = true;
		try {
			await addDiscoverItem(type, item);
			showToast(`Added ${item.title}`, 'success', 2500);
		} catch (e) {
			showError(e);
		} finally {
			adding = false;
		}
	}
</script>

<AddButton loggedIn={$user !== null} {inList} {adding} {loginHref} onadd={add} />
