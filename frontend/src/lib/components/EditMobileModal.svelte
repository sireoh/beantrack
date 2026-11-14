<!--
  Mobile/tablet edit modal. Pass the same panel the desktop dropdown uses
  (TvEditPanel for shows, StatusPicker for movies) as children.
  Closes with the X button, the backdrop or Escape.
-->
<script lang="ts">
	import type { Snippet } from 'svelte';
	import { X } from 'lucide-svelte';

	let {
		open = $bindable(false),
		title,
		children
	}: { open?: boolean; title: string; children: Snippet } = $props();

	let dialog: HTMLDialogElement;

	$effect(() => {
		if (open && !dialog.open) dialog.showModal();
		else if (!open && dialog.open) dialog.close();
	});
</script>

<dialog bind:this={dialog} class="modal modal-bottom sm:modal-middle" onclose={() => (open = false)}>
	<div class="modal-box">
		<div class="mb-4 flex items-start gap-2">
			<h3 class="flex-1 text-lg font-bold">{title}</h3>
			<button
				type="button"
				class="btn btn-circle btn-ghost btn-sm"
				aria-label="Close"
				onclick={() => (open = false)}
			>
				<X size={18} />
			</button>
		</div>
		{#if open}{@render children()}{/if}
	</div>
	<form method="dialog" class="modal-backdrop"><button aria-label="Close">close</button></form>
</dialog>
