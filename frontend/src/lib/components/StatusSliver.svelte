<script lang="ts">
	import { STATUS_COLORS, STATUS_LABELS, type WatchStatus } from '$lib/status';

	let { status }: { status: WatchStatus } = $props();
</script>

<div
	class="h-12 w-1.5 rounded-full"
	style:background-color={STATUS_COLORS[status]}
	title={STATUS_LABELS[status]}
	role="img"
	aria-label={STATUS_LABELS[status]}
></div>
