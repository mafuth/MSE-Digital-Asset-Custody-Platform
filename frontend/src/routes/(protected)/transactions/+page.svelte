<script lang="ts">
	import { auth } from "$lib/auth.svelte";
	import { getTransactionHistory } from "$lib/api";
	import { onMount } from "svelte";
	import * as Card from "$lib/components/ui/card/index.js";
	import { Button } from "$lib/components/ui/button/index.js";
	import * as Table from "$lib/components/ui/table/index.js";
	import { Skeleton } from "$lib/components/ui/skeleton/index.js";
	import DateRangePicker from "$lib/components/date-range-picker.svelte";
	import {
		ArrowUpRight,
		ArrowDownLeft,
		History,
		Search,
		Filter,
		CalendarIcon,
		Printer,
		FileText,
	} from "@lucide/svelte";
	import type { DateRange } from "bits-ui";
	import { getLocalTimeZone, today } from "@internationalized/date";
	import ReceiptModal from "$lib/components/receipt-modal.svelte";

	let transactions = $state<any[]>([]);
	let loading = $state(true);
	let dateRange = $state<DateRange | undefined>({
		start: today(getLocalTimeZone()).subtract({ days: 30 }),
		end: today(getLocalTimeZone()),
	});

	let selectedTransaction = $state<any>(null);
	let showReceipt = $state(false);

	function openReceipt(tx: any) {
		selectedTransaction = tx;
		showReceipt = true;
	}

	async function loadTransactions() {
		if (!auth.token) return;
		loading = true;
		try {
			const startStr = dateRange?.start
				? dateRange.start.toDate(getLocalTimeZone()).toISOString()
				: undefined;
			const endStr = dateRange?.end
				? dateRange.end.toDate(getLocalTimeZone()).toISOString()
				: undefined;
			transactions = await getTransactionHistory(
				auth.token,
				startStr,
				endStr,
			);
		} catch (e) {
			console.error("Failed to load transactions:", e);
		} finally {
			loading = false;
		}
	}

	function formatDate(dateStr: string) {
		return new Date(dateStr).toLocaleDateString(undefined, {
			year: "numeric",
			month: "short",
			day: "numeric",
			hour: "2-digit",
			minute: "2-digit",
		});
	}

	onMount(loadTransactions);
</script>

<div
	class="flex flex-1 flex-col overflow-x-hidden overflow-y-auto px-6 py-6 md:px-10 md:py-8"
>
	<div class="mx-auto flex w-full max-w-7xl flex-1 flex-col">
		<div
			class="mb-6 flex flex-col gap-4 md:flex-row md:items-end md:justify-between"
		>
			<div class="space-y-1">
				<h1 class="text-3xl font-bold tracking-tight text-foreground">
					Transaction History
				</h1>
				<p class="text-sm text-muted-foreground">
					View and filter all your physical asset transactions.
				</p>
			</div>

			<div class="flex items-center gap-2">
				<DateRangePicker
					bind:value={dateRange}
					class="w-full sm:w-auto"
				/>
				<Button
					onclick={loadTransactions}
					disabled={loading}
					size="sm"
					class="gap-2 h-9"
				>
					{#if loading}
						<div
							class="h-4 w-4 animate-spin rounded-full border-2 border-current border-t-transparent"
						></div>
					{:else}
						<Search class="h-4 w-4" />
					{/if}
					Apply Filters
				</Button>
			</div>
		</div>
		<div class="rounded-xl border border-slate-200/60 overflow-hidden shadow-sm bg-card">
			<Table.Root>
				<Table.Header>
					<Table.Row class="hover:bg-transparent border-b bg-muted/30">
						<Table.Head
							class="w-[100px] h-11 text-[10px] font-bold uppercase tracking-widest px-6"
							>Type</Table.Head
						>
						<Table.Head
							class="h-11 text-[10px] font-bold uppercase tracking-widest"
							>Metal</Table.Head
						>
						<Table.Head
							class="h-11 text-[10px] font-bold uppercase tracking-widest"
							>Date & Time</Table.Head
						>
						<Table.Head
							class="h-11 text-[10px] font-bold uppercase tracking-widest"
							>Quantity</Table.Head
						>
						<Table.Head
							class="h-11 text-[10px] font-bold uppercase tracking-widest"
							>Status</Table.Head
						>
						<Table.Head
							class="text-right h-11 text-[10px] font-bold uppercase tracking-widest px-6"
							>Transaction ID</Table.Head
						>
					</Table.Row>
				</Table.Header>
				<Table.Body>
					{#if loading}
						{#each Array(5) as _}
							<Table.Row>
								<Table.Cell class="px-6"
									><Skeleton class="h-6 w-16" /></Table.Cell
								>
								<Table.Cell
									><Skeleton class="h-6 w-24" /></Table.Cell
								>
								<Table.Cell
									><Skeleton class="h-6 w-32" /></Table.Cell
								>
								<Table.Cell
									><Skeleton class="h-6 w-20" /></Table.Cell
								>
								<Table.Cell
									><Skeleton class="h-6 w-16" /></Table.Cell
								>
								<Table.Cell class="text-right px-6"
									><Skeleton
										class="ml-auto h-6 w-32"
									/></Table.Cell
								>
							</Table.Row>
						{/each}
					{:else if transactions.length > 0}
						{#each transactions as tx}
							<Table.Row
								class="group transition-colors hover:bg-slate-50/80 border-b last:border-0 cursor-pointer"
								onclick={() => openReceipt(tx)}
							>
								<Table.Cell class="px-6">
									<div class="flex items-center gap-2">
										<div
											class={tx.type === "DEPOSIT"
												? "flex size-7 items-center justify-center rounded-md bg-emerald-50 text-emerald-600"
												: "flex size-7 items-center justify-center rounded-md bg-rose-50 text-rose-600"}
										>
											{#if tx.type === "DEPOSIT"}
												<ArrowUpRight class="size-3.5" />
											{:else}
												<ArrowDownLeft class="size-3.5" />
											{/if}
										</div>
										<span
											class="text-[11px] font-bold tracking-tight uppercase"
										>
											{tx.type}
										</span>
									</div>
								</Table.Cell>
								<Table.Cell>
									<div class="flex flex-col">
										<span class="font-semibold text-sm"
											>{tx.metal?.name || "Unknown"}</span
										>
										<span
											class="text-[10px] text-muted-foreground"
											>{tx.metal?.code || ""}</span
										>
									</div>
								</Table.Cell>
								<Table.Cell
									class="text-xs text-muted-foreground whitespace-nowrap"
								>
									{formatDate(tx.created_at)}
								</Table.Cell>
								<Table.Cell>
									<span class="font-bold text-sm tracking-tight"
										>{tx.quantity} KG</span
									>
								</Table.Cell>
								<Table.Cell>
									<div
										class="inline-flex items-center rounded-md border border-emerald-100 bg-emerald-50/50 px-2 py-0.5 text-[10px] font-bold text-emerald-700 uppercase tracking-tighter"
									>
										{tx.status}
									</div>
								</Table.Cell>
								<Table.Cell class="text-right px-6">
									<code
										class="text-[11px] font-mono text-muted-foreground bg-slate-50 px-1.5 py-0.5 rounded border border-slate-100 group-hover:bg-white group-hover:border-slate-200 transition-colors"
									>
										{tx.id.substring(0, 8)}...{tx.id.substring(
											tx.id.length - 8,
										)}
									</code>
								</Table.Cell>
							</Table.Row>
						{/each}
					{:else}
						<Table.Row>
							<Table.Cell colspan={6} class="h-[300px] text-center">
								<div
									class="flex flex-col items-center justify-center gap-3 text-muted-foreground/60"
								>
									<History class="size-8 opacity-40" />
									<p class="text-sm font-medium">
										No transactions found for the selected
										criteria.
									</p>
									<Button
										variant="outline"
										size="sm"
										class="h-8 text-xs"
										onclick={() => {
											dateRange = {
												start: today(
													getLocalTimeZone(),
												).subtract({ years: 1 }),
												end: today(getLocalTimeZone()),
											};
											loadTransactions();
										}}
									>
										Clear filters
									</Button>
								</div>
							</Table.Cell>
						</Table.Row>
					{/if}
				</Table.Body>
			</Table.Root>
		</div>
	</div>
</div>

<ReceiptModal bind:open={showReceipt} transaction={selectedTransaction} />
