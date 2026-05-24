"""Headless Playwright script to capture screenshots of key public pages.

Requires `playwright` to be installed and browsers to be installed (`playwright install`).
Saves screenshots to `results/plots/ui-screenshots/`.
"""
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "results" / "plots" / "ui-screenshots"
OUT.mkdir(parents=True, exist_ok=True)

PAGES = [
    ("/", "home.png"),
    ("/", "home-hero.png"),
    ("/", "home-cards.png"),
    ("/?_page=about", "about.png"),
    ("/?_page=services", "services.png"),
    ("/?_page=contact", "contact.png"),
]


def run():
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(viewport={"width": 1200, "height": 900})
        for path, name in PAGES:
            url = f"http://127.0.0.1:8501{path}"
            print("Loading", url)
            page.goto(url, wait_until="networkidle")
            # give Streamlit a moment to render
            page.wait_for_timeout(800)
            out_path = OUT / name
            page.screenshot(path=str(out_path), full_page=True)
            print("Saved", out_path)
        browser.close()


if __name__ == "__main__":
    run()
