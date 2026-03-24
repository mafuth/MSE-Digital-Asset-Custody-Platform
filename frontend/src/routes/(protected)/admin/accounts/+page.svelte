<script lang="ts">
	import { auth } from "$lib/auth.svelte";
	import { getAdminAccounts, updateAdminAccount, getAdminAccountPortfolio } from "$lib/api";
	import { onMount } from "svelte";
	import * as Card from "$lib/components/ui/card/index.js";
	import * as Table from "$lib/components/ui/table/index.js";
	import { Button } from "$lib/components/ui/button/index.js";
	import { Skeleton } from "$lib/components/ui/skeleton/index.js";
	import { Badge } from "$lib/components/ui/badge/index.js";
	import { Users, Mail, Shield, UserCheck, UserX, Eye } from "@lucide/svelte";

	let accounts = $state<any[]>([]);
	let loading = $state(true);
	
	let selectedAccountId = $state<string | null>(null);
	let portfolio = $state<any>(null);
	let loadingPortfolio = $state(false);

	async function loadAccounts() {
		if (!auth.token) return;
		try {
			accounts = await getAdminAccounts(auth.token);
		} catch (e) {
			console.error("Failed to load accounts:", e);
		} finally {
			loading = false;
		}
	}

	async function toggleStatus(account: any) {
		if (!auth.token) return;
		const newStatus = account.status === "active" ? "blocked" : "active";
		try {
			await updateAdminAccount(auth.token, account.id, { status: newStatus });
			await loadAccounts();
		} catch (e) {
			console.error("Failed to update status:", e);
		}
	}

	async function viewPortfolio(accountId: string) {
		if (!auth.token) return;
		selectedAccountId = accountId;
		loadingPortfolio = true;
		try {
			portfolio = await getAdminAccountPortfolio(auth.token, accountId);
		} catch (e) {
			console.error("Failed to load portfolio:", e);
		} finally {
			loadingPortfolio = false;
		}
	}

	onMount(loadAccounts);
</script>

<div class="flex flex-1 flex-col px-6 py-6 md:px-10 md:py-8">
	<div class="mx-auto flex w-full max-w-7xl flex-1 flex-col">
		<div class="mb-8 flex flex-col gap-4 md:flex-row md:items-end md:justify-between">
			<div class="space-y-1">
				<h1 class="text-3xl font-bold tracking-tight text-foreground">
					User Management
				</h1>
				<p class="text-sm text-muted-foreground">
					Manage customer accounts and monitor individual portfolios.
				</p>
			</div>
		</div>

		<div class="grid gap-8 lg:grid-cols-12">
			<!-- Accounts Table -->
			<div class={selectedAccountId ? "lg:col-span-8" : "lg:col-span-12"}>
				<div class="rounded-xl border border-slate-200/60 overflow-hidden shadow-sm bg-card">
					<Table.Root>
						<Table.Header>
							<Table.Row class="hover:bg-transparent border-b bg-muted/30">
								<Table.Head class="h-11 text-[10px] font-bold uppercase tracking-widest px-6">User</Table.Head>
								<Table.Head class="h-11 text-[10px] font-bold uppercase tracking-widest">Type</Table.Head>
								<Table.Head class="h-11 text-[10px] font-bold uppercase tracking-widest">Status</Table.Head>
								<Table.Head class="h-11 text-[10px] font-bold uppercase tracking-widest text-right px-6">Actions</Table.Head>
							</Table.Row>
						</Table.Header>
						<Table.Body>
							{#if loading}
								{#each Array(5) as _}
									<Table.Row>
										<Table.Cell class="px-6"><Skeleton class="h-10 w-full" /></Table.Cell>
										<Table.Cell><Skeleton class="h-6 w-16" /></Table.Cell>
										<Table.Cell><Skeleton class="h-6 w-16" /></Table.Cell>
										<Table.Cell class="text-right px-6"><Skeleton class="h-8 w-24 ml-auto" /></Table.Cell>
									</Table.Row>
								{/each}
							{:else}
								{#each accounts as account}
									<Table.Row class="group transition-colors border-b last:border-0 hover:bg-slate-50/80 {selectedAccountId === account.id ? 'bg-primary/5' : ''}">
										<Table.Cell class="px-6">
											<div class="flex items-center gap-3">
												<div class="flex size-9 items-center justify-center rounded-full bg-slate-100 text-slate-600">
													<Users class="size-4" />
												</div>
												<div class="flex flex-col">
													<span class="font-bold text-sm tracking-tight">{account.name}</span>
													<div class="flex items-center gap-1.5 text-[10px] text-muted-foreground">
														<Mail class="size-2.5" />
														{account.email}
													</div>
												</div>
											</div>
										</Table.Cell>
										<Table.Cell>
											<div class="flex items-center gap-1.5 text-[10px] font-black uppercase tracking-widest">
												<Shield class="size-3 text-slate-400" />
												{account.type}
											</div>
										</Table.Cell>
										<Table.Cell>
											<Badge variant={account.status === 'active' ? 'default' : 'destructive'} class="text-[9px] font-black uppercase px-2 py-0">
												{account.status}
											</Badge>
										</Table.Cell>
										<Table.Cell class="text-right px-6 whitespace-nowrap">
											<div class="flex items-center justify-end gap-2">
												<Button variant="outline" size="sm" class="h-8 px-2.5 gap-1.5 text-[10px] font-black uppercase tracking-widest" onclick={() => viewPortfolio(account.id)}>
													<Eye class="size-3.5" />
													Details
												</Button>
												<Button 
													variant={account.status === 'active' ? 'ghost' : 'outline'} 
													size="sm" 
													class="h-8 w-8 p-0" 
													onclick={() => toggleStatus(account)}
													title={account.status === "active" ? "Suspend Account" : "Activate Account"}
												>
													{#if account.status === "active"}
														<UserX class="size-4 text-destructive" />
													{:else}
														<UserCheck class="size-4 text-emerald-600" />
													{/if}
												</Button>
											</div>
										</Table.Cell>
									</Table.Row>
								{/each}
							{/if}
						</Table.Body>
					</Table.Root>
				</div>
			</div>

			<!-- Portfolio Details -->
			{#if selectedAccountId}
				<div class="lg:col-span-4 space-y-6">
					<Card.Root class="sticky top-6">
						<Card.Header class="flex flex-row items-center justify-between pb-2">
							<div>
								<Card.Title class="text-base font-black uppercase tracking-wider">Portfolio Assets</Card.Title>
								<Card.Description class="text-[10px] font-bold uppercase tracking-widest">Customer Valuation Report</Card.Description>
							</div>
							<Button variant="ghost" size="sm" class="h-8 w-8 p-0" onclick={() => selectedAccountId = null}>×</Button>
						</Card.Header>
						<Card.Content>
							{#if loadingPortfolio}
								<div class="space-y-4 pt-4">
									<Skeleton class="h-12 w-full" />
									<Skeleton class="h-24 w-full" />
									<Skeleton class="h-24 w-full" />
								</div>
							{:else if portfolio}
								<div class="space-y-6 pt-4">
									<div class="bg-slate-50 p-4 rounded-xl border border-slate-100">
										<span class="text-[9px] font-black text-slate-400 uppercase tracking-widest">Total Valuation</span>
										<div class="text-2xl font-black text-primary">${portfolio.total_valuation?.toLocaleString()}</div>
									</div>

									<div class="space-y-3">
										<span class="text-[10px] font-black uppercase tracking-widest text-muted-foreground px-1">Holdings Breakdown</span>
										{#each Object.entries(portfolio.assets) as [code, asset]: [string, any]}
											<div class="flex items-center justify-between p-3 border border-slate-100 rounded-lg hover:border-primary/20 transition-colors">
												<div class="flex flex-col">
													<span class="text-xs font-black">{asset.name}</span>
													<span class="text-[9px] font-bold text-muted-foreground uppercase">{code}</span>
												</div>
												<div class="text-right">
													<div class="text-xs font-black">{asset.quantity.toFixed(3)} KG</div>
													<div class="text-[9px] font-bold text-emerald-600">${asset.valuation?.toLocaleString()}</div>
												</div>
											</div>
										{/each}
										
										{#if Object.keys(portfolio.assets).length === 0}
											<div class="text-center py-8 text-muted-foreground/50 italic text-xs">No assets in portfolio</div>
										{/if}
									</div>
								</div>
							{:else}
								<div class="text-center py-12 text-muted-foreground text-sm">Failed to load portfolio data</div>
							{/if}
						</Card.Content>
					</Card.Root>
				</div>
			{/if}
		</div>
	</div>
</div>
