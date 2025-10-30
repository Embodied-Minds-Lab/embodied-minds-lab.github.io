import type { APIRoute } from "astro";
import { i18n } from "astro:config/client";
import { getCollection } from "astro:content";
import { getRelativeLocaleUrl } from "astro:i18n";
import { Feed } from "feed";
import config from "$config";
import i18nit from "$i18n";

export async function getStaticPaths() {
	return i18n!.locales.map(locale => ({ params: { locale: locale == i18n?.defaultLocale ? undefined : (locale as string) } }));
}

/**
 * GET endpoint for generating feeds
 * Supports filtering by language, series, and tags
 */
export const GET: APIRoute = async ({ site, params }) => {
	const { locale: language = i18n?.defaultLocale! } = params;
	const t = i18nit(language);

	// Initialize feed with site metadata and configuration
	const feed = new Feed({
		title: config.title,
		description: config.description,
		author: config.author,
		// Handle copyright based on license type - CC0 has special formatting
		copyright: config.copyright.type == "CC0 1.0"
			? "CC0 1.0 – No Rights Reserved"
			: `${config.copyright.type} © ${config.copyright.year} ${typeof config.author == "string" ? config.author : config.author.name}`,
		image: new URL("favicon-96x96.png", site).toString(),		// Feed image/logo
		favicon: new URL("favicon.ico", site).toString(),			// Feed favicon
		id: site!.toString(),										// Unique feed identifier
		link: site!.toString(),										// Feed's associated website
	});

	// Aggregate items from publications
	let items = [];

	if (config.feed?.section?.includes("publications") || config.feed?.section === "*" || config.feed?.section === undefined) {
		let publications = (await getCollection("publications", publication => {
			// Extract language from the file path structure
			const [locale, ...id] = publication.id.split("/");

			// Attach locale and link
			(<any>publication).link = new URL(getRelativeLocaleUrl(locale, `/publications/${id.join("/")}`), site).toString();
			
			// Create a timestamp from year for sorting (set to January 1st of that year)
			(<any>publication).data.timestamp = new Date(publication.data.year, 0, 1);

			// Apply filtering criteria
			let published = !publication.data.draft;		// Exclude draft posts
			let localed = language == locale;		// Language filter

			// Include publication only if it passes all filters
			return published && localed;
		}));

		items.push(...publications);
	}

	// Sort all items by timestamp and limit to configured number
	items = items
		.sort((a, b) => {
			const timeA = (<any>a.data).timestamp?.getTime ? (<any>a.data).timestamp.getTime() : 0;
			const timeB = (<any>b.data).timestamp?.getTime ? (<any>b.data).timestamp.getTime() : 0;
			return timeB - timeA;
		})
		.slice(0, config.feed?.limit || items.length);									// Limit to number of items

	// Add each filtered item as a feed item
	items.forEach((item) => {
		const itemData: any = item.data;
		const feedItem: any = {
			id: item.id,
			title: item.data.title,
			link: (<any>item).link,
			date: itemData.timestamp || new Date(),
		};
		
		// Add authors for publications
		if ('authors' in item.data && item.data.authors) {
			feedItem.author = item.data.authors.map((author: string) => ({ name: author }));
		}
		
		// Add venue info as description for publications
		if ('venue' in item.data && 'year' in item.data) {
			feedItem.description = `${item.data.venue} (${item.data.year})`;
		}
		
		// Add content if available
		if (item.rendered?.html) {
			feedItem.content = item.rendered.html;
		}
		
		// Add tags as categories
		if (item.data.tags && item.data.tags.length > 0) {
			feedItem.category = item.data.tags.map((tag: string) => ({ term: tag }));
		}
		
		feed.addItem(feedItem);
	});

	// Append stylesheet declaration to the feed
	const XML = feed.atom1().replace(
		/(<\?xml version="1\.0" encoding="utf-8".*\?>)/,
		'$1\n<?xml-stylesheet type="text/xsl" href="feed.xsl"?>'
	);

	return new Response(XML, { headers: { "Content-Type": "application/xml" } });
}
