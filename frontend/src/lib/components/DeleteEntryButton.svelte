<script lang="ts">
	import { Trash2 } from 'lucide-svelte';

	let { ondelete }: { ondelete: () => void } = $props();
</script>

<button
	type="button"
	class="btn w-full justify-start btn-outline btn-sm btn-error"
	onclick={ondelete}
>
	<Trash2 size={16} />
	Delete
</button>
