<script lang="ts">
	import type PositionSightingMetadata from '$lib/types/positionSightingMetadata';
	import { toTimestampStr } from '$lib/utils';

	export let positionSightings: [PositionSightingMetadata];
	export let videoLengthSec: number;
	export let videoBaseUrl: URL;

	const barBubbleClasses = [
		'h-4',
		'w-4',
		'bg-slate-100',
		'text-blue-500',
		'rounded-full',
		'absolute',
		'-bottom-[150%]',
		'border-slate-500',
		'border-2'
	].join(' ');

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

	let timestamps = positionSightings.map((ps) => toTimestampStr(ps.secIntoVideo));
	let isHovered = positionSightings.map((_) => false);
</script>

<div class="w-full pb-4 pt-6">
	<div class="h-1 bg-blue-300 rounded-full" bind:clientWidth={barWidth}>
		{#each urls as url, i}
			{@const pxOffset = pxOffsets[i]}
			{@const showTimestamp = isHovered[i]}
			<!-- svelte-ignore a11y-mouse-events-have-key-events -->
			<a
				class={barBubbleClasses}
				href={url}
				style="left: {pxOffset}px; z-index: {i}"
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
