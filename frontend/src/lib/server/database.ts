import { env } from '$env/dynamic/private';
import type PositionSightingMetadata from '$lib/types/positionSightingMetadata';
import type VideoPositions from '$lib/types/videoPositions';
import knex from 'knex';
import VideoListItem from '$lib/ui/videoListItem.svelte';

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
			'v.length as videoLength',
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
		.where('p.fen', '=', fen)
		.orderBy('v.id', 'ps.sec_into_video')
		.limit(50);
	console.info(`Fetched ${result.length} results from db for fen ${fen}`);
	return result;
}

export async function getVideosMatching(fen: string): Promise<Array<VideoPositions>> {
	const allPositionSightings = await getSightingsOfPosition(fen);
	const videoPositions = new Map<string, VideoPositions>();

	for (const posSighting of allPositionSightings) {
		const vidId = posSighting.videoId;
		if (videoPositions.has(vidId)) {
			const vidPos = videoPositions.get(vidId) as VideoPositions;
			vidPos.positionSightings.push(posSighting);
		} else {
			const vidPositions: VideoPositions = {
				videoId: vidId,
				videoLength: posSighting.videoLength,
				videoTitle: posSighting.videoTitle,
				thumbnailUrl: posSighting.thumbnailUrl,
				channelName: posSighting.channelName,
				channelUrl: posSighting.channelUrl,
				positionSightings: [posSighting]
			};
			videoPositions.set(vidId, vidPositions);
		}
	}
	return Array.from(videoPositions.values());
}
