const form = document.getElementById('upload-form');
const fileInput = document.getElementById('file-input');
const convertButton = document.getElementById('convert-button');
const statusMessage = document.getElementById('status-message');

form.addEventListener('submit', (e) => {
    e.preventDefault();

    if (fileInput.files.length === 0) {
        statusMessage.textContent = 'No file selected';
        return;
    }

    const file = fileInput.files[0];
    const formData = new FormData();
    formData.append('file', file);

    statusMessage.textContent = 'Conversion in progress...';

    fetch('/convert', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            statusMessage.innerHTML = `Conversion completed. Download the file <a href="${data.download_link}">here</a>.`;
        } else {
            statusMessage.textContent = data.message;
        }
    })
    .catch(error => {
        console.error(error);
        statusMessage.textContent = 'An error occurred during conversion.';
    });
});