<script lang="ts">
	import { Chessground } from 'chessground/chessground';
	import type { Config } from 'chessground/config';
	import 'chessground/assets/chessground.base.css';
	import 'chessground/assets/chessground.brown.css';
	import 'chessground/assets/chessground.cburnett.css';
	import '$lib/chessboard.css';
	import { onMount } from 'svelte';
	import type { Api } from 'chessground/api';

	export let fen = '';
	let cg: Api;
	let board: HTMLElement;
	let config: Config = {
		viewOnly: true
	};

	onMount(() => {
		cg = Chessground(board, config);
	});
</script>

<div bind:this={board} class="h-full aspect-square relative" />

