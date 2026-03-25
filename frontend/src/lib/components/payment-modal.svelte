<script lang="ts">
	import * as Dialog from "$lib/components/ui/dialog";
	import { Button } from "$lib/components/ui/button";
	import { Input } from "$lib/components/ui/input";
	import { Label } from "$lib/components/ui/label";
	import {
		CreditCard,
		ShieldCheck,
		Lock,
		Info,
		ArrowRight,
		CheckCircle2,
		Loader2,
	} from "@lucide/svelte";

	let {
		show = $bindable(false),
		assetName = "Metal Asset",
		quantity = 0,
		total = 0,
		onConfirm = () => {},
	} = $props();

	let cardNumber = $state("4242 4242 4242 4242");
	let expiry = $state("12/28");
	let cvc = $state("•••");
	let processing = $state(false);
	let completed = $state(false);


	async function handlePayment() {
		processing = true;
		// Artificial delay for gateway communication simulation
		await new Promise((resolve) => setTimeout(resolve, 2000));
		processing = false;
		completed = true;

		// Another small delay for success checkmark visibility
		await new Promise((resolve) => setTimeout(resolve, 1000));

		onConfirm();
		show = false;
		// Reset state for next time
		setTimeout(() => {
			completed = false;
		}, 500);
	}
</script>

<Dialog.Root bind:open={show}>
	<Dialog.Content
		class="max-w-sm p-0 gap-0 overflow-hidden rounded-xl border border-slate-200 shadow-xl"
	>
		<Dialog.Header class="p-4 mb-5">
			<div class="flex items-center gap-2">
				<div
					class="size-6 rounded-md bg-primary text-primary-foreground flex items-center justify-center"
				>
					<Lock class="size-3.5" />
				</div>
				<Dialog.Title
					class="text-sm font-black tracking-tight uppercase"
					>Security Gateway</Dialog.Title
				>
			</div>
			<Dialog.Description
				class="text-[10px] font-bold text-slate-400 mt-0.5"
				>Bare Metals Custody Protocol v4.2</Dialog.Description
			>
		</Dialog.Header>

		<div class="p-5 space-y-6 bg-white">
			{#if !completed}
				<!-- Order Summary (Compact) -->
				<div
					class="rounded-lg bg-slate-50 border border-slate-100 p-3 space-y-2"
				>
					<div
						class="flex justify-between items-center text-[10px] font-bold uppercase tracking-widest text-slate-400"
					>
						<span>Asset Breakdown</span>
						<span>Total</span>
					</div>
					<div class="flex justify-between items-end">
						<div class="space-y-0.5">
							<p class="text-xs font-black text-slate-900">
								{assetName}
							</p>
							<p class="text-[10px] text-slate-500 font-medium">
								{quantity.toFixed(1)} KG Ingress
							</p>
						</div>
						<div class="text-right">
							<p class="text-xs font-black text-primary">
								${total.toLocaleString(undefined, {
									minimumFractionDigits: 2,
									maximumFractionDigits: 2,
								})}
							</p>
						</div>
					</div>
				</div>

				<!-- Form -->
				<div class="space-y-4">
					<div class="space-y-2">
						<Label
							class="text-[10px] font-black uppercase tracking-widest text-slate-400 ml-0.5"
							>Card Number</Label
						>
						<div class="relative">
							<Input
								bind:value={cardNumber}
								class="pl-9 h-9 text-xs font-bold border-slate-200 rounded-lg focus-visible:ring-primary"
							/>
							<CreditCard
								class="absolute left-3 top-2.5 size-3.5 text-slate-300"
							/>
						</div>
					</div>

					<div class="grid grid-cols-2 gap-3">
						<div class="space-y-2">
							<Label
								class="text-[10px] font-black uppercase tracking-widest text-slate-400 ml-0.5"
								>Expiry</Label
							>
							<Input
								bind:value={expiry}
								class="h-9 text-xs font-bold border-slate-200 rounded-lg"
							/>
						</div>
						<div class="space-y-2">
							<Label
								class="text-[10px] font-black uppercase tracking-widest text-slate-400 ml-0.5"
								>CVC</Label
							>
							<Input
								bind:value={cvc}
								class="h-9 text-xs font-bold border-slate-200 rounded-lg"
							/>
						</div>
					</div>
				</div>

				<div
					class="flex items-start gap-2 p-2.5 rounded-lg bg-amber-50/50 border border-amber-100/50"
				>
					<Info class="size-3.5 text-amber-500 shrink-0 mt-0.5" />
					<p
						class="text-[9px] font-semibold text-amber-800/70 leading-normal italic"
					>
						Demonstration mode. Transactions are authorized for
						record only.
					</p>
				</div>

				<Button
					variant="default"
					size="sm"
					class="w-full h-9 rounded-lg font-black text-[11px] uppercase tracking-widest shadow-sm shadow-primary/10 transition-all hover:translate-y-[-1px] active:translate-y-[0px]"
					onclick={handlePayment}
					disabled={processing}
				>
					{#if processing}
						<Loader2 class="size-3 animate-spin mr-2" />
						Syncing...
					{:else}
						Initialize Ingress
						<ArrowRight class="size-3 ml-2" />
					{/if}
				</Button>
			{:else}
				<div
					class="flex flex-col items-center justify-center py-10 space-y-3 animate-in fade-in zoom-in duration-300"
				>
					<div
						class="size-16 rounded-full bg-emerald-50 flex items-center justify-center border-2 border-emerald-100 shadow-sm"
					>
						<CheckCircle2 class="size-8 text-emerald-500" />
					</div>
					<div class="text-center space-y-1">
						<h4
							class="font-black text-sm text-slate-900 uppercase tracking-tight"
						>
							Authorization Success
						</h4>
						<p class="text-[10px] font-bold text-slate-400">
							Finalizing audit trail...
						</p>
					</div>
				</div>

				<div
					class="flex items-center justify-center gap-2 py-4 border-t border-slate-50"
				>
					<ShieldCheck class="size-3 text-emerald-500" />
					<span
						class="text-[8px] font-black uppercase tracking-[0.2em] text-emerald-600/60"
						>Verified & Encrypted</span
					>
				</div>
			{/if}
		</div>
	</Dialog.Content>
</Dialog.Root>
