from flask import Flask, request, redirect, url_for, send_from_directory, render_template, flash, session
import os

app = Flask(__name__)
app.secret_key = 'supersecretkey'

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'mp4', 'mkv', 'avi', 'srt'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 1024 * 1024 * 1024 * 1024  # 1TB limit, practically unlimited

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    files = os.listdir(app.config['UPLOAD_FOLDER'])
    user_files = session.get('user_files', [])
    return render_template('index.html', files=files, user_files=user_files)

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'files' not in request.files:
        flash('No file part')
        return redirect(request.url)
    
    files = request.files.getlist('files')
    uploaded_files = []
    
    for file in files:
        if file.filename == '':
            continue
        if file and allowed_file(file.filename):
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], file.filename))
            uploaded_files.append(file.filename)

    if 'user_files' not in session:
        session['user_files'] = []
    session['user_files'].extend(uploaded_files)
    
    flash('Files uploaded successfully')
    return redirect(url_for('index'))

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/download/<filename>')
def download_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename, as_attachment=True)

@app.route('/remove/<filename>', methods=['POST'])
def remove_file(filename):
    if 'user_files' in session and filename in session['user_files']:
        try:
            os.remove(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            session['user_files'].remove(filename)
            flash('File removed successfully')
        except Exception as e:
            flash(f'Error removing file: {str(e)}')
    else:
        flash('File not found in your list')
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
