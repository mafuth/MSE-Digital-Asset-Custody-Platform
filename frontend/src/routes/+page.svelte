<script lang="ts">
	import * as Card from "$lib/components/ui/card/index.js";
	import { Button } from "$lib/components/ui/button/index.js";
	import { cn } from "$lib/utils.js";

	let { data } = $props();
	const prices = data.prices;

	const getPriceColor = (code: string) => {
		switch (code.toUpperCase()) {
			case "GOLD":
				return "text-yellow-500";
			case "SILVER":
				return "text-slate-400";
			case "PLATINUM":
				return "text-cyan-400";
			default:
				return "text-primary";
		}
	};
</script>

<div
	class="container mx-auto flex min-h-[calc(100vh-4rem)] flex-col items-center justify-center gap-16 px-6 py-12 md:gap-24 md:px-10"
>
	<!-- Consolidated Hero & Market Section -->
	<section class="grid w-full items-center gap-12 lg:grid-cols-2 lg:gap-24">
		<div
			class="flex flex-col items-center gap-8 text-center lg:items-start lg:text-left"
		>
			<div class="flex flex-col gap-4">
				<h1
					class="text-4xl font-extrabold tracking-tight sm:text-5xl md:text-6xl lg:text-7xl"
				>
					The Future of <span class="text-primary">Metal Custody</span
					>
				</h1>
				<p
					class="mx-auto max-w-[600px] text-lg text-muted-foreground sm:text-xl lg:mx-0"
				>
					Secure, transparent, and real-time. Manage your precious
					metal portfolio with unparalleled precision and
					institutional-grade security.
				</p>
			</div>
			<div class="flex w-full flex-col gap-4 sm:w-auto sm:flex-row">
				<Button size="lg" class="w-full px-8 sm:w-auto" href="/login"
					>Join Now</Button
				>
				<Button
					size="lg"
					variant="outline"
					class="w-full px-8 sm:w-auto"
					href="/login">Login</Button
				>
			</div>
			<div class="flex items-center gap-4 text-sm text-muted-foreground">
				<div class="flex -space-x-2">
					{#each Array(4) as _}
						<div
							class="bg-muted size-8 rounded-full border-2 border-background"
						></div>
					{/each}
				</div>
				<p>2,000+ investors</p>
			</div>
		</div>

		<!-- Market Insights Integrated into Hero -->
		<div class="flex flex-col gap-6 w-full lg:max-w-md ml-auto">
			<div class="flex flex-col gap-2 text-center lg:text-left px-2">
				<h2 class="text-2xl font-bold tracking-tight">
					Market Insights
				</h2>
				<p
					class="text-sm text-muted-foreground font-medium uppercase tracking-widest"
				>
					Current Prices
				</p>
			</div>

			<div class="grid gap-4 sm:grid-cols-2 lg:grid-cols-1">
				{#if prices && prices.length > 0}
					{#each prices as metal}
						<Card.Root
							class="group transition-all hover:shadow-lg dark:hover:shadow-primary/5 p-0 border-l-4"
							style="border-left-color: currentColor;"
						>
							<Card.Header
								class="flex flex-row items-center justify-between py-4"
							>
								<div class="flex flex-col gap-0.5">
									<Card.Title class="text-lg font-bold"
										>{metal.name}</Card.Title
									>
									<Card.Description
										class="font-mono text-[10px] uppercase tracking-widest"
										>{metal.code}</Card.Description
									>
								</div>
								<div class="flex flex-col items-end gap-1">
									<p class="text-xl font-bold tracking-tight">
										${metal.price_kg.toLocaleString(
											undefined,
											{
												minimumFractionDigits: 0,
												maximumFractionDigits: 0,
											},
										)}
									</p>
									<div class="flex items-center gap-1.5">
										<div
											class={cn(
												"size-2 animate-pulse rounded-full bg-current",
												getPriceColor(metal.code),
											)}
										></div>
										<span
											class="text-[10px] font-bold text-muted-foreground uppercase"
											>{new Date(
												metal.updated_at,
											).toLocaleTimeString([], {
												hour: "2-digit",
												minute: "2-digit",
											})}</span
										>
									</div>
								</div>
							</Card.Header>
						</Card.Root>
					{/each}
				{:else}
					<div
						class="col-span-full rounded-xl border-2 border-dashed border-muted-foreground/20 py-8 text-center"
					>
						<p class="font-medium text-muted-foreground">
							Market data currently unavailable.
						</p>
					</div>
				{/if}
			</div>
		</div>
	</section>
</div>
