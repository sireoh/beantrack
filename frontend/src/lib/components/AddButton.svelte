<!-- The card "Add" button: login link when logged out, "Added" when in the list, spinner while adding. -->
<script lang="ts">
	import { Check, LogIn, Plus } from 'lucide-svelte';

	let {
		loggedIn,
		inList,
		adding,
		loginHref = '/login',
		disabledReason = null,
		onadd
	}: {
		loggedIn: boolean;
		inList: boolean;
		adding: boolean;
		loginHref?: string;
		/** When set, the button is disabled and this explains why (tooltip). */
		disabledReason?: string | null;
		onadd: () => void;
	} = $props();
</script>

{#if !loggedIn}
	<!-- <a href={loginHref} class="btn btn-sm btn-primary" aria-label="Log in to add">
		<LogIn size={16} />
		<span class="hidden sm:inline">Login to Add</span>
	</a> -->
{:else if inList}
	<button class="btn btn-sm" disabled aria-label="Already in your list">
		<Check size={16} />
		<span class="hidden sm:inline">Added</span>
	</button>
{:else}
	<button
		class="btn btn-sm btn-primary"
		disabled={adding || disabledReason !== null}
		title={disabledReason ?? undefined}
		aria-label="Add"
		onclick={onadd}
	>
		{#if adding}
			<span class="loading loading-xs loading-spinner"></span>
		{:else}
			<Plus size={16} />
		{/if}
		<span class="hidden sm:inline">Add</span>
	</button>
{/if}
