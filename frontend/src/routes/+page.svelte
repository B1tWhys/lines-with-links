<script lang="ts">
	import { goto } from '$app/navigation';
	import Chessboard from '$lib/ui/chessboard.svelte';
	import VideoListItem from '$lib/ui/videoListItem.svelte';
	import type { PageData } from './$types';
	import { page } from '$app/stores';

	export let data: PageData;

	let startingPosition =
		$page.url.searchParams.get('fen') || 'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1';

	async function onNewFen(fen: string) {
		console.log(`loading new fen: ${fen}`);
		const url = $page.url;
		url.searchParams.set('fen', fen);
		goto(url, { invalidateAll: true });
	}
</script>

<div class="h-screen w-full bg-slate-800 flex px-3">
	<ul class="max-w-md overflow-scroll pr-4 pt-1">
		{#each data.sightings as videoPositions (videoPositions.videoId)}
			<VideoListItem {videoPositions} />
		{/each}
	</ul>

	<div class="flex w-full justify-center">
		<Chessboard onPositionChange={onNewFen} {startingPosition}/>
	</div>
</div>
