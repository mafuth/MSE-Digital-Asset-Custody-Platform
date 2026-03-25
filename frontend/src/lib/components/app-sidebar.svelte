<script lang="ts">
	import { auth } from "$lib/auth.svelte";
	import NavMain from "./nav-main.svelte";
	import NavProjects from "./nav-projects.svelte";
	import NavSecondary from "./nav-secondary.svelte";
	import NavUser from "./nav-user.svelte";
	import * as Sidebar from "$lib/components/ui/sidebar/index.js";
	import type { ComponentProps } from "svelte";

	import LayoutDashboardIcon from "@lucide/svelte/icons/layout-dashboard";
	import PieChartIcon from "@lucide/svelte/icons/pie-chart";
	import HistoryIcon from "@lucide/svelte/icons/history";
	import TrendingUpIcon from "@lucide/svelte/icons/trending-up";
	import DatabaseIcon from "@lucide/svelte/icons/database";
	import UsersIcon from "@lucide/svelte/icons/users";
	import GlobeIcon from "@lucide/svelte/icons/globe";
	import FileTextIcon from "@lucide/svelte/icons/file-text";
	import SettingsIcon from "@lucide/svelte/icons/settings";
	import LifeBuoyIcon from "@lucide/svelte/icons/life-buoy";
	import SendIcon from "@lucide/svelte/icons/send";
	import GemIcon from "@lucide/svelte/icons/gem";
	import ShoppingBagIcon from "@lucide/svelte/icons/shopping-bag";
	import { Button } from "$lib/components/ui/button/index.js";
	import VaultIcon from "@lucide/svelte/icons/vault";
	import ShieldCheckIcon from "@lucide/svelte/icons/shield-check";

	let {
		ref = $bindable(null),
		...restProps
	}: ComponentProps<typeof Sidebar.Root> = $props();

	const isAdmin = $derived(auth.user?.type === "admin");

	const navPlatform = [
		{
			title: "Dashboard",
			url: "/",
			icon: LayoutDashboardIcon,
		},
		{
			title: "My Transactions",
			url: "/transactions",
			icon: HistoryIcon,
		},
	];

	const navAdmin = $derived(
		isAdmin
			? [
					{
						title: "Authorization Desk",
						url: "/admin/requests",
						icon: ShieldCheckIcon,
					},
					{
						title: "Vault Hub",
						url: "/admin/vaults",
						icon: VaultIcon,
					},
					{
						title: "Metals",
						url: "/admin/metals",
						icon: DatabaseIcon,
					},
					{
						title: "User Management",
						url: "/admin/accounts",
						icon: UsersIcon,
					},
				]
			: [],
	);

	const navSecondary = [
		{
			title: "Support",
			url: "mailto:support@baremetalspvt.com",
			icon: LifeBuoyIcon,
		},
	];

	const userData = $derived({
		name: auth.user?.name || "User",
		email: auth.user?.email || "",
		avatar: "/avatars/user.jpg",
	});
</script>

<Sidebar.Root bind:ref variant="inset" {...restProps}>
	<Sidebar.Header>
		<Sidebar.Menu>
			<Sidebar.MenuItem>
				<Sidebar.MenuButton size="lg">
					{#snippet child({ props })}
						<a href="/" {...props}>
							<div
								class="bg-primary text-primary-foreground flex aspect-square size-8 items-center justify-center rounded-lg"
							>
								<GemIcon class="size-4" />
							</div>
							<div
								class="grid flex-1 text-start text-sm leading-tight"
							>
								<span class="truncate font-medium"
									>Bare Metals</span
								>
								<span class="truncate text-xs"
									>Modern Custody</span
								>
							</div>
						</a>
					{/snippet}
				</Sidebar.MenuButton>
			</Sidebar.MenuItem>
		</Sidebar.Menu>
	</Sidebar.Header>
	<Sidebar.Content>
		<NavMain items={navPlatform} label="Platform" />
		{#if isAdmin}
			<NavMain items={navAdmin} label="Admin" />
		{/if}
		<div class="px-4 py-4 mt-auto">
			<NavSecondary items={navSecondary} />
			<Button variant="default" class="w-full" href="/buy">
				<DatabaseIcon class="size-4" />
				Buy Storage
			</Button>
		</div>
	</Sidebar.Content>
	<Sidebar.Footer class="border-t">
		<NavUser user={userData} />
	</Sidebar.Footer>
</Sidebar.Root>
