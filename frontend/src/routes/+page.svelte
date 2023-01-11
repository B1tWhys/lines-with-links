<script lang="ts">
	import { goto } from '$app/navigation';
	import Chessboard from '$lib/ui/chessboard.svelte';
	import VideoListItem from '$lib/ui/videoListItem.svelte';
	import type { PageData } from './$types';
	import { page } from '$app/stores';

	export let data: PageData;

	async function onNewFen(fen: string) {
		console.log(`loading new fen: ${fen}`);
		const url = $page.url;
		url.searchParams.set('fen', fen);
		goto(url, { invalidateAll: true });
	}
</script>

<div class="min-h-screen w-full bg-slate-800 flex overflow-hidden">
	<nav class="mx-4 pt-2 h-full">
		<ul class="max-h-screen max-w-lg overflow-scroll">
			{#each data.sightings as videoPositions}
				<VideoListItem {videoPositions} />
			{/each}
		</ul>
	</nav>

	<div class="max-h-screen flex w-full justify-center">
		<Chessboard onPositionChange={onNewFen} />
	</div>
</div>
