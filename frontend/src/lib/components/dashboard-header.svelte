<script lang="ts">
	import { auth } from "$lib/auth.svelte";
	import * as Sidebar from "$lib/components/ui/sidebar/index.js";
	import { Separator } from "$lib/components/ui/separator/index.js";
	import NavUser from "$lib/components/nav-user.svelte";

	const userData = $derived({
		name: auth.user?.name || "User",
		email: auth.user?.email || "",
		avatar: "/avatars/user.jpg",
	});
</script>

<header
	class="sticky top-0 z-30 flex h-16 shrink-0 items-center justify-between border-b bg-background/80 px-4 backdrop-blur-md rounded-t-xl"
>
	<div class="flex items-center gap-2">
		<Sidebar.Trigger class="-ms-1" />
		<Separator
			orientation="vertical"
			class="me-2 data-[orientation=vertical]:h-4"
		/>
	</div>

	<div class="flex items-center gap-4">
		<NavUser user={userData} />
	</div>
</header>
