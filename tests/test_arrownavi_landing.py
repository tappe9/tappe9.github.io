"""ArrowNavi の公開ランディングページ契約を検証する。"""

from __future__ import annotations

import re
import unittest
from html.parser import HTMLParser
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PUBLIC_ORIGIN = "https://tappe9.github.io"

LOCALES = {
    "ja": {
        "file": Path("ArrowNavi/index.html"),
        "url": f"{PUBLIC_ORIGIN}/ArrowNavi/",
        "store_url": "https://apps.apple.com/jp/app/arrownavi-compass/id6773170809",
        "image": "/ArrowNavi/assets/ja-direction.png",
        "scenes": (
            ("散歩", "街歩き"),
            ("旅行", "寄り道"),
            ("駅", "待ち合わせ"),
        ),
        "features": (
            ("矢印", "距離"),
            ("地図検索", "長押し", "現在地"),
            ("複数", "目的地", "切り替え"),
            ("apple watch", "同期"),
        ),
    },
    "en": {
        "file": Path("ArrowNavi/en/index.html"),
        "url": f"{PUBLIC_ORIGIN}/ArrowNavi/en/",
        "store_url": "https://apps.apple.com/us/app/arrownavi-compass/id6773170809",
        "image": "/ArrowNavi/assets/en-direction.png",
        "scenes": (
            ("walk",),
            ("travel", "detour"),
            ("station", "meeting"),
        ),
        "features": (
            ("arrow", "distance"),
            ("map search", "long press", "current location"),
            ("multiple", "destination", "switch"),
            ("apple watch", "sync"),
        ),
    },
    "ko": {
        "file": Path("ArrowNavi/ko/index.html"),
        "url": f"{PUBLIC_ORIGIN}/ArrowNavi/ko/",
        "store_url": "https://apps.apple.com/kr/app/arrownavi-compass/id6773170809",
        "image": "/ArrowNavi/assets/ko-direction.png",
        "scenes": (
            ("산책",),
            ("여행", "둘러"),
            ("역", "약속"),
        ),
        "features": (
            ("화살표", "거리"),
            ("지도 검색", "길게 누르기", "현재 위치"),
            ("여러", "목적지", "전환"),
            ("apple watch", "동기"),
        ),
    },
}


class Element:
    def __init__(self, tag: str, attrs: dict[str, str | None]):
        self.tag = tag
        self.attrs = attrs
        self.children: list[Element | str] = []

    def text(self) -> str:
        return " ".join(
            child.text() if isinstance(child, Element) else child
            for child in self.children
        )

    def descendants(self, tag: str | None = None):
        for child in self.children:
            if isinstance(child, Element):
                if tag is None or child.tag == tag:
                    yield child
                yield from child.descendants(tag)


class DocumentParser(HTMLParser):
    VOID_ELEMENTS = {
        "area", "base", "br", "col", "embed", "hr", "img", "input",
        "link", "meta", "param", "source", "track", "wbr",
    }

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.root = Element("document", {})
        self.stack = [self.root]

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]):
        element = Element(tag, dict(attrs))
        self.stack[-1].children.append(element)
        if tag not in self.VOID_ELEMENTS:
            self.stack.append(element)

    def handle_startendtag(self, tag: str, attrs: list[tuple[str, str | None]]):
        self.stack[-1].children.append(Element(tag, dict(attrs)))

    def handle_endtag(self, tag: str):
        for index in range(len(self.stack) - 1, 0, -1):
            if self.stack[index].tag == tag:
                del self.stack[index:]
                break

    def handle_data(self, data: str):
        self.stack[-1].children.append(data)


def parse_page(relative_path: Path) -> Element:
    path = ROOT / relative_path
    source = path.read_text(encoding="utf-8") if path.is_file() else ""
    parser = DocumentParser()
    parser.feed(source)
    parser.close()
    return parser.root


def all_elements(root: Element, tag: str | None = None) -> list[Element]:
    return list(root.descendants(tag))


def first_meta_content(root: Element, *, name: str | None = None, prop: str | None = None):
    for element in root.descendants("meta"):
        if name is not None and element.attrs.get("name") == name:
            return element.attrs.get("content")
        if prop is not None and element.attrs.get("property") == prop:
            return element.attrs.get("content")
    return None


def normalized_text(root: Element) -> str:
    return re.sub(r"\s+", " ", root.text()).strip().lower()


class ArrowNaviLandingTests(unittest.TestCase):
    def test_each_locale_has_the_expected_app_store_cta(self):
        for locale, contract in LOCALES.items():
            with self.subTest(locale=locale):
                root = parse_page(contract["file"])
                links = [
                    anchor for anchor in root.descendants("a")
                    if anchor.attrs.get("href") == contract["store_url"]
                ]
                self.assertTrue(links, f"{locale} page needs its regional App Store CTA")

    def test_each_locale_has_semantic_hero_heading_and_accessible_screenshot(self):
        for locale, contract in LOCALES.items():
            with self.subTest(locale=locale):
                root = parse_page(contract["file"])
                main_elements = all_elements(root, "main")
                self.assertTrue(main_elements, f"{locale} page needs a main landmark")
                if not main_elements:
                    continue
                main = main_elements[0]
                self.assertTrue(all_elements(main, "h1"), f"{locale} hero needs a heading")

                images = all_elements(main, "img")
                self.assertEqual(1, len(images), f"{locale} landing uses one hero screenshot")
                if len(images) != 1:
                    continue
                image = images[0]
                self.assertEqual(contract["image"], image.attrs.get("src"))
                self.assertTrue((image.attrs.get("alt") or "").strip(), "hero image needs useful alt text")
                self.assertEqual("1284", image.attrs.get("width"))
                self.assertEqual("2778", image.attrs.get("height"))
                self.assertNotEqual("lazy", image.attrs.get("loading"), "hero must load eagerly")

    def test_each_locale_links_all_languages_and_marks_the_current_page(self):
        expected_paths = {
            "ja": "/ArrowNavi/",
            "en": "/ArrowNavi/en/",
            "ko": "/ArrowNavi/ko/",
        }
        for locale, contract in LOCALES.items():
            with self.subTest(locale=locale):
                root = parse_page(contract["file"])
                language_navs = [
                    nav for nav in root.descendants("nav")
                    if all(
                        any(anchor.attrs.get("href") == path for anchor in nav.descendants("a"))
                        for path in expected_paths.values()
                    )
                ]
                self.assertTrue(language_navs, f"{locale} page needs links to all three locales")
                if not language_navs:
                    continue
                anchors = [
                    anchor for anchor in language_navs[0].descendants("a")
                    if anchor.attrs.get("href") in expected_paths.values()
                ]
                current = [anchor for anchor in anchors if anchor.attrs.get("aria-current") == "page"]
                self.assertEqual(1, len(current), f"{locale} language link needs aria-current=page")
                if current:
                    self.assertEqual(expected_paths[locale], current[0].attrs.get("href"))

    def test_each_locale_has_canonical_open_graph_and_complete_hreflang(self):
        hreflang_targets = {
            "ja": f"{PUBLIC_ORIGIN}/ArrowNavi/",
            "en": f"{PUBLIC_ORIGIN}/ArrowNavi/en/",
            "ko": f"{PUBLIC_ORIGIN}/ArrowNavi/ko/",
            "x-default": f"{PUBLIC_ORIGIN}/ArrowNavi/",
        }
        for locale, contract in LOCALES.items():
            with self.subTest(locale=locale):
                root = parse_page(contract["file"])
                titles = all_elements(root, "title")
                self.assertTrue(titles and titles[0].text().strip(), f"{locale} page needs a document title")
                canonical = [
                    link for link in root.descendants("link")
                    if "canonical" in (link.attrs.get("rel") or "").split()
                ]
                self.assertEqual([contract["url"]], [link.attrs.get("href") for link in canonical])
                self.assertTrue(any(
                    element.attrs.get("lang") == locale for element in root.descendants("html")
                ), f"{locale} HTML needs its language code")

                self.assertEqual(contract["url"], first_meta_content(root, prop="og:url"))
                self.assertEqual("website", first_meta_content(root, prop="og:type"))
                for prop in ("og:title", "og:description", "og:image", "og:image:alt"):
                    self.assertTrue(first_meta_content(root, prop=prop), f"missing {prop} for {locale}")
                self.assertEqual(f"{PUBLIC_ORIGIN}{contract['image']}", first_meta_content(root, prop="og:image"))
                self.assertEqual("1284", first_meta_content(root, prop="og:image:width"))
                self.assertEqual("2778", first_meta_content(root, prop="og:image:height"))
                self.assertTrue(first_meta_content(root, name="description"), f"missing description for {locale}")

                alternatives = {
                    link.attrs.get("hreflang"): link.attrs.get("href")
                    for link in root.descendants("link")
                    if "alternate" in (link.attrs.get("rel") or "").split()
                    and link.attrs.get("hreflang")
                }
                self.assertEqual(hreflang_targets, alternatives)

    def test_each_locale_describes_three_scenes_and_four_features(self):
        for locale, contract in LOCALES.items():
            with self.subTest(locale=locale):
                content = normalized_text(parse_page(contract["file"]))
                for scene in contract["scenes"]:
                    self.assertTrue(
                        all(term.lower() in content for term in scene),
                        f"{locale} page is missing a use scene: {scene}",
                    )
                for feature in contract["features"]:
                    for term in feature:
                        self.assertIn(term.lower(), content, f"{locale} page is missing feature detail: {term}")

    def test_hero_screenshots_exist_as_small_full_resolution_pngs(self):
        png_signature = b"\x89PNG\r\n\x1a\n"
        for locale in LOCALES:
            with self.subTest(locale=locale):
                path = ROOT / "ArrowNavi" / "assets" / f"{locale}-direction.png"
                self.assertTrue(path.is_file(), f"missing {path.relative_to(ROOT)}")
                if not path.is_file():
                    continue
                payload = path.read_bytes()
                self.assertLessEqual(len(payload), 512 * 1024, "each landing image must be <=512 KiB")
                self.assertGreaterEqual(len(payload), 24, "PNG header is incomplete")
                if len(payload) >= 24:
                    self.assertEqual(png_signature, payload[:8], "hero image must be PNG")
                    self.assertEqual((1284, 2778), (
                        int.from_bytes(payload[16:20], "big"),
                        int.from_bytes(payload[20:24], "big"),
                    ), "hero PNG must use the approved iPhone screenshot dimensions")

    def test_japanese_landing_keeps_links_to_existing_help_pages(self):
        root = parse_page(LOCALES["ja"]["file"])
        for path in (
            "/ArrowNavi/privacy-policy/",
            "/ArrowNavi/support/",
            "/ArrowNavi/compass-help/",
        ):
            with self.subTest(path=path):
                self.assertTrue(
                    any(anchor.attrs.get("href") == path for anchor in root.descendants("a")),
                    f"the landing page must retain its {path} link",
                )
                self.assertTrue((ROOT / path.lstrip("/") / "index.html").is_file())

if __name__ == "__main__":
    unittest.main()
