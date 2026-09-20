document.addEventListener('DOMContentLoaded', () => {
    initHomeClassifier();
});

let homeSelectedFile = null;

function initHomeClassifier() {
    const dropZone = document.getElementById('homeDropZone');
    const imageInput = document.getElementById('homeImageInput');

    if (!dropZone || !imageInput) return;

    dropZone.addEventListener('click', () => imageInput.click());

    imageInput.addEventListener('change', (e) => {
        if (e.target.files.length > 0) {
            handleHomeFileSelected(e.target.files[0]);
        }
    });

    dropZone.addEventListener('dragover', (e) => {
        e.preventDefault();
        dropZone.classList.add('drag-over');
    });

    dropZone.addEventListener('dragleave', () => dropZone.classList.remove('drag-over'));

    dropZone.addEventListener('drop', (e) => {
        e.preventDefault();
        dropZone.classList.remove('drag-over');
        if (e.dataTransfer.files.length > 0) {
            handleHomeFileSelected(e.dataTransfer.files[0]);
        }
    });
}

function handleHomeFileSelected(file) {
    if (!file.type.startsWith('image/')) {
        alert('Please select a valid image file.');
        return;
    }

    homeSelectedFile = file;
    const reader = new FileReader();
    reader.onload = (e) => {
        const preview = document.getElementById('homeImagePreview');
        const prompt = document.querySelector('.drop-zone-prompt');
        preview.src = e.target.result;
        preview.classList.remove('hidden');
        prompt.classList.add('hidden');
        document.getElementById('homeClassifyBtn').disabled = false;
    };
    reader.readAsDataURL(file);
}

async function homeQuickClassify() {
    if (!homeSelectedFile) return;

    const resultBox = document.getElementById('homeResultBox');
    resultBox.innerHTML = '<div class="spinner"></div><p>Processing with AI Model...</p>';

    const formData = new FormData();
    formData.append('image', homeSelectedFile);

    try {
        const response = await fetch('/api/classify', {
            method: 'POST',
            body: formData
        });

        const data = await response.json();

        if (data.success) {
            resultBox.innerHTML = `
                <div class="result-card-inner">
                    <h3>Prediction: <span style="color:#10b981;">${data.category_name}</span></h3>
                    <p><strong>Waste Type:</strong> ${data.waste_type}</p>
                    <p><strong>Recommended Bin:</strong> <span class="badge-${data.recommended_bin_color.toLowerCase()}">${data.recommended_bin_color} Bin</span></p>
                    <p><strong>Confidence:</strong> ${data.confidence_percent}</p>
                    <div class="suggestion-box" style="margin-top:0.8rem;">
                        <span class="suggestion-title">💡 Segregation Advice:</span>
                        <p class="suggestion-text">${data.disposal_suggestion}</p>
                    </div>
                    <div style="margin-top:1rem; display:flex; gap:0.5rem;">
                        <a href="/routes" class="btn btn-primary btn-sm">🗺️ Proceed to Route Optimization</a>
                        <a href="/dashboard" class="btn btn-secondary btn-sm">📊 View Dashboard</a>
                    </div>
                </div>
            `;
        } else {
            resultBox.innerHTML = `<p class="text-danger">Error: ${data.message}</p>`;
        }
    } catch (err) {
        resultBox.innerHTML = `<p class="text-danger">Communication error: ${err.message}</p>`;
    }
}
