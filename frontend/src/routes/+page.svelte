<script lang="ts">
	import Chessboard from '$lib/ui/chessboard.svelte';
	import VideoListItem from '$lib/ui/videoListItem.svelte';
	import { page } from '$app/stores';
	import { fen } from '$lib/stores';
	import { onMount } from 'svelte';
	import type VideoPositions from '$lib/types/videoPositions';
	import VideoList from '$lib/ui/videoList.svelte';
	import SearchButton from '$lib/ui/searchButton.svelte';

	let videosPromise = updatePositions();
	let fenInputValue = $fen;

	async function updatePositions(): Promise<[VideoPositions]> {
		fenInputValue = $fen;
		let url = new URL($page.url);
		url.pathname = 'vids';
		url.searchParams.set('fen', $fen);
		const resp = await fetch(url);
		return await resp.json();
	}

	onMount(() => {
		videosPromise = updatePositions();
		fen.subscribe(() => (videosPromise = updatePositions()));
	});

	function onFenFormSubmit() {
		fen.set(fenInputValue);
	}
</script>

<div class="bg-slate-800 h-screen flex flex-col items-center gap-2 xl:flex-row-reverse">
	<div
		class="aspect-square max-w-lg w-full rounded-none min-[512px]:rounded-md overflow-clip xl:max-w-full xl:max-h-screen xl:w-auto xl:h-screen"
	>
		<Chessboard />
	</div>
	<form on:submit|preventDefault={onFenFormSubmit}>
		<input class="rounded inline-block" type="text" bind:value={fenInputValue} />
		<SearchButton />
	</form>
	{#await videosPromise}
		<div class="text-slate-100 text-lg w-full h-full flex justify-center items-center">
			loading...
		</div>
	{:then videos}
		<ul class="overflow-y-scroll overflow-x-hidden px-3">
			{#each videos as positions (positions.videoId)}
				<VideoListItem videoPositions={positions} />
			{/each}
		</ul>
	{/await}
</div>
