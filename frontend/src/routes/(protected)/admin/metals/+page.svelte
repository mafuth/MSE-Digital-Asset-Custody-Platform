<script lang="ts">
	import { auth } from "$lib/auth.svelte";
	import { getMetals, addMetal } from "$lib/api";
	import { onMount } from "svelte";
	import * as Card from "$lib/components/ui/card/index.js";
	import * as Table from "$lib/components/ui/table/index.js";
	import { Button } from "$lib/components/ui/button/index.js";
	import { Input } from "$lib/components/ui/input/index.js";
	import { Label } from "$lib/components/ui/label/index.js";
	import { Skeleton } from "$lib/components/ui/skeleton/index.js";
	import { Plus, Database, TrendingUp } from "@lucide/svelte";

	let metals = $state<any[]>([]);
	let loading = $state(true);
	let submitting = $state(false);

	let newMetal = $state({
		code: "",
		name: "",
		current_price_kg: 0,
		category: ""
	});

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

	async function handleSubmit(e: Event) {
		e.preventDefault();
		if (!auth.token) return;
		submitting = true;
		try {
			await addMetal(auth.token, newMetal);
			newMetal = { code: "", name: "", current_price_kg: 0, category: "" };
			await loadMetals();
		} catch (e) {
			console.error("Failed to add metal:", e);
            alert("Failed to add metal. Ensure the code is unique.");
		} finally {
			submitting = false;
		}
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
		</div>

		<div class="grid gap-8 lg:grid-cols-12">
			<!-- Add Metal Form -->
			<div class="lg:col-span-4">
				<Card.Root>
					<Card.Header>
						<Card.Title class="text-base font-black uppercase tracking-wider flex items-center gap-2">
							<Plus class="size-4" />
							Add New Metal
						</Card.Title>
						<Card.Description class="text-xs uppercase font-bold tracking-widest opacity-60">System Inventory Definition</Card.Description>
					</Card.Header>
					<Card.Content>
						<form onsubmit={handleSubmit} class="space-y-4">
							<div class="space-y-2">
								<Label for="code" class="text-[10px] font-black uppercase tracking-widest">Symbol / Code</Label>
								<Input id="code" placeholder="e.g. AU99" bind:value={newMetal.code} required />
							</div>
							<div class="space-y-2">
								<Label for="name" class="text-[10px] font-black uppercase tracking-widest">Display Name</Label>
								<Input id="name" placeholder="e.g. 24K Gold" bind:value={newMetal.name} required />
							</div>
							<div class="space-y-2">
								<Label for="price" class="text-[10px] font-black uppercase tracking-widest">Initial Price (per KG)</Label>
								<Input id="price" type="number" step="0.01" bind:value={newMetal.current_price_kg} required />
							</div>
							<div class="space-y-2">
								<Label for="category" class="text-[10px] font-black uppercase tracking-widest">Asset Category</Label>
								<Input id="category" placeholder="e.g. Precious Metals" bind:value={newMetal.category} required />
							</div>
							<Button type="submit" class="w-full h-11 font-black uppercase tracking-widest text-xs gap-2" disabled={submitting}>
								{#if submitting}
									<div class="h-4 w-4 animate-spin rounded-full border-2 border-current border-t-transparent"></div>
								{:else}
									<Database class="size-4" />
								{/if}
								Create Asset
							</Button>
						</form>
					</Card.Content>
				</Card.Root>
			</div>

			<!-- Metals Table -->
			<div class="lg:col-span-8">
				<div class="rounded-xl border border-slate-200/60 overflow-hidden shadow-sm bg-card">
					<Table.Root>
						<Table.Header>
							<Table.Row class="hover:bg-transparent border-b bg-muted/30">
								<Table.Head class="h-11 text-[10px] font-bold uppercase tracking-widest px-6">Asset</Table.Head>
								<Table.Head class="h-11 text-[10px] font-bold uppercase tracking-widest">Market Price</Table.Head>
								<Table.Head class="h-11 text-[10px] font-bold uppercase tracking-widest">Config</Table.Head>
							</Table.Row>
						</Table.Header>
						<Table.Body>
							{#if loading}
								{#each Array(4) as _}
									<Table.Row>
										<Table.Cell class="px-6"><Skeleton class="h-10 w-full" /></Table.Cell>
										<Table.Cell><Skeleton class="h-6 w-24" /></Table.Cell>
										<Table.Cell><Skeleton class="h-6 w-16" /></Table.Cell>
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
											<div class="flex items-center gap-1.5 text-sm font-black">
												<TrendingUp class="size-3.5 text-emerald-500" />
												${metal.current_price_kg?.toLocaleString()}
												<span class="text-[10px] font-bold opacity-40">/ KG</span>
											</div>
										</Table.Cell>
										<Table.Cell>
											<Button variant="ghost" size="sm" class="text-[10px] font-black uppercase tracking-widest h-8">Update</Button>
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
</div>
