/**
 * Locale-aware UI strings + date formatting for the public site.
 * The site is zh-first (default locale, no URL prefix) with optional
 * /en/ translations. Every user-visible string lives here so templates
 * stay free of hard-coded copy.
 */

export type UiLocale = "zh" | "en";

export function getUiLocale(locals: unknown): UiLocale {
	const locale = (locals as { locale?: string } | undefined)?.locale;
	return locale === "en" ? "en" : "zh";
}

const strings = {
	zh: {
		search: "搜索",
		searchPlaceholder: "搜索文章...",
		searchPosts: "搜索文章",
		searchHint: "输入关键词搜索文章。",
		noResults: (q: string) => `没有找到与「${q}」相关的内容`,
		resultsCount: (n: number, q: string) => `${n} 条与「${q}」相关的结果`,
		allPosts: "全部文章",
		latest: "最新",
		viewAll: "查看全部",
		articles: (n: number) => `${n} 篇文章`,
		minRead: (m: number) => `${m} 分钟阅读`,
		noPosts: "还没有文章。",
		noPostsYet: "还没有文章",
		createFirst: "去后台写第一篇",
		onThisPage: "本页目录",
		author: (n: number) => (n > 1 ? "作者" : "作者"),
		published: "发布于",
		readingTime: "阅读时间",
		tags: "标签",
		continueReading: "继续阅读",
		notFound: "页面不存在",
		notFoundDesc: "你访问的页面不存在或已被移动。",
		backHome: "返回首页",
		category: "分类",
		posts: (n: number) => `${n} 篇`,
		noPostsInCategory: "该分类下还没有文章。",
		untitled: "无标题",
		page: "页面",
	},
	en: {
		search: "Search",
		searchPlaceholder: "Search posts...",
		searchPosts: "Search posts",
		searchHint: "Enter a search term to find posts.",
		noResults: (q: string) => `No results for "${q}"`,
		resultsCount: (n: number, q: string) => `${n} result${n === 1 ? "" : "s"} for "${q}"`,
		allPosts: "All Posts",
		latest: "Latest",
		viewAll: "View all",
		articles: (n: number) => `${n} ${n === 1 ? "article" : "articles"}`,
		minRead: (m: number) => `${m} min read`,
		noPosts: "No posts yet.",
		noPostsYet: "No posts yet",
		createFirst: "Create a post",
		onThisPage: "On this page",
		author: (n: number) => (n > 1 ? "Authors" : "Author"),
		published: "Published",
		readingTime: "Reading time",
		tags: "Tags",
		continueReading: "Continue reading",
		notFound: "Page not found",
		notFoundDesc: "The page you're looking for doesn't exist.",
		backHome: "Go back home",
		category: "Category",
		posts: (n: number) => `${n} ${n === 1 ? "post" : "posts"}`,
		noPostsInCategory: "No posts in this category yet.",
		untitled: "Untitled",
		page: "Page",
	},
} as const;

export function t(locale: UiLocale) {
	return strings[locale];
}

const LOCALE_TAGS: Record<UiLocale, string> = { zh: "zh-CN", en: "en-US" };

/** Locale-aware date: 2026年9月2日 (zh) / Sep 2, 2026 (en) */
export function formatDate(date: Date | null | undefined, locale: UiLocale = "zh"): string | null {
	if (!date) return null;
	return date.toLocaleDateString(LOCALE_TAGS[locale], {
		year: "numeric",
		month: "short",
		day: "numeric",
	});
}
