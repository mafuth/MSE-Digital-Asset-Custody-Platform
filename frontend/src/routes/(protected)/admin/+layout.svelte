<script lang="ts">
    import { auth } from "$lib/auth.svelte";
    import { goto } from "$app/navigation";
    import { onMount } from "svelte";

    let { children } = $props();

    // Immediate redirect if we're certain they shouldn't be here
    $effect(() => {
        if (auth.initialized && auth.user) {
            if (auth.user.type !== "admin") {
                goto("/");
            }
        } else if (auth.initialized && !auth.user) {
            goto("/login");
        }
    });
</script>

{#if auth.initialized && auth.user?.type === "admin"}
    {@render children()}
{:else}
    <div class="flex min-h-screen items-center justify-center bg-slate-50/50">
        <div class="flex flex-col items-center gap-4">
            <div
                class="size-10 rounded-full border-4 border-primary/20 border-t-primary animate-spin"
            ></div>
            <p
                class="text-[10px] font-black uppercase tracking-widest text-slate-400"
            >
                Verifying Access
            </p>
        </div>
    </div>
{/if}
