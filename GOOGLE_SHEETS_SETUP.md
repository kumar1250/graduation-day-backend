# Google Sheets Setup Guide

This backend no longer uses a database or local Excel files. There is
**no `db.sqlite3`, no `manage.py migrate`, and no local `.xlsx` files
to write to.** All data — the student roster and every submitted
registration — lives in one Google Sheet, split across two tabs:

- **Students** — the roster (roll number → student details). The very
  first time the app runs against a brand-new Google Sheet, this tab
  auto-fills itself from `data/students.xlsx`, which ships in the repo.
  You don't need to copy/paste anything for this part.
- **Registrations** — one row per submitted registration. This is the
  data that used to disappear on Render restarts; now it's safe.

You do **not** need to change any code. Just do the one-time setup
below, then set two environment variables. Total time: about 5 minutes.

---

## Step 1 — Create a Google Cloud project

1. Go to https://console.cloud.google.com/
2. Click the project dropdown (top-left) → **New Project**
3. Name it anything, e.g. `registration-backend` → **Create**
4. Make sure the new project is selected before continuing

## Step 2 — Enable the Google Sheets and Drive APIs

1. Search **"Google Sheets API"** in the top search bar → open it → **Enable**
2. Search **"Google Drive API"** → open it → **Enable**
   (needed so the service account can open the sheet by ID)

## Step 3 — Create a Service Account

This is a "robot user" your backend logs in as.

1. Search **"Service Accounts"** → open it
2. **+ Create Service Account**
3. Name it e.g. `registration-sheets-bot` → **Create and Continue**
4. Skip the role step → **Continue** → **Done**

## Step 4 — Create and download the JSON key

1. Click the service account you just made → **Keys** tab
2. **Add Key** → **Create new key** → **JSON** → **Create**
3. A `.json` file downloads — keep it safe. **Never commit it to git
   or share it publicly**, it's a credential.
4. Open it and note the `"client_email"` field, e.g.
   `registration-sheets-bot@registration-backend.iam.gserviceaccount.com`
   — you'll need it in Step 6.

## Step 5 — Create the Google Sheet

1. Go to https://sheets.google.com/ → **Blank spreadsheet**
2. Rename it to anything, e.g. `Registration Backend Data`
3. Copy the ID from the URL:
   ```
   https://docs.google.com/spreadsheets/d/1AbCdEfGhIjKlMnOpQrStUvWxYz/edit
                                          ^^^^^^^^^^^^^^^^^^^^^^^^^^^ this is the ID
   ```
   Leave the sheet otherwise empty — the app creates the `Students` and
   `Registrations` tabs (with headers, and the roster auto-seeded)
   automatically the first time it runs.

## Step 6 — Share the Sheet with your service account

1. In the sheet, click **Share** (top-right)
2. Paste in the `client_email` from Step 4
3. Set permission to **Editor**
4. Uncheck "Notify people" → **Share**

## Step 7 — Set the environment variables

You need two values:

- **`GOOGLE_SHEET_ID`** — the ID from Step 5
- **`GOOGLE_SERVICE_ACCOUNT_JSON`** — the *entire contents* of the JSON
  file from Step 4

### On Render

1. Render dashboard → your web service → **Environment**
2. **Add Environment Variable**:
   - Key: `GOOGLE_SHEET_ID` → Value: (the sheet ID)
3. **Add Environment Variable** again:
   - Key: `GOOGLE_SERVICE_ACCOUNT_JSON` → Value: paste the entire
     `.json` file contents (multi-line is fine, Render accepts it)
4. **Save Changes** — Render redeploys automatically

### For local development

Copy `.env.example` to `.env` and fill in:

```
GOOGLE_SHEET_ID=1AbCdEfGhIjKlMnOpQrStUvWxYz
GOOGLE_SERVICE_ACCOUNT_JSON='{"type": "service_account", "project_id": "...", ...}'
```

## Step 8 — Install the new dependency

Already added to `requirements.txt` (`gspread`, `google-auth`,
`python-dotenv`). Render installs it automatically. Locally:

```bash
pip install -r requirements.txt
```

## Step 9 — Verify it worked

1. Redeploy (or restart locally) and open your Google Sheet
2. You should see a **Students** tab appear, pre-filled with the ~670
   students from `data/students.xlsx`
3. Submit a test registration through your site/API
4. A **Registrations** tab appears with your test row
5. Restart the Render service (or wait 15+ minutes on the free tier)
   and check again — the row is still there. That's the fix confirmed.
6. Delete the test row from the sheet directly when done testing.

---

## No database, by design

This project's API never touches Django's ORM, admin, or auth — so
`INSTALLED_APPS` and `DATABASES` were trimmed to remove them entirely.
There's nothing to migrate:

```bash
$ python manage.py migrate
# django.core.exceptions.ImproperlyConfigured: settings.DATABASES is
# improperly configured — expected, since there's no database.
```

If you ever add something that genuinely needs Django's ORM (e.g. a
real admin-login system), you'd add `django.contrib.auth` and a
`DATABASES` entry back in `core/settings.py` at that point — but
nothing in this app currently needs it.

## Troubleshooting

**"GOOGLE_SERVICE_ACCOUNT_JSON is not set"**
The env var is missing on Render/locally. Re-check Step 7.

**"GOOGLE_SERVICE_ACCOUNT_JSON is not valid JSON"**
Something got cut off when pasting. Re-copy the full `.json` file.

**"Google Sheet not found for GOOGLE_SHEET_ID"**
Either the ID is wrong (Step 5) or the sheet wasn't shared with the
service account's `client_email` as **Editor** (Step 6).

**Students tab is empty / didn't auto-seed**
The seed only runs if `data/students.xlsx` is present in the deployed
repo and the Students tab has no data rows yet. If you added rows
manually first, seeding is skipped (it never overwrites existing data).

**Rate limit errors under heavy simultaneous load**
Google Sheets allows 60 write requests/minute per service account by
default — fine for normal registration traffic.
