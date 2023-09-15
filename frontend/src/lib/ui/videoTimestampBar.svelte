<script lang="ts">
	import type PositionSightingMetadata from '$lib/types/positionSightingMetadata';
	import { toTimestampStr } from '$lib/utils';

	export let positionSightings: [PositionSightingMetadata];
	export let videoBaseUrl: URL;
	export let showHint: Boolean;

	$: hintBubbleIdx = showHint ? positionSightings.length / 2 : null;

	const barBubbleClasses = [
		'h-4',
		'w-4',
		'bg-rose-500',
		'text-blue-500',
		'rounded-full',
		'absolute',
		'-bottom-[10px]',
		'border-rose-800',
		'border-2'
	].join(' ');

	let barWidth: number;

	let urls = positionSightings.map((ps) => {
		let url = new URL(videoBaseUrl);
		url.searchParams.append('t', Math.round(ps.secIntoVideo).toString());
		return url.toString();
	});

	let pctsIntoVideo = positionSightings.map((ps) => ps.secIntoVideo / ps.videoLength);
	$: pxOffsets = pctsIntoVideo.map((pct) => (barWidth - 10) * pct);

	let timestamps = positionSightings.map((ps) => toTimestampStr(ps.secIntoVideo));
	let isHovered = positionSightings.map((_) => false);
</script>

<div class="w-full pb-4 pt-6">
	<div class="h-1 bg-blue-300 rounded-full" bind:clientWidth={barWidth}>
		{#each positionSightings as sighting, i (sighting.videoId + sighting.secIntoVideo)}
			{@const pxOffset = pxOffsets[i]}
			{@const showTimestamp = isHovered[i]}
			{@const dispHint = hintBubbleIdx == i}
			{@const url = urls[i]}
			<div class="absolute" style="left: {pxOffset}px; z-index: {Math.min(i, 49)}">
				{#if showTimestamp}
					<div class="absolute bottom-3 text-slate-100 text-center text-sm -translate-x-1/3">
						{timestamps[i]}
					</div>
				{:else if dispHint}
					<div
						class="absolute bottom-3 text-gray-800 text-center text-sm bg-white rounded-sm w-36 p-1 mb-2 -translate-x-1/2"
					>
						Hint: Try clicking on these red bubbles<br />&#128071;
					</div>
				{/if}
				<!-- svelte-ignore a11y-mouse-events-have-key-events -->
				<a
					class={barBubbleClasses}
					href={url}
					target="_blank"
					rel="noreferrer"
					on:mouseover={() => (isHovered[i] = true)}
					on:mouseout={() => (isHovered[i] = false)}
				/>
			</div>
		{/each}
	</div>
</div>
