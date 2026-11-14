<!--
  Desktop edit menu: a pencil button opening a popover that is anchored to it with CSS
  anchor positioning (see `.anchored-menu` in app.css). `position-try-fallbacks` flips it
  above and/or to the other side when it would overflow the viewport, e.g. on the last rows.
  The popover is light-dismissed (outside click / Escape). Its content is only mounted once
  the menu has been opened, so nothing is fetched for rows the user never edits.
-->
<script lang="ts">
	import type { Snippet } from 'svelte';
	import { Pencil } from 'lucide-svelte';

	let { label, children }: { label: string; children: Snippet } = $props();

	const uid = $props.id();
	const popoverId = `edit-menu-${uid}`;
	const anchorName = `--edit-anchor-${uid}`;

	let opened = $state(false);
</script>

<button
	type="button"
	class="btn btn-square btn-ghost btn-sm"
	aria-label={label}
	title={label}
	popovertarget={popoverId}
	style:anchor-name={anchorName}
>
	<Pencil size={16} />
</button>
<div
	id={popoverId}
	popover="auto"
	class="anchored-menu w-80 rounded-box border border-base-300 bg-base-100 p-3 text-base-content shadow-xl"
	style:position-anchor={anchorName}
	ontoggle={(e) => {
		if ((e as ToggleEvent).newState === 'open') opened = true;
	}}
>
	{#if opened}{@render children()}{/if}
</div>
