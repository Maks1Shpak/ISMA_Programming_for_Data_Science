from playwright.sync_api import sync_playwright

URL = 'http://127.0.0.1:8501'
with sync_playwright() as p:
    browser = p.chromium.launch(headless=True, args=['--no-sandbox'])
    page = browser.new_page()
    page.goto(URL)
    sel = page.locator('select[aria-label="Select appointment to edit / delete"]')
    print('select count', sel.count())
    if sel.count() > 0:
        vals = sel.evaluate('el => Array.from(el.options).map(o => ({value:o.value, text:o.text}))')
        print('options:', vals)
    else:
        # try to read rendered options text
        opts = page.locator('div[role="option"]').all_text_contents()
        print('div options sample:', opts[:10])
    browser.close()
