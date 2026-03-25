<script lang="ts">
	import { IsMobile } from "$lib/hooks/is-mobile.svelte";
	import * as Dialog from "$lib/components/ui/dialog/index.js";
	import * as Sheet from "$lib/components/ui/sheet/index.js";
	import { Button } from "$lib/components/ui/button/index.js";
	import { Input } from "$lib/components/ui/input/index.js";
	import { Label } from "$lib/components/ui/label/index.js";
	import {
		Database,
		TrendingUp,
		Loader2,
		Check,
		Plus,
		Tag,
	} from "@lucide/svelte";
	import { auth } from "$lib/auth.svelte";
	import { addMetal, updateMetal } from "$lib/api";

	type Props = {
		open: boolean;
		metal?: any; // If provided, we are in EDIT mode
		onSuccess?: () => void;
	};

	let {
		open = $bindable(false),
		metal,
		onSuccess,
	}: Props = $props();
	const isMobile = new IsMobile();

	// Form state
	let name = $state("");
	let code = $state("");
	let category = $state("");
	let price = $state("");
	let barWeight = $state("");
	let loading = $state(false);
	let error = $state<string | null>(null);
	let lastSuccess = $state<string | null>(null);

	// Reset form when opening/closing or changing metal
	$effect(() => {
		if (open) {
			if (metal) {
				name = metal.name;
				code = metal.code;
				category = metal.category;
				price = metal.current_price_kg.toString();
				barWeight = metal.bar_kg?.toString() || "0";
			} else {
				name = "";
				code = "";
				category = "";
				price = "";
				barWeight = "";
			}
			error = null;
			lastSuccess = null;
		}
	});

	async function handleSubmit() {
		if (!auth.token) return;

		loading = true;
		error = null;
		lastSuccess = null;

		const data = {
			name,
			code,
			category,
			current_price_kg: parseFloat(price),
			bar_kg: parseFloat(barWeight) || 0,
		};

		try {
			if (metal) {
				await updateMetal(auth.token, metal.id, data);
				lastSuccess = "Metal updated successfully.";
			} else {
				await addMetal(auth.token, data);
				lastSuccess = "Metal created successfully.";
			}
			
			onSuccess?.();

			// Close modal after success
			setTimeout(() => {
				if (lastSuccess) {
					open = false;
					lastSuccess = null;
				}
			}, 1500);
		} catch (e: any) {
			error = e.message || "Operation failed";
			console.error("Metal operation error:", e);
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

		<div class="grid gap-5">
			<div class="grid gap-2">
				<Label
					for="code"
					class="text-[10px] font-black uppercase tracking-widest text-slate-400 ml-1"
					>Asset Code (Symbol)</Label
				>
				<div class="relative">
					<Input
						id="code"
						placeholder="e.g. AU99"
						bind:value={code}
						class="pl-11 h-12 w-full rounded-xl border-slate-200 font-black text-sm bg-slate-50/30"
					/>
					<Tag
						class="absolute left-4 top-1/2 -translate-y-1/2 size-4 text-slate-300"
					/>
				</div>
			</div>

			<div class="grid gap-2">
				<Label
					for="name"
					class="text-[10px] font-black uppercase tracking-widest text-slate-400 ml-1"
					>Asset Name</Label
				>
				<div class="relative">
					<Input
						id="name"
						placeholder="e.g. 24K Gold"
						bind:value={name}
						class="pl-11 h-12 w-full rounded-xl border-slate-200 font-black text-sm bg-slate-50/30"
					/>
					<Database
						class="absolute left-4 top-1/2 -translate-y-1/2 size-4 text-slate-300"
					/>
				</div>
			</div>

			<div class="grid gap-2">
				<Label
					for="category"
					class="text-[10px] font-black uppercase tracking-widest text-slate-400 ml-1"
					>Category</Label
				>
				<div class="relative">
					<Input
						id="category"
						placeholder="e.g. Precious Metals"
						bind:value={category}
						class="pl-11 h-12 w-full rounded-xl border-slate-200 font-black text-sm bg-slate-50/30"
					/>
					<Tag
						class="absolute left-4 top-1/2 -translate-y-1/2 size-4 text-slate-300"
					/>
				</div>
			</div>

			<div class="grid gap-2">
				<Label
					for="price"
					class="text-[10px] font-black uppercase tracking-widest text-slate-400 ml-1"
					>Market Price (per KG)</Label
				>
				<div class="relative">
					<Input
						id="price"
						type="number"
						step="0.01"
						placeholder="65000"
						bind:value={price}
						class="pl-11 h-12 w-full rounded-xl border-slate-200 font-black text-sm bg-slate-50/30"
					/>
					<TrendingUp
						class="absolute left-4 top-1/2 -translate-y-1/2 size-4 text-slate-300"
					/>
				</div>
			</div>

			<div class="grid gap-2">
				<Label
					for="barWeight"
					class="text-[10px] font-black uppercase tracking-widest text-slate-400 ml-1"
					>Physical bar Weight (KG)</Label
				>
				<div class="relative">
					<Input
						id="barWeight"
						type="number"
						step="0.001"
						placeholder="12.4"
						bind:value={barWeight}
						class="pl-11 h-12 w-full rounded-xl border-slate-200 font-black text-sm bg-slate-50/30"
					/>
					<Plus
						class="absolute left-4 top-1/2 -translate-y-1/2 size-4 text-slate-300"
					/>
				</div>
			</div>
		</div>

		{#if error}
			<div
				class="rounded-xl bg-red-50 p-3.5 text-[10px] font-black uppercase tracking-tight text-red-600 border border-red-100 flex items-center gap-2 animate-in fade-in slide-in-from-top-1"
			>
				<div class="size-1.5 rounded-full bg-red-500"></div>
				{error}
			</div>
		{/if}

		<Button
			class="w-full h-12 mt-2 font-black uppercase tracking-widest shadow-2xl shadow-primary/20 rounded-xl group"
			disabled={!name || !code || !category || !price || parseFloat(price) <= 0 || loading || lastSuccess !== null}
			onclick={handleSubmit}
		>
			{#if loading}
				<Loader2 class="mr-2 size-4 animate-spin" />
				Processing...
			{:else}
				{#if metal}
					Update Asset Parameters
				{:else}
					Initialize New Asset
				{/if}
			{/if}
		</Button>
	</div>
{/snippet}

{#if isMobile.current}
	<Sheet.Root bind:open>
		<Sheet.Content side="bottom" class="rounded-t-[2.5rem] p-7 sm:max-w-full">
			<Sheet.Header class="text-left mb-2">
				<Sheet.Title class="text-2xl font-black uppercase tracking-tighter"
					>{metal ? 'Edit Asset' : 'Initialize Asset'}</Sheet.Title
				>
				<Sheet.Description
					class="text-[10px] font-black uppercase tracking-widest text-slate-400"
					>{metal ? 'Modify asset configuration' : 'Register a new physical asset node'}</Sheet.Description
				>
			</Sheet.Header>
			{@render content()}
		</Sheet.Content>
	</Sheet.Root>
{:else}
	<Dialog.Root bind:open>
		<Dialog.Content class="sm:max-w-[440px] rounded-[2rem] p-8">
			<Dialog.Header class="mb-2">
				<Dialog.Title class="text-3xl font-black uppercase tracking-tighter"
					>{metal ? 'Edit Asset' : 'Initialize Asset'}</Dialog.Title
				>
				<Dialog.Description
					class="text-[10px] font-black uppercase tracking-widest text-slate-400"
					>{metal ? 'Modify asset configuration' : 'Register a new physical asset node'}</Dialog.Description
				>
			</Dialog.Header>
			{@render content()}
		</Dialog.Content>
	</Dialog.Root>
{/if}
