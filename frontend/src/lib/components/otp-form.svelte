<script lang="ts">
	import * as Card from "$lib/components/ui/card/index.js";
	import {
		FieldGroup,
		Field,
		FieldLabel,
		FieldDescription,
	} from "$lib/components/ui/field/index.js";
	import { Input } from "$lib/components/ui/input/index.js";
	import { Button } from "$lib/components/ui/button/index.js";
	import { cn } from "$lib/utils.js";
	import { ChevronLeft, Loader2 } from "@lucide/svelte";
	import { verifyOtp } from "$lib/api";
	import type { HTMLAttributes } from "svelte/elements";

	let { class: className, ...restProps }: HTMLAttributes<HTMLDivElement> =
		$props();

	const id = $props.id();

	let otp = $state("");
	let loading = $state(false);
	let error = $state<string | null>(null);
	let message = $state<string | null>(null);

	async function handleSubmit(e: SubmitEvent) {
		e.preventDefault();
		loading = true;
		error = null;
		message = null;
		try {
			const res = await verifyOtp(otp);
			message = res.message;
		} catch (err: any) {
			error = err.message;
		} finally {
			loading = false;
		}
	}
</script>

<div class={cn("relative flex flex-col gap-6", className)} {...restProps}>
	<div class="absolute right-4 top-4 z-10">
		<Button
			size="icon"
			href="/login"
			class="size-8 rounded-full border"
		>
			<ChevronLeft class="size-4" />
			<span class="sr-only">Back to Login</span>
		</Button>
	</div>
	<Card.Root class="overflow-hidden p-0">
		<Card.Content class="grid p-0 md:grid-cols-2">
			<form class="p-6 md:p-8" onsubmit={handleSubmit}>
				<FieldGroup>
					<div class="flex flex-col items-center gap-2 text-center">
						<h1 class="text-2xl font-bold">OTP Verification</h1>
						<p class="text-muted-foreground text-balance text-sm">
							Enter the 6-digit code sent to your email
						</p>
					</div>
					{#if error}
						<div
							class="bg-destructive/15 text-destructive rounded-lg p-3 text-sm font-medium"
						>
							{error}
						</div>
					{/if}
					{#if message}
						<div
							class="bg-primary/15 text-primary rounded-lg p-3 text-sm font-medium"
						>
							{message}
						</div>
					{/if}
					<Field>
						<FieldLabel for="otp-{id}">Verification Code</FieldLabel
						>
						<Input
							id="otp-{id}"
							type="text"
							maxlength={6}
							placeholder="123456"
							class="text-center font-mono text-2xl tracking-[1em]"
							bind:value={otp}
							required
						/>
					</Field>
					<Field>
						<Button type="submit" disabled={loading}>
							{#if loading}
								<Loader2 class="mr-2 h-4 w-4 animate-spin" />
							{/if}
							Verify Code
						</Button>
					</Field>
					<div class="flex flex-col gap-2">
						<FieldDescription class="text-center">
							Didn't receive a code? <a href="##">Resend</a>
						</FieldDescription>
					</div>
				</FieldGroup>
			</form>
			<div class="bg-muted relative hidden md:block">
				<img
					src="/login-side.gif"
					alt="placeholder"
					class="absolute inset-0 h-full w-full object-cover dark:brightness-[0.2] dark:grayscale"
				/>
			</div>
		</Card.Content>
	</Card.Root>
</div>
