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
	import { register } from "$lib/api";
	import { auth } from "$lib/auth.svelte";
	import { goto } from "$app/navigation";
	import type { HTMLAttributes } from "svelte/elements";

	let { class: className, ...restProps }: HTMLAttributes<HTMLDivElement> =
		$props();

	const id = $props.id();

	let name = $state("");
	let email = $state("");
	let password = $state("");
	let confirmPassword = $state("");
	let loading = $state(false);
	let error = $state<string | null>(null);

	async function handleSubmit(e: SubmitEvent) {
		e.preventDefault();
		if (password !== confirmPassword) {
			error = "Passwords do not match";
			return;
		}
		loading = true;
		error = null;
		try {
			await register({ name, email, password });
			// Redirect to login after signup
			goto("/login");
		} catch (err: any) {
			error = err.message;
		} finally {
			loading = false;
		}
	}
</script>

<div class={cn("relative flex flex-col gap-6", className)} {...restProps}>
	<div class="absolute right-4 top-4 z-10">
		<Button size="icon" href="/login" class="size-8 rounded-full border">
			<ChevronLeft class="size-4" />
			<span class="sr-only">Back to Login</span>
		</Button>
	</div>
	<Card.Root class="overflow-hidden p-0">
		<Card.Content class="grid p-0 md:grid-cols-2">
			<form class="p-6 md:p-8" onsubmit={handleSubmit}>
				<FieldGroup>
					<div class="flex flex-col items-center gap-2 text-center">
						<h1 class="text-2xl font-bold">Create an account</h1>
						<p class="text-muted-foreground text-balance text-sm">
							Enter your details below to get started
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
						<FieldLabel for="name-{id}">Full Name</FieldLabel>
						<Input
							id="name-{id}"
							placeholder="John Doe"
							bind:value={name}
							required
						/>
					</Field>
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
						<FieldLabel for="password-{id}">Password</FieldLabel>
						<Input
							id="password-{id}"
							type="password"
							bind:value={password}
							required
						/>
					</Field>
					<Field>
						<FieldLabel for="confirm-password-{id}"
							>Confirm Password</FieldLabel
						>
						<Input
							id="confirm-password-{id}"
							type="password"
							bind:value={confirmPassword}
							required
						/>
					</Field>
					<Field>
						<Button type="submit" disabled={loading}>
							{#if loading}
								<Loader2 class="mr-2 h-4 w-4 animate-spin" />
							{/if}
							Create Account
						</Button>
					</Field>
					<FieldDescription class="text-center">
						Already have an account? <a href="/login">Login</a>
					</FieldDescription>
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
