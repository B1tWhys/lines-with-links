<script lang="ts">
	import type PositionSightingMetadata from '$lib/types/positionSightingMetadata';
	import { toTimestampStr } from '$lib/utils';

	export let positionSightings: [PositionSightingMetadata];
	export let videoBaseUrl: URL;

	const barBubbleClasses = [
		'h-4',
		'w-4',
		'bg-rose-500',
		'text-blue-500',
		'rounded-full',
		'absolute',
		'-bottom-[150%]',
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
			{@const url = urls[i]}
			<!-- svelte-ignore a11y-mouse-events-have-key-events -->
			<a
				class={barBubbleClasses}
				href={url}
				style="left: {pxOffset}px; z-index: {Math.min(i, 49)}"
				target="_blank"
				rel="noreferrer"
				on:mouseover={() => (isHovered[i] = true)}
				on:mouseout={() => (isHovered[i] = false)}
			>
				{#if showTimestamp}
					<div class="absolute bottom-3 text-slate-100 text-center text-sm -translate-x-1/3">
						{timestamps[i]}
					</div>
				{/if}
			</a>
		{/each}
	</div>
</div>
