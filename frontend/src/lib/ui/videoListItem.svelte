<script lang="ts">
	import type VideoPositions from '../types/videoPositions';
	import VideoTimestampBar from './videoTimestampBar.svelte';

	export let videoPositions: VideoPositions;

	let url = new URL('https://www.youtube.com/watch');
	url.searchParams.append('v', videoPositions.videoId);
	// FIXME: get the real value from the DB (once i put it there)
	let videoLength = Math.max(...videoPositions.positionSightings.map((ps) => ps.secIntoVideo));
</script>

<li class="my-2 border border-zinc-900 bg-gray-900 rounded-md px-3 pt-3">
		<div class="flex flex-row">
			<a href={url.toString()} class="mr-2 flex-shrink-0">
				<img class="h-[94px] w-[168px] object-cover rounded-md"
					src={videoPositions.thumbnailUrl}
					alt="{videoPositions.videoTitle} - {videoPositions.channelName}"
				/>
			</a>
			<div class="flex-shrink">
				<a class="text-white font-bold mb-1" href={url.toString()}>{videoPositions.videoTitle}</a>
				<div class="text-slate-300 text-sm">
					<a href={videoPositions.channelUrl} target="_blank" rel="noreferrer">
						{videoPositions.channelName}
					</a>
				</div>
			</div>
		</div>
		<VideoTimestampBar
			positionSightings={videoPositions.positionSightings}
			videoLengthSec={videoLength}
			videoBaseUrl={url}
		/>
</li>
