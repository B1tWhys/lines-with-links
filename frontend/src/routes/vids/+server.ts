import type { RequestHandler } from './$types';
import { getSightingsOfPosition, getVideosMatching } from '$lib/server/database';
import { json } from '@sveltejs/kit';

export const GET: RequestHandler = async ({ url }) => {
	let fen: string =
		url.searchParams.get('fen') || 'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1';

	fen = fen.trim();
	const firstWhitespace = fen.indexOf(' ');
	if (firstWhitespace > 0) {
		fen = fen.substring(0, firstWhitespace);
	}
	const data = await getVideosMatching(fen);
	return json(data);
};
