<script lang="ts">
	import { Chessground } from 'chessground/chessground';
	import type { Config } from 'chessground/config';
	import 'chessground/assets/chessground.base.css';
	import 'chessground/assets/chessground.brown.css';
	import 'chessground/assets/chessground.cburnett.css';
	import '$lib/ui/chessboard.css';
	import { onMount } from 'svelte';
	import type { Api } from 'chessground/api';
	import { Chess, type Square } from 'chess.js';
	import { toColor, toDests } from '$lib/utils';
	import type { Key, SquareNode } from 'chessground/types';
	import { fen } from '$lib/stores';

	const chess = new Chess();
	let cg: Api;
	let board: HTMLElement;
	let config: Config = {
		fen: $fen,
		movable: {
			color: toColor(chess),
			free: false,
			dests: toDests(chess),
			events: {
				after: afterMove
			}
		},
		draggable: {
			showGhost: true
		}
	};

	onMount(() => {
		cg = Chessground(board, config);
	});

	function afterMove(from: Key, to: Key) {
		chess.move({ from: from as Square, to: to as Square });
		cg.set({
			turnColor: toColor(chess),
			movable: {
				color: toColor(chess),
				dests: toDests(chess)
			}
		});
		fen.set(chess.fen());
	}
</script>

<div bind:this={board} class="h-full aspect-square relative" />
