<script lang="ts">
	import EuroOutline from 'flowbite-svelte-icons/EuroOutline.svelte';
	import Card from 'flowbite-svelte/Card.svelte';
	export let amount: number;
	$: rounded = amount.toFixed(2);
</script>

<Card
	size="xs"
	class="bg-transparent dark:bg-transparent border-none shadow-none place-self-center"
>
	<div class="flex-row flex gap-x-0.5">
		<EuroOutline class="w-4 h-6" />
		{rounded} left to spend today.
	</div>
</Card>
