<script lang="ts">
	import Label from 'flowbite-svelte/Label.svelte';
	import Textarea from 'flowbite-svelte/Textarea.svelte';
	import PaperPlaneOutline from 'flowbite-svelte-icons/PaperPlaneOutline.svelte';
	import Button from 'flowbite-svelte/Button.svelte';

	export let input = '';
	export let action: () => Promise<void>;
	export let disabled = false;
	function handleInput(event: Event) {
		const textarea = event.target as HTMLTextAreaElement;
		if (textarea.scrollHeight > 280) {
			textarea.style.overflowY = '';
		} else {
			textarea.style.height = 'auto';
			textarea.style.overflowY = 'hidden';
		}
		textarea.style.height = textarea.scrollHeight + 'px';
		input = textarea.value;
	}

	const handleKeydown = async (event: KeyboardEvent): Promise<void> => {
		const { key, shiftKey } = event;

		if (key === 'Enter') {
			if (shiftKey) {
				input += '\n';
			} else {
				event.preventDefault();
				await action();
				input = '';
			}
		}
	};
</script>

<div class="sticky bottom-0 bg-white dark:bg-gray-800 pb-4 box-content">
	<div class="lg:mx-40 flex flex-row bg-primary-300 dark:bg-gray-700 place-items-center rounded-md">
		<Label for="textarea-id" class="sr-only ">Your message</Label>
		<Textarea
			class="bg-transparent border-none placeholder:pl-4 resize-none max-h-52 py-2 focus:border-none focus:ring-0 dark:focus:ring-0 dark:focus:border-none text-lg placeholder:text-primary-900 "
			id="textarea-id"
			placeholder="Ask me a question about my projects..."
			name="message"
			rows="1"
			tabindex="0"
			dir="auto"
			on:input={handleInput}
			bind:value={input}
			on:keydown={handleKeydown}
		/>
		<Button
			{disabled}
			class=" bg-primary-900 rounded-md mr-2 my-2 dark:bg-gray-950"
			on:click={action}
		>
			<PaperPlaneOutline class=" text-primary-100 " />
		</Button>
	</div>
</div>
