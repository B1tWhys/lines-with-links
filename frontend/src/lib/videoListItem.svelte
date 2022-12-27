<script lang="ts">
	import type PositionSightingMetadata from './types/positionSightingMetadata';

	export let positionSighting: PositionSightingMetadata;
	let url = new URL('https://www.youtube.com/watch');
	url.searchParams.append('v', positionSighting.videoId);
	url.searchParams.append('t', `${positionSighting.secIntoVideo}s`);
</script>

<li class="my-2">
	<a class="flex flex-row" href={url.toString()} target="_blank" rel="noreferrer">
		<img
			class="mr-2 h-24 w-40"
			src={positionSighting.thumbnailUrl}
			alt="{positionSighting.videoTitle} - {positionSighting.channelName}"
		/>
		<div>
			<div class="text-white font-bold mb-3">{positionSighting.videoTitle}</div>
			<div class="text-slate-300 text-sm">
				<a href={positionSighting.channelUrl} target="_blank" rel="noreferrer">{positionSighting.channelName}</a>
			</div>
		</div>
	</a>
</li>
