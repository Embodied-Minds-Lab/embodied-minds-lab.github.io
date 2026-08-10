import type { APIRoute } from "astro";

// Allow every crawler. The previous version allowed only four named bots and
// served `User-agent: * / Disallow: /` to everyone else, which kept the site out
// of most search indexes and all AI retrieval.
export const GET: APIRoute = ({ site }) => {
	const text = `User-agent: *
Allow: /

Sitemap: ${new URL("sitemap-index.xml", site)}
`;

	return new Response(text, { headers: { "Content-Type": "text/plain; charset=utf-8" } });
};
