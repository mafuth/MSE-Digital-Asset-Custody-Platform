<script lang="ts">
	import { auth } from "$lib/auth.svelte";
	import { getAdminAccounts, updateAdminAccount, getAdminAccountPortfolio } from "$lib/api";
	import { onMount } from "svelte";
	import * as Card from "$lib/components/ui/card/index.js";
	import * as Table from "$lib/components/ui/table/index.js";
	import { Button } from "$lib/components/ui/button/index.js";
	import { Skeleton } from "$lib/components/ui/skeleton/index.js";
	import { Badge } from "$lib/components/ui/badge/index.js";
	import { Users, Mail, Shield, UserCheck, UserX, Eye, Warehouse, History as HistoryIcon, ShieldCheck, Waves } from "@lucide/svelte";
	import * as Dialog from "$lib/components/ui/dialog/index.js";
	import * as Select from "$lib/components/ui/select/index.js";
	import { Separator } from "$lib/components/ui/separator/index.js";

	let accounts = $state<any[]>([]);
	let loading = $state(true);
	
	let selectedAccountId = $state<string | null>(null);
	let selectedAccount = $derived(accounts.find(a => a.id === selectedAccountId));
	let portfolio = $state<any>(null);
	let loadingPortfolio = $state(false);
	let showDetailsModal = $state(false);

	async function closeDetails() {
		showDetailsModal = false;
		// delay clearing to prevent flickering during close animation
		setTimeout(() => {
			if (!showDetailsModal) {
				selectedAccountId = null;
				portfolio = null;
			}
		}, 200);
	}

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

	async function toggleRole(account: any) {
		if (!auth.token || !account) return;
		const newType = account.type === "customer" ? "admin" : "customer";
		
		try {
			await updateAdminAccount(auth.token, account.id, { type: newType });
			await loadAccounts();
		} catch (e) {
			console.error("Failed to update role:", e);
		}
	}
	
	async function updateRole(accountId: string, newType: string) {
		if (!auth.token) return;
		try {
			await updateAdminAccount(auth.token, accountId, { type: newType });
			await loadAccounts();
		} catch (e) {
			console.error("Failed to update role:", e);
		}
	}

	async function viewPortfolio(accountId: string) {
		if (!auth.token) return;
		selectedAccountId = accountId;
		showDetailsModal = true;
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
			<div class="lg:col-span-12">
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

			<!-- Portfolio Details Modal -->
			<Dialog.Root bind:open={showDetailsModal}>
				<Dialog.Content class="sm:max-w-2xl max-h-[90vh] p-0 overflow-hidden flex flex-col rounded-xl border-slate-200 shadow-2xl">
					{#if loadingPortfolio}
						<div class="flex flex-col items-center justify-center py-20 gap-4">
							<div class="size-10 rounded-full border-4 border-primary/20 border-t-primary animate-spin"></div>
							<p class="text-xs font-black uppercase tracking-widest text-slate-400">Loading Agency Report...</p>
						</div>
					{:else if portfolio && selectedAccount}
						<div class="flex flex-col flex-1 overflow-y-auto">
							<!-- Header -->
							<div class="p-6 pr-14 border-b border-slate-100 bg-white relative">
								<div class="flex items-center justify-between">
									<div class="flex items-center gap-4">
										<div class="size-10 rounded-full bg-slate-50 flex items-center justify-center text-slate-400 border border-slate-100">
											<Users class="size-5" />
										</div>
										<div class="flex flex-col">
											<h2 class="text-base font-black tracking-tight uppercase">{selectedAccount.name}</h2>
											<div class="flex items-center gap-2 mt-0.5">
												<span class="flex items-center gap-1 text-[10px] font-bold text-muted-foreground uppercase tracking-widest">
													<Mail class="size-2.5" />
													{selectedAccount.email}
												</span>
											</div>
										</div>
									</div>
									<div class="text-right">
										<div class="text-[9px] font-black uppercase tracking-widest text-slate-400 mb-0.5">Global Valuation</div>
										<div class="text-2xl font-black text-primary tracking-tighter">${portfolio.total_valuation?.toLocaleString()}</div>
									</div>
								</div>
							</div>

							<!-- Rights & Authority -->
							<div class="px-6 py-4 bg-slate-50 border-b border-slate-200">
								<div class="flex items-center justify-between gap-8">
									<div class="flex items-center gap-3 flex-1">
										<span class="text-[9px] font-black uppercase tracking-widest text-slate-500 whitespace-nowrap">User Type:</span>
										<div class="flex-1 max-w-[180px]">
											<Select.Root 
												type="single"
												bind:value={selectedAccount.type}
												onValueChange={(val) => updateRole(selectedAccount.id, val)}
												disabled={selectedAccount.id === auth.user?.id}
											>
												<Select.Trigger class="h-7 text-[9px] font-black uppercase tracking-widest bg-white border-slate-200 rounded-md">
													{selectedAccount.type === 'admin' ? 'Admin Desk' : 'Customer Portal'}
												</Select.Trigger>
												<Select.Content>
													<Select.Item value="customer" class="text-[9px] font-black uppercase tracking-widest py-1.5 focus:bg-primary/5 focus:text-primary">Customer Portal</Select.Item>
													<Select.Item value="admin" class="text-[9px] font-black uppercase tracking-widest py-1.5 focus:bg-primary/5 focus:text-primary">Admin Desk</Select.Item>
												</Select.Content>
											</Select.Root>
										</div>
									</div>
									<div class="flex items-center gap-3">
										<span class="text-[9px] font-black uppercase tracking-widest text-slate-500">Security:</span>
										<Badge variant={selectedAccount.status === 'active' ? 'default' : 'destructive'} class="text-[8px] font-black uppercase px-2 h-5 flex items-center">
											{selectedAccount.status}
										</Badge>
									</div>
								</div>
							</div>

							<!-- Holdings List -->
							<div class="p-6 pt-4 space-y-4">
								<h3 class="text-[10px] font-black uppercase tracking-widest text-slate-400 px-1">Institutional Holdings Registry</h3>
								<div class="rounded-xl border border-slate-200 overflow-hidden shadow-sm">
									<Table.Root>
										<Table.Header class="bg-slate-50/50">
											<Table.Row class="hover:bg-transparent border-b h-8">
												<Table.Head class="text-[9px] font-black uppercase tracking-widest px-4">Asset & Bar Ref</Table.Head>
												<Table.Head class="text-[9px] font-black uppercase tracking-widest text-right">Physical Weight</Table.Head>
												<Table.Head class="text-[9px] font-black uppercase tracking-widest text-right px-4">Vault Name</Table.Head>
											</Table.Row>
										</Table.Header>
										<Table.Body>
											{#each Object.entries(portfolio.assets) as [code, asset]: [string, any]}
												<Table.Row class="border-b last:border-0 bg-white">
													<Table.Cell class="px-4 py-3">
														<div class="flex flex-col">
															<span class="text-[11px] font-black uppercase tracking-tight">{asset.name}</span>
															<span class="text-[9px] font-bold text-slate-400 uppercase tracking-widest">{code}</span>
														</div>
													</Table.Cell>
													<Table.Cell class="text-right py-3 whitespace-nowrap">
														<div class="flex flex-col">
															<span class="text-[11px] font-bold tracking-tight">{asset.quantity.toFixed(3)} KG</span>
															<div class="flex justify-end gap-2 mt-0.5">
																<div class="flex items-center gap-1">
																	<div class="size-1 rounded-full bg-primary/40"></div>
																	<span class="text-[8px] font-black uppercase text-slate-400">A: {asset.breakdown.ALLOCATED.quantity.toFixed(3)}</span>
																</div>
																<div class="flex items-center gap-1">
																	<div class="size-1 rounded-full bg-emerald-400/40"></div>
																	<span class="text-[8px] font-black uppercase text-slate-400">U: {asset.breakdown.UNALLOCATED.quantity.toFixed(3)}</span>
																</div>
															</div>
														</div>
													</Table.Cell>
													<Table.Cell class="text-right px-4 py-3 whitespace-nowrap">
														<span class="text-[9px] font-black text-slate-400 uppercase tracking-widest">Global Registry</span>
													</Table.Cell>
												</Table.Row>

												<!-- Nested Allocated Bars with Serial -->
												{#if asset.breakdown.ALLOCATED.bars.length > 0}
													{#each asset.breakdown.ALLOCATED.bars as bar}
														<Table.Row class="bg-slate-50/20 border-b border-dashed border-slate-100 last:border-solid last:border-slate-200 hover:bg-slate-50 transition-colors">
															<Table.Cell class="pl-10 py-2">
																<div class="flex items-center gap-2">
																	<ShieldCheck class="size-3 text-primary/40" />
																	<div class="flex flex-col">
																		<span class="text-[8px] font-black uppercase text-slate-400 tracking-widest leading-none mb-1">Bar Ref Number</span>
																		<code class="text-[10px] font-mono font-bold text-slate-500 bg-white border border-slate-100 px-1.5 py-0.5 rounded shadow-sm leading-none">{bar.serial}</code>
																	</div>
																</div>
															</Table.Cell>
															<Table.Cell class="text-right py-2">
																<span class="text-[10px] font-bold text-slate-500">{bar.weight.toFixed(3)} KG</span>
															</Table.Cell>
															<Table.Cell class="text-right px-4 py-2">
																<div class="flex items-center justify-end gap-1.5 text-[10px] font-bold text-primary uppercase">
																	<Warehouse class="size-3" />
																	{bar.vault}
																</div>
															</Table.Cell>
														</Table.Row>
													{/each}
												{/if}
											{/each}
											
											{#if Object.keys(portfolio.assets).length === 0}
												<Table.Row>
													<Table.Cell colspan={3} class="h-32 text-center text-[10px] font-bold uppercase tracking-widest text-slate-300">
														No institutional assets registered
													</Table.Cell>
												</Table.Row>
											{/if}
										</Table.Body>
									</Table.Root>
								</div>
							</div>
						</div>
					{:else}
						<div class="flex flex-col items-center justify-center py-20 gap-4">
							<div class="size-16 rounded-full bg-slate-50 flex items-center justify-center text-slate-300">
								<Mail class="size-8" />
							</div>
							<p class="text-xs font-black uppercase tracking-widest text-slate-400">Failed to generate administrative report</p>
						</div>
					{/if}
				</Dialog.Content>
			</Dialog.Root>
		</div>
	</div>
</div>
