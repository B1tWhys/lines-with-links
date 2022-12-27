import type { PageLoad } from './$types';

export const load: PageLoad = async ({ fetch, url }) => {
	const fen = url.searchParams.get('fen');
	let path = 'vids?';
	if (fen) path += new URLSearchParams({ fen: fen });
	const resp = await fetch(path);
	return { sightings: resp.json() };
};
