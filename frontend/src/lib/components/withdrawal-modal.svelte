<script lang="ts">
	import { IsMobile } from "$lib/hooks/is-mobile.svelte";
	import * as Dialog from "$lib/components/ui/dialog/index.js";
	import * as Sheet from "$lib/components/ui/sheet/index.js";
	import { Button } from "$lib/components/ui/button/index.js";
	import { Input } from "$lib/components/ui/input/index.js";
	import { Label } from "$lib/components/ui/label/index.js";
	import * as Select from "$lib/components/ui/select/index.js";
	import {
		ShieldCheck,
		ArrowUpRight,
		Scale,
		Loader2,
		Warehouse,
		Waves,
		MoveRight,
		Check,
		Trash2,
		Plus,
	} from "@lucide/svelte";
	import { auth } from "$lib/auth.svelte";
	import { withdrawMetal } from "$lib/api";

	type Props = {
		open: boolean;
		vault: any;
		portfolio: any;
		metals: any[];
		onSuccess?: () => void;
	};

	let {
		open = $bindable(false),
		vault,
		portfolio,
		metals,
		onSuccess,
	}: Props = $props();
	const isMobile = new IsMobile();

	// Form state
	let selectedMetal = $state("");
	let custodyProtocol = $state("UNALLOCATED");
	let amount = $state("");
	let barSerials = $state([""]);
	let loading = $state(false);
	let error = $state<string | null>(null);
	let lastSuccess = $state<string | null>(null);

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

	// Derived: user's metal holdings combined with full metals list
	let metalOptions = $derived(
		metals.map((m) => {
			const portfolioData = portfolio?.assets?.[m.code] || {
				quantity: 0,
				storage_breakdown: { ALLOCATED: 0, UNALLOCATED: 0 },
			};
			return {
				id: m.id,
				code: m.code,
				name: m.name,
				bar_kg: m.bar_kg,
				quantity: portfolioData.quantity,
				breakdown: portfolioData.storage_breakdown,
			};
		}),
	);

	let currentMetalData = $derived(
		metalOptions.find((m) => m.code === selectedMetal),
	);

	let remainingInVault = $derived(currentMetalData?.quantity || 0);

	let amountToSubmit = $derived.by(() => {
		if (custodyProtocol === "ALLOCATED" && currentMetalData?.bar_kg > 0) {
			return barSerials.length * currentMetalData.bar_kg;
		}
		return parseFloat(amount) || 0;
	});

	async function handleWithdraw() {
		if (!auth.token || !selectedMetal || !vault) return;

		loading = true;
		error = null;
		lastSuccess = null;

		try {
			const metalId = currentMetalData?.id;
			if (!metalId) {
				throw new Error("Metal metadata not found. Please try again.");
			}

			if (custodyProtocol === "ALLOCATED") {
				const emptySerials = barSerials.filter(s => !s.trim());
				if (emptySerials.length > 0) {
					error = "All bar reference numbers (serial numbers) are required for allocated storage.";
					return;
				}
			}

			await withdrawMetal(auth.token, {
				metal_id: metalId,
				quantity_kg: amountToSubmit,
				storage_type: custodyProtocol,
				vault_id: vault.id,
				serial_number:
					custodyProtocol === "ALLOCATED" && barSerials.length === 1
						? barSerials[0]
						: undefined,
				serial_numbers:
					custodyProtocol === "ALLOCATED" && barSerials.length > 1
						? barSerials
						: undefined,
			});

			lastSuccess = `Dispatch request for ${amountToSubmit.toFixed(2)}kg submitted for approval.`;
			onSuccess?.();

			// Reset form
			setTimeout(() => {
				if (lastSuccess) {
					open = false;
					lastSuccess = null;
					amount = "";
					selectedMetal = "";
					barSerials = [""];
				}
			}, 2000);
		} catch (e: any) {
			error = e.message || "Withdrawal failed";
			console.error("Withdrawal error:", e);
		} finally {
			loading = false;
		}
	}
</script>

{#snippet content()}
	<div class="flex flex-col gap-6 py-4">
		{#if lastSuccess}
			<div
				class="rounded-xl bg-emerald-50 p-4 border border-emerald-100 flex items-center gap-3 animate-in fade-in zoom-in-95"
			>
				<div
					class="flex size-8 items-center justify-center rounded-full bg-emerald-500 text-white shadow-lg shadow-emerald-500/20"
				>
					<Check class="size-4" />
				</div>
				<div class="flex flex-col">
					<span class="text-xs font-black uppercase text-emerald-900"
						>Success</span
					>
					<span class="text-[10px] font-bold text-emerald-700"
						>{lastSuccess}</span
					>
				</div>
			</div>
		{/if}

		<div
			class="flex flex-col gap-3 rounded-xl bg-slate-900 p-5 text-white shadow-xl shadow-slate-900/10"
		>
			<div class="flex items-center justify-between">
				<div class="flex items-center gap-3">
					<div
						class="flex size-9 items-center justify-center rounded-lg bg-white/10"
					>
						<Warehouse class="size-4 text-white" />
					</div>
					<div class="flex flex-col">
						<span
							class="text-[9px] font-black uppercase tracking-widest text-slate-500"
							>Facility Dispatch</span
						>
						<span class="text-sm font-black tracking-tight"
							>{vault?.name}</span
						>
					</div>
				</div>
				<div class="text-right">
					<div
						class="size-1.5 rounded-full bg-emerald-500 shadow-[0_0_8px_rgba(16,185,129,0.5)] ml-auto mb-1"
					></div>
					<span
						class="text-[9px] font-bold uppercase tracking-widest text-slate-500"
						>{vault?.location}</span
					>
				</div>
			</div>
		</div>

		<div class="grid gap-5">
			<div class="grid gap-2">
				<Label
					for="metal"
					class="text-[10px] font-black uppercase tracking-widest text-slate-400 ml-1"
					>Select Asset</Label
				>
				<Select.Root type="single" bind:value={selectedMetal}>
					<Select.Trigger
						class="h-11 w-full rounded-xl border-slate-200 font-bold text-sm bg-slate-50/30"
					>
						<div class="flex items-center gap-2">
							{selectedMetal || "Select a metal"}
						</div>
					</Select.Trigger>
					<Select.Content
						class="rounded-xl border-slate-200 shadow-2xl"
					>
						{#each metalOptions as metal}
							<Select.Item
								value={metal.code}
								label={metal.name}
								class="rounded-lg py-2.5"
							>
								<div
									class="flex w-full items-center justify-between"
								>
									<span class="font-black text-sm"
										>{metal.name}</span
									>
									<span
										class="rounded-md bg-slate-100 px-1.5 py-0.5 text-[9px] font-black text-slate-500"
										>{metal.quantity.toFixed(3)} KG</span
									>
								</div>
							</Select.Item>
						{/each}
					</Select.Content>
				</Select.Root>
			</div>

			<div class="space-y-3">
				<Label
					class="text-[10px] font-black uppercase tracking-widest text-slate-400 ml-1"
					>Custody Protocol</Label
				>
				<div class="grid grid-cols-2 gap-3">
					<button
						type="button"
						class="flex flex-col items-center justify-center rounded-xl border p-4 transition-all {custodyProtocol ===
						'UNALLOCATED'
							? 'border-primary bg-primary/[0.01] shadow-sm'
							: 'border-slate-100 bg-slate-50/20 hover:border-slate-200'}"
						onclick={() => (custodyProtocol = "UNALLOCATED")}
					>
						<Waves
							class="size-5 mb-2 {custodyProtocol ===
							'UNALLOCATED'
								? 'text-primary'
								: 'text-slate-300'}"
						/>
						<span class="text-xs font-black text-slate-700"
							>Unallocated</span
						>
						<span
							class="text-[8px] text-slate-400 font-black uppercase mt-0.5 tracking-tight"
							>Shared Pool</span
						>
					</button>
					<button
						type="button"
						class="flex flex-col items-center justify-center rounded-xl border p-4 transition-all {custodyProtocol ===
						'ALLOCATED'
							? 'border-primary bg-primary/[0.01] shadow-sm'
							: 'border-slate-100 bg-slate-50/20 hover:border-slate-200'}"
						onclick={() => (custodyProtocol = "ALLOCATED")}
					>
						<ShieldCheck
							class="size-5 mb-2 {custodyProtocol === 'ALLOCATED'
								? 'text-primary'
								: 'text-slate-300'}"
						/>
						<span class="text-xs font-black text-slate-700"
							>Allocated</span
						>
						<span
							class="text-[8px] text-slate-400 font-black uppercase mt-0.5 tracking-tight"
							>Specific Bar</span
						>
					</button>
				</div>
			</div>

			<div class="grid gap-2">
				<div class="flex items-center justify-between ml-1">
					<Label
						for="amount"
						class="text-[10px] font-black uppercase tracking-widest text-slate-400"
						>Withdrawal Quantity</Label
					>
					{#if selectedMetal}
						<span
							class="text-[9px] font-black text-primary uppercase"
						>
							{#if custodyProtocol === "ALLOCATED" && currentMetalData?.bar_kg > 0}
								Estimated: {amountToSubmit.toFixed(1)} KG
							{:else}
								Available: {remainingInVault.toFixed(3)} KG
							{/if}
						</span>
					{/if}
				</div>
				{#if custodyProtocol === "UNALLOCATED"}
					<div class="relative animate-in fade-in slide-in-from-top-2">
						<Input
							id="amount"
							type="number"
							placeholder="0.000"
							bind:value={amount}
							class="pl-11 h-12 w-full rounded-lg border-slate-200 font-black text-lg bg-slate-50/30"
						/>
						<Scale
							class="absolute left-4 top-1/2 -translate-y-1/2 size-4 text-slate-300"
						/>
						<div
							class="absolute right-4 top-1/2 -translate-y-1/2 text-[10px] font-black text-slate-400 uppercase tracking-widest"
						>
							KG
						</div>
					</div>
				{/if}
			</div>

			{#if custodyProtocol === "ALLOCATED"}
				<div class="grid gap-3 animate-in fade-in slide-in-from-top-2">
					<div class="flex items-center justify-between ml-1">
						<Label
							class="text-[10px] font-black uppercase tracking-widest text-slate-400"
							>Bar Reference Numbers</Label
						>
					</div>

					<div class="grid gap-3">
						{#each barSerials as serial, i}
							<div
								class="flex items-center gap-2 group animate-in fade-in slide-in-from-left-2"
								style="animation-delay: {i * 50}ms"
							>
								<div class="relative flex-1">
									<Input
										placeholder="Enter Serial Number..."
										bind:value={barSerials[i]}
										class="pl-11 h-12 w-full rounded-lg border-slate-200 font-black text-sm bg-slate-50/30 focus-visible:ring-primary"
										required
									/>
									<ShieldCheck
										class="absolute left-4 top-1/2 -translate-y-1/2 size-4 text-slate-300"
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
						class="w-full border-dashed border-slate-200 text-slate-400 hover:text-primary hover:border-primary hover:bg-primary/[0.02] h-11 rounded-lg font-bold text-xs"
						onclick={addBar}
					>
						<Plus class="size-3.5 mr-2" />
						Add More Bars
					</Button>
				</div>
			{/if}
		</div>

		{#if selectedMetal}
			<div class="grid grid-cols-2 gap-3 opacity-80">
				<div
					class="rounded-lg border border-slate-100 p-3 bg-slate-50/50"
				>
					<div class="flex items-center gap-2 mb-1.5">
						<ShieldCheck class="size-3 text-slate-400" />
						<span
							class="text-[8px] font-black uppercase tracking-widest text-slate-400"
							>Allocated</span
						>
					</div>
					<div class="font-black text-sm text-slate-700">
						{currentMetalData?.breakdown.ALLOCATED.toFixed(3)}
						<span class="text-[9px] opacity-40 font-bold">KG</span>
					</div>
				</div>
				<div
					class="rounded-lg border border-slate-100 p-3 bg-slate-50/50"
				>
					<div class="flex items-center gap-2 mb-1.5">
						<Waves class="size-3 text-slate-400" />
						<span
							class="text-[8px] font-black uppercase tracking-widest text-slate-400"
							>Unallocated</span
						>
					</div>
					<div class="font-black text-sm text-slate-700">
						{currentMetalData?.breakdown.UNALLOCATED.toFixed(3)}
						<span class="text-[9px] opacity-40 font-bold">KG</span>
					</div>
				</div>
			</div>
		{/if}

		{#if error}
			<div
				<div class="rounded-lg bg-red-50 p-3.5 text-[10px] font-black uppercase tracking-tight text-red-600 border border-red-100 flex items-center gap-2 animate-in fade-in slide-in-from-top-1"
			>
				<div class="size-1.5 rounded-full bg-red-500"></div>
				{error}
			</div>
		{/if}

		<Button
			class="w-full h-12 mt-2 font-black uppercase tracking-widest shadow-xl shadow-primary/10 rounded-lg group text-xs"
			disabled={!selectedMetal ||
				!amountToSubmit ||
				amountToSubmit <= 0 ||
				loading ||
				lastSuccess !== null ||
				(custodyProtocol === "ALLOCATED" && barSerials.some(s => !s.trim()))}
			onclick={handleWithdraw}
		>
			{#if loading}
				<Loader2 class="mr-2 size-4 animate-spin" />
				Processing Dispatch...
			{:else if lastSuccess}
				Authorized
			{:else}
				Authorize Withdrawal
				<MoveRight
					class="size-4 ml-2 transition-transform group-hover:translate-x-1"
				/>
			{/if}
		</Button>
	</div>
{/snippet}

{#if isMobile.current}
	<Sheet.Root bind:open>
		<Sheet.Content
			side="bottom"
			class="rounded-t-2xl p-7 sm:max-w-full"
		>
			<Sheet.Header class="text-left mb-2">
				<Sheet.Title
					class="text-2xl font-black uppercase tracking-tighter"
					>Asset Withdrawal</Sheet.Title
				>
				<Sheet.Description
					class="text-[10px] font-black uppercase tracking-widest text-slate-400"
					>Initiate secure facility transfer</Sheet.Description
				>
			</Sheet.Header>
			{@render content()}
		</Sheet.Content>
	</Sheet.Root>
{:else}
	<Dialog.Root bind:open>
		<Dialog.Content class="sm:max-w-[440px] rounded-2xl p-8">
			<Dialog.Header class="mb-2">
				<Dialog.Title
					class="text-3xl font-black uppercase tracking-tighter"
					>Asset Withdrawal</Dialog.Title
				>
				<Dialog.Description
					class="text-[10px] font-black uppercase tracking-widest text-slate-400"
					>Initiate secure facility transfer protocols</Dialog.Description
				>
			</Dialog.Header>
			{@render content()}
		</Dialog.Content>
	</Dialog.Root>
{/if}
