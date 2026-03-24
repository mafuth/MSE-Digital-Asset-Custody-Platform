<script lang="ts">
	import { Dialog as DialogPrimitive } from "bits-ui";

	let {
		children,
		open = $bindable(false),
		...restProps
	}: DialogPrimitive.RootProps = $props();
</script>

<DialogPrimitive.Root bind:open {...restProps}>
	{@render children?.()}
</DialogPrimitive.Root>
