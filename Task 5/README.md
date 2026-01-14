# Car Service Booking App (Task 5)

A lightweight Streamlit app for booking car service appointments.

How to run:

1. Change directory to `Task 5`:

```bash
cd "Task 5"
```

2. Install Streamlit if not already installed:

```bash
pip install streamlit
```

3. Run the app:

```bash
streamlit run streamlit_service_app.py
```

If you prefer running from the repository root:

```bash
cd "Task 5" && streamlit run streamlit_service_app.py
```

Files:
- `streamlit_service_app.py` — main app (includes time-conflict checks, edit/delete UI, filters, search, and pagination)
- `appointments.csv` — stores appointments (created on first booking)

Notes:
- Data is stored locally in the `Task 5` folder.
- Time conflicts: the app prevents creating an appointment at the same date/time (optionally with a buffer in minutes).
- Edit/Delete: select an appointment to edit or delete (deletion requires confirmation).
- Filters and search are available (by date range, issue type, and text search in name/contact/notes).
- Export filtered results or the full dataset as CSV.
- Settings include "Buffer minutes" to block nearby time slots (0 = disabled).
- Streamlit runs in the browser and does not require an X server.
