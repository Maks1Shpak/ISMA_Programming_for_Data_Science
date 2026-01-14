"""
Service Booking App — Streamlit UI

Run:
    pip install streamlit
    cd "Task 5" && streamlit run streamlit_service_app.py

Features:
- Form for booking an appointment: name, contact, date, time, issue type, notes
- Stores submitted appointments to `appointments.csv` in the same folder
- Allows viewing and exporting the appointments
"""

from __future__ import annotations

import csv
import os
from datetime import datetime, date, time, timedelta
from typing import List, Dict

import streamlit as st

APP_CSV = "appointments.csv"
ISSUE_TYPES = [
    "Regular Maintenance",
    "Engine Problem",
    "Electrical / Battery",
    "Brakes / Suspension",
    "Tires / Wheels",
    "Other",
]


def ensure_csv_exists(path: str) -> None:
    if not os.path.exists(path):
        with open(path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["timestamp", "name", "contact", "date", "time", "issue_type", "notes"])


def append_appointment(path: str, row: List[str]) -> None:
    ensure_csv_exists(path)
    with open(path, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(row)


def read_appointments(path: str) -> List[Dict[str, str]]:
    if not os.path.exists(path):
        return []
    with open(path, "r", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        return list(reader)


# Additional helpers for edit/delete and checks
def overwrite_appointments(path: str, rows: List[Dict[str, str]]) -> None:
    """Atomically overwrite CSV with given rows (list of dicts)."""
    if not rows:
        # Write header-only file
        with open(path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["timestamp", "name", "contact", "date", "time", "issue_type", "notes"])
        return

    keys = list(rows[0].keys())
    tmp = path + ".tmp"
    with open(tmp, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=keys)
        writer.writeheader()
        for r in rows:
            writer.writerow(r)
    os.replace(tmp, path)


def delete_appointment(path: str, timestamp: str) -> bool:
    """Delete an appointment by timestamp. Returns True if deleted."""
    rows = read_appointments(path)
    new_rows = [r for r in rows if r.get("timestamp") != timestamp]
    if len(new_rows) == len(rows):
        return False
    overwrite_appointments(path, new_rows)
    return True


def update_appointment(path: str, timestamp: str, new_row: Dict[str, str]) -> bool:
    """Update appointment with given timestamp. Returns True if updated."""
    rows = read_appointments(path)
    updated = False
    for i, r in enumerate(rows):
        if r.get("timestamp") == timestamp:
            rows[i] = new_row
            updated = True
            break
    if updated:
        overwrite_appointments(path, rows)
    return updated


def find_conflict(path: str, appt_date: str, appt_time: str, ignore_ts: str | None = None, buffer_minutes: int = 0) -> bool:
    """Return True if another appointment exists with same date and time or within buffer minutes.
    Optionally ignore an appointment by timestamp."""
    rows = read_appointments(path)
    # convert requested time to minutes
    try:
        req_h, req_m = map(int, appt_time.split(":"))
        req_total = req_h * 60 + req_m
    except Exception:
        req_total = None
    for r in rows:
        if ignore_ts and r.get("timestamp") == ignore_ts:
            continue
        if r.get("date") != appt_date:
            continue
        other_time = r.get("time")
        if not other_time:
            continue
        # exact match
        if req_total is not None:
            try:
                oh, om = map(int, other_time.split(":"))
                other_total = oh * 60 + om
            except Exception:
                if r.get("time") == appt_time:
                    return True
                continue
            if buffer_minutes and abs(other_total - req_total) <= buffer_minutes:
                return True
            if other_total == req_total and buffer_minutes == 0:
                return True
        else:
            # fallback to exact string compare
            if r.get("time") == appt_time:
                return True
    return False


# Helpers for filtering and pagination
def filter_appointments(rows: List[Dict[str, str]], date_from: date, date_to: date, types: List[str], query: str) -> List[Dict[str, str]]:
    q = (query or "").strip().lower()
    out = []
    for r in rows:
        try:
            rd = datetime.fromisoformat(r['date']).date()
        except Exception:
            continue
        if rd < date_from or rd > date_to:
            continue
        if types and r.get('issue_type') not in types:
            continue
        if q:
            # search in name, contact and notes
            hay = (r.get('name','').lower() + ' ' + r.get('contact','').lower() + ' ' + r.get('notes','').lower())
            if q not in hay:
                continue
        out.append(r)
    # sort by date then time
    out.sort(key=lambda x: (x.get('date',''), x.get('time','')))
    return out



st.set_page_config(page_title="Car Service Booking", layout="centered")
st.title("Car Service — Appointment Booking")
st.markdown("Select date, time, and issue type. Data is saved locally to `appointments.csv`.")

# Optional settings for validations / UX
with st.expander("Settings (optional)", expanded=False):
    st.session_state['buffer_minutes'] = st.number_input(
        "Buffer minutes around appointments (0 = disabled)",
        min_value=0, max_value=1440,
        value=st.session_state.get('buffer_minutes', 0), step=15,
        help="Blocks booking within +/- buffer minutes around existing appointments",
    )

with st.form(key="appointment_form"):
    name = st.text_input("Customer name", max_chars=100)
    contact = st.text_input("Contact (phone or email)")

    col1, col2 = st.columns(2)
    with col1:
        appt_date = st.date_input("Date", value=date.today())
    with col2:
        appt_time = st.time_input("Time", value=datetime.now().time().replace(second=0, microsecond=0))

    issue_type = st.selectbox("Issue type / request", options=ISSUE_TYPES)
    notes = st.text_area("Additional notes (optional)")

    submitted = st.form_submit_button("Book appointment")

    if submitted:
        # Basic validation
        errors = []
        if not name.strip():
            errors.append("Ім'я обов'язкове")
        if not contact.strip():
            errors.append("Контакт обов'язковий")
        # Date must not be in the past
        today = date.today()
        if appt_date < today:
            errors.append("Дата не може бути в минулому")

        if errors:
            for e in errors:
                st.error(e)
        else:
            nd = appt_date.isoformat()
            nt = appt_time.strftime("%H:%M")
            buffer = st.session_state.get('buffer_minutes', 0)
            # conflict check (with optional buffer)
            if find_conflict(APP_CSV, nd, nt, buffer_minutes=buffer):
                st.error(f"There is already an appointment at this time — choose another date/time (buffer: {buffer} min)")
            else:
                timestamp = datetime.now().isoformat()
                row = [timestamp, name.strip(), contact.strip(), nd, nt, issue_type, notes.strip()]
                append_appointment(APP_CSV, row)
                st.success("Appointment saved successfully!")

# Show appointments, edit/delete with filters, pagination and export
st.markdown("---")
st.header("Saved appointments")
appointments = read_appointments(APP_CSV)
# show flash message from previous action (delete / update)
if st.session_state.get('last_action_message'):
    st.success(st.session_state.pop('last_action_message'))

# Initialize session state for pagination and pending deletion
if 'page' not in st.session_state:
    st.session_state['page'] = 1
if 'pending_delete' not in st.session_state:
    st.session_state['pending_delete'] = None

if not appointments:
    st.info("No appointments yet.")
else:
    # Filters
    with st.expander("Filters & Search", expanded=False):
        # sensible defaults
        default_from = date.today() - timedelta(days=30)
        default_to = date.today() + timedelta(days=365)
        colf1, colf2, colf3 = st.columns([1,1,2])
        with colf1:
            date_from = st.date_input("From (date)", value=default_from)
            date_to = st.date_input("To (date)", value=default_to)
        with colf2:
            types = st.multiselect("Issue types", options=ISSUE_TYPES, default=ISSUE_TYPES)
        with colf3:
            q = st.text_input("Search (name, contact or notes)")

    # Apply filtering
    filtered = filter_appointments(appointments, date_from, date_to, types, q)

    # Pagination controls
    colp1, colp2, colp3 = st.columns([1,2,1])
    with colp1:
        page_size = st.selectbox("Показати на сторінці", options=[5, 10, 25], index=0)
    total = len(filtered)
    pages = max(1, (total + page_size - 1) // page_size)
    # reset page if out of range
    if st.session_state['page'] > pages:
        st.session_state['page'] = pages

    with colp2:
        if st.button("◀", key='prev') and st.session_state['page'] > 1:
            st.session_state['page'] -= 1
        st.write(f"Page {st.session_state['page']} / {pages} — total: {total}")
        if st.button("▶", key='next') and st.session_state['page'] < pages:
            st.session_state['page'] += 1

    # selection / edit area
    start = (st.session_state['page'] - 1) * page_size
    end = start + page_size
    page_rows = filtered[start:end]

    options = [f"{r['date']} {r['time']} — {r['name']} (id: {r['timestamp']})" for r in page_rows]
    sel = st.selectbox("Select appointment to edit / delete", options=["(not selected)"] + options, index=0)

    if sel != "(not selected)":
        ts = sel.split("id: ")[-1].rstrip(')')
        current = next((r for r in appointments if r.get('timestamp') == ts), None)
        if current:
            st.subheader("Appointment details")
            st.write(f"**{current['date']} {current['time']} — {current['name']}**")
            st.write(f"Contact: {current['contact']} | Type: {current['issue_type']}")
            if current.get('notes'):
                st.write(f"Notes: {current['notes']}")

            with st.form(key=f"edit_form_{ts}"):
                new_name = st.text_input("Name", value=current['name'])
                new_contact = st.text_input("Contact", value=current['contact'])
                new_date = st.date_input("Date", value=datetime.fromisoformat(current['date']).date())
                new_time = st.time_input("Time", value=datetime.strptime(current['time'], "%H:%M").time())
                new_issue = st.selectbox("Issue type / request", options=ISSUE_TYPES, index=ISSUE_TYPES.index(current['issue_type']) if current['issue_type'] in ISSUE_TYPES else 0)
                new_notes = st.text_area("Notes", value=current.get('notes',''))
                edit_subm = st.form_submit_button("Save changes")

                if edit_subm:
                    nd = new_date.isoformat()
                    nt = new_time.strftime("%H:%M")
                    buffer = st.session_state.get('buffer_minutes', 0)
                    # check conflict including buffer
                    conflict = find_conflict(APP_CSV, nd, nt, ignore_ts=current['timestamp'], buffer_minutes=buffer)
                    if conflict:
                        st.error("Cannot save: an appointment already exists at that time (or within buffer)")
                    else:
                        new_row = {
                            'timestamp': current['timestamp'],
                            'name': new_name.strip(),
                            'contact': new_contact.strip(),
                            'date': nd,
                            'time': nt,
                            'issue_type': new_issue,
                            'notes': new_notes.strip(),
                        }
                        ok = update_appointment(APP_CSV, current['timestamp'], new_row)
                        if ok:
                            # set flash message and rerun so the updated data is shown immediately
                            st.session_state['last_action_message'] = "Appointment updated"
                            # trigger a rerun by updating query params (works across Streamlit versions)
                            qp = dict(st.query_params) if st.query_params else {}
                            qp['_refresh'] = str(int(datetime.now().timestamp()))
                            st.query_params = qp
                            st.stop()
                        else:
                            st.error("Failed to update appointment")

            # delete action sets a single pending delete id (centralized confirmation shown below)
            if st.button("Delete appointment", key=f"del_{ts}"):
                st.session_state['pending_delete'] = ts

    # centralized confirmation area (only one visible at a time)
    if st.session_state.get('pending_delete'):
        pd_ts = st.session_state['pending_delete']
        pd_current = next((r for r in appointments if r.get('timestamp') == pd_ts), None)
        if pd_current:
            st.warning(f"Confirm deletion of appointment: {pd_current['date']} {pd_current['time']} — {pd_current['name']}")
            cold1, cold2 = st.columns([1,1])
            with cold1:
                if st.button("Confirm deletion", key="confirm_delete"):
                    if delete_appointment(APP_CSV, pd_ts):
                        # clear pending and prepare new pagination, then rerun to refresh UI
                        st.session_state['pending_delete'] = None
                        appointments = read_appointments(APP_CSV)
                        filtered = filter_appointments(appointments, date_from, date_to, types, q)
                        total = len(filtered)
                        pages = max(1, (total + page_size - 1) // page_size)
                        if st.session_state['page'] > pages:
                            st.session_state['page'] = pages
                        st.session_state['last_action_message'] = "Appointment deleted"
                        # trigger a rerun by updating query params (works across Streamlit versions)
                        qp = dict(st.query_params) if st.query_params else {}
                        qp['_refresh'] = str(int(datetime.now().timestamp()))
                        st.query_params = qp
                        st.stop()
                    else:
                        st.error("Failed to delete appointment")
                        st.session_state['pending_delete'] = None
            with cold2:
                if st.button("Cancel", key="cancel_delete"):
                    st.session_state['pending_delete'] = None

    st.markdown("---")

    # show page results (latest first within filtered selection)
    for i, r in enumerate(reversed(page_rows), start=1 + start):
        st.write(f"**{i}. {r['date']} {r['time']} — {r['name']}**")
        st.write(f" Contact: {r['contact']} | Type: {r['issue_type']}")
        if r.get("notes"):
            st.write(f"  Notes: {r['notes']}")
        st.markdown("---")

    # Export filtered results (CSV)
    if filtered:
        keys = list(filtered[0].keys())
        csv_filtered = "\n".join([",".join(keys)] + [",".join([r.get(k,"") for k in keys]) for r in filtered]).encode('utf-8')
        st.download_button("Export filtered CSV", data=csv_filtered, file_name="appointments_filtered.csv", mime="text/csv")
    # Full export (all appointments)
    if appointments:
        keys_all = list(appointments[0].keys())
        csv_all = "\n".join([",".join(keys_all)] + [",".join([r.get(k,"") for k in keys_all]) for r in appointments]).encode('utf-8')
        st.download_button("Export all CSV", data=csv_all, file_name="appointments_all.csv", mime="text/csv")

st.markdown("---")
st.info("Tip: run from the `Task 5` folder: `cd \"Task 5\" && streamlit run streamlit_service_app.py`")
