<script lang="ts">
	import Chessboard from '$lib/chessboard.svelte';
	import type VideoMetadata from '$lib/types/videoMetadata';
	import VideoListItem from '$lib/videoListItem.svelte';

	const videoMetadata: VideoMetadata = {
		title: '100% PERFECT Chess!',
		videoUrl: 'https://www.youtube.com/watch?v=vRAXtMOcnVI',
		thumbnailUrl: 'https://i.ytimg.com/vi/vRAXtMOcnVI/sddefault.jpg',
		channelName: 'GothamChess',
		channelUrl: 'https://www.youtube.com/channel/UCQHX6ViZmPsWiYSFAyS0a3Q',
		startAt: 30
	};
</script>

<div class="min-h-screen w-full bg-slate-800 flex">
	<nav class="mx-4 pt-2 h-full">
		<ul>
			{#each Array(20) as i}
				<VideoListItem {videoMetadata} />
			{/each}
		</ul>
	</nav>

	<div class="max-h-screen flex w-full justify-center">
		<Chessboard />
	</div>
</div>
