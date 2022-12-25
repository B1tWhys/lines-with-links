<script lang="ts">
	import type VideoMetadata from './types/videoMetadata';

	export let videoMetadata: VideoMetadata;
	$: vidLink = new URL(videoMetadata.videoUrl);
	$: vidLink.searchParams.append('t', `${videoMetadata.startAt}s`);
</script>

<li>
	<a class="flex flex-row" href={vidLink.toString()} target="_blank" rel="noreferrer">
		<img
			class="mr-2 h-24 w-40"
			src={videoMetadata.thumbnailUrl}
			alt="{videoMetadata.title} - {videoMetadata.channelName}"
		/>
		<div>
			<div class="text-white font-bold mb-3">{videoMetadata.title}</div>
			<div class="text-slate-300 text-sm">
				<p>{videoMetadata.channelName}</p>
			</div>
		</div>
	</a>
</li>
