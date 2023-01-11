<script lang="ts">
	import type VideoPositions from '../types/videoPositions';
	import VideoTimestampBar from './videoTimestampBar.svelte';

	export let videoPositions: VideoPositions;
	let expanded = true;

	let url = new URL('https://www.youtube.com/watch');
	url.searchParams.append('v', videoPositions.videoId);
	// FIXME: get the real value from the DB (once i put it there)
	let videoLength = Math.max(...videoPositions.positionSightings.map((ps) => ps.secIntoVideo));
</script>

<li class="my-2 border border-zinc-900 bg-gray-900 rounded-md px-3 pt-3">
	<!-- svelte-ignore a11y-click-events-have-key-events -->
	<div on:click={() => (expanded = true)}>
		<div class="flex flex-row">
			<img
				class="mr-2 h-24 object-scale-down rounded-md"
				src={videoPositions.thumbnailUrl}
				alt="{videoPositions.videoTitle} - {videoPositions.channelName}"
			/>
			<div>
				<div class="text-white font-bold mb-1">{videoPositions.videoTitle}</div>
				<div class="text-slate-300 text-sm">
					<a href={videoPositions.channelUrl} target="_blank" rel="noreferrer">
						{videoPositions.channelName}
					</a>
				</div>
			</div>
		</div>
		{#if expanded}
			<VideoTimestampBar
				positionSightings={videoPositions.positionSightings}
				videoLengthSec={videoLength}
				videoBaseUrl={url}
			/>
		{/if}
	</div>
</li>
