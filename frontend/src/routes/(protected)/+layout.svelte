<script lang="ts">
    import { auth } from "$lib/auth.svelte";
    import { goto } from "$app/navigation";
    import { onMount } from "svelte";
    import AppSidebar from "$lib/components/app-sidebar.svelte";
    import * as Sidebar from "$lib/components/ui/sidebar/index.js";
    import DashboardHeader from "$lib/components/dashboard-header.svelte";

    let { children } = $props();

    // In Svelte 5, we can use an effect to handle redirection
    $effect(() => {
        if (auth.initialized && !auth.user) {
            goto("/login");
        }
    });
</script>

{#if auth.user}
    <Sidebar.Provider>
        <AppSidebar />
        <Sidebar.Inset class="flex flex-col">
            <DashboardHeader />
            {@render children()}
        </Sidebar.Inset>
    </Sidebar.Provider>
{:else if !auth.initialized}
    <div class="flex min-h-screen items-center justify-center">
        <div class="text-muted-foreground animate-pulse text-sm">
            We are checking a few things before we can let you in
        </div>
    </div>
{/if}
