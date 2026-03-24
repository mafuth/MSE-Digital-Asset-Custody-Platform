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
        User
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
            second: "2-digit"
		});
	}
</script>

<Dialog.Root bind:open>
	<Dialog.Content class="sm:max-w-[500px] border-none bg-slate-50/50 p-0 overflow-hidden shadow-2xl">
		<div class="print-container bg-white p-8 md:p-12 shadow-inner min-h-[600px] flex flex-col">
            <!-- Receipt Header -->
            <div class="flex flex-col items-center text-center mb-10 border-b border-dashed border-slate-200 pb-10">
                <div class="size-16 rounded-full bg-slate-900 flex items-center justify-center mb-4 shadow-xl">
                    <ShieldCheck class="size-8 text-primary" />
                </div>
                <h2 class="text-2xl font-black uppercase tracking-tighter">Bare Metals Pvt.</h2>
                <p class="text-[10px] font-black uppercase tracking-[0.2em] text-slate-400">Institutional Custody Receipt</p>
                
                <div class="mt-8 flex items-center gap-2 px-4 py-1.5 rounded-full bg-emerald-50 border border-emerald-100 italic">
                    <CheckCircle2 class="size-3.5 text-emerald-500" />
                    <span class="text-[11px] font-black uppercase text-emerald-700 tracking-tight">Verified & Authorized</span>
                </div>
            </div>

            <!-- Receipt Body -->
            <div class="space-y-8 flex-1">
                <!-- Transaction Type & Status -->
                <div class="flex justify-between items-start">
                    <div>
                        <span class="text-[9px] font-black uppercase tracking-widest text-slate-400 block mb-1">Entry Type</span>
                        <div class="flex items-center gap-2">
                            <span class={cn(
                                "text-lg font-black uppercase tracking-tight",
                                transaction?.type === 'DEPOSIT' ? 'text-emerald-600' : 'text-rose-600'
                            )}>
                                {transaction?.type || 'N/A'}
                            </span>
                        </div>
                    </div>
                    <div class="text-right">
                        <span class="text-[9px] font-black uppercase tracking-widest text-slate-400 block mb-1">Status</span>
                        <span class="text-xs font-black uppercase tracking-widest bg-slate-100 px-2 py-0.5 rounded">
                            {transaction?.status || 'COMPLETED'}
                        </span>
                    </div>
                </div>

                <!-- Asset Details -->
                <div class="grid grid-cols-2 gap-8 py-6 border-y border-dashed border-slate-100">
                    <div>
                        <span class="text-[9px] font-black uppercase tracking-widest text-slate-400 block mb-1">Physical Asset</span>
                        <div class="flex flex-col">
                            <span class="font-black text-slate-900">{transaction?.metal?.name || 'Metal Asset'}</span>
                            <span class="text-[10px] font-bold text-slate-400 uppercase tracking-widest font-mono">{transaction?.metal?.code || '---'}</span>
                        </div>
                    </div>
                    <div>
                        <span class="text-[9px] font-black uppercase tracking-widest text-slate-400 block mb-1">Total Mass</span>
                        <div class="flex items-baseline gap-1">
                            <span class="text-xl font-black text-slate-900">{transaction?.quantity || '0.000'}</span>
                            <span class="text-xs font-bold text-slate-400 uppercase">KG</span>
                        </div>
                    </div>
                </div>

                <!-- Metadata Grid -->
                <div class="grid gap-6">
                    <div class="flex items-center justify-between">
                        <div class="flex items-center gap-2">
                            <Calendar class="size-3.5 text-slate-300" />
                            <span class="text-[10px] font-black uppercase tracking-widest text-slate-400">Timestamp</span>
                        </div>
                        <span class="text-[11px] font-bold text-slate-700">{transaction?.created_at ? formatDate(transaction.created_at) : '---'}</span>
                    </div>

                    <div class="flex items-center justify-between">
                        <div class="flex items-center gap-2">
                            <Hash class="size-3.5 text-slate-300" />
                            <span class="text-[10px] font-black uppercase tracking-widest text-slate-400">Reference ID</span>
                        </div>
                        <code class="text-[10px] font-mono font-bold text-slate-500 bg-slate-50 px-2 py-1 rounded select-all break-all text-right max-w-[200px]">
                            {transaction?.id || '---'}
                        </code>
                    </div>

                    <div class="flex items-center justify-between">
                        <div class="flex items-center gap-2">
                            <User class="size-3.5 text-slate-300" />
                            <span class="text-[10px] font-black uppercase tracking-widest text-slate-400">Account ID</span>
                        </div>
                        <code class="text-[10px] font-mono font-bold text-slate-400 truncate max-w-[120px]">
                            {transaction?.account_id || '---'}
                        </code>
                    </div>
                </div>
            </div>

            <!-- Footer / Security -->
            <div class="mt-auto pt-10 border-t border-dashed border-slate-200">
                <div class="flex items-center justify-center gap-1.5 mb-2">
                    <ShieldCheck class="size-4 text-slate-300" />
                    <span class="text-[8px] font-black uppercase tracking-[0.3em] text-slate-300">Sovereign Custody Guaranteed</span>
                </div>
                <div class="flex flex-col items-center italic opacity-30">
                    <div class="w-full h-8 bg-black/5 rounded-md mb-2 flex items-center justify-center">
                        <span class="text-[7px] font-mono text-black uppercase tracking-[0.5em]">CERTIFIED INSTITUTIONAL RECORD</span>
                    </div>
                </div>
            </div>
        </div>

        <!-- Action Bar (Hidden on Print) -->
		<div class="flex gap-3 p-6 bg-slate-100/80 backdrop-blur-md border-t border-slate-200 print:hidden">
            <Button variant="outline" class="flex-1 font-black uppercase tracking-widest text-[10px] h-10 rounded-xl" onclick={() => open = false}>
                Dismiss
            </Button>
            <Button class="flex-1 font-black uppercase tracking-widest text-[10px] h-10 rounded-xl shadow-xl shadow-primary/20" onclick={handlePrint}>
                <Printer class="size-3.5 mr-2" />
                Print Receipt
            </Button>
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
