<!-- Export / import the user's watchlists as a JSON file. -->
<script lang="ts">
	import { Download, Upload } from 'lucide-svelte';
	import { api } from '$lib/api/client';
	import type { ProfileImportResult } from '$lib/api/types';
	import { invalidateLists } from '$lib/stores/lists';
	import { showError, showToast } from '$lib/stores/toasts';

	let exporting = $state(false);
	let importing = $state(false);
	let result = $state<ProfileImportResult | null>(null);
	let fileInput: HTMLInputElement;

	async function exportLists() {
		exporting = true;
		try {
			const data = await api.exportProfile();
			const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
			const url = URL.createObjectURL(blob);
			const link = document.createElement('a');
			link.href = url;
			link.download = `beantrack-export-${new Date().toISOString().slice(0, 10)}.json`;
			link.click();
			URL.revokeObjectURL(url);
		} catch (e) {
			showError(e);
		} finally {
			exporting = false;
		}
	}

	async function importFile(event: Event) {
		const input = event.currentTarget as HTMLInputElement;
		const file = input.files?.[0];
		input.value = ''; // allow choosing the same file again
		if (!file) return;

		let data: unknown;
		try {
			data = JSON.parse(await file.text());
		} catch {
			showToast(`${file.name} is not a valid JSON file`);
			return;
		}

		importing = true;
		result = null;
		try {
			result = await api.importProfile(data);
			invalidateLists(); // the list pages refetch on their next visit
		} catch (e) {
			showError(e);
		} finally {
			importing = false;
		}
	}
</script>

<section class="card bg-base-200">
	<div class="card-body gap-4">
		<h2 class="card-title">Import / export watchlists</h2>
		<p class="text-sm text-base-content/70">
			The export holds your list entries only (IDs, status, progress and dates). Show and movie
			details are looked up again when you import.
		</p>

		<div class="flex flex-wrap gap-2">
			<button type="button" class="btn btn-primary" disabled={exporting} onclick={exportLists}>
				{#if exporting}<span class="loading loading-xs loading-spinner"></span>{:else}<Download
						size={18}
					/>{/if}
				Export
			</button>
			<button type="button" class="btn" disabled={importing} onclick={() => fileInput.click()}>
				{#if importing}<span class="loading loading-xs loading-spinner"></span>{:else}<Upload
						size={18}
					/>{/if}
				{importing ? 'Importing…' : 'Import'}
			</button>
			<input
				bind:this={fileInput}
				type="file"
				accept=".json,application/json"
				class="hidden"
				onchange={importFile}
			/>
		</div>

		{#if importing}
			<p class="text-sm text-base-content/70">
				Titles that aren't cached on the server yet are fetched one by one, so a large import can
				take a minute.
			</p>
		{/if}

		{#if result}
			<div role="status" class="alert {result.failed ? 'alert-warning' : 'alert-success'}">
				<span>
					Imported {result.imported}
					{result.imported === 1 ? 'entry' : 'entries'}{#if result.skipped}, {result.skipped} already
						in your lists{/if}{#if result.failed}, {result.failed} failed{/if}.
				</span>
			</div>
			{#if result.failures.length}
				<ul class="list-inside list-disc text-sm text-base-content/80">
					{#each result.failures as failure, i (i)}
						<li>
							<span class="font-mono">{failure.imdb ?? '?'}</span>
							({failure.kind === 'tv' ? 'TV' : 'movie'}): {failure.reason}
						</li>
					{/each}
				</ul>
			{/if}
		{/if}
	</div>
</section>
