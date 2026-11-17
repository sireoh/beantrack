<!-- Admin only (the backend enforces it too): empty the cached TMDB Discover pages. -->
<script lang="ts">
	import { Eraser } from 'lucide-svelte';
	import { api } from '$lib/api/client';
	import { showError, showToast } from '$lib/stores/toasts';
	import ConfirmModal from './ConfirmModal.svelte';

	let confirmOpen = $state(false);

	async function clear() {
		try {
			await api.clearDiscoverCache();
			showToast('Discover cache cleared', 'success');
		} catch (e) {
			showError(e);
		}
	}
</script>

<section class="card border border-warning/40 bg-base-200">
	<div class="card-body gap-4">
		<h2 class="card-title">Admin · Discover cache</h2>
		<p class="text-sm text-base-content/70">
			Discover pages from TMDB are cached for 24 hours. Clearing the cache makes the next visit
			fetch fresh pages.
		</p>
		<div>
			<button type="button" class="btn btn-warning" onclick={() => (confirmOpen = true)}>
				<Eraser size={18} />
				Clear discover cache
			</button>
		</div>
	</div>
</section>

<ConfirmModal
	bind:open={confirmOpen}
	title="Clear the discover cache?"
	message="Every cached TV and movie Discover page is deleted. They are fetched from TMDB again the next time someone opens them."
	confirmLabel="Clear cache"
	danger
	onconfirm={clear}
/>
