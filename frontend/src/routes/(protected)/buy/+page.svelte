<script lang="ts">
	import { auth } from "$lib/auth.svelte";
	import { getPortfolio, getVaults, depositMetal, getMetals } from "$lib/api";
	import { onMount } from "svelte";
	import PaymentModal from "$lib/components/payment-modal.svelte";
	import * as Card from "$lib/components/ui/card/index.js";
	import { Button } from "$lib/components/ui/button/index.js";
	import { Input } from "$lib/components/ui/input/index.js";
	import { Label } from "$lib/components/ui/label/index.js";
	import * as Select from "$lib/components/ui/select/index.js";
	import { Separator } from "$lib/components/ui/separator/index.js";
	import { Skeleton } from "$lib/components/ui/skeleton/index.js";
	import {
		ArrowUpRight,
		Warehouse,
		Scale,
		MoveRight,
		Waves,
		ShieldCheck,
		AlertCircle,
		Check,
		Info,
		Plus,
		Trash2,
		Hash,
	} from "@lucide/svelte";

	let portfolio = $state<any>(null);
	let vaults = $state<any[]>([]);
	let metals = $state<any[]>([]);
	let loading = $state(true);
	let submitting = $state(false);
	let lastSuccess = $state<string | null>(null);
	let error = $state<string | null>(null);
	let showPaymentModal = $state(false);

	// Form state
	let selectedMetalId = $state("");
	let selectedVaultId = $state("");
	let quantity = $state<number>(1);
	let storageType = $state("UNALLOCATED");
	let serialNumber = $state("");
	let barSerials = $state([""]);

	async function loadPageData() {
		if (!auth.token) return;
		try {
			loading = true;
			const [p, v, m] = await Promise.all([
				getPortfolio(auth.token),
				getVaults(auth.token),
				getMetals(auth.token),
			]);
			portfolio = p;
			vaults = v;
			metals = m;

			// Priority to select initial data
			if (metals.length > 0 && !selectedMetalId) {
				selectedMetalId = metals[0].id;
			}
			if (vaults.length > 0 && !selectedVaultId) {
				selectedVaultId = vaults[0].id;
			}
		} catch (e: any) {
			console.error("Failed to load store assets page:", e);
			error = "Initialization failed. Please check connection.";
		} finally {
			loading = false;
		}
	}

	function addBar() {
		barSerials.push("");
	}

	function removeBar(index: number) {
		if (barSerials.length > 1) {
			barSerials.splice(index, 1);
		} else {
			barSerials[0] = "";
		}
	}

	function handleAuthorizeClick() {
		if (!selectedMetalId || !selectedVaultId || quantityToSubmit <= 0) {
			error = "Missing required ingress parameters.";
			return;
		}

		if (storageType === "ALLOCATED") {
			const emptySerials = barSerials.filter(s => !s.trim());
			if (emptySerials.length > 0) {
				error = "All bar reference numbers (serial numbers) are required for allocated storage.";
				return;
			}
		}

		error = null;
		showPaymentModal = true;
	}

	async function processDeposit() {
		submitting = true;
		error = null;
		lastSuccess = null;

		try {
			if (!auth.token) throw new Error("Authentication required");
			await depositMetal(auth.token, {
				metal_id: selectedMetalId,
				quantity_kg: quantityToSubmit,
				storage_type: storageType,
				vault_id: selectedVaultId,
				serial_number:
					storageType === "ALLOCATED" && barSerials.length === 1
						? barSerials[0]
						: undefined,
				serial_numbers:
					storageType === "ALLOCATED" && barSerials.length > 1
						? barSerials
						: undefined,
			});

			lastSuccess = `Ingress request for ${quantityToSubmit.toFixed(2)}kg submitted for authorization.`;
			await loadPageData(); // Refresh metrics
			if (storageType === "UNALLOCATED") quantity = 1;
			barSerials = [""];
		} catch (e: any) {
			error = e.message;
		} finally {
			submitting = false;
		}
	}

	onMount(loadPageData);

	// Reactive derived values
	const selectedVault = $derived(
		vaults.find((v) => v.id === selectedVaultId),
	);
	const selectedMetal = $derived(
		metals.find((m) => m.id === selectedMetalId),
	);
	const vaultLoadPercent = $derived(
		selectedVault
			? (selectedVault.current_load_kg / selectedVault.capacity_kg) * 100
			: 0,
	);

	const metalLabel = $derived(
		selectedMetal
			? `${selectedMetal.name} (${selectedMetal.code})`
			: "Select Metal",
	);
	const vaultLabel = $derived(selectedVault?.name || "Select Vault");

	const quantityToSubmit = $derived.by(() => {
		if (storageType === "ALLOCATED" && (selectedMetal?.bar_kg ?? 0) > 0) {
			return barSerials.length * selectedMetal.bar_kg;
		}
		return quantity;
	});

	const totalDue = $derived(quantityToSubmit * (selectedMetal?.current_price_kg ?? 0));
</script>

<PaymentModal
	bind:show={showPaymentModal}
	assetName={metalLabel}
	quantity={quantityToSubmit}
	total={totalDue}
	onConfirm={processDeposit}
/>

<div
	class="flex flex-1 flex-col overflow-x-hidden overflow-y-auto px-4 py-6 md:px-6 md:py-8 lg:px-10"
>
	<div class="mx-auto flex w-full max-w-5xl flex-1 flex-col">
		<!-- Dashboard-style Header (More Compact) -->
		<div
			class="mb-8 flex flex-col gap-6 md:flex-row md:items-end md:justify-between"
		>
			<div class="space-y-1">
				<h1 class="text-3xl font-extrabold tracking-tight lg:text-4xl">
					Store Assets
				</h1>
				<p class="text-sm text-muted-foreground font-medium">
					Authorize physical asset ingress into secure facilities.
				</p>
			</div>

			<div
				class="flex flex-col items-start gap-4 md:flex-row md:items-center md:gap-6"
			>
				{#if lastSuccess}
					<div
						class="rounded-lg bg-emerald-50 px-3 py-1.5 text-[11px] font-bold text-emerald-700 border border-emerald-100 flex items-center gap-2 animate-in fade-in slide-in-from-right-4"
					>
						<Check class="size-3.5" />
						{lastSuccess}
					</div>
				{/if}
			</div>
		</div>

		{#if error}
			<div
				class="mb-6 flex items-center gap-3 p-3 border border-red-100 bg-red-50 text-red-900 rounded-lg animate-in fade-in slide-in-from-top-2"
			>
				<AlertCircle class="size-4 shrink-0" />
				<span class="text-xs font-bold">{error}</span>
			</div>
		{/if}

		<!-- Main Grid (More Compact) -->
		<div
			class="flex flex-1 flex-col gap-6 lg:grid lg:grid-cols-12 lg:gap-8"
		>
			<!-- Left Column: Ingress Form -->
			<div class="flex flex-col lg:col-span-8">
				<Card.Root
					class="flex flex-1 flex-col rounded-xl overflow-hidden border-slate-200/60 shadow-sm p-0"
				>
					<Card.Header
						class="pb-6 pt-6 px-6 border-b border-slate-50"
					>
						<div class="flex items-center gap-3">
							<div
								class="flex size-8 items-center justify-center rounded-lg bg-primary text-primary-foreground shadow-sm"
							>
								<ArrowUpRight class="size-4" />
							</div>
							<div>
								<Card.Title class="text-lg"
									>Ingress Authorization</Card.Title
								>
								<Card.Description class="text-xs"
									>Register physical bars and confirm facility
									destination.</Card.Description
								>
							</div>
						</div>
					</Card.Header>

					<Card.Content class="px-6 py-8 space-y-6">
						{#if loading}
							<div class="space-y-6">
								<div class="grid gap-6 sm:grid-cols-2">
									<div class="space-y-2">
										<Skeleton class="h-3 w-20" /><Skeleton
											class="h-10 w-full rounded-lg"
										/>
									</div>
									<div class="space-y-2">
										<Skeleton class="h-3 w-20" /><Skeleton
											class="h-10 w-full rounded-lg"
										/>
									</div>
								</div>
								<div class="space-y-2">
									<Skeleton class="h-3 w-32" /><Skeleton
										class="h-10 w-full rounded-lg"
									/>
								</div>
							</div>
						{:else}
							<div class="grid gap-6 sm:grid-cols-2">
								<!-- Asset Selector -->
								<div class="space-y-2">
									<Label
										class="text-[10px] font-black uppercase tracking-widest text-slate-400 ml-0.5"
										>Asset Category</Label
									>
									<Select.Root
										type="single"
										bind:value={selectedMetalId}
									>
										<Select.Trigger
											class="h-10 w-full rounded-lg border-slate-200 font-bold text-sm bg-slate-50/30"
										>
											{metalLabel}
										</Select.Trigger>
										<Select.Content
											class="rounded-lg border-slate-200"
										>
											{#each metals as metal}
												<Select.Item
													value={metal.id}
													label={metal.name}
													class="rounded-md text-sm font-semibold"
												>
													{metal.name} ({metal.code})
												</Select.Item>
											{/each}
										</Select.Content>
									</Select.Root>
								</div>

								<!-- Facility Selector (Moved to Top Row) -->
								<div class="space-y-2">
									<Label
										class="text-[10px] font-black uppercase tracking-widest text-slate-400 ml-0.5"
										>Target Facility</Label
									>
									<Select.Root
										type="single"
										bind:value={selectedVaultId}
									>
										<Select.Trigger
											class="h-10 w-full rounded-lg border-slate-200 font-bold text-sm bg-slate-50/30"
										>
											<div
												class="flex items-center gap-2"
											>
												<Warehouse
													class="size-4 text-primary/70"
												/>
												{vaultLabel}
											</div>
										</Select.Trigger>
										<Select.Content
											class="rounded-lg border-slate-200"
										>
											{#each vaults as vault}
												<Select.Item
													value={vault.id}
													label={vault.name}
													class="rounded-md p-2"
												>
													<div
														class="flex flex-col gap-0.5"
													>
														<div
															class="font-bold text-slate-700 text-sm"
														>
															{vault.name}
														</div>
														<div
															class="text-[9px] text-slate-400 font-bold uppercase tracking-widest"
														>
															{vault.location}
														</div>
													</div>
												</Select.Item>
											{/each}
										</Select.Content>
									</Select.Root>
								</div>
							</div>

							<!-- Protocol Toggle (Second Row) -->
							<div class="space-y-3">
								<Label
									class="text-[10px] font-black uppercase tracking-widest text-slate-400 ml-0.5"
									>Custody Protocol</Label
								>
								<div class="grid grid-cols-2 gap-4">
									<button
										type="button"
										class="flex flex-col items-center justify-center rounded-xl border p-4 transition-all {storageType ===
										'UNALLOCATED'
											? 'border-primary bg-primary/[0.03] shadow-[inset_0_2px_4px_rgba(0,0,0,0.02)]'
											: 'border-slate-100 bg-slate-50/20 hover:border-slate-200'}"
										onclick={() =>
											(storageType = "UNALLOCATED")}
									>
										<Waves
											class="size-5 mb-2 {storageType ===
											'UNALLOCATED'
												? 'text-primary'
												: 'text-slate-300'}"
										/>
										<span
											class="text-xs font-bold text-slate-700"
											>Unallocated</span
										>
										<span
											class="text-[9px] text-slate-400 font-bold uppercase mt-0.5"
											>Shared Pool</span
										>
									</button>
									<button
										type="button"
										class="flex flex-col items-center justify-center rounded-xl border p-4 transition-all {storageType ===
										'ALLOCATED'
											? 'border-primary bg-primary/[0.03] shadow-[inset_0_2px_4px_rgba(0,0,0,0.02)]'
											: 'border-slate-100 bg-slate-50/20 hover:border-slate-200'}"
										onclick={() =>
											(storageType = "ALLOCATED")}
									>
										<ShieldCheck
											class="size-5 mb-2 {storageType ===
											'ALLOCATED'
												? 'text-primary'
												: 'text-slate-300'}"
										/>
										<span
											class="text-xs font-bold text-slate-700"
											>Allocated</span
										>
										<span
											class="text-[9px] text-slate-400 font-bold uppercase mt-0.5"
											>Specific Bar</span
										>
									</button>
								</div>
							</div>

							<Separator class="bg-slate-50" />

							<!-- Mass / Bar Reference List (Bottom Row) -->
							{#if storageType === "UNALLOCATED"}
								<div
									class="space-y-2 animate-in fade-in slide-in-from-bottom-2 duration-300"
								>
									<Label
										class="text-[10px] font-black uppercase tracking-widest text-slate-400 ml-0.5"
										>Total Mass (KG)</Label
									>
									<div class="relative">
										<Input
											type="number"
											step="0.1"
											bind:value={quantity}
											class="pl-10 h-11 w-full rounded-xl border-slate-200 font-black text-lg bg-slate-50/30 text-primary"
										/>
										<Scale
											class="absolute left-3.5 top-3.5 size-4 text-slate-300"
										/>
									</div>
								</div>
							{:else}
								<div
									class="space-y-4 animate-in fade-in slide-in-from-bottom-2 duration-300"
								>
									<div
										class="flex items-center justify-between"
									>
										<Label
											class="text-[10px] font-black uppercase tracking-widest text-slate-400 ml-0.5"
											>Bar Reference Numbers</Label
										>
										{#if selectedMetal?.bar_kg > 0}
											<div
												class="flex items-center gap-2 rounded-full bg-primary/5 px-2 py-1 border border-primary/10"
											>
												<span
													class="text-[9px] font-bold text-primary uppercase"
													>Estimated: {quantityToSubmit.toFixed(
														1,
													)} KG</span
												>
											</div>
										{/if}
									</div>

									<div class="grid gap-3">
										{#each barSerials as serial, i}
											<div
												class="flex items-center gap-2 group animate-in fade-in slide-in-from-left-2"
												style="animation-delay: {i *
													50}ms"
											>
												<div class="relative flex-1">
													<Input
														placeholder="Enter Serial Number..."
														bind:value={
															barSerials[i]
														}
														class="pl-10 h-10 w-full rounded-lg border-slate-200 font-bold text-sm bg-slate-50/30 focus-visible:ring-primary"
														required
													/>
													<Hash
														class="absolute left-3.5 top-3 size-4 text-slate-300"
													/>
												</div>
												<Button
													variant="ghost"
													size="icon"
													class="size-10 rounded-lg text-slate-300 hover:text-red-500 hover:bg-red-50 shrink-0"
													onclick={() => removeBar(i)}
												>
													<Trash2 class="size-4" />
												</Button>
											</div>
										{/each}
									</div>

									<Button
										variant="outline"
										class="w-full border-dashed border-slate-200 text-slate-400 hover:text-primary hover:border-primary hover:bg-primary/[0.02] h-10 rounded-lg font-bold text-xs"
										onclick={addBar}
									>
										<Plus class="size-3.5 mr-2" />
										Add More Bars
									</Button>

									{#if !(selectedMetal?.bar_kg > 0)}
										<div
											class="mt-4 p-3 rounded-lg bg-amber-50 border border-amber-100 flex items-start gap-3"
										>
											<AlertCircle
												class="size-4 text-amber-500 shrink-0 mt-0.5"
											/>
											<div class="space-y-1">
												<p
													class="text-[10px] font-bold text-amber-800 leading-tight"
												>
													Variable Weight Detected
												</p>
												<p
													class="text-[9px] font-medium text-amber-700/70 leading-normal"
												>
													This asset category does not
													have a standard bar weight.
													Please specify total mass
													below.
												</p>
												<Input
													type="number"
													step="0.1"
													bind:value={quantity}
													class="h-8 mt-2 rounded-md border-amber-200 font-bold text-xs bg-white text-amber-900"
													placeholder="Total KG"
												/>
											</div>
										</div>
									{/if}
								</div>
							{/if}

							<!-- Transaction Summary -->
							{#if selectedMetal}
								<div class="mt-8 space-y-3 rounded-xl bg-slate-50/80 p-5 border border-slate-100 shadow-sm animate-in fade-in slide-in-from-bottom-2">
									<div class="flex items-center justify-between">
										<span class="text-[9px] font-black uppercase tracking-widest text-slate-400">Current Unit Price</span>
										<div class="flex items-center gap-1.5 font-bold text-slate-700">
											<span class="text-xs">${selectedMetal.current_price_kg.toLocaleString(undefined, { minimumFractionDigits: 2 })}</span>
											<span class="text-[9px] text-slate-400 uppercase tracking-tighter">/ KG</span>
										</div>
									</div>
									<div class="flex items-center justify-between">
										<span class="text-[9px] font-black uppercase tracking-widest text-slate-400">Weight Authorization</span>
										<span class="text-xs font-black text-slate-700 uppercase tracking-tight">{quantityToSubmit.toFixed(3)} KG</span>
									</div>
									
									<Separator class="bg-slate-200/50" />
									
									<div class="flex items-center justify-between pt-1">
										<div class="flex flex-col">
											<span class="text-[10px] font-black uppercase tracking-widest text-primary leading-none">Total Authorization Due</span>
											<span class="text-[8px] font-bold text-slate-400 uppercase tracking-widest mt-1">Institutional Storage Protocol</span>
										</div>
										<span class="text-2xl font-black text-primary tracking-tighter leading-none">
											${totalDue.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
										</span>
									</div>
								</div>
							{/if}
						{/if}
					</Card.Content>

					<Card.Footer class="p-6 pt-0">
						<Button
							size="lg"
							class="w-full h-11 text-sm font-bold rounded-lg shadow-sm group"
							onclick={handleAuthorizeClick}
							disabled={submitting || loading}
						>
							{#if submitting}
								<div
									class="size-4 animate-spin rounded-full border-2 border-white border-t-transparent mr-2"
								></div>
								Processing...
							{:else}
								Authorize Ingress
								<MoveRight
									class="size-4 ml-2 transition-transform group-hover:translate-x-1"
								/>
							{/if}
						</Button>
					</Card.Footer>
				</Card.Root>
			</div>

			<!-- Right Column: Analytics Sidebar (More Compact) -->
			<div class="flex flex-col gap-6 lg:col-span-4 lg:gap-8">
				<!-- Vault Distribution Analytics -->
				<Card.Root
					class="flex flex-col border border-slate-200/60 shadow-sm bg-white text-slate-900 rounded-xl overflow-hidden p-0"
				>
					<Card.Content class="space-y-6 px-6 py-8">
						{#if loading}
							<div class="space-y-4">
								<Skeleton
									class="h-12 w-full rounded-lg bg-slate-50"
								/>
								<Skeleton
									class="h-1.5 w-full rounded-full bg-slate-50"
								/>
							</div>
						{:else if selectedVault}
							<div class="space-y-6">
								<div
									class="flex items-end justify-between border-b border-slate-50 pb-4"
								>
									<div>
										<span
											class="text-[8px] font-black uppercase tracking-widest text-slate-400 mb-1 block"
											>Facility</span
										>
										<span
											class="text-sm font-black tracking-tight text-slate-900"
											>{selectedVault.name}</span
										>
									</div>
									<div class="text-right">
										<div
											class="size-1.5 rounded-full bg-emerald-500 shadow-[0_0_8px_rgba(16,185,129,0.5)]"
										></div>
									</div>
								</div>

								<div class="space-y-3">
									<div class="flex justify-between items-end">
										<span
											class="text-[9px] font-bold uppercase tracking-widest text-slate-400"
											>Utilization Ratio</span
										>
										<span
											class="text-lg font-black text-primary"
											>{vaultLoadPercent.toFixed(
												1,
											)}%</span
										>
									</div>
									<div
										class="h-1.5 w-full bg-slate-100 rounded-full overflow-hidden"
									>
										<div
											class="h-full bg-primary rounded-full transition-all duration-1000"
											style="width: {vaultLoadPercent}%"
										></div>
									</div>
								</div>

								<div class="grid grid-cols-2 gap-3">
									<div
										class="p-3 rounded-xl bg-slate-50/50 border border-slate-100"
									>
										<span
											class="text-[8px] font-bold uppercase tracking-widest text-slate-400 block mb-1"
											>Capacity</span
										>
										<span
											class="text-xs font-black text-slate-700"
											>{selectedVault.capacity_kg.toLocaleString()}
											<span
												class="text-[9px] text-slate-400 font-bold"
												>KG</span
											></span
										>
									</div>
									<div
										class="p-3 rounded-xl bg-emerald-50/30 border border-emerald-100/50 text-emerald-700"
									>
										<span
											class="text-[8px] font-bold uppercase tracking-widest text-emerald-600/50 block mb-1"
											>Available</span
										>
										<span class="text-xs font-black"
											>{(
												selectedVault.capacity_kg -
												selectedVault.current_load_kg
											).toLocaleString()}
											<span
												class="text-[9px] text-emerald-600/30 font-bold"
												>KG</span
											></span
										>
									</div>
								</div>
							</div>
						{:else}
							<div
								class="py-12 flex flex-col items-center justify-center text-slate-400 gap-3 opacity-40"
							>
								<Info class="size-6" />
								<span
									class="text-[9px] font-bold uppercase tracking-widest"
									>No Facility Selected</span
								>
							</div>
						{/if}
					</Card.Content>
				</Card.Root>

				<!-- Sovereign Security Label (More Compact) -->
				<div
					class="p-4 rounded-xl bg-white border border-slate-200 shadow-sm flex items-start gap-4"
				>
					<div
						class="size-10 rounded-lg bg-amber-50 text-amber-600 flex items-center justify-center shrink-0 border border-amber-100"
					>
						<ShieldCheck class="size-5" />
					</div>
					<div class="space-y-0.5">
						<h4
							class="text-xs font-bold text-slate-900 tracking-tight"
						>
							Sovereign Custody
						</h4>
						<p
							class="text-[10px] font-medium text-slate-500 leading-normal"
						>
							Institutional holdings verified and insured by state
							entities.
						</p>
					</div>
				</div>
			</div>
		</div>
	</div>

	<!-- Spacing -->
	<div class="h-12"></div>
</div>
