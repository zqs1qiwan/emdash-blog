/**
 * UI strings + date formatting for the public site.
 * The site is zh-only (single-language). Former per-locale string
 * table replaced with fixed Chinese copy.
 */

export const ui = {
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
	author: "作者",
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
	searching: "搜索中...",
	searchNoResults: "没有找到相关内容",
	navigate: "导航",
	home: "首页",
	connect: "链接",
} as const;

/** zh-CN short date: 2026年9月2日 */
export function formatDate(date: Date | null | undefined): string | null {
	if (!date) return null;
	return date.toLocaleDateString("zh-CN", {
		year: "numeric",
		month: "short",
		day: "numeric",
	});
}
