import type { PageServerLoad } from './$types';
import { getSightingsOfPosition } from '$lib/server/database';

export const load: PageServerLoad = async ({ route }) => {
	// const fen = route.id;
	const fen = 'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR';
	return { sightings: await getSightingsOfPosition(fen) };
};
