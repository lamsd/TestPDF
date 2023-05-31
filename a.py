import subprocess
from flask import Flask, request, jsonify, send_from_directory, render_template
from werkzeug.utils import secure_filename
from pathlib import Path
from queue import Queue
import threading
from celery import Celery

app = Flask(__name__)

UPLOAD_FOLDER = Path('/home/ubuntu/python-project/upload')
OUTPUT_FOLDER = Path('/home/ubuntu/python-project/download')
ALLOWED_EXTENSIONS = {'docx'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['OUTPUT_FOLDER'] = OUTPUT_FOLDER

task_queue = Queue()
task_status = {}
task_lock = threading.Lock()


# Create a Celery instance
celery = Celery(app.name, broker='redis://localhost:6379/0')

# Set the task result backend
celery.conf.update(
    result_backend='redis://localhost:6379/0',
    task_track_started=True
)


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@celery.task
def convert_file(file_path, output_filename):
    command = ['unoconv', '-f', 'pdf', '-o', output_filename, file_path]
    try:
        subprocess.Popen(command)
        print('Conversion started:', file_path)
    except subprocess.CalledProcessError as e:
        print('Conversion failed:', e)


def process_conversion(file, file_path):
    file.save(file_path)
    output_file = file_path.with_suffix('.pdf')
    output_filename = OUTPUT_FOLDER / output_file.name

    # Start the Celery task for file conversion
    convert_file.delay(file_path, output_filename)

    # Generate download link
    download_link = f'/download?filename={output_file.name}'

    response = {'success': True, 'message': 'Conversion in progress', 'download_link': download_link}
    return jsonify(response)


def conversion_worker():
    while True:
        file_path, output_filename = task_queue.get()

        if file_path not in task_status or task_status[file_path] != 'in_progress':
            # Skip the task if it is not marked as in progress
            task_queue.task_done()
            continue

        try:
            convert_file(file_path, output_filename)
            with task_lock:
                task_status[file_path] = 'completed'
                print('Conversion completed:', file_path)
        except Exception as e:
            with task_lock:
                task_status[file_path] = 'failed'
                print('Conversion failed:', file_path, e)

        task_queue.task_done()

@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')

@app.route('/convert', methods=['POST'])
def convert():
    if 'file' not in request.files:
        response = {'success': False, 'message': 'No file uploaded'}
        return jsonify(response)

    file = request.files['file']
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file_path = UPLOAD_FOLDER / filename

        return process_conversion(file, file_path)

    response = {'success': False, 'message': 'Invalid file extension'}
    return jsonify(response)

@app.route('/download', methods=['GET'])
def download():
    filename = request.args.get('filename')
    return send_from_directory(app.config['OUTPUT_FOLDER'], filename, as_attachment=True)

if __name__ == '__main__':
    # Start the conversion worker thread
    conversion_thread = threading.Thread(target=conversion_worker)
    conversion_thread.daemon = True
    conversion_thread.start()

    app.run()

