<script lang="ts">
	import * as Card from "$lib/components/ui/card/index.js";
	import {
		FieldGroup,
		Field,
		FieldLabel,
		FieldDescription,
		FieldSeparator,
	} from "$lib/components/ui/field/index.js";
	import { Input } from "$lib/components/ui/input/index.js";
	import { Button } from "$lib/components/ui/button/index.js";
	import { cn } from "$lib/utils.js";
	import { ChevronLeft, Loader2 } from "@lucide/svelte";
	import { login, getMarketPrices, type MetalPrice } from "$lib/api";
	import { auth } from "$lib/auth.svelte";
	import { goto } from "$app/navigation";
	import { Scale, Database } from "@lucide/svelte";
	import type { HTMLAttributes } from "svelte/elements";

	let { class: className, ...restProps }: HTMLAttributes<HTMLDivElement> =
		$props();

	const id = $props.id();

	let email = $state("");
	let password = $state("");
	let loading = $state(false);
	let error = $state<string | null>(null);
	let prices = $state<MetalPrice[]>([]);

	$effect(() => {
		getMarketPrices().then((res) => (prices = res));
	});

	async function handleSubmit(e: SubmitEvent) {
		e.preventDefault();
		loading = true;
		error = null;
		try {
			const res = await login({ email, password });
			auth.setToken(res.access_token);
			await auth.init();
			goto("/");
		} catch (err: any) {
			error = err.message;
		} finally {
			loading = false;
		}
	}
</script>

<div class={cn("relative flex flex-col gap-6", className)} {...restProps}>
	<Card.Root class="overflow-hidden p-0">
		<Card.Content class="grid p-0 md:grid-cols-2">
			<form class="p-6 md:p-8" onsubmit={handleSubmit}>
				<FieldGroup>
					<div class="flex flex-col items-center gap-2 text-center">
						<h1 class="text-2xl font-bold">Welcome back</h1>
						<p class="text-muted-foreground text-balance">
							Login to your account
						</p>
					</div>
					{#if error}
						<div
							class="bg-destructive/15 text-destructive rounded-lg p-3 text-sm font-medium"
						>
							{error}
						</div>
					{/if}
					<Field>
						<FieldLabel for="email-{id}">Email</FieldLabel>
						<Input
							id="email-{id}"
							type="email"
							placeholder="m@example.com"
							bind:value={email}
							required
						/>
					</Field>
					<Field>
						<div class="flex items-center">
							<FieldLabel for="password-{id}">Password</FieldLabel
							>
							<a
								href="/reset-password"
								class="ms-auto text-sm underline-offset-2 hover:underline"
							>
								Forgot your password?
							</a>
						</div>
						<Input
							id="password-{id}"
							type="password"
							bind:value={password}
							required
						/>
					</Field>
					<Field>
						<Button type="submit" disabled={loading}>
							{#if loading}
								<Loader2 class="mr-2 h-4 w-4 animate-spin" />
							{/if}
							Login
						</Button>
					</Field>
					<FieldDescription class="text-center">
						Don't have an account? <a href="/register">Sign up</a>
					</FieldDescription>
				</FieldGroup>
			</form>
			<div
				class="bg-slate-50 relative hidden md:flex flex-col items-center justify-center p-8 overflow-hidden border-l"
			>
				<div
					class="absolute inset-0 opacity-40 bg-[radial-gradient(circle_at_center,_var(--tw-gradient-stops))] from-primary/20 via-transparent to-transparent animate-pulse"
				></div>
				<div class="w-full space-y-4 max-w-[280px] z-10">
					{#if prices.length > 0}
						{#each prices as metal}
							<div
								class="flex items-center justify-between p-4 bg-white border border-slate-200 rounded-lg shadow-sm hover:border-primary/30 transition-all group"
							>
								<div class="flex items-center gap-3">
									<Scale
										class="size-4 text-primary transition-transform group-hover:scale-110"
									/>
									<div class="flex flex-col">
										<span
											class="text-[10px] font-black text-slate-900 uppercase"
											>{metal.name}</span
										>
									</div>
								</div>
								<div class="text-right">
									<p
										class="text-[10px] font-black text-slate-950 tracking-tighter"
									>
										${metal.price_kg.toLocaleString()}
									</p>
								</div>
							</div>
						{/each}
					{:else}
						<div
							class="py-12 flex flex-col items-center gap-2 opacity-20"
						>
							<Database class="size-6 text-slate-900" />
							<span
								class="text-[8px] font-black uppercase tracking-widest text-slate-900"
								>Loading Metals...</span
							>
						</div>
					{/if}
				</div>
			</div>
		</Card.Content>
	</Card.Root>
</div>
