<script lang="ts">
	import type VideoPositions from '../types/videoPositions';
	import VideoTimestampBar from './videoTimestampBar.svelte';

	export let videoPositions: VideoPositions;

	let url = new URL('https://www.youtube.com/watch');
	url.searchParams.append('v', videoPositions.videoId);
</script>

<li class="my-2 border border-zinc-900 bg-gray-900 rounded-md px-3 pt-3">
	<div class="flex flex-row">
		<a href={url.toString()} class="pr-2 flex-shrink-0" target="_blank" rel="noreferrer">
			<img
				class="h-[94px] w-[168px] object-cover rounded-md"
				src={videoPositions.thumbnailUrl}
				alt="{videoPositions.videoTitle} - {videoPositions.channelName}"
			/>
		</a>
		<div class="flex-shrink">
			<a class="text-white font-bold mb-1" href={url.toString()} target="_blank" rel="noreferrer">
				{videoPositions.videoTitle}
			</a>
			<div class="text-slate-300 text-sm">
				<a href={videoPositions.channelUrl} target="_blank" rel="noreferrer">
					{videoPositions.channelName}
				</a>
			</div>
		</div>
	</div>
	<VideoTimestampBar positionSightings={videoPositions.positionSightings} videoBaseUrl={url} />
</li>
