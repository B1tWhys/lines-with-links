<script lang="ts">
	import type VideoPositions from '$lib/types/videoPositions';
	import VideoListItem from './videoListItem.svelte';

	export let videos: [VideoPositions];
</script>

<ul class="overflow-y-scroll overflow-x-hidden px-3">
	{#each videos as positions (positions.videoId)}
		<VideoListItem videoPositions={positions} />
	{/each}
</ul>
