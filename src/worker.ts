import handler, { createScheduledHandler, PluginBridge } from "@emdash-cms/cloudflare/worker";

export { PluginBridge };

// Cache-Control policy (honored by Workers Cache once `cache.enabled` is set
// in wrangler.jsonc; see https://developers.cloudflare.com/workers/cache/):
// - Static assets & media files (immutable storage keys / hashed names):
//   1 year, immutable.
// - Public HTML (home / posts / category / tag / pages): short browser TTL,
//   longer CDN TTL with stale-while-revalidate so new posts appear <= 5 min.
// - Feeds / sitemap / robots: 1 hour.
// - Admin, API (except public media files), search and any personalized
//   response (session cookie / Authorization present): no-store.
// Personalized pages are never cached: Base.astro renders an Admin link when
// Astro.locals.user is set, so a request carrying a non-CF cookie bypasses.
const STATIC_CACHE = "public, max-age=31536000, s-maxage=31536000, immutable";
const HTML_CACHE = "public, max-age=60, s-maxage=300, stale-while-revalidate=86400";
const FEED_CACHE = "public, max-age=3600, s-maxage=3600, stale-while-revalidate=86400";
const NO_STORE = "private, no-store";

function isPersonalized(request: Request): boolean {
	if (request.headers.has("Authorization")) return true;
	const cookie = request.headers.get("Cookie");
	if (!cookie) return false;
	// __cf_bm / cf_* are Cloudflare bot-management cookies, not identity.
	const names = cookie
		.split(";")
		.map((c) => c.trim().split("=")[0])
		.filter(Boolean);
	return names.some((n) => n !== "__cf_bm" && !n.startsWith("cf_"));
}

function cacheControlFor(url: URL, status: number): string | null {
	const path = url.pathname;
	if (path.startsWith("/_emdash/api/media/file/")) return STATIC_CACHE;
	if (path.startsWith("/_emdash/")) return NO_STORE;
	if (path.startsWith("/_astro/")) return STATIC_CACHE;
	if (
		path === "/rss.xml" ||
		path === "/sitemap.xml" ||
		path === "/sitemap-posts.xml" ||
		path === "/robots.txt" ||
		path === "/llms.txt"
	) {
		return FEED_CACHE;
	}
	if (path === "/search") return NO_STORE;
	const ext = path.split(".").pop()?.toLowerCase();
	if (
		["css", "js", "jpg", "jpeg", "png", "gif", "webp", "svg", "ico", "woff", "woff2", "avif"].includes(ext ?? "")
	) {
		return STATIC_CACHE;
	}
	if (
		path === "/" ||
		path.startsWith("/posts") ||
		path.startsWith("/category/") ||
		path.startsWith("/tag/") ||
		path.startsWith("/pages/")
	) {
		return HTML_CACHE;
	}
	if (status === 404) return "public, max-age=60, s-maxage=300, stale-while-revalidate=60";
	return null;
}

async function fetchWithCacheHeaders(
	request: Request,
	env: Env,
	ctx: ExecutionContext,
): Promise<Response> {
	const response = await handler.fetch(request, env, ctx);
	const method = request.method;
	if (method !== "GET" && method !== "HEAD") return response;
	if (response.status !== 200 && response.status !== 404) return response;
	if (response.headers.has("Set-Cookie")) return response;

	if (isPersonalized(request)) {
		const headers = new Headers(response.headers);
		headers.set("Cache-Control", NO_STORE);
		return new Response(response.body, { status: response.status, headers });
	}

	const url = new URL(request.url);
	const value = cacheControlFor(url, response.status);
	if (!value) return response;
	// Respect an explicit no-store/private already set downstream, except for
	// media files whose storage keys are immutable (upstream sends max-age=0).
	const existing = response.headers.get("Cache-Control") ?? "";
	const isMedia = url.pathname.startsWith("/_emdash/api/media/file/");
	if (!isMedia && /(^|,)\s*(no-store|private)/.test(existing)) return response;
	const headers = new Headers(response.headers);
	headers.set("Cache-Control", value);
	return new Response(response.body, { status: response.status, headers });
}

export default {
	...handler,
	fetch: fetchWithCacheHeaders,
	scheduled: createScheduledHandler(),
} satisfies ExportedHandler;
