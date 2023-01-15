<script lang="ts">
	import { Chessground } from 'chessground/chessground';
	import type { Config } from 'chessground/config';
	import 'chessground/assets/chessground.base.css';
	import 'chessground/assets/chessground.brown.css';
	import 'chessground/assets/chessground.cburnett.css';
	import '$lib/ui/chessboard.css';
	import { onMount } from 'svelte';
	import type { Api } from 'chessground/api';
	import { Chess, type Move, type Square } from 'chess.js';
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

	let redoStack = new Array<Move>();

	onMount(() => {
		cg = Chessground(board, config);
	});

	function afterMove(from: Key, to: Key) {
		chess.move({ from: from as Square, to: to as Square });
		redoStack = [];
		syncWithChessGameState();
	}

	function syncWithChessGameState() {
		const newFen = chess.fen();
		cg.set({
			turnColor: toColor(chess),
			fen: newFen,
			movable: {
				color: toColor(chess),
				dests: toDests(chess)
			}
		});
		fen.set(newFen);
	}

	function undoMove() {
		console.debug('Undoing move');
		const move = chess.undo();
		if (move) {
			redoStack.push(move);
			syncWithChessGameState();
		}
	}

	function redoMove() {
		console.debug('Redoing move');
		if (redoStack.length > 0) {
			console.info('Redoing move');
			const move = redoStack.pop()!;
			chess.move(move);
			syncWithChessGameState();
		}
	}

	function handleKeydown(event: KeyboardEvent) {
		const code = event.code;
		if (code === 'ArrowLeft') {
			event.preventDefault();
			undoMove();
		} else if (code === 'ArrowRight') {
			event.preventDefault();
			redoMove();
		}
	}
</script>

<svelte:window on:keydown={handleKeydown} />

<div bind:this={board} class="h-full aspect-square relative" />
