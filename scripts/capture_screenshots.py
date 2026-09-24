"""
scripts/capture_screenshots.py
Automates high-resolution screenshots of the deployed Streamlit dashboard
using Playwright to fulfill Section 18 specifications.
"""

import time
from pathlib import Path
from playwright.sync_api import sync_playwright

OUT_DIR = Path("docs/screenshots")
OUT_DIR.mkdir(parents=True, exist_ok=True)

BASE_URL = "http://localhost:8501"


def capture_all():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        # Desktop context
        context = browser.new_context(viewport={"width": 1440, "height": 900}, device_scale_factor=2)
        page = context.new_page()

        print("Navigating to Overview...")
        page.goto(BASE_URL, wait_until="networkidle", timeout=60000)
        time.sleep(3)

        # 01_overview.png
        page.screenshot(path=str(OUT_DIR / "01_overview.png"), full_page=False)
        print("Captured 01_overview.png")

        # 02_student_checkin.png & 03_prediction_result.png & 04_explanation.png
        print("Navigating to Student Check-In...")
        try:
            page.get_by_role("link", name="Student Check-In").click()
        except Exception:
            page.get_by_text("Student Check-In").click()
        time.sleep(3)

        page.screenshot(path=str(OUT_DIR / "02_student_checkin.png"), full_page=False)
        print("Captured 02_student_checkin.png")

        # Find and click Analyze / Predict button if present
        try:
            # Look for button to analyze
            btn = page.locator("button:has-text('Analyze'), button:has-text('Predict'), button:has-text('Check')").first
            if btn.is_visible():
                btn.click()
                time.sleep(3)
        except Exception as e:
            print("Analyze click note:", e)

        # 03_prediction_result.png
        page.screenshot(path=str(OUT_DIR / "03_prediction_result.png"), full_page=False)
        print("Captured 03_prediction_result.png")

        # Scroll to explanation
        page.evaluate("window.scrollBy(0, 500)")
        time.sleep(1)
        page.screenshot(path=str(OUT_DIR / "04_explanation.png"), full_page=False)
        print("Captured 04_explanation.png")

        # 05_explore_improvements.png & 06_counterfactual.png
        print("Navigating to Explore Improvements...")
        try:
            page.get_by_role("link", name="Explore Improvements").click()
        except Exception:
            page.get_by_text("Explore Improvements").click()
        time.sleep(3)

        page.screenshot(path=str(OUT_DIR / "05_explore_improvements.png"), full_page=False)
        print("Captured 05_explore_improvements.png")

        # Scroll down for counterfactual
        page.evaluate("window.scrollBy(0, 450)")
        time.sleep(1)
        page.screenshot(path=str(OUT_DIR / "06_counterfactual.png"), full_page=False)
        print("Captured 06_counterfactual.png")

        # 07_class_insights.png
        print("Navigating to Class Insights...")
        try:
            page.get_by_role("link", name="Class Insights").click()
        except Exception:
            page.get_by_text("Class Insights").click()
        time.sleep(3)

        page.screenshot(path=str(OUT_DIR / "07_class_insights.png"), full_page=False)
        print("Captured 07_class_insights.png")

        # 08_topic_analysis.png
        print("Navigating to Cohort Analytics...")
        try:
            page.get_by_role("link", name="Cohort Analytics").click()
        except Exception:
            page.get_by_text("Cohort Analytics").click()
        time.sleep(3)

        page.screenshot(path=str(OUT_DIR / "08_topic_analysis.png"), full_page=False)
        print("Captured 08_topic_analysis.png")

        # 09_model_evaluation.png & 10_fairness.png
        print("Navigating to Trust & Fairness...")
        try:
            page.get_by_role("link", name="Trust & Fairness").click()
        except Exception:
            page.get_by_text("Trust & Fairness").click()
        time.sleep(3)

        # Tab 1: Model evaluation
        page.screenshot(path=str(OUT_DIR / "09_model_evaluation.png"), full_page=False)
        print("Captured 09_model_evaluation.png")

        # Click Fairness tab if tabs exist
        try:
            tab = page.locator("button[role='tab']:has-text('Fairness'), [data-baseweb='tab']:has-text('Fairness')").first
            if tab.is_visible():
                tab.click()
                time.sleep(2)
        except Exception as e:
            print("Fairness tab note:", e)

        page.screenshot(path=str(OUT_DIR / "10_fairness.png"), full_page=False)
        print("Captured 10_fairness.png")

        # 11_about_project.png
        print("Navigating to About Project...")
        try:
            page.get_by_role("link", name="About Project").click()
        except Exception:
            page.get_by_text("About Project").click()
        time.sleep(3)

        page.screenshot(path=str(OUT_DIR / "11_about_project.png"), full_page=False)
        print("Captured 11_about_project.png")

        context.close()

        # 12_mobile.png
        print("Capturing mobile view...")
        mobile_ctx = browser.new_context(
            viewport={"width": 390, "height": 844}, 
            is_mobile=True, 
            has_touch=True,
            device_scale_factor=2
        )
        mob_page = mobile_ctx.new_page()
        mob_page.goto(BASE_URL, wait_until="networkidle", timeout=60000)
        time.sleep(3)
        mob_page.screenshot(path=str(OUT_DIR / "12_mobile.png"), full_page=False)
        print("Captured 12_mobile.png")
        mobile_ctx.close()

        browser.close()
        print("All screenshots successfully captured in docs/screenshots/")


if __name__ == "__main__":
    capture_all()
