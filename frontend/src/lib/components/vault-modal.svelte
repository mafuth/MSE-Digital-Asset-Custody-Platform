<script lang="ts">
	import { IsMobile } from "$lib/hooks/is-mobile.svelte";
	import * as Dialog from "$lib/components/ui/dialog/index.js";
	import * as Sheet from "$lib/components/ui/sheet/index.js";
	import { Button } from "$lib/components/ui/button/index.js";
	import { Input } from "$lib/components/ui/input/index.js";
	import { Label } from "$lib/components/ui/label/index.js";
	import * as Select from "$lib/components/ui/select/index.js";
	import {
		Warehouse,
		MapPin,
		Scale,
		Loader2,
		Check,
		Plus,
		Pencil,
	} from "@lucide/svelte";
	import { auth } from "$lib/auth.svelte";
	import { addVault, updateVault } from "$lib/api";

	type Props = {
		open: boolean;
		vault?: any; // If provided, we are in EDIT mode
		onSuccess?: () => void;
	};

	let {
		open = $bindable(false),
		vault,
		onSuccess,
	}: Props = $props();
	const isMobile = new IsMobile();

	// Form state
	let name = $state("");
	let location = $state("");
	let capacity = $state("");
	let status = $state("ACTIVE");
	let loading = $state(false);
	let error = $state<string | null>(null);
	let lastSuccess = $state<string | null>(null);

	// Reset form when opening/closing or changing vault
	$effect(() => {
		if (open) {
			if (vault) {
				name = vault.name;
				location = vault.location;
				capacity = vault.capacity_kg.toString();
				status = vault.status;
			} else {
				name = "";
				location = "";
				capacity = "";
				status = "ACTIVE";
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
			location,
			capacity_kg: parseFloat(capacity),
			status,
		};

		try {
			if (vault) {
				await updateVault(auth.token, vault.id, data);
				lastSuccess = "Vault updated successfully.";
			} else {
				await addVault(auth.token, data);
				lastSuccess = "Vault created successfully.";
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
			console.error("Vault operation error:", e);
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
					for="name"
					class="text-[10px] font-black uppercase tracking-widest text-slate-400 ml-1"
					>Vault Name</Label
				>
				<div class="relative">
					<Input
						id="name"
						placeholder="e.g. Genesis Primary"
						bind:value={name}
						class="pl-11 h-12 w-full rounded-xl border-slate-200 font-black text-sm bg-slate-50/30"
					/>
					<Warehouse
						class="absolute left-4 top-1/2 -translate-y-1/2 size-4 text-slate-300"
					/>
				</div>
			</div>

			<div class="grid gap-2">
				<Label
					for="location"
					class="text-[10px] font-black uppercase tracking-widest text-slate-400 ml-1"
					>Location</Label
				>
				<div class="relative">
					<Input
						id="location"
						placeholder="e.g. Zurich, Switzerland"
						bind:value={location}
						class="pl-11 h-12 w-full rounded-xl border-slate-200 font-black text-sm bg-slate-50/30"
					/>
					<MapPin
						class="absolute left-4 top-1/2 -translate-y-1/2 size-4 text-slate-300"
					/>
				</div>
			</div>

			<div class="grid gap-2">
				<Label
					for="capacity"
					class="text-[10px] font-black uppercase tracking-widest text-slate-400 ml-1"
					>Total Capacity (KG)</Label
				>
				<div class="relative">
					<Input
						id="capacity"
						type="number"
						placeholder="10000"
						bind:value={capacity}
						class="pl-11 h-12 w-full rounded-xl border-slate-200 font-black text-sm bg-slate-50/30"
					/>
					<Scale
						class="absolute left-4 top-1/2 -translate-y-1/2 size-4 text-slate-300"
					/>
				</div>
			</div>

			<div class="grid gap-2">
				<Label
					for="status"
					class="text-[10px] font-black uppercase tracking-widest text-slate-400 ml-1"
					>Operational Status</Label
				>
				<Select.Root type="single" bind:value={status}>
					<Select.Trigger
						class="h-11 w-full rounded-xl border-slate-200 font-bold text-sm bg-slate-50/30"
					>
						{status}
					</Select.Trigger>
					<Select.Content class="rounded-xl border-slate-200 shadow-2xl">
						<Select.Item value="ACTIVE" label="Active" class="rounded-lg py-2.5">
							<span class="font-black text-sm uppercase">Active</span>
						</Select.Item>
						<Select.Item value="FULL" label="Full" class="rounded-lg py-2.5">
							<span class="font-black text-sm uppercase">Full</span>
						</Select.Item>
						<Select.Item value="MAINTENANCE" label="Maintenance" class="rounded-lg py-2.5">
							<span class="font-black text-sm uppercase">Maintenance</span>
						</Select.Item>
					</Select.Content>
				</Select.Root>
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
			disabled={!name || !location || !capacity || parseFloat(capacity) <= 0 || loading || lastSuccess !== null}
			onclick={handleSubmit}
		>
			{#if loading}
				<Loader2 class="mr-2 size-4 animate-spin" />
				Processing...
			{:else}
				{#if vault}
					Update Vault Configuration
				{:else}
					Initialize New Facility
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
					>{vault ? 'Edit Vault' : 'Initialize Vault'}</Sheet.Title
				>
				<Sheet.Description
					class="text-[10px] font-black uppercase tracking-widest text-slate-400"
					>{vault ? 'Modify facility parameters' : 'Register a new storage node'}</Sheet.Description
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
					>{vault ? 'Edit Vault' : 'Initialize Vault'}</Dialog.Title
				>
				<Dialog.Description
					class="text-[10px] font-black uppercase tracking-widest text-slate-400"
					>{vault ? 'Modify facility parameters' : 'Register a new storage node'}</Dialog.Description
				>
			</Dialog.Header>
			{@render content()}
		</Dialog.Content>
	</Dialog.Root>
{/if}
