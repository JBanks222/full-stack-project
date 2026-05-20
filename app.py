import os
from datetime import datetime

from flask import Flask, render_template, redirect, url_for, session, request, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Replace with a secure key

# Configure the database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///study_vault.db'  # Use SQLite for simplicity
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = os.path.join(app.root_path, 'static', 'uploads')
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'bmp', 'webp'}

db = SQLAlchemy(app)

# Define the User model
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(128), nullable=False)
    posts = db.relationship('BlogPost', backref='author', cascade='all, delete-orphan')
    comments = db.relationship('Comment', backref='author', cascade='all, delete-orphan')
    likes = db.relationship('PostLike', backref='user', cascade='all, delete-orphan')
    notes = db.relationship('Note', backref='user', cascade='all, delete-orphan')

# Define the Task model
class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    category = db.Column(db.String(64), nullable=False, default='Personal')
    due_date = db.Column(db.Date, nullable=True)
    reminder = db.Column(db.DateTime, nullable=True)
    completed = db.Column(db.Boolean, nullable=False, default=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

# Define the Note model
class Note(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    subject = db.Column(db.String(100), nullable=False, default='General')
    filename = db.Column(db.String(260), nullable=False)
    uploaded_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

# Define the BlogPost model
class BlogPost(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    category = db.Column(db.String(64), nullable=False, default='Personal')
    tags = db.Column(db.String(256), nullable=True)
    published = db.Column(db.Boolean, nullable=False, default=True)
    published_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    author_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    comments = db.relationship('Comment', backref='post', cascade='all, delete-orphan')
    likes = db.relationship('PostLike', backref='post', cascade='all, delete-orphan')

# Define the Comment model
class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    post_id = db.Column(db.Integer, db.ForeignKey('blog_post.id'), nullable=False)
    author_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

# Define the PostLike model
class PostLike(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey('blog_post.id'), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    __table_args__ = (db.UniqueConstraint('user_id', 'post_id', name='unique_user_post_like'),)

# Initialize the database
with app.app_context():
    db.create_all()

@app.route('/')
def index():
    if 'logged_in' in session and session['logged_in']:
        return redirect(url_for('workspace'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'logged_in' in session and session['logged_in']:
        return redirect(url_for('workspace'))
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password, password):
            session['logged_in'] = True
            session['user_id'] = user.id
            session['user_email'] = user.email
            return redirect(url_for('workspace'))
        return render_template('login.html', error='Invalid credentials')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    return redirect(url_for('login'))

@app.route('/workspace')
def workspace():
    if 'logged_in' not in session or not session['logged_in']:
        return redirect(url_for('login'))

    active_tasks = Task.query.filter_by(user_id=session['user_id'], completed=False).order_by(Task.due_date.asc(), Task.id.desc()).limit(5).all()
    completed_tasks_count = Task.query.filter_by(user_id=session['user_id'], completed=True).count()
    active_tasks_count = Task.query.filter_by(user_id=session['user_id'], completed=False).count()
    posts_count = BlogPost.query.filter_by(author_id=session['user_id'], published=True).count()
    notes_count = Note.query.filter_by(user_id=session['user_id']).count()
    recent_posts = BlogPost.query.filter_by(author_id=session['user_id'], published=True).order_by(BlogPost.published_at.desc()).limit(3).all()
    recent_notes = Note.query.filter_by(user_id=session['user_id']).order_by(Note.uploaded_at.desc()).limit(3).all()

    return render_template(
        'workspace.html',
        user_email=session.get('user_email'),
        active_tasks=active_tasks,
        completed_tasks_count=completed_tasks_count,
        active_tasks_count=active_tasks_count,
        posts_count=posts_count,
        notes_count=notes_count,
        recent_posts=recent_posts,
        recent_notes=recent_notes,
    )

@app.route('/tasks')
def tasks():
    if 'logged_in' not in session or not session['logged_in']:
        return redirect(url_for('login'))

    tasks = Task.query.filter_by(user_id=session['user_id']).order_by(Task.completed.asc(), Task.due_date.asc(), Task.id.asc()).all()
    categories = ['Academic', 'Personal', 'Deadline', 'Other']
    return render_template('tasks.html', tasks=tasks, categories=categories)

@app.route('/tasks/add', methods=['POST'])
def add_task():
    if 'logged_in' not in session or not session['logged_in']:
        return redirect(url_for('login'))

    title = request.form.get('title', '').strip()
    category = request.form.get('category', 'Personal')
    due_date_value = request.form.get('due_date', '').strip()
    reminder_value = request.form.get('reminder', '').strip()

    if not title:
        return redirect(url_for('tasks'))

    due_date = datetime.fromisoformat(due_date_value).date() if due_date_value else None
    reminder = datetime.fromisoformat(reminder_value) if reminder_value else None

    new_task = Task(
        title=title,
        category=category,
        due_date=due_date,
        reminder=reminder,
        user_id=session['user_id'],
    )
    db.session.add(new_task)
    db.session.commit()
    return redirect(url_for('tasks'))

@app.route('/tasks/<int:task_id>/update', methods=['POST'])
def update_task(task_id):
    if 'logged_in' not in session or not session['logged_in']:
        return redirect(url_for('login'))

    task = Task.query.filter_by(id=task_id, user_id=session['user_id']).first_or_404()
    title = request.form.get('title', '').strip()
    category = request.form.get('category', 'Personal')
    due_date_value = request.form.get('due_date', '').strip()
    reminder_value = request.form.get('reminder', '').strip()
    completed_value = request.form.get('completed') == 'on'

    task.title = title or task.title
    task.category = category
    task.due_date = datetime.fromisoformat(due_date_value).date() if due_date_value else None
    task.reminder = datetime.fromisoformat(reminder_value) if reminder_value else None
    task.completed = completed_value

    db.session.commit()
    return redirect(url_for('tasks'))

@app.route('/tasks/<int:task_id>/delete', methods=['POST'])
def delete_task(task_id):
    if 'logged_in' not in session or not session['logged_in']:
        return redirect(url_for('login'))

    task = Task.query.filter_by(id=task_id, user_id=session['user_id']).first_or_404()
    db.session.delete(task)
    db.session.commit()
    return redirect(url_for('tasks'))

@app.route('/journal')
def journal():
    if 'logged_in' not in session or not session['logged_in']:
        return redirect(url_for('login'))

    posts = BlogPost.query.filter_by(published=True).order_by(BlogPost.published_at.desc()).all()
    return render_template('journal.html', posts=posts)

@app.route('/post_editor', methods=['GET', 'POST'])
def post_editor():
    if 'logged_in' not in session or not session['logged_in']:
        return redirect(url_for('login'))

    categories = ['Academic', 'Personal', 'Study Tips', 'Project']
    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        content = request.form.get('content', '').strip()
        category = request.form.get('category', 'Personal')
        tags = request.form.get('tags', '').strip()
        published = request.form.get('published') == 'on'

        if not title or not content:
            return render_template('post_editor.html', categories=categories, error='Title and content are required.')

        new_post = BlogPost(
            title=title,
            content=content,
            category=category,
            tags=tags,
            published=published,
            author_id=session['user_id'],
        )
        db.session.add(new_post)
        db.session.commit()
        return redirect(url_for('journal'))

    return render_template('post_editor.html', categories=categories)

@app.route('/posts/<int:post_id>')
def post_detail(post_id):
    if 'logged_in' not in session or not session['logged_in']:
        return redirect(url_for('login'))

    post = BlogPost.query.filter_by(id=post_id).first_or_404()
    liked = PostLike.query.filter_by(post_id=post.id, user_id=session['user_id']).first() is not None
    return render_template('post_detail.html', post=post, liked=liked)

@app.route('/posts/<int:post_id>/comment', methods=['POST'])
def post_comment(post_id):
    if 'logged_in' not in session or not session['logged_in']:
        return redirect(url_for('login'))

    post = BlogPost.query.filter_by(id=post_id, published=True).first_or_404()
    content = request.form.get('comment', '').strip()
    if content:
        comment = Comment(content=content, post_id=post.id, author_id=session['user_id'])
        db.session.add(comment)
        db.session.commit()
    return redirect(url_for('post_detail', post_id=post.id))

@app.route('/posts/<int:post_id>/like', methods=['POST'])
def post_like(post_id):
    if 'logged_in' not in session or not session['logged_in']:
        return redirect(url_for('login'))

    post = BlogPost.query.filter_by(id=post_id, published=True).first_or_404()
    existing_like = PostLike.query.filter_by(post_id=post.id, user_id=session['user_id']).first()
    if existing_like:
        db.session.delete(existing_like)
    else:
        db.session.add(PostLike(post_id=post.id, user_id=session['user_id']))
    db.session.commit()
    return redirect(request.referrer or url_for('post_detail', post_id=post.id))

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/vault')
def vault():
    if 'logged_in' not in session or not session['logged_in']:
        return redirect(url_for('login'))

    notes = Note.query.filter_by(user_id=session['user_id']).order_by(Note.uploaded_at.desc()).all()
    return render_template('vault.html', notes=notes)

@app.route('/vault/upload', methods=['POST'])
def upload_note():
    if 'logged_in' not in session or not session['logged_in']:
        return redirect(url_for('login'))

    file = request.files.get('image')
    title = request.form.get('title', '').strip() or 'Untitled Note'
    subject = request.form.get('subject', 'General').strip() or 'General'

    if not file or file.filename == '' or not allowed_file(file.filename):
        return redirect(url_for('vault'))

    filename = secure_filename(file.filename)
    save_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    if os.path.exists(save_path):
        name, ext = os.path.splitext(filename)
        filename = f"{name}_{int(datetime.utcnow().timestamp())}{ext}"
        save_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)

    file.save(save_path)

    note = Note(title=title, subject=subject, filename=filename, user_id=session['user_id'])
    db.session.add(note)
    db.session.commit()
    return redirect(url_for('vault'))

@app.route('/notes/<int:note_id>/preview')
def note_preview(note_id):
    if 'logged_in' not in session or not session['logged_in']:
        return redirect(url_for('login'))

    note = Note.query.filter_by(id=note_id, user_id=session['user_id']).first_or_404()
    return render_template('note_preview.html', note=note)

@app.route('/notes/<int:note_id>/download')
def download_note(note_id):
    if 'logged_in' not in session or not session['logged_in']:
        return redirect(url_for('login'))

    note = Note.query.filter_by(id=note_id, user_id=session['user_id']).first_or_404()
    return send_from_directory(app.config['UPLOAD_FOLDER'], note.filename, as_attachment=True)

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        if User.query.filter_by(email=email).first():
            return render_template('signup.html', error='Email already exists')
        # Use a supported method name for Werkzeug (pbkdf2 with sha256)
        hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
        new_user = User(email=email, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        session['logged_in'] = True
        session['user_id'] = new_user.id
        session['user_email'] = new_user.email
        return redirect(url_for('workspace'))
    return render_template('signup.html')

@app.before_request
def require_login():
    allowed_routes = ['login', 'signup', 'static']
    if 'logged_in' not in session and request.endpoint not in allowed_routes:
        return redirect(url_for('login'))


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)