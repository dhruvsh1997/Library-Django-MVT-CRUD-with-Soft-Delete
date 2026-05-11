# 📚 Library — Django MVT CRUD with Soft Delete

A minimal Django web app for managing a personal book library. Built using the classic **Model–View–Template (MVT)** pattern **without** Django Forms — every input is pulled from `request.POST` and validated by hand. The point of this project is to feel the friction of manual CRUD so the form-based version makes sense by contrast.

It also demonstrates a **soft-delete + 24-hour recovery window** pattern, with a management command that hard-deletes expired records.

---

## ✨ Features

- Add, list, search, edit, and delete books
- Soft delete with a 24-hour grace period (Trash bin)
- Restore deleted books within the window
- Permanent (hard) delete option
- Automatic cleanup of expired soft-deleted records via a Django management command
- Clean dark-themed UI with inline CSS + JS (no frontend build step)

---

## 🧱 Tech Stack

- Python 3.10+
- Django 4.x or 5.x
- SQLite (default; swap freely in `settings.py`)
- No JavaScript framework — vanilla JS sprinkles only

---

## 📁 Project Structure

```
library_project/
├── library_project/
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── library/
│   ├── management/
│   │   └── commands/
│   │       └── cleanup_deleted.py
│   ├── migrations/
│   ├── templates/
│   │   └── library/
│   │       ├── book_list.html
│   │       ├── book_form.html
│   │       ├── book_confirm_delete.html
│   │       ├── book_confirm_hard_delete.html
│   │       └── trash_list.html
│   ├── models.py
│   ├── urls.py
│   └── views.py
└── manage.py
```

---

## 🚀 Setup

```bash
# 1. Clone and enter the project
git clone <your-repo-url>
cd library_project

# 2. Create a virtual environment
python -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate

# 3. Install dependencies
pip install django

# 4. Apply migrations
python manage.py makemigrations
python manage.py migrate

# 5. (Optional) Create a superuser for the admin
python manage.py createsuperuser

# 6. Run the dev server
python manage.py runserver
```

Open <http://localhost:8000/> and you're in.

---

## 🗺 Routes

| Method | URL                            | Purpose                  |
|--------|--------------------------------|--------------------------|
| GET    | `/`                            | List + search books      |
| GET/POST | `/add/`                      | Add a new book           |
| GET/POST | `/<id>/edit/`                | Edit a book              |
| GET/POST | `/<id>/delete/`              | Soft delete              |
| GET    | `/trash/`                      | View deleted books       |
| GET    | `/<id>/restore/`               | Restore from trash       |
| GET/POST | `/<id>/hard-delete/`         | Permanently delete       |

---

## 🗑 Soft Delete Concept

Every model that inherits from `SoftDeleteModel` gets:

- `is_deleted` (bool) and `deleted_at` (datetime) fields
- A default manager (`objects`) that **hides** soft-deleted rows from every query
- An escape-hatch manager (`all_objects`) that returns everything
- A `.delete()` override — soft delete by default, `delete(hard=True)` for real removal
- A `.restore()` method
- An `is_recoverable` property (True if still inside the 24h window)

Calling `Book.objects.all()` automatically excludes soft-deleted books — no extra filtering needed throughout the codebase.

---

## ⏰ Scheduling the Cleanup Command

The hard delete after 24 hours is performed by:

```bash
python manage.py cleanup_deleted
```

This project uses **plain OS cron** (no third-party scheduler library) so you can see how scheduling works at the most basic level before reaching for `django-crontab` or Celery in later projects.

### Linux / macOS — using `cron`

`cron` is a built-in Unix scheduler. Each user has a "crontab" (cron table) — a list of jobs to run on a schedule.

**Step 1.** Edit your crontab:

```bash
crontab -e
```

The first time, it asks you to pick an editor (`nano` is fine).

**Step 2.** Add a line at the bottom. Run the cleanup every day at 3:00 AM:

```cron
0 3 * * * cd /absolute/path/to/library_project && /absolute/path/to/venv/bin/python manage.py cleanup_deleted >> /tmp/library_cleanup.log 2>&1
```

Breaking that line down:

- `0 3 * * *` — at minute 0, hour 3, every day, every month, every weekday
- `cd /absolute/path/to/library_project` — switch into the project directory (cron starts in your home dir)
- `/absolute/path/to/venv/bin/python` — use the venv's Python (cron does **not** know about your `source venv/bin/activate`)
- `manage.py cleanup_deleted` — the command to run
- `>> /tmp/library_cleanup.log 2>&1` — append stdout *and* stderr to a log file so you can debug failures

**Step 3.** Save and exit. List your scheduled jobs to confirm:

```bash
crontab -l
```

**Step 4.** Test the command runs successfully outside cron first:

```bash
cd /absolute/path/to/library_project
source venv/bin/activate
python manage.py cleanup_deleted
```

Common gotchas:

- Use absolute paths everywhere — cron's `$PATH` is minimal.
- Cron sends email to the local user on errors; if you don't have mail set up, redirect to a logfile (as above) or you'll never see the failures.
- If your project depends on environment variables (`DATABASE_URL`, `SECRET_KEY`, etc.), set them inside the cron line or `source` an env file: `0 3 * * * cd /path && . .env && /path/venv/bin/python manage.py cleanup_deleted`.

### Windows — using Task Scheduler

1. Open **Task Scheduler** (search the Start menu).
2. Click **Create Basic Task** → name it "Library Cleanup".
3. Trigger: **Daily**, at 3:00 AM.
4. Action: **Start a program**.
   - Program/script: `C:\path\to\venv\Scripts\python.exe`
   - Add arguments: `manage.py cleanup_deleted`
   - Start in: `C:\path\to\library_project`
5. Finish, then right-click the task → **Run** to test it once.

### Manual testing without waiting a day

To verify soft delete + cleanup works end-to-end, temporarily change the window in `models.py` from `timedelta(days=1)` to `timedelta(minutes=2)`, delete a book, wait two minutes, run `python manage.py cleanup_deleted`, and confirm it's gone from `Book.all_objects`. Revert when done.

---

## 🧠 Concepts Covered

- Django MVT request → URL → view → template → response cycle
- Models, ORM, QuerySets, lazy evaluation
- Manual `request.POST` extraction and validation (the friction Forms remove)
- Custom model managers
- Abstract base models
- Management commands
- Soft vs hard delete + recovery windows
- OS-level scheduling with cron / Task Scheduler

---

## 📜 License

MIT
