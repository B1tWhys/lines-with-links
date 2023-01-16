import type { Color, Key } from 'chessground/types';
import { type ChessInstance, SQUARES, type Chess } from 'chess.js';

export function toDests(chess: ChessInstance): Map<Key, Key[]> {
	const dests = new Map();
	SQUARES.forEach((s) => {
		const ms = chess.moves({ square: s, verbose: true });
		if (ms.length)
			dests.set(
				s,
				ms.map((m) => m.to)
			);
	});
	return dests;
}

export function toColor(chess: ChessInstance): Color {
	return chess.turn() === 'w' ? 'white' : 'black';
}

export function toTimestampStr(totalSec: number): string {
	const hrs = Math.floor(totalSec / 3600);
	const min = Math.floor((totalSec % 3600) / 60);
	const sec = Math.floor(totalSec % 60);
	
	const components = [
		String(min).padStart(2, '0'),
		String(sec).padStart(2, '0'),
	];
	if (hrs > 0) {
		components.unshift(String(hrs))
	}
	return components.join(':');
}