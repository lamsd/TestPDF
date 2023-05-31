import subprocess
import time


def convert_file(file_path, output_filename):
    # command =  ['libreoffice', '--headless', '--convert-to', 'pdf', '--outdir', output_filename, file_path]
    # command = ['unoconv', '-f', 'pdf', '-o', output_filename, file_path]
    command = ['abiword', f'--to={output_filename}', file_path]
    try:
        start = time.time()
        subprocess.run(command)
        print(time.time() - start)
        print('Conversion started:', file_path)
    except subprocess.CalledProcessError as e:
        print('Conversion failed:', e)

convert_file('/home/ubuntu/python-project/upload/Ban_sao_cua_IELTS_4000_Academic_Word_List_docx-55679622.docx', '/home/ubuntu/python-project/download/Ban_sao_cua_IELTS_4000_Academic_Word_List_docx-55679622.pdf')