import os
import subprocess
from flask import Flask, request, jsonify, send_from_directory, render_template
from werkzeug.utils import secure_filename
from pathlib import Path
from queue import Queue
import threading

app = Flask(__name__)

UPLOAD_FOLDER = Path('upload')
OUTPUT_FOLDER = Path('download')
ALLOWED_EXTENSIONS = {'docx'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['OUTPUT_FOLDER'] = OUTPUT_FOLDER

task_queue = Queue()
task_status = {}
task_lock = threading.Lock()


def allowed_file(filename):
    # print(filename)
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def convert_file(file_path, output_filename):
    # command = ['abiword', f'--to={output_filename}', file_path]
    # command = ['unoconvert', '--convert-to', 'pdf', file_path, output_filename]
    # command = ['libreoffice', '--nologo', '--infilter=Text (encoded):UTF8','--headless', '--convert-to', 'pdf', '--outdir', output_filename, file_path]
    command = ['libreoffice', '--infilter=Text (encoded):UTF8', '--headless', '--convert-to', 'pdf', '--outdir', output_filename, file_path]
    try:
        
        subprocess.Popen(command)
        print('Conversion started:', file_path)
    except subprocess.CalledProcessError as e:
        print('Conversion failed:', e)

def process_conversion(file, file_path):
    file.save(file_path)
    output_file = file_path.with_suffix('.pdf')
    output_filename = os.path.join(app.config['OUTPUT_FOLDER'], os.path.basename(output_file))
    with task_lock:
        task_status[file_path] = 'in_progress'

    # Start a new task for file conversion
    task_queue.put((file_path, output_filename))

    # Generate download link
    download_link = "/download?filename={}/{}".format(output_file.name, output_file.name)

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

# @app.route('/status', methods=['GET'])
# def download():
#     filename = request.args.get('filename')
#     if not os.path.isfile(os.path.join(app.config['OUTPUT_FOLDER'], os.path.basename(filename))):
#         return jsonify({'success': False, 'message': 'file is processing'})
#     return jsonify({'success': True})

@app.route('/download', methods=['GET'])
def download():
    filename = request.args.get('filename')
    return send_from_directory(app.config['OUTPUT_FOLDER'], filename, as_attachment=True)

if __name__ == '__main__':
    # Start the conversion worker thread
    conversion_thread = threading.Thread(target=conversion_worker)
    conversion_thread.daemon = True
    conversion_thread.start()
    app.debug = True
    app.run()

