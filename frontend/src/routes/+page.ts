import { getMarketPrices } from '$lib/api';
import type { PageLoad } from './$types';

export const load: PageLoad = async () => {
	const prices = await getMarketPrices();
	return { prices };
};
