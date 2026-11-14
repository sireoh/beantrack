<script lang="ts">
	import { CircleAlert, CircleCheck } from 'lucide-svelte';
	import { toasts } from '$lib/stores/toasts';
</script>

<div class="toast toast-end toast-bottom z-50" aria-live="polite">
	{#each $toasts as toast (toast.id)}
		<div role="alert" class="alert {toast.kind === 'error' ? 'alert-error' : 'alert-success'}">
			{#if toast.kind === 'error'}<CircleAlert size={18} />{:else}<CircleCheck size={18} />{/if}
			<span>{toast.message}</span>
		</div>
	{/each}
</div>
