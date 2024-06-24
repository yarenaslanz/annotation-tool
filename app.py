from flask import Flask, request, send_file, render_template

import subprocess
import os
import tempfile
import time

app = Flask(__name__)

UPLOAD_FOLDER = 'uploads'
CROPPED_FOLDER = 'cropped'
ALLOWED_EXTENSIONS = {'mp4', 'avi', 'mpeg', 'mkv'}

app.config['UPLOAD_FOLDER'] = os.path.join(os.path.dirname(__file__), UPLOAD_FOLDER)
app.config['CROPPED_FOLDER'] = os.path.join(os.path.dirname(__file__), CROPPED_FOLDER)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_video():
    start_time = time.time()
    if 'file' not in request.files:
        return 'No file part'

    file = request.files['file']
    if file.filename == '':
        return 'No selected file'

    if file and allowed_file(file.filename):
        filename = file.filename
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)
        end_time = time.time()
        duration = end_time - start_time
        print(f"Uploading video took {duration} seconds")
        return filename 
    else:
        return 'Invalid file format'

@app.route('/clip', methods=['POST'])
def clip_video():
    start_time_measure = time.time()
    start_time = request.form.get('start_time')
    end_time = request.form.get('end_time')
    file = request.files.get('file')

    if not file:
        return 'No file selected'

    filename = file.filename
    input_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    output_filename = 'clipped_' + filename
    output_path = os.path.join(app.config['CROPPED_FOLDER'], output_filename)

    try:
        subprocess.run(['ffmpeg', '-i', input_path, '-ss', start_time, '-to', end_time, '-c', 'copy', output_path], check=True)
    except subprocess.CalledProcessError as e:
        return f'Error: {e.stderr}'
    
    end_time_measure = time.time()
    duration = end_time_measure - start_time_measure
    print(f"Clipping video took {duration} seconds")

    if os.path.exists(output_path):
        #Return the clipped video file
        return send_file(output_path)
    else:
        return 'Video clipping failed: Output file not found'

@app.route('/uploads/<filename>')
def get_video(filename):
    return send_file(os.path.join(app.config['UPLOAD_FOLDER'], filename))

if __name__ == '__main__':
    app.run(debug=True, port=8080)