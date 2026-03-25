<script lang="ts">
	import { auth } from "$lib/auth.svelte";
	import { getMetals } from "$lib/api";
	import { onMount } from "svelte";
	import * as Table from "$lib/components/ui/table/index.js";
	import { Button } from "$lib/components/ui/button/index.js";
	import { Skeleton } from "$lib/components/ui/skeleton/index.js";
	import { Plus, Database, TrendingUp, Pencil } from "@lucide/svelte";
	import MetalModal from "$lib/components/metal-modal.svelte";

	let metals = $state<any[]>([]);
	let loading = $state(true);
	let showMetalModal = $state(false);
	let selectedMetal = $state<any>(null);

	async function loadMetals() {
		if (!auth.token) return;
		try {
			metals = await getMetals(auth.token);
		} catch (e) {
			console.error("Failed to load metals:", e);
		} finally {
			loading = false;
		}
	}

	function openNewMetal() {
		selectedMetal = null;
		showMetalModal = true;
	}

	function openEditMetal(metal: any) {
		selectedMetal = metal;
		showMetalModal = true;
	}

	onMount(loadMetals);
</script>

<div class="flex flex-1 flex-col px-6 py-6 md:px-10 md:py-8">
	<div class="mx-auto flex w-full max-w-7xl flex-1 flex-col">
		<div class="mb-8 flex flex-col gap-4 md:flex-row md:items-end md:justify-between">
			<div class="space-y-1">
				<h1 class="text-3xl font-bold tracking-tight text-foreground">
					Metal Management
				</h1>
				<p class="text-sm text-muted-foreground">
					Configure available assets and market prices.
				</p>
			</div>
			<Button onclick={openNewMetal} class="h-11 font-black uppercase tracking-widest text-xs gap-2 shadow-lg shadow-primary/20">
				<Plus class="size-4" />
				Initialize New Asset
			</Button>
		</div>

		<div class="grid gap-8">
			<div class="rounded-xl border border-slate-200/60 overflow-hidden shadow-sm bg-card">
				<Table.Root>
					<Table.Header>
						<Table.Row class="hover:bg-transparent border-b bg-muted/30">
							<Table.Head class="h-11 text-[10px] font-bold uppercase tracking-widest px-6">Asset</Table.Head>
							<Table.Head class="h-11 text-[10px] font-bold uppercase tracking-widest">Category</Table.Head>
							<Table.Head class="h-11 text-[10px] font-bold uppercase tracking-widest">Market Price</Table.Head>
							<Table.Head class="h-11 text-[10px] font-bold uppercase tracking-widest text-right px-6">Actions</Table.Head>
						</Table.Row>
					</Table.Header>
					<Table.Body>
						{#if loading}
							{#each Array(4) as _}
								<Table.Row>
									<Table.Cell class="px-6"><Skeleton class="h-10 w-full" /></Table.Cell>
									<Table.Cell><Skeleton class="h-6 w-24" /></Table.Cell>
									<Table.Cell><Skeleton class="h-6 w-24" /></Table.Cell>
									<Table.Cell class="px-6 text-right"><Skeleton class="h-8 w-8 ml-auto" /></Table.Cell>
								</Table.Row>
							{/each}
						{:else}
							{#each metals as metal}
								<Table.Row class="group transition-colors border-b last:border-0 hover:bg-slate-50/80">
									<Table.Cell class="px-6">
										<div class="flex items-center gap-3">
											<div class="flex size-9 items-center justify-center rounded-lg bg-primary/10 text-primary">
												<Database class="size-5" />
											</div>
											<div class="flex flex-col">
												<span class="font-bold text-sm tracking-tight">{metal.name}</span>
												<span class="text-[10px] font-mono text-muted-foreground">{metal.code}</span>
											</div>
										</div>
									</Table.Cell>
									<Table.Cell>
										<span class="text-xs font-bold text-muted-foreground uppercase tracking-wider">{metal.category}</span>
									</Table.Cell>
									<Table.Cell>
										<div class="flex items-center gap-1.5 text-sm font-black">
											<TrendingUp class="size-3.5 text-emerald-500" />
											${metal.current_price_kg?.toLocaleString()}
											<span class="text-[10px] font-bold opacity-40">/ KG</span>
										</div>
									</Table.Cell>
									<Table.Cell class="px-6 text-right">
										<Button variant="ghost" size="sm" class="h-8 w-8 p-0" onclick={() => openEditMetal(metal)}>
											<Pencil class="size-3.5" />
										</Button>
									</Table.Cell>
								</Table.Row>
							{/each}
						{/if}
					</Table.Body>
				</Table.Root>
			</div>
		</div>
	</div>
</div>

<MetalModal bind:open={showMetalModal} metal={selectedMetal} onSuccess={loadMetals} />
