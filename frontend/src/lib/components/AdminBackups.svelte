<!-- Admin only (the backend enforces it too): manual B2 snapshots and restore. -->
<script lang="ts">
	import { onMount } from 'svelte';
	import { DatabaseBackup, History, RefreshCw } from 'lucide-svelte';
	import { api, ApiError } from '$lib/api/client';
	import type { Backup } from '$lib/api/types';
	import { formatBytes, formatDateTime } from '$lib/format';
	import { resetLists } from '$lib/stores/lists';
	import { showError, showToast } from '$lib/stores/toasts';
	import { loadUser } from '$lib/stores/user';
	import ConfirmModal from './ConfirmModal.svelte';

	let backups = $state<Backup[] | null>(null);
	let listError = $state<string | null>(null);
	let creating = $state(false);
	let restoreTarget = $state<Backup | null>(null);
	let confirmOpen = $state(false);

	const describe = (b: Backup) => `${formatDateTime(b.created_at)} · ${formatBytes(b.size)}`;

	async function refresh() {
		listError = null;
		try {
			backups = await api.listBackups();
		} catch (e) {
			listError = e instanceof ApiError ? e.message : 'Could not list backups';
		}
	}

	async function createBackup() {
		creating = true;
		try {
			const backup = await api.createBackup();
			showToast(`Backup saved: ${describe(backup)}`, 'success');
			await refresh();
		} catch (e) {
			showError(e);
		} finally {
			creating = false;
		}
	}

	function askRestore(backup: Backup) {
		restoreTarget = backup;
		confirmOpen = true;
	}

	async function restore() {
		if (!restoreTarget) return;
		try {
			const result = await api.restoreBackup(restoreTarget.name);
			showToast(`Restored ${describe(result.restored)}`, 'success', 6000);
			// Everything may have changed (including whether this session still exists).
			resetLists();
			await loadUser();
			await refresh();
		} catch (e) {
			showError(e);
		}
	}

	onMount(refresh);
</script>

<section class="card border border-warning/40 bg-base-200">
	<div class="card-body gap-4">
		<h2 class="card-title">Admin · Database backups</h2>
		<p class="text-sm text-base-content/70">
			Manual snapshots of the SQLite database, stored in the B2 bucket next to the Litestream
			replica.
		</p>

		<div class="flex flex-wrap gap-2">
			<button type="button" class="btn btn-primary" disabled={creating} onclick={createBackup}>
				{#if creating}<span class="loading loading-xs loading-spinner"></span>{:else}<DatabaseBackup
						size={18}
					/>{/if}
				Back up now
			</button>
			<button type="button" class="btn btn-ghost" onclick={refresh} aria-label="Refresh list">
				<RefreshCw size={18} />
			</button>
		</div>

		<h3 class="font-semibold">Restore</h3>
		{#if listError}
			<div role="alert" class="alert alert-error">{listError}</div>
		{:else if backups === null}
			<span class="loading loading-spinner"></span>
		{:else if backups.length === 0}
			<p class="text-sm text-base-content/60">No manual backups yet.</p>
		{:else}
			<ul class="menu w-full rounded-box bg-base-100 p-1">
				{#each backups as backup (backup.name)}
					<li>
						<button type="button" class="justify-between" onclick={() => askRestore(backup)}>
							<span>
								{describe(backup)}
								{#if backup.name.includes('-pre-restore')}
									<span class="ml-1 badge badge-ghost badge-sm">before restore</span>
								{/if}
							</span>
							<span class="flex items-center gap-1 text-sm opacity-70"><History size={16} /> Restore</span>
						</button>
					</li>
				{/each}
			</ul>
		{/if}
	</div>
</section>

<ConfirmModal
	bind:open={confirmOpen}
	title="Restore this backup?"
	message={restoreTarget
		? `The live database will be replaced with the backup from ${describe(restoreTarget)}. ` +
			'Changes made since then will be lost (a safety backup of the current data is taken first).'
		: ''}
	confirmLabel="Restore"
	danger
	onconfirm={restore}
/>
