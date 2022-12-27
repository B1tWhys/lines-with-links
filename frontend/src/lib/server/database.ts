import { env } from '$env/dynamic/private';
import type PositionSightingMetadata from '$lib/types/positionSightingMetadata';
import knex from 'knex';

const db = knex({
	client: 'pg',
	connection: env.DATABASE_URL,
	searchPath: ['public']
});

export async function getSightingsOfPosition(
	fen: string
): Promise<Array<PositionSightingMetadata>> {
	await new Promise((resolve) => setTimeout(resolve, 2000));
	return [
		{
			videoTitle:
				"Miniature Game | Scholar's Mate Vs Sicilian Defense | GM Naroditsky’s Top Theory Speedrun",
			videoId: 'GqdveDSL2SA',
			thumbnailUrl: 'https://i.ytimg.com/vi/GqdveDSL2SA/sddefault.jpg',
			secIntoVideo: 0,
			channelName: 'Daniel Naroditsky',
			channelUrl: 'https://www.youtube.com/@DanielNaroditskyGM'
		},
		{
			videoTitle:
				"Miniature Game | Scholar's Mate Vs Sicilian Defense | GM Naroditsky’s Top Theory Speedrun",
			videoId: 'GqdveDSL2SA',
			thumbnailUrl: 'https://i.ytimg.com/vi/GqdveDSL2SA/sddefault.jpg',
			secIntoVideo: 27.9,
			channelName: 'Daniel Naroditsky',
			channelUrl: 'https://www.youtube.com/@DanielNaroditskyGM'
		}
	];
}
