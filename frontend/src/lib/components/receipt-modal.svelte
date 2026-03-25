<script lang="ts">
    import * as Dialog from "$lib/components/ui/dialog/index.js";
    import { Button } from "$lib/components/ui/button/index.js";
    import {
        Printer,
        Download,
        ShieldCheck,
        Warehouse,
        Scale,
        CheckCircle2,
        Hash,
        Calendar,
        User,
    } from "@lucide/svelte";
    import { cn } from "$lib/utils";

    type Props = {
        open: boolean;
        transaction: any;
    };

    let { open = $bindable(false), transaction }: Props = $props();

    function handlePrint() {
        window.print();
    }

    function formatDate(dateStr: string) {
        return new Date(dateStr).toLocaleDateString(undefined, {
            year: "numeric",
            month: "long",
            day: "numeric",
            hour: "2-digit",
            minute: "2-digit",
            second: "2-digit",
        });
    }
</script>

<Dialog.Root bind:open>
    <Dialog.Content
        class="sm:max-w-[420px] border-none bg-slate-50/50 p-0 overflow-hidden shadow-2xl rounded-[2rem]"
    >
        <div
            class="print-container bg-white p-6 md:p-8 shadow-inner min-h-[480px] flex flex-col relative"
        >
            <!-- Receipt Header -->
            <div
                class="flex flex-col items-center text-center mb-6 border-b border-dashed border-slate-200 pb-6 mt-2"
            >
                <div
                    class="size-12 rounded-full bg-slate-900 flex items-center justify-center mb-3 shadow-lg"
                >
                    <ShieldCheck class="size-6 text-primary" />
                </div>
                <h2
                    class="text-xl font-black uppercase tracking-tighter text-slate-900"
                >
                    Bare Metals Pvt.
                </h2>
                <p
                    class="text-[9px] font-black uppercase tracking-[0.2em] text-slate-500"
                >
                    Institutional Custody Receipt
                </p>

                <div
                    class="mt-4 flex items-center gap-1.5 px-3 py-1 rounded-full bg-emerald-50 border border-emerald-100 italic"
                >
                    <CheckCircle2 class="size-3 text-emerald-500" />
                    <span
                        class="text-[9px] font-black uppercase text-emerald-700 tracking-tight"
                        >Verified & Authorized</span
                    >
                </div>
            </div>

            <!-- Receipt Body -->
            <div class="space-y-6 flex-1">
                <!-- Transaction Type & Status -->
                <div class="flex justify-between items-start">
                    <div>
                        <span
                            class="text-[8px] font-black uppercase tracking-widest text-slate-500 block mb-0.5"
                            >Entry Type</span
                        >
                        <span
                            class={cn(
                                "text-sm font-black uppercase tracking-tight",
                                transaction?.type === "DEPOSIT"
                                    ? "text-emerald-600"
                                    : "text-rose-600",
                            )}
                        >
                            {transaction?.type || "N/A"}
                        </span>
                    </div>
                    <div class="text-right">
                        <span
                            class="text-[8px] font-black uppercase tracking-widest text-slate-500 block mb-0.5"
                            >Status</span
                        >
                        <span
                            class="text-[10px] font-black uppercase tracking-widest bg-slate-100 px-1.5 py-0.5 rounded text-slate-700"
                        >
                            {transaction?.status || "COMPLETED"}
                        </span>
                    </div>
                </div>

                <!-- Asset Details -->
                <div
                    class="grid grid-cols-2 gap-4 py-4 border-y border-dashed border-slate-100"
                >
                    <div>
                        <span
                            class="text-[8px] font-black uppercase tracking-widest text-slate-500 block mb-0.5"
                            >Physical Asset</span
                        >
                        <div class="flex flex-col">
                            <span class="font-black text-slate-900 text-sm"
                                >{transaction?.metal?.name ||
                                    "Metal Asset"}</span
                            >
                            <span
                                class="text-[9px] font-bold text-slate-500 uppercase tracking-widest font-mono"
                                >{transaction?.metal?.code || "---"}</span
                            >
                        </div>
                    </div>
                    <div>
                        <span
                            class="text-[8px] font-black uppercase tracking-widest text-slate-500 block mb-0.5"
                            >Total Mass</span
                        >
                        <div class="flex items-baseline gap-1">
                            <span class="text-lg font-black text-slate-900"
                                >{transaction?.quantity || "0.000"}</span
                            >
                            <span
                                class="text-[10px] font-bold text-slate-500 uppercase"
                                >KG</span
                            >
                        </div>
                    </div>
                </div>

                <!-- Metadata Grid -->
                <div class="grid gap-4">
                    <div
                        class="flex items-center justify-between border-b border-slate-50 pb-2"
                    >
                        <div
                            class="flex items-center gap-1.5 whitespace-nowrap"
                        >
                            <Calendar class="size-3 text-slate-400" />
                            <span
                                class="text-[9px] font-black uppercase tracking-widest text-slate-500"
                                >Timestamp</span
                            >
                        </div>
                        <span class="text-[10px] font-bold text-slate-900"
                            >{transaction?.created_at
                                ? formatDate(transaction.created_at)
                                : "---"}</span
                        >
                    </div>

                    <div
                        class="flex items-center justify-between border-b border-slate-50 pb-2"
                    >
                        <div
                            class="flex items-center gap-1.5 whitespace-nowrap"
                        >
                            <Hash class="size-3 text-slate-400" />
                            <span
                                class="text-[9px] font-black uppercase tracking-widest text-slate-500"
                                >Ref ID</span
                            >
                        </div>
                        <code
                            class="text-[9px] font-mono font-bold text-slate-700 bg-slate-50 px-1.5 py-0.5 rounded select-all break-all text-right ml-4"
                        >
                            {transaction?.id || "---"}
                        </code>
                    </div>

					<div
						class="flex items-center justify-between border-b border-slate-50 pb-2"
					>
						<div
							class="flex items-center gap-1.5 whitespace-nowrap"
						>
							<Warehouse class="size-3 text-slate-400" />
							<span
								class="text-[9px] font-black uppercase tracking-widest text-slate-500"
								>Vault</span
							>
						</div>
						<span class="text-[10px] font-bold text-slate-900"
							>{transaction?.vault?.name || "N/A"}</span>
					</div>

					{#if transaction?.bar_ref_id}
						<div
							class="flex items-center justify-between border-b border-slate-50 pb-2 bg-primary/[0.02] -mx-4 px-4 py-2"
						>
							<div
								class="flex items-center gap-1.5 whitespace-nowrap"
							>
								<ShieldCheck class="size-3 text-primary/60" />
								<span
									class="text-[9px] font-black uppercase tracking-widest text-primary/70"
									>Bar Ref ID</span
								>
							</div>
							<code class="text-[10px] font-mono font-black text-primary bg-primary/5 px-2 py-0.5 rounded border border-primary/10 shadow-sm">
								{transaction.bar_ref_id}
							</code>
						</div>
					{/if}

					<div class="flex items-center justify-between">
						<div
							class="flex items-center gap-1.5 whitespace-nowrap"
						>
							<User class="size-3 text-slate-400" />
							<span
								class="text-[9px] font-black uppercase tracking-widest text-slate-500"
								>Account</span
							>
						</div>
						<code
							class="text-[9px] font-mono font-bold text-slate-600 break-all text-right ml-4"
						>
							{transaction?.account_id || "---"}
						</code>
					</div>
                </div>
            </div>

            <!-- Footer / Security -->
            <div class="mt-8 pt-6 border-t border-dashed border-slate-200">
                <div class="flex items-center justify-center gap-1.5 mb-2">
                    <ShieldCheck class="size-3 text-slate-300" />
                    <span
                        class="text-[7px] font-black uppercase tracking-[0.3em] text-slate-300"
                        >Sovereign Custody Guaranteed</span
                    >
                </div>
                <div class="flex flex-col items-center italic opacity-20">
                    <div
                        class="w-full h-6 bg-black/5 rounded-md mb-1 flex items-center justify-center"
                    >
                        <span
                            class="text-[6px] font-mono text-black uppercase tracking-[0.5em]"
                            >CERTIFIED INSTITUTIONAL RECORD</span
                        >
                    </div>
                </div>
            </div>
        </div>
    </Dialog.Content>
</Dialog.Root>

<style>
    @media print {
        :global(body > *:not(.print-container)) {
            display: none !important;
        }
        :global(body) {
            background: white !important;
            padding: 0 !important;
            margin: 0 !important;
        }
        .print-container {
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            padding: 2cm !important;
            box-shadow: none !important;
            border: none !important;
        }
        :global(.dialog-overlay) {
            display: none !important;
        }
    }
</style>
