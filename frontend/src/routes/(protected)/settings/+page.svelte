<script lang="ts">
	import { auth } from "$lib/auth.svelte";
	import * as Card from "$lib/components/ui/card/index.js";
	import { Input } from "$lib/components/ui/input/index.js";
	import { Label } from "$lib/components/ui/label/index.js";
	import { Button } from "$lib/components/ui/button/index.js";
	import { Separator } from "$lib/components/ui/separator/index.js";
	import { updateMe, changePassword } from "$lib/api";
	import UserIcon from "@lucide/svelte/icons/user";
	import LockIcon from "@lucide/svelte/icons/lock";
	import SaveIcon from "@lucide/svelte/icons/save";
	import ShieldHandIcon from "@lucide/svelte/icons/shield-half";

	let name = $state(auth.user?.name || "");
	let email = $state(auth.user?.email || "");
	
	let currentPassword = $state("");
	let newPassword = $state("");
	let confirmPassword = $state("");

	let loadingProfile = $state(false);
	let loadingPassword = $state(false);

	async function handleUpdateProfile() {
		if (!auth.token) return;
		loadingProfile = true;
		try {
			const updatedUser = await updateMe(auth.token, { name, email });
			auth.setUser(updatedUser);
			alert("Profile updated successfully!");
		} catch (e: any) {
			alert(e.message || "Failed to update profile");
		} finally {
			loadingProfile = false;
		}
	}

	async function handleChangePassword() {
		if (!auth.token) return;
		if (newPassword !== confirmPassword) {
			alert("New passwords do not match");
			return;
		}
		loadingPassword = true;
		try {
			await changePassword(auth.token, {
				current_password: currentPassword,
				new_password: newPassword
			});
			currentPassword = "";
			newPassword = "";
			confirmPassword = "";
			alert("Password updated successfully!");
		} catch (e: any) {
			alert(e.message || "Failed to change password");
		} finally {
			loadingPassword = false;
		}
	}
</script>

<div class="flex-1 space-y-8 p-8 pt-6">
	<div class="flex items-center justify-between space-y-2">
		<h2 class="text-3xl font-bold tracking-tight">Account Settings</h2>
	</div>

	<div class="grid gap-8 md:grid-cols-2 lg:grid-cols-2">
		<Card.Root class="border-none shadow-md bg-card/50 backdrop-blur-sm">
			<Card.Header>
				<div class="flex items-center gap-2">
					<UserIcon class="size-5 text-primary" />
					<Card.Title>Profile Information</Card.Title>
				</div>
				<Card.Description>
					Update your account's profile information and email address.
				</Card.Description>
			</Card.Header>
			<Card.Content class="space-y-4">
				<div class="space-y-2">
					<Label for="name">Full Name</Label>
					<Input id="name" bind:value={name} placeholder="Your Name" class="bg-background/50" />
				</div>
				<div class="space-y-2">
					<Label for="email">Email Address</Label>
					<Input id="email" type="email" bind:value={email} placeholder="your@email.com" class="bg-background/50" />
				</div>
			</Card.Content>
			<Card.Footer>
				<Button onclick={handleUpdateProfile} disabled={loadingProfile} class="w-full">
					{#if loadingProfile}
						Saving...
					{:else}
						<SaveIcon class="mr-2 size-4" /> Save Changes
					{/if}
				</Button>
			</Card.Footer>
		</Card.Root>

		<Card.Root class="border-none shadow-md bg-card/50 backdrop-blur-sm">
			<Card.Header>
				<div class="flex items-center gap-2">
					<LockIcon class="size-5 text-primary" />
					<Card.Title>Change Password</Card.Title>
				</div>
				<Card.Description>
					Ensure your account is using a long, random password to stay secure.
				</Card.Description>
			</Card.Header>
			<Card.Content class="space-y-4">
				<div class="space-y-2">
					<Label for="current-password">Current Password</Label>
					<Input id="current-password" type="password" bind:value={currentPassword} class="bg-background/50" />
				</div>
				<Separator class="my-4" />
				<div class="space-y-2">
					<Label for="new-password">New Password</Label>
					<Input id="new-password" type="password" bind:value={newPassword} class="bg-background/50" />
				</div>
				<div class="space-y-2">
					<Label for="confirm-password">Confirm New Password</Label>
					<Input id="confirm-password" type="password" bind:value={confirmPassword} class="bg-background/50" />
				</div>
			</Card.Content>
			<Card.Footer>
				<Button onclick={handleChangePassword} disabled={loadingPassword} class="w-full" variant="secondary">
					{#if loadingPassword}
						Updating...
					{:else}
						<ShieldHandIcon class="mr-2 size-4" /> Update Password
					{/if}
				</Button>
			</Card.Footer>
		</Card.Root>
	</div>
</div>
