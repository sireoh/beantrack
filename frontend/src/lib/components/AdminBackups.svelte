<!-- Admin only (the backend enforces it too): manual B2 snapshots, restore and delete. -->
<script lang="ts">
	import { onMount } from 'svelte';
	import { DatabaseBackup, History, RefreshCw, Trash2 } from 'lucide-svelte';
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
	let restoreOpen = $state(false);
	let deleteTarget = $state<Backup | null>(null);
	let deleteOpen = $state(false);

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
		restoreOpen = true;
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

	function askDelete(backup: Backup) {
		deleteTarget = backup;
		deleteOpen = true;
	}

	async function remove() {
		if (!deleteTarget) return;
		try {
			await api.deleteBackup(deleteTarget.id);
			showToast(`Deleted backup from ${formatDateTime(deleteTarget.created_at)}`, 'success');
		} catch (e) {
			showError(e);
		}
		await refresh();
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

		<h3 class="font-semibold">Backups</h3>
		{#if listError}
			<div role="alert" class="alert alert-error">{listError}</div>
		{:else if backups === null}
			<span class="loading loading-spinner"></span>
		{:else if backups.length === 0}
			<p class="text-sm text-base-content/60">No manual backups yet.</p>
		{:else}
			<ul class="flex flex-col divide-y divide-base-300 rounded-box bg-base-100">
				{#each backups as backup (backup.id)}
					<li class="flex flex-wrap items-center gap-2 px-3 py-2">
						<span class="min-w-0 flex-1">
							{describe(backup)}
							{#if backup.name.includes('-pre-restore')}
								<span class="ml-1 badge badge-ghost badge-sm">before restore</span>
							{/if}
						</span>
						<button type="button" class="btn btn-sm" onclick={() => askRestore(backup)}>
							<History size={16} /> Restore
						</button>
						<button
							type="button"
							class="btn btn-ghost btn-sm text-error"
							aria-label="Delete backup from {formatDateTime(backup.created_at)}"
							onclick={() => askDelete(backup)}
						>
							<Trash2 size={16} />
							<span class="hidden sm:inline">Delete</span>
						</button>
					</li>
				{/each}
			</ul>
		{/if}
	</div>
</section>

<ConfirmModal
	bind:open={restoreOpen}
	title="Restore this backup?"
	message={restoreTarget
		? `The live database will be replaced with the backup from ${describe(restoreTarget)}. ` +
			'Changes made since then will be lost (a safety backup of the current data is taken first).'
		: ''}
	confirmLabel="Restore"
	danger
	onconfirm={restore}
/>

<ConfirmModal
	bind:open={deleteOpen}
	title={deleteTarget
		? `Delete backup from ${formatDateTime(deleteTarget.created_at)}? This can't be undone.`
		: 'Delete backup?'}
	confirmLabel="Delete"
	danger
	onconfirm={remove}
/>
