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
	const result = await db
		.select(
			'v.id as videoId',
			'v.title as videoTitle',
			'v.thumbnail_url as thumbnailUrl',
			'c.channel_name as channelName',
			'c.channel_url as channelUrl',
			'ps.sec_into_video as secIntoVideo'
		)
		.from('position_sightings as ps')
		.leftJoin('positions as p', 'ps.position_id', 'p.id')
		.leftJoin('videos as v', 'ps.video_id', 'v.id')
		.leftJoin('channels as c', 'v.channel_id', 'c.id')
		.where('p.fen', '=', fen);
	console.info(`Fetched ${result.length} results from db for fen ${fen}`);
	return result;
}
