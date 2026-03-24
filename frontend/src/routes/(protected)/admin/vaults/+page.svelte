<script lang="ts">
	import { auth } from "$lib/auth.svelte";
	import { getVaults } from "$lib/api";
	import { onMount } from "svelte";
	import * as Card from "$lib/components/ui/card/index.js";
	import * as Table from "$lib/components/ui/table/index.js";
	import { Progress } from "$lib/components/ui/progress/index.js";
	import { Skeleton } from "$lib/components/ui/skeleton/index.js";
	import { Badge } from "$lib/components/ui/badge/index.js";
	import { Warehouse, ShieldCheck, MapPin } from "@lucide/svelte";

	let vaults = $state<any[]>([]);
	let loading = $state(true);

	// Derived metrics
	let totalCapacity = $derived(
		vaults.reduce((sum, v) => sum + (v.capacity_kg || 0), 0),
	);
	let currentLoad = $derived(
		vaults.reduce((sum, v) => sum + (v.current_load_kg || 0), 0),
	);
	let globalUtilization = $derived(
		totalCapacity > 0 ? (currentLoad / totalCapacity) * 100 : 0,
	);

	async function loadVaults() {
		if (!auth.token) return;
		try {
			vaults = await getVaults(auth.token);
		} catch (e) {
			console.error("Failed to load vaults:", e);
		} finally {
			loading = false;
		}
	}

	onMount(loadVaults);
</script>

<div class="flex flex-1 flex-col px-6 py-6 md:px-10 md:py-8">
	<div class="mx-auto flex w-full max-w-7xl flex-1 flex-col">
		<div class="mb-8 flex flex-col gap-4 md:flex-row md:items-end md:justify-between">
			<div class="space-y-1">
				<h1 class="text-3xl font-bold tracking-tight text-foreground">
					Vault Management
				</h1>
				<p class="text-sm text-muted-foreground">
					Monitor and manage physical storage facilities.
				</p>
			</div>
		</div>

		<div class="grid gap-6 md:grid-cols-3 mb-8">
			<Card.Root>
				<Card.Header class="pb-2">
					<Card.Title class="text-[10px] font-black uppercase tracking-widest text-muted-foreground">Total Capacity</Card.Title>
				</Card.Header>
				<Card.Content>
					<div class="text-2xl font-black">{totalCapacity.toLocaleString()} <span class="text-xs font-bold opacity-40">KG</span></div>
				</Card.Content>
			</Card.Root>
			<Card.Root>
				<Card.Header class="pb-2">
					<Card.Title class="text-[10px] font-black uppercase tracking-widest text-muted-foreground">Current Load</Card.Title>
				</Card.Header>
				<Card.Content>
					<div class="text-2xl font-black">{currentLoad.toLocaleString()} <span class="text-xs font-bold opacity-40">KG</span></div>
				</Card.Content>
			</Card.Root>
			<Card.Root>
				<Card.Header class="pb-2">
					<Card.Title class="text-[10px] font-black uppercase tracking-widest text-muted-foreground">Global Utilization</Card.Title>
				</Card.Header>
				<Card.Content>
					<div class="flex items-center gap-4">
						<div class="text-2xl font-black">{globalUtilization.toFixed(1)}%</div>
						<Progress value={globalUtilization} class="h-2 bg-slate-100 flex-1" />
					</div>
				</Card.Content>
			</Card.Root>
		</div>

		<div class="rounded-xl border border-slate-200/60 overflow-hidden shadow-sm bg-card">
			<Table.Root>
				<Table.Header>
					<Table.Row class="hover:bg-transparent border-b bg-muted/30">
						<Table.Head class="h-11 text-[10px] font-bold uppercase tracking-widest px-6">Facility</Table.Head>
						<Table.Head class="h-11 text-[10px] font-bold uppercase tracking-widest">Location</Table.Head>
						<Table.Head class="h-11 text-[10px] font-bold uppercase tracking-widest">Utilization</Table.Head>
						<Table.Head class="h-11 text-[10px] font-bold uppercase tracking-widest">Load / Capacity</Table.Head>
						<Table.Head class="h-11 text-[10px] font-bold uppercase tracking-widest">Status</Table.Head>
					</Table.Row>
				</Table.Header>
				<Table.Body>
					{#if loading}
						{#each Array(3) as _}
							<Table.Row>
								<Table.Cell class="px-6"><Skeleton class="h-6 w-32" /></Table.Cell>
								<Table.Cell><Skeleton class="h-6 w-24" /></Table.Cell>
								<Table.Cell><Skeleton class="h-2 w-32" /></Table.Cell>
								<Table.Cell><Skeleton class="h-6 w-20" /></Table.Cell>
								<Table.Cell><Skeleton class="h-6 w-16" /></Table.Cell>
							</Table.Row>
						{/each}
					{:else}
						{#each vaults as vault}
							{@const util = (vault.current_load_kg / vault.capacity_kg) * 100}
							<Table.Row class="group transition-colors border-b last:border-0 hover:bg-slate-50/80">
								<Table.Cell class="px-6">
									<div class="flex items-center gap-3">
										<div class="flex size-8 items-center justify-center rounded-lg bg-slate-900 text-white">
											<Warehouse class="size-4" />
										</div>
										<span class="font-bold text-sm tracking-tight">{vault.name}</span>
									</div>
								</Table.Cell>
								<Table.Cell>
									<div class="flex items-center gap-1.5 text-xs text-muted-foreground">
										<MapPin class="size-3" />
										{vault.location}
									</div>
								</Table.Cell>
								<Table.Cell>
									<div class="flex items-center gap-3">
										<Progress value={util} class="h-1.5 w-24 bg-slate-100 {util > 90 ? '[&>div]:bg-amber-500' : '[&>div]:bg-primary'}" />
										<span class="text-[10px] font-black text-primary">{util.toFixed(0)}%</span>
									</div>
								</Table.Cell>
								<Table.Cell>
									<div class="flex flex-col">
										<span class="text-sm font-bold tracking-tight">{vault.current_load_kg.toLocaleString()} KG</span>
										<span class="text-[9px] font-bold text-muted-foreground uppercase tracking-widest">Limit: {vault.capacity_kg.toLocaleString()} KG</span>
									</div>
								</Table.Cell>
								<Table.Cell>
									<Badge variant={vault.status === 'ACTIVE' ? 'default' : 'secondary'} class="text-[9px] font-black uppercase">
										{vault.status}
									</Badge>
								</Table.Cell>
							</Table.Row>
						{/each}
					{/if}
				</Table.Body>
			</Table.Root>
		</div>
	</div>
</div>
