<script lang="ts">
	import { Moon, Sun } from 'lucide-svelte';
	import { chooseTheme, theme } from '$lib/stores/theme';
</script>

<label class="flex cursor-pointer items-center justify-between gap-2">
	<span>Theme</span>
	<span class="flex items-center gap-2">
		<Sun size={16} aria-hidden="true" />
		<input
			type="checkbox"
			class="toggle toggle-sm"
			aria-label="Dark mode"
			checked={$theme !== 'light'}
			onchange={(e) => chooseTheme(e.currentTarget.checked ? 'dark' : 'light')}
		/>
		<Moon size={16} aria-hidden="true" />
	</span>
</label>
