from flask import Flask, render_template, send_file, redirect, url_for, flash, request, session
import os
from datetime import datetime
import glob
from functools import wraps

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'  # Change this to a secure secret key

# Video directory
VIDEO_DIR = os.path.dirname(os.path.abspath(__file__))

# Login credentials (in a real app, use a proper database)
USERNAME = "admin"
PASSWORD = "admin123"  # Change this to a secure secret key

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'logged_in' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def get_video_files():
    """Get all video files with their details"""
    video_files = []
    for file in glob.glob(os.path.join(VIDEO_DIR, "*.h264")):
        file_info = {
            'name': os.path.basename(file),
            'size': os.path.getsize(file),
            'created': datetime.fromtimestamp(os.path.getctime(file)),
            'path': file
        }
        video_files.append(file_info)
    return sorted(video_files, key=lambda x: x['created'], reverse=True)

def format_file_size(size_bytes):
    """Convert bytes to human readable format"""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.1f} TB"

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        if username == USERNAME and password == PASSWORD:
            session['logged_in'] = True
            flash('You were successfully logged in')
            return redirect(url_for('index'))
        else:
            flash('Invalid credentials')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    flash('You were logged out')
    return redirect(url_for('login'))

@app.route('/')
@login_required
def index():
    videos = get_video_files()
    return render_template('index.html', 
                         videos=videos, 
                         format_file_size=format_file_size)

@app.route('/download/<filename>')
@login_required
def download_file(filename):
    try:
        return send_file(
            os.path.join(VIDEO_DIR, filename),
            as_attachment=True,
            download_name=filename
        )
    except Exception as e:
        flash(f"Error downloading file: {str(e)}")
        return redirect(url_for('index'))

@app.route('/delete/<filename>', methods=['POST'])
@login_required
def delete_file(filename):
    try:
        file_path = os.path.join(VIDEO_DIR, filename)
        if os.path.exists(file_path):
            os.remove(file_path)
            flash(f"Successfully deleted {filename}")
        else:
            flash(f"File {filename} not found")
    except Exception as e:
        flash(f"Error deleting file: {str(e)}")
    return redirect(url_for('index'))

@app.route('/delete_all', methods=['POST'])
@login_required
def delete_all():
    try:
        files_deleted = 0
        for file in glob.glob(os.path.join(VIDEO_DIR, "app.h264")):
            os.remove(file)
            files_deleted += 1
        if files_deleted > 0:
            flash(f"Successfully deleted {files_deleted} video(s)")
        else:
            flash("No videos found to delete")
    except Exception as e:
        flash(f"Error deleting videos: {str(e)}")
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True) 