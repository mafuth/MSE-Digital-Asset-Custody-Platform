<script lang="ts">
	import { auth } from "$lib/auth.svelte";
	import { getPendingRequests, approveRequest, rejectRequest } from "$lib/api";
	import { onMount } from "svelte";
	import * as Card from "$lib/components/ui/card/index.js";
	import { Button } from "$lib/components/ui/button/index.js";
	import { Badge } from "$lib/components/ui/badge/index.js";
	import { 
		Check, 
		X, 
		Loader2, 
		ShieldAlert, 
		ArrowUpRight, 
		ArrowDownLeft,
		Calendar,
		User,
		Scale,
		Warehouse
	} from "@lucide/svelte";
	import { cn } from "$lib/utils";

	let requests = $state<any[]>([]);
	let loading = $state(true);
	let processingId = $state<string | null>(null);

	async function loadRequests() {
		if (!auth.token) return;
		try {
			loading = true;
			requests = await getPendingRequests(auth.token);
		} catch (e) {
			console.error("Failed to load requests:", e);
		} finally {
			loading = false;
		}
	}

	async function handleApprove(id: string) {
		if (!auth.token) return;
		processingId = id;
		try {
			await approveRequest(auth.token, id);
			await loadRequests();
		} catch (e) {
			console.error("Approval failed:", e);
		} finally {
			processingId = null;
		}
	}

	async function handleReject(id: string) {
		if (!auth.token) return;
		processingId = id;
		try {
			await rejectRequest(auth.token, id);
			await loadRequests();
		} catch (e) {
			console.error("Rejection failed:", e);
		} finally {
			processingId = null;
		}
	}

	function formatDate(dateStr: string) {
		return new Date(dateStr).toLocaleString(undefined, {
			month: 'short',
			day: 'numeric',
			hour: '2-digit',
			minute: '2-digit'
		});
	}

	onMount(loadRequests);
</script>

<div class="flex flex-1 flex-col overflow-x-hidden p-4 md:p-6 lg:p-10">
	<div class="mx-auto w-full max-w-6xl space-y-8">
		<div class="flex flex-col gap-2">
			<h1 class="text-3xl font-black tracking-tight lg:text-4xl text-slate-900">
				Authorization Desk
			</h1>
			<p class="text-xs font-black uppercase tracking-widest text-slate-400">
				Manage pending physical asset movements and secure dispatches
			</p>
		</div>

		{#if loading}
			<div class="flex h-64 items-center justify-center">
				<Loader2 class="size-8 animate-spin text-primary opacity-20" />
			</div>
		{:else if requests.length === 0}
			<Card.Root class="border-dashed border-slate-200 bg-slate-50/30">
				<Card.Content class="flex flex-col items-center justify-center py-24 text-center">
					<div class="size-16 rounded-full bg-white shadow-sm flex items-center justify-center mb-4 border border-slate-100">
						<Check class="size-8 text-emerald-500 opacity-20" />
					</div>
					<h3 class="text-lg font-black text-slate-900">Zero Pending Dispatches</h3>
					<p class="text-[10px] font-black uppercase tracking-widest text-slate-400 mt-1">All ingress and egress requests are verified</p>
				</Card.Content>
			</Card.Root>
		{:else}
		{:else}
			<div class="space-y-3">
				{#each requests as req}
					<Card.Root class="overflow-hidden border-slate-200/50 shadow-sm hover:border-slate-300 transition-all bg-white">
						<div class="flex items-stretch">
							<!-- Status Bar -->
							<div class={cn(
								"w-1 shrink-0",
								req.type === "DEPOSIT" ? "bg-emerald-500" : "bg-rose-500"
							)}></div>
							
							<div class="flex flex-1 items-center justify-between py-3 px-4 gap-4">
								<div class="flex items-center gap-6 overflow-hidden">
									<!-- Type Icon -->
									<div class={cn(
										"size-8 rounded-lg flex items-center justify-center shrink-0 border",
										req.type === "DEPOSIT" ? "bg-emerald-50 border-emerald-100 text-emerald-600" : "bg-rose-50 border-rose-100 text-rose-600"
									)}>
										{#if req.type === "DEPOSIT"}
											<ArrowUpRight class="size-4" />
										{:else}
											<ArrowDownLeft class="size-4" />
										{/if}
									</div>

									<!-- User & Contact -->
									<div class="flex flex-col min-w-[140px] max-w-[180px]">
										<div class="flex items-center gap-1.5 overflow-hidden">
											<span class="text-[11px] font-black text-slate-900 truncate tracking-tight">{req.account?.name}</span>
										</div>
										<span class="text-[9px] font-bold text-slate-400 truncate tracking-tight lowercase">{req.account?.email}</span>
									</div>

									<!-- Asset info -->
									<div class="flex flex-col min-w-[100px]">
										<span class="text-[11px] font-black text-slate-900 tracking-tight">{req.metal?.name}</span>
										<div class="flex items-center gap-1">
											<span class={cn(
												"text-[8px] font-black uppercase tracking-widest px-1 rounded-[3px] border",
												req.type === 'DEPOSIT' ? 'text-emerald-600 bg-emerald-50/50 border-emerald-100/50' : 'text-rose-600 bg-rose-50/50 border-rose-100/50'
											)}>
												{req.type === 'DEPOSIT' ? 'Ingress' : 'Egress'}
											</span>
											<span class="text-[8px] font-bold text-slate-300 uppercase tracking-widest">{req.storage_type}</span>
										</div>
									</div>

									<!-- Quantity -->
									<div class="flex flex-col min-w-[80px]">
										<span class="text-[11px] font-black text-slate-700">
											{req.quantity_kg.toFixed(3)} <span class="text-[9px] font-bold opacity-30">KG</span>
										</span>
										<span class="text-[8px] font-black uppercase tracking-widest text-slate-400">Net Weight</span>
									</div>

									<!-- Facility -->
									<div class="flex flex-col min-w-[120px]">
										<span class="text-[11px] font-black text-slate-700 truncate">{req.vault?.name}</span>
										<div class="flex items-center gap-1 text-slate-400">
											<Warehouse class="size-2.5" />
											<span class="text-[8px] font-black uppercase tracking-widest">{req.vault?.location}</span>
										</div>
									</div>

									<!-- Bar Reference / Metadata -->
									{#if req.serial_number}
										<div class="flex flex-col">
											<div class="flex items-center gap-1 px-1.5 py-0.5 rounded-md bg-slate-900 text-white border border-slate-800">
												<span class="text-[8px] font-black uppercase tracking-[0.2em] opacity-40">REF</span>
												<code class="text-[10px] font-mono font-bold tracking-tight italic">
													{req.serial_number}
												</code>
											</div>
										</div>
									{/if}
								</div>

								<!-- Actions & Timestamp -->
								<div class="flex items-center gap-6 shrink-0">
									<div class="text-right flex flex-col items-end">
										<span class="text-[9px] font-black text-slate-900 leading-none">{formatDate(req.created_at).split(',')[0]}</span>
										<span class="text-[8px] font-bold text-slate-400 uppercase tracking-widest mt-0.5">{formatDate(req.created_at).split(',')[1]}</span>
									</div>

									<div class="flex items-center gap-2 border-l border-slate-100 pl-4">
										<Button 
											variant="ghost" 
											size="sm" 
											class="h-8 px-3 text-rose-500 hover:text-rose-600 hover:bg-rose-50 font-black uppercase tracking-widest text-[9px] rounded-lg"
											onclick={() => handleReject(req.id)}
											disabled={processingId === req.id}
										>
											Reject
										</Button>
										<Button 
											variant="default"
											size="sm" 
											class="h-8 px-4 font-black uppercase tracking-widest text-[9px] rounded-lg shadow-sm"
											onclick={() => handleApprove(req.id)}
											disabled={processingId === req.id}
										>
											{#if processingId === req.id}
												<Loader2 class="size-3 animate-spin mr-1.5" />
											{/if}
											Approve
										</Button>
									</div>
								</div>
							</div>
						</div>
					</Card.Root>
				{/each}
			</div>
		{/if}
	</div>
</div>
