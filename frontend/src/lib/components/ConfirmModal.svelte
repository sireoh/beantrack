<!-- Yes/no confirmation, built on the existing modal shell (EditMobileModal). -->
<script lang="ts">
	import EditMobileModal from './EditMobileModal.svelte';

	let {
		open = $bindable(false),
		title,
		message,
		confirmLabel,
		danger = false,
		onconfirm
	}: {
		open?: boolean;
		title: string;
		message?: string;
		confirmLabel: string;
		danger?: boolean;
		/** May be async; the modal stays open (buttons busy) until it settles. */
		onconfirm: () => unknown;
	} = $props();

	let busy = $state(false);

	async function confirm() {
		if (busy) return;
		busy = true;
		try {
			await onconfirm();
			open = false;
		} finally {
			busy = false;
		}
	}
</script>

<EditMobileModal bind:open {title}>
	{#if message}<p class="mb-4 text-base-content/80">{message}</p>{/if}
	<div class="modal-action mt-2">
		<button type="button" class="btn btn-ghost" disabled={busy} onclick={() => (open = false)}>
			Cancel
		</button>
		<button
			type="button"
			class="btn {danger ? 'btn-error' : 'btn-primary'}"
			disabled={busy}
			onclick={confirm}
		>
			{#if busy}<span class="loading loading-xs loading-spinner"></span>{/if}
			{confirmLabel}
		</button>
	</div>
</EditMobileModal>
