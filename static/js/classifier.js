document.addEventListener('DOMContentLoaded', () => {
    initUploadControls();
    loadDetectionHistory();
});

let selectedFile = null;

function initUploadControls() {
    const dropZone = document.getElementById('dropZone');
    const imageInput = document.getElementById('imageInput');

    dropZone.addEventListener('click', () => imageInput.click());

    imageInput.addEventListener('change', (e) => {
        if (e.target.files.length > 0) {
            handleFileSelected(e.target.files[0]);
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
            handleFileSelected(e.dataTransfer.files[0]);
        }
    });
}

function handleFileSelected(file) {
    if (!file.type.startsWith('image/')) {
        alert('Please select a valid image file (PNG, JPG, WEBP).');
        return;
    }

    selectedFile = file;
    const reader = new FileReader();
    reader.onload = (e) => {
        const preview = document.getElementById('imagePreview');
        const prompt = document.querySelector('.drop-zone-prompt');
        preview.src = e.target.result;
        preview.classList.remove('hidden');
        prompt.classList.add('hidden');
        document.getElementById('classifyBtn').disabled = false;
    };
    reader.readAsDataURL(file);
}

function resetForm() {
    selectedFile = null;
    document.getElementById('imageInput').value = '';
    document.getElementById('imagePreview').classList.add('hidden');
    document.querySelector('.drop-zone-prompt').classList.remove('hidden');
    document.getElementById('classifyBtn').disabled = true;
    
    document.getElementById('placeholderState').classList.remove('hidden');
    document.getElementById('loadingState').classList.add('hidden');
    document.getElementById('resultContent').classList.add('hidden');
}

async function processClassification() {
    if (!selectedFile) return;

    const loadingState = document.getElementById('loadingState');
    const placeholderState = document.getElementById('placeholderState');
    const resultContent = document.getElementById('resultContent');
    const classifyBtn = document.getElementById('classifyBtn');

    placeholderState.classList.add('hidden');
    resultContent.classList.add('hidden');
    loadingState.classList.remove('hidden');
    classifyBtn.disabled = true;

    const formData = new FormData();
    formData.append('image', selectedFile);

    try {
        const response = await fetch('/api/classify', {
            method: 'POST',
            body: formData
        });

        const data = await response.json();

        loadingState.classList.add('hidden');
        classifyBtn.disabled = false;

        if (data.success) {
            renderResults(data);
            loadDetectionHistory(); // Refresh DB history table
        } else {
            alert('Classification error: ' + (data.message || 'Unknown error'));
            placeholderState.classList.remove('hidden');
        }
    } catch (err) {
        loadingState.classList.add('hidden');
        classifyBtn.disabled = false;
        alert('Server communication error: ' + err.message);
        placeholderState.classList.remove('hidden');
    }
}

function renderResults(data) {
    document.getElementById('resultContent').classList.remove('hidden');

    document.getElementById('resCategory').textContent = data.category_name;
    document.getElementById('resConfidence').textContent = data.confidence_percent;
    document.getElementById('resWasteType').textContent = `Waste Type: ${data.waste_type}`;
    document.getElementById('resSuggestion').textContent = data.disposal_suggestion;

    const binBadge = document.getElementById('binBadge');
    const binColorText = document.getElementById('binColorText');

    binBadge.textContent = `${data.recommended_bin_color} Bin`;
    binColorText.textContent = `Recommended Bin: ${data.recommended_bin_color} Bin`;

    if (data.recommended_bin_color === 'Green') {
        binBadge.className = 'bin-badge bin-green';
    } else if (data.recommended_bin_color === 'Blue') {
        binBadge.className = 'bin-badge bin-blue';
    } else {
        binBadge.className = 'bin-badge bin-black';
    }

    const imgRef = document.getElementById('resImageRef');
    imgRef.href = data.image_url;
    imgRef.textContent = data.image_url.split('/').pop();

    document.getElementById('resUserId').textContent = data.user_id ? `User #${data.user_id}` : 'Guest User (Null)';
    document.getElementById('dbStatusBadge').textContent = `Stored in DB (Record #${data.detection_id})`;
}

async function loadDetectionHistory() {
    const tbody = document.getElementById('historyTableBody');
    try {
        const response = await fetch('/api/detections');
        const data = await response.json();

        if (data.success && data.detections.length > 0) {
            tbody.innerHTML = data.detections.map(r => `
                <tr>
                    <td>#${r.id}</td>
                    <td><img src="${r.image_path}" class="thumb-img" alt="scan"></td>
                    <td><strong>${r.category_name}</strong></td>
                    <td><span class="type-tag">${r.waste_type}</span></td>
                    <td><span class="badge-${r.bin_color.toLowerCase()}">${r.bin_color} Bin</span></td>
                    <td>${(r.confidence_score * 100).toFixed(1)}%</td>
                    <td class="text-sm-suggestion">${r.disposal_suggestion}</td>
                    <td>${r.user_id ? `User #${r.user_id}` : 'Guest'}</td>
                    <td>${r.detected_at}</td>
                </tr>
            `).join('');
        } else {
            tbody.innerHTML = `<tr><td colspan="9" class="text-center">No detection records stored yet.</td></tr>`;
        }
    } catch (err) {
        tbody.innerHTML = `<tr><td colspan="9" class="text-center text-danger">Error loading history: ${err.message}</td></tr>`;
    }
}
