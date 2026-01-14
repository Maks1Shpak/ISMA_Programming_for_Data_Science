"""Capture real screenshots from the running Streamlit app using Playwright.

Generates assets/booking_real.png, assets/edit_real.png, assets/delete_real.png
"""
import time
from datetime import datetime
from pathlib import Path
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout

ASSETS = Path(__file__).with_name('assets')
ASSETS.mkdir(exist_ok=True)

URL = 'http://127.0.0.1:8501'

# wait for HTTP server ready before using Playwright
import requests

def wait_for_http(url, timeout=30):
    for _ in range(timeout * 2):
        try:
            r = requests.get(url, timeout=1)
            if r.status_code == 200:
                return True
        except Exception:
            pass
        time.sleep(0.5)
    return False


def wait_for_app(page):
    # wait for main title
    for _ in range(20):
        try:
            if page.locator('text=Car Service — Appointment Booking').count() > 0:
                return True
        except Exception:
            pass
        time.sleep(0.5)
    return False

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True, args=['--no-sandbox'])
    context = browser.new_context(viewport={'width':1200, 'height':900})
    page = context.new_page()
    print('Opening', URL)
    page.goto(URL, wait_until='domcontentloaded', timeout=60000)
    if not wait_for_app(page):
        raise SystemExit('App did not start in time')

    # unique name to identify our appointment
    uniq = f"AutoTester-{int(datetime.utcnow().timestamp())}"

    # BOOKING: fill the form and submit
    print('Filling booking form...')
    page.get_by_label('Customer name').fill(uniq)
    page.get_by_label('Contact (phone or email)').fill('tester@example.com')
    # leave date/time default
    # choose 'Regular Maintenance' option (try both <select> and custom widget paths)
    sel = page.locator('select[aria-label="Issue type / request"]')
    if sel.count() > 0:
        try:
            sel.select_option(index=0)
        except Exception:
            # fallback: pick by value
            vals = sel.evaluate('el => Array.from(el.options).map(o => o.value)')
            if vals:
                sel.select_option(vals[0])
    else:
        # custom combobox path: click and click the visible option
        page.get_by_label('Issue type / request').click()
        page.locator('text=Regular Maintenance').first.click()

    page.get_by_label('Additional notes (optional)').fill('Automated booking for screenshots')
    page.get_by_role('button', name='Book appointment').click()

    try:
        page.wait_for_selector('text=Appointment saved successfully!', timeout=5000)
    except PlaywrightTimeout:
        print('Warning: Save confirmation not detected')

    # wait for appointment to appear in the list
    try:
        page.wait_for_selector(f'text={uniq}', timeout=5000)
    except Exception:
        print('Warning: created appointment text not visible yet')

    time.sleep(0.6)
    booking_img = ASSETS / 'booking_real.png'
    page.screenshot(path=str(booking_img), full_page=True)
    print('Saved', booking_img)

    # also capture the appointments list view
    time.sleep(0.6)
    list_img = ASSETS / 'list_real.png'
    # scroll to the bottom where 'Saved appointments' are shown
    try:
        el = page.locator('text=Saved appointments')
        if el.count() > 0:
            el.scroll_into_view_if_needed()
    except Exception:
        pass
    page.screenshot(path=str(list_img), full_page=True)
    print('Saved', list_img)

    # SELECT the appointment in the selectbox
    print('Selecting created appointment...')
    # first try the HTML select element
    select = page.locator('select[aria-label="Select appointment to edit / delete"]')
    if select.count() > 0:
        try:
            # try to select by option text containing uniq
            vals = select.evaluate('el => Array.from(el.options).map(o => ({value:o.value, text:o.text}))')
            sel_val = None
            for v in vals:
                if uniq in v['text']:
                    sel_val = v['value']
                    break
            if sel_val:
                select.select_option(sel_val)
            else:
                # pick the second option as fallback
                if len(vals) > 1:
                    select.select_option(vals[1]['value'])
        except Exception as e:
            print('Warning selecting from <select> failed', e)
    else:
        # fallback: set combobox value directly to the option text (simulate user typing/selecting)
        try:
            # read appointments CSV to find our uniq row and build the option text exactly as Streamlit displays
            import csv
            APP_CSV = 'Task 5/appointments.csv'
            option_text = None
            try:
                with open(APP_CSV, 'r', encoding='utf-8') as f:
                    reader = csv.DictReader(f)
                    for r in reader:
                        if uniq in r.get('name',''):
                            option_text = f"{r.get('date','')} {r.get('time','')} — {r.get('name','')}"
                            break
            except Exception:
                option_text = None

            comb = page.locator('input[role="combobox"][aria-label*="Select appointment to edit / delete"]')
            if comb.count() == 0:
                comb = page.locator('input[role="combobox"]')

            if option_text:
                comb.click()
                # set the value via JS and dispatch events
                page.evaluate("(el, v) => { el.value = v; el.dispatchEvent(new Event('input',{bubbles:true})); el.dispatchEvent(new Event('change',{bubbles:true})); }", comb.element_handle(), option_text)
                comb.press('Enter')
            else:
                # fallback: try keyboard nav
                comb.click()
                comb.press('ArrowDown')
                comb.press('ArrowDown')
                comb.press('Enter')
        except Exception as e:
            print('Warning: selecting appointment via UI failed', e)

    # wait a short while for UI to show the details
    time.sleep(1.0)

    # EDIT: ensure the edit form is visible, change time to 11:00 and save
    print('Editing appointment...')
    try:
        page.wait_for_selector('text=Appointment details', timeout=5000)
    except Exception:
        print('Warning: Appointment details not visible after selection')

    # change time input
    try:
        page.get_by_label('Time').fill('11:00')
    except Exception:
        # some streamlit time inputs might be split; try to set value via JS
        try:
            page.evaluate("document.querySelector('input[type=time]').value = '11:00'")
        except Exception:
            print('Warning: could not set time via JS')

    try:
        # wait for the Save changes button to appear and click it
        page.get_by_role('button', name='Save changes').wait_for(state='visible', timeout=5000)
        page.get_by_role('button', name='Save changes').click()
    except Exception:
        print('Warning: Save changes button not found or not clickable')

    try:
        page.wait_for_selector('text=Appointment updated', timeout=5000)
    except PlaywrightTimeout:
        print('Warning: Update confirmation not detected')
    time.sleep(0.6)
    edit_img = ASSETS / 'edit_real.png'
    page.screenshot(path=str(edit_img), full_page=True)
    print('Saved', edit_img)

    # DELETE: click delete and confirm
    print('Initiating delete...')
    page.get_by_role('button', name='Delete appointment').click()
    time.sleep(0.4)
    # confirm delete
    page.get_by_role('button', name='Confirm deletion').click()
    try:
        page.wait_for_selector('text=Appointment deleted', timeout=5000)
    except PlaywrightTimeout:
        print('Warning: Delete confirmation not detected')
    time.sleep(0.6)
    delete_img = ASSETS / 'delete_real.png'
    page.screenshot(path=str(delete_img), full_page=True)
    print('Saved', delete_img)

    browser.close()

print('Done capturing real screenshots')
