import { QuartzTransformerPlugin } from "../types"

/**
 * Converts Obsidian-style sized markdown images (before remark-parse):
 *
 *   ![](path/to/file.jpg =200x)      → width 200, height automatic
 *   ![](path/to/file.jpg =200x100)   → width and height
 *
 * Standard CommonMark does not allow spaces in `(...)` link destinations, so
 * this runs as a text transform and emits inline HTML. CrawlLinks still
 * rewrites relative `src` on the resulting `<img>` like normal images.
 */
const sizedImageRegex = /!\[([^\]]*)\]\(([^)\s]+)\s*=\s*(\d+)x(\d*)\)/g

function escapeHtmlAttr(s: string): string {
  return s
    .replace(/&/g, "&amp;")
    .replace(/"/g, "&quot;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
}

export const MarkdownSizedImages: QuartzTransformerPlugin = () => ({
  name: "MarkdownSizedImages",
  textTransform(_ctx, src) {
    return src.replace(sizedImageRegex, (_full, alt: string, url: string, w: string, h: string) => {
      const heightPart = h ? ` height="${escapeHtmlAttr(h)}"` : ""
      return `<img src="${escapeHtmlAttr(url)}" alt="${escapeHtmlAttr(alt ?? "")}" width="${escapeHtmlAttr(w)}"${heightPart} />`
    })
  },
})
