import type PositionSightingMetadata from "./positionSightingMetadata";

export default interface VideoPositions {
	videoId: string;
	videoTitle: string;
	videoLength: number;
	thumbnailUrl: string;
	channelName: string;
	channelUrl: string;
  positionSightings: [PositionSightingMetadata];
}
