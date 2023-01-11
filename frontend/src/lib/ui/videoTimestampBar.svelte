<script lang="ts">
	import type PositionSightingMetadata from '$lib/types/positionSightingMetadata';

	export let positionSightings: [PositionSightingMetadata];
	export let videoLengthSec: number;
	export let videoBaseUrl: URL;

	let barWidth: number;

	let urls = positionSightings.map((ps) => {
		let url = new URL(videoBaseUrl);
		url.searchParams.append('t', Math.round(ps.secIntoVideo).toString());
		return url.toString();
	});

  // FIXME when i've added the video length to the DB
	let pctsIntoVideo = positionSightings.map((ps) => {
		return Math.random();
	});
  pctsIntoVideo[0] = 0;
  pctsIntoVideo[pctsIntoVideo.length - 1] = 1;

	$: pxOffsets = pctsIntoVideo.map((pct) => (barWidth - 10) * pct);
</script>

<div class="w-full py-3">
	<div class="h-1 bg-blue-300 rounded-full pr-3" bind:clientWidth={barWidth}>
    <div>
		{#each urls as url, i}
      {@const pxOffset = pxOffsets[i]}
			<div
				class="h-3 w-3 bg-slate-100 text-blue-500 rounded-full inline absolute -bottom-full"
				style="left: {pxOffset}px"
			/>
		{/each}
    </div>
	</div>
</div>
