# full-stack-project

A Flask-based study workspace application for students to manage tasks, notes, blog posts, and learning resources.

## Features

- Authentication
  - User signup and login with secure password hashing.
  - Session-based access control for protected routes.

- Workspace dashboard
  - Summary of active tasks, completed tasks, published blog posts, and uploaded notes.
  - Recent activity lists for tasks, blog posts, and notes.

- Task manager
  - Create, update, and delete tasks.
  - Categorize tasks by academic, personal, deadline, or custom labels.
  - Set optional due dates and reminders.
  - Mark tasks as completed for progress tracking.

- Blog / journal section
  - Write and publish blog posts about study experiences, tips, or projects.
  - Categorize posts and attach tags.
  - View published posts in a blog list.
  - Comment on posts and like/unlike posts for engagement.

- Note vault with image upload
  - Upload handwritten or digital note images.
  - Store notes with title and subject metadata.
  - Preview uploaded notes and download the image files.

## Application structure

- `app.py` - main Flask application and route definitions.
- `templates/` - Jinja2 templates for HTML pages.
- `static/css/style.css` - global application styling.
- `static/js/main.js` - UI behavior for previews, task editing, and navigation.
- `static/uploads/` - stored note image uploads.

## Setup

1. Create and activate a Python virtual environment:

```bash
python3 -m venv venv
source venv/bin/activate
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Run the app:

```bash
python app.py
```

4. Open the app in your browser at `http://localhost:5000`.

## Notes

- The application uses SQLite for data storage with `study_vault.db`.
- Uploaded note images are saved in `static/uploads` and referenced from the database.
- The app is currently configured to run in debug mode for local development.

## Routes

- `/` - redirect to login or workspace depending on authentication.
- `/login` - login page.
- `/signup` - registration page.
- `/workspace` - user dashboard.
- `/tasks` - task manager.
- `/tasks/add`, `/tasks/<id>/update`, `/tasks/<id>/delete` - task CRUD actions.
- `/journal` - blog list.
- `/post_editor` - create blog posts.
- `/posts/<id>` - blog post detail.
- `/posts/<id>/comment` - add a comment.
- `/posts/<id>/like` - toggle post like.
- `/vault` - note upload vault.
- `/vault/upload` - upload a note image.
- `/notes/<id>/preview` - note preview page.
- `/notes/<id>/download` - download note image.


