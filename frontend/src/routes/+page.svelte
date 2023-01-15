<script lang="ts">
	import Chessboard from '$lib/ui/chessboard.svelte';
	import VideoListItem from '$lib/ui/videoListItem.svelte';
	import { page } from '$app/stores';
	import { fen } from '$lib/stores';
	import { onMount } from 'svelte';
	import type VideoPositions from '$lib/types/videoPositions';

	async function updatePositions(): Promise<[VideoPositions]> {
		let url = new URL($page.url);
		url.pathname = 'vids';
		url.searchParams.set('fen', $fen);
		const resp = await fetch(url);
		return await resp.json();
	}

	let videosPromise = updatePositions();

	onMount(() => {
		videosPromise = updatePositions();
		fen.subscribe(() => (videosPromise = updatePositions()));
	});
</script>

<div class="bg-slate-800 h-screen flex flex-col">
	<div class="flex-shrink-0">
		<Chessboard />
	</div>
	{#await videosPromise}
		<div class="text-slate-100 text-lg w-full h-full flex justify-center items-center">
			loading...
		</div>
	{:then videos}
		<ul class="overflow-y-scroll overflow-x-hidden p-3">
			{#each videos as positions (positions.videoId)}
				<VideoListItem videoPositions={positions} />
			{/each}
		</ul>
	{/await}
</div>
