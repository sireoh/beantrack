<!--
  Desktop edit menu: a pencil button opening a daisyUI (focus-based) dropdown.
  The content is only mounted once the menu has been opened, so nothing is fetched
  for rows the user never edits.
-->
<script lang="ts">
	import type { Snippet } from 'svelte';
	import { Pencil } from 'lucide-svelte';

	let { label, children }: { label: string; children: Snippet } = $props();

	let opened = $state(false);
</script>

<div class="dropdown dropdown-end" onfocusin={() => (opened = true)}>
	<div tabindex="0" role="button" class="btn btn-square btn-ghost btn-sm" aria-label={label} title={label}>
		<Pencil size={16} />
	</div>
	<div
		tabindex="-1"
		class="dropdown-content z-30 mt-1 w-80 rounded-box border border-base-300 bg-base-100 p-3 shadow-xl"
	>
		{#if opened}{@render children()}{/if}
	</div>
</div>
