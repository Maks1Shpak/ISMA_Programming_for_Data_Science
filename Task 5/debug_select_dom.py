from playwright.sync_api import sync_playwright

URL = 'http://127.0.0.1:8501'
with sync_playwright() as p:
    browser = p.chromium.launch(headless=True, args=['--no-sandbox'])
    page = browser.new_page()
    page.goto(URL)
    import time; time.sleep(1)
    elems = page.locator('label:has-text("Select appointment to edit / delete")')
    print('labels count', elems.count())
    if elems.count() > 0:
        for i in range(elems.count()):
            el = elems.nth(i)
            print('label outerHTML:', el.evaluate('e => e.outerHTML'))
            parent = el.evaluate_handle('e => e.closest("div")')
            if parent:
                try:
                    print('parent outer:', parent.evaluate('p=>p.outerHTML')[:2000])
                except Exception as e:
                    print('parent evaluate error', e)
    else:
        print('No label nodes found')
    # also try to find any select element
    sel = page.locator('select')
    print('select count', sel.count())
    if sel.count() > 0:
        print('select outer:', sel.nth(0).evaluate('s => s.outerHTML'))
    browser.close()
