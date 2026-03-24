<script lang="ts">
	import { auth } from "$lib/auth.svelte";
	import { getPortfolio, getVaults, getMetals } from "$lib/api";
	import { onMount } from "svelte";
	import * as Card from "$lib/components/ui/card/index.js";
	import { Button } from "$lib/components/ui/button/index.js";
	import { Progress } from "$lib/components/ui/progress/index.js";
	import { Separator } from "$lib/components/ui/separator/index.js";
	import { Skeleton } from "$lib/components/ui/skeleton/index.js";
	import { Badge } from "$lib/components/ui/badge/index.js";
	import { Warehouse, ShieldCheck, MoveRight, ArrowUpRight } from "@lucide/svelte";
	import WithdrawalModal from "$lib/components/withdrawal-modal.svelte";

	let portfolio = $state<any>(null);
	let vaults = $state<any[]>([]);
	let metals = $state<any[]>([]);
	let loading = $state(true);

	let showWithdrawModal = $state(false);
	let selectedVault = $state<any>(null);

	function openWithdrawal(vault: any) {
		selectedVault = vault;
		showWithdrawModal = true;
	}

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

	async function loadDashboard() {
		if (!auth.token) return;
		try {
			const [p, v, m] = await Promise.all([
				getPortfolio(auth.token),
				getVaults(auth.token),
				getMetals(auth.token),
			]);
			portfolio = p;
			vaults = v;
			metals = m;
		} catch (e) {
			console.error("Failed to load dashboard data:", e);
		} finally {
			loading = false;
		}
	}

	onMount(loadDashboard);
</script>

<div
	class="flex flex-1 flex-col overflow-x-hidden overflow-y-auto px-4 py-8 md:px-6 md:py-10 lg:px-10"
>
	<div class="mx-auto flex w-full max-w-7xl flex-1 flex-col">
		<div
			class="mb-8 flex flex-col gap-6 lg:mb-10 lg:flex-row lg:items-center lg:justify-between"
		>
			<div class="space-y-1.5 text-center sm:text-left">
				<h1 class="text-3xl font-extrabold tracking-tight sm:text-4xl">
					Vault Monitor
				</h1>
			</div>

			<div
				class="grid grid-cols-2 gap-4 gap-y-6 sm:gap-6 lg:flex lg:gap-8"
			>
				<div
					class="flex flex-col items-center sm:items-start lg:items-end"
				>
					<span
						class="text-[10px] font-black uppercase tracking-widest text-slate-400"
						>Inventory Value</span
					>
					{#if loading}
						<Skeleton class="mt-1 h-8 w-32" />
					{:else}
						<div
							class="mt-0.5 text-xl font-black tracking-tight sm:text-2xl"
						>
							${portfolio?.total_valuation?.toLocaleString()}
						</div>
					{/if}
				</div>
				<Separator
					orientation="vertical"
					class="hidden h-10 lg:block opacity-50"
				/>
				<div
					class="flex flex-col items-center sm:items-start lg:items-end"
				>
					<span
						class="text-[10px] font-black uppercase tracking-widest text-slate-400"
						>Physical Payload</span
					>
					{#if loading}
						<Skeleton class="mt-1 h-8 w-24" />
					{:else}
						<div
							class="mt-0.5 text-xl font-black tracking-tight sm:text-2xl"
						>
							{currentLoad.toFixed(1)}
							<span class="text-sm font-bold opacity-40">KG</span>
						</div>
					{/if}
				</div>
			</div>
		</div>

		<!-- Main Storage Grid -->
		<div class="grid gap-6 lg:grid-cols-12 lg:gap-8">
			<div class="lg:col-span-12 flex flex-col gap-6">
				<Card.Root
					class="border-0 shadow-lg shadow-slate-200/40 rounded-xl overflow-hidden bg-white"
				>
					<Card.Header class="border-b border-slate-50 pb-6">
						<div
							class="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between"
						>
							<div class="flex items-center gap-3">
								<div
									class="flex size-10 items-center justify-center rounded-lg bg-slate-900 text-white shadow-xl shadow-slate-900/20"
								>
									<Warehouse class="size-5" />
								</div>
								<div>
									<Card.Title
										class="text-base font-black uppercase tracking-wider"
										>Facility Surveillance</Card.Title
									>
									<Card.Description
										class="text-[10px] font-bold text-slate-400 uppercase tracking-widest"
										>Distributed Custody Network Nodes</Card.Description
									>
								</div>
							</div>
						</div>
					</Card.Header>
					<Card.Content class="p-4 pt-8 sm:p-8">
						<div
							class="grid gap-4 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 sm:gap-6"
						>
							{#if loading}
								{#each Array(4) as _}
									<Skeleton class="h-40 rounded-2xl" />
								{/each}
							{:else}
								{#each vaults as vault}
									{@const util =
										(vault.current_load_kg /
											vault.capacity_kg) *
										100}
									<button
										class="group relative w-full text-left rounded-2xl border border-slate-100 bg-white p-4 transition-all hover:scale-[1.02] hover:border-primary/20 hover:shadow-2xl hover:shadow-slate-200/60 sm:p-5"
										onclick={() => openWithdrawal(vault)}
									>
										<div
											class="mb-6 flex items-center justify-between"
										>
											<div class="flex flex-col gap-1">
												<span
													class="text-xs font-black uppercase tracking-tight text-slate-900"
													>{vault.name}</span
												>
												<span
													class="text-[9px] font-bold text-slate-400 uppercase tracking-widest"
													>{vault.location}</span
												>
											</div>
											<div
												class="size-2 rounded-full {util >
												90
													? 'animate-pulse bg-amber-500 shadow-[0_0_10px_rgba(245,158,11,0.6)]'
													: 'bg-emerald-500 shadow-[0_0_10px_rgba(16,185,129,0.4)]'}"
											></div>
										</div>

										<div class="space-y-4">
											<div
												class="flex items-end justify-between"
											>
												<div class="flex flex-col">
													<div
														class="mb-1 flex items-center gap-1.5"
													>
														<ShieldCheck
															class="size-3 text-emerald-500"
														/>
														<span
															class="text-[9px] font-black text-slate-400 uppercase tracking-widest"
															>Active Payload</span
														>
													</div>
													<span
														class="text-lg font-black tracking-tighter text-slate-900 sm:text-xl"
														>{vault.current_load_kg.toFixed(
															1,
														)}
														<span
															class="text-xs font-bold opacity-20"
															>KG</span
														></span
													>
												</div>
												<div class="text-right">
													<div
														class="text-[10px] font-black text-primary"
													>
														{util.toFixed(0)}%
													</div>
												</div>
											</div>
											<Progress
												value={util}
												class="h-2 {util > 90
													? '[&>div]:bg-amber-500'
													: '[&>div]:bg-primary'} bg-slate-50"
											/>
										</div>

										<!-- Hover Indicator -->
										<div class="absolute bottom-4 right-4 opacity-0 transition-opacity group-hover:opacity-100">
											<ArrowUpRight class="size-4 text-primary" />
										</div>
									</button>
								{/each}
							{/if}
						</div>
					</Card.Content>
				</Card.Root>
			</div>
		</div>
	</div>
</div>

<WithdrawalModal
	bind:open={showWithdrawModal}
	vault={selectedVault}
	{portfolio}
	{metals}
	onSuccess={loadDashboard}
/>
