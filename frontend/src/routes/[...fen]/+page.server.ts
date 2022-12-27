import type { PageServerLoad } from './$types';
import { getSightingsOfPosition } from '$lib/server/database';

export const load: PageServerLoad = async ({ route }) => {
	const fen = route.id;
	return { sightings: await getSightingsOfPosition(fen) };
};
