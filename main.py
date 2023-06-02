import os
import subprocess
from flask import Flask, request, jsonify, send_from_directory, render_template
from werkzeug.utils import secure_filename
from pathlib import Path
from queue import Queue
import threading
from time import sleep
from shutil import rmtree
from datetime import datetime

app = Flask(__name__)

if  os.path.exists("upload"):
    rmtree("upload")
if  os.path.exists("download"):
    rmtree("download")

sleep(5)

if not os.path.exists("upload"):
    os.makedirs("upload")
if not os.path.exists("download"):
    os.makedirs("download")
sleep(5)

UPLOAD_FOLDER = Path('upload')
OUTPUT_FOLDER = Path('download')

ALLOWED_EXTENSIONS = {'docx'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['OUTPUT_FOLDER'] = OUTPUT_FOLDER

task_queue = Queue()
task_status = {}
task_lock = threading.Lock()


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def convert_file(file_path, output_filename):
    command = ['libreoffice','--headless', '--convert-to', 'pdf', '--outdir', output_filename, file_path]
    try:
        subprocess.Popen(command)
        print('Conversion started:', file_path)
    except subprocess.CalledProcessError as e:
        print('Conversion failed:', e)

def process_conversion(file, file_path, time_data):
    file.save(file_path)
    output_file = file_path.with_suffix('.pdf')
    output_filename = os.path.join(app.config['OUTPUT_FOLDER'], time_data)#os.path.basename(output_file))
    with task_lock:
        task_status[file_path] = 'in_progress'

    # Start a new task for file conversion
    task_queue.put((file_path, output_filename))

    download_link = "/download?filename={}/{}".format(time_data, output_file.name)

    response = {'success': True, 'message': 'Conversion in progress', 'download_link': download_link}
    return jsonify(response)

def conversion_worker():
    while True:
        file_path, output_filename = task_queue.get()

        if file_path not in task_status or task_status[file_path] != 'in_progress':
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
    if 'file' in request.files:
        data = request.files["file"]
        filename = secure_filename(data.filename)
        time_data = str(datetime.now())
        file_path = UPLOAD_FOLDER  / filename
        return process_conversion(data, file_path, time_data)

    response = {'success': False, 'message': 'Invalid file extension'}
    return jsonify(response)


@app.route('/download', methods=['GET'])
def download():
    filename = request.args.get('filename')
    return send_from_directory(app.config['OUTPUT_FOLDER'], filename, as_attachment=True)

if __name__ == '__main__':
    conversion_thread = threading.Thread(target=conversion_worker)
    conversion_thread.daemon = True
    conversion_thread.start()
    app.debug = True
    app.run()

