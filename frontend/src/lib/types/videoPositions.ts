import type PositionSightingMetadata from "./positionSightingMetadata";

export default interface VideoPositions {
	videoId: string;
	videoTitle: string;
	thumbnailUrl: string;
	channelName: string;
	channelUrl: string;
  positionSightings: [PositionSightingMetadata];
}
