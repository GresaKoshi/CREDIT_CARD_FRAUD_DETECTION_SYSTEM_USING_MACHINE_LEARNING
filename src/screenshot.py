"""Capture screenshots of the FraudGuard ML dashboard pages for the thesis
documentation (Chapter 5 - System Implementation)."""
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "outputs" / "screenshots"
OUT.mkdir(parents=True, exist_ok=True)

BASE = "http://127.0.0.1:5057"

PAGES = [
    ("01_dashboard", "/"),
    ("02_transactions", "/transactions"),
    ("03_transactions_flagged", "/transactions?filter=flagged"),
    ("04_analyze", "/analyze"),
    ("05_reports", "/reports"),
]

with sync_playwright() as p:
    browser = p.chromium.launch()
    page = browser.new_page(viewport={"width": 1440, "height": 900})

    for name, path in PAGES:
        page.goto(BASE + path, wait_until="networkidle")
        page.wait_for_timeout(400)
        page.screenshot(path=str(OUT / f"{name}.png"), full_page=True)
        print("Captured", name)

    # Analyze page with a scored transaction (submit the form)
    page.goto(BASE + "/analyze", wait_until="networkidle")
    page.select_option("select[name=sample_idx]", index=1)
    page.click("button[type=submit]")
    page.wait_for_load_state("networkidle")
    page.wait_for_timeout(400)
    page.screenshot(path=str(OUT / "06_analyze_result.png"), full_page=True)
    print("Captured 06_analyze_result")

    browser.close()

print("All screenshots saved to", OUT)
