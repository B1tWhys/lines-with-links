<script lang="ts">
	import Chessboard from '$lib/chessboard.svelte';
	import VideoListItem from '$lib/videoListItem.svelte';
	import type { PageData } from './$types';

	export let data: PageData;

</script>

<div class="min-h-screen w-full bg-slate-800 flex">
	<nav class="mx-4 pt-2 h-full">
	<ul>
		{#each data.sightings as positionSighting}
			<VideoListItem {positionSighting} />
		{/each}
	</ul>
	</nav>

	<div class="max-h-screen flex w-full justify-center">
		<Chessboard />
	</div>
</div>
