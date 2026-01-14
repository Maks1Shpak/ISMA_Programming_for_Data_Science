from playwright.sync_api import sync_playwright
URL = 'http://127.0.0.1:8501'
with sync_playwright() as p:
    browser = p.chromium.launch(headless=True, args=['--no-sandbox'])
    page = browser.new_page()
    page.goto(URL)
    import time; time.sleep(1)
    body = page.locator('body').inner_text()
    print(body[:2000])
    browser.close()
