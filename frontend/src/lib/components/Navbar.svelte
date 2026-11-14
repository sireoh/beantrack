<script lang="ts">
	import {
		Bean,
		ChevronDown,
		Film,
		LogIn,
		LogOut,
		Settings,
		Tv,
		UserRound
	} from 'lucide-svelte';
	import { page } from '$app/state';
	import { closeDropdown } from '$lib/list-view';
	import { logout, user, userLoaded } from '$lib/stores/user';
	import SearchBar from './SearchBar.svelte';
	import ThemeController from './ThemeController.svelte';

	// Search needs a login, and /search has its own search bar.
	const showSearch = $derived($user !== null && page.url.pathname !== '/search');

	async function handleLogout() {
		closeDropdown();
		await logout();
	}
</script>

<header class="sticky top-0 z-40 bg-base-200 shadow-sm">
	<nav class="navbar gap-2 px-2 sm:px-4">
		<div class="shrink-0">
			<a href="/" class="btn gap-1 px-2 text-lg btn-ghost sm:text-xl">
				<Bean size={22} class="text-primary" />
				BeanTrack
			</a>
		</div>

		<div class="hidden flex-1 justify-center md:flex">
			{#if showSearch}
				<div class="w-full max-w-xl"><SearchBar size="sm" /></div>
			{/if}
		</div>

		<div class="ml-auto shrink-0">
			{#if !$userLoaded}
				<div class="skeleton size-8 rounded-full"></div>
			{:else if $user}
				<div class="dropdown dropdown-end">
					<div tabindex="0" role="button" class="btn gap-2 px-2 btn-ghost">
						<div class="avatar">
							<div class="w-8 rounded-full bg-base-300">
								{#if $user.avatar_url}
									<img src={$user.avatar_url} alt="" />
								{:else}
									<UserRound size={20} class="m-1.5" />
								{/if}
							</div>
						</div>
						<span class="hidden max-w-32 truncate sm:inline">{$user.username}</span>
						<ChevronDown size={16} />
					</div>
					<ul
						tabindex="-1"
						class="dropdown-content menu z-50 mt-2 w-56 rounded-box bg-base-100 p-2 shadow-lg"
					>
						<li><a href="/tvlist" onclick={closeDropdown}><Tv size={16} /> TV List</a></li>
						<li>
							<a href="/movielist" onclick={closeDropdown}><Film size={16} /> Movie List</a>
						</li>
						<li>
							<a href="/settings" onclick={closeDropdown}><Settings size={16} /> Settings</a>
						</li>
						<li class="pointer-events-none my-1 h-px bg-base-300" role="separator"></li>
						<li><ThemeController /></li>
						<li><button type="button" onclick={handleLogout}><LogOut size={16} /> Logout</button></li>
					</ul>
				</div>
			{:else}
				<a href="/login" class="btn btn-sm btn-primary">
					<LogIn size={16} />
					<span class="hidden sm:inline">Login</span>
				</a>
			{/if}
		</div>
	</nav>

	<!-- Phones: the search bar gets its own row under the navbar. -->
	{#if showSearch}
		<div class="px-2 pb-2 md:hidden"><SearchBar size="sm" /></div>
	{/if}
</header>
