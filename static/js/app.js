// PDF Organizer Web Interface - Main JavaScript

let uploadedFiles = [];
let analysisResults = [];
let apiKeySaved = false;  // The server never returns the key itself.

// Initialize on page load
document.addEventListener('DOMContentLoaded', () => {
    initializeApp();
});

function initializeApp() {
    syncThemeButton();
    setupDragDrop();
    setupFileInput();
    loadSettings();
    updateAPIKeyLink();
}

function toggleTheme() {
    const current = document.documentElement.dataset.theme || 'light';
    const next = current === 'dark' ? 'light' : 'dark';
    document.documentElement.dataset.theme = next;
    localStorage.setItem('chwezi-theme', next);
    syncThemeButton();
}

function syncThemeButton() {
    const button = document.getElementById('themeToggle');
    if (!button) return;
    const current = document.documentElement.dataset.theme || 'light';
    const icon = document.createElement('span');
    icon.className = `ui-icon ${current === 'dark' ? 'icon-sun' : 'icon-moon'}`;
    icon.setAttribute('aria-hidden', 'true');
    button.replaceChildren(icon, document.createTextNode(current === 'dark' ? 'Light mode' : 'Dark mode'));
    button.setAttribute('aria-pressed', String(current === 'dark'));
}

function iconMarkup(name) {
    return `<span class="ui-icon icon-${name}" aria-hidden="true"></span>`;
}

function escapeHtml(value) {
    return String(value).replace(/[&<>'"]/g, character => ({
        '&': '&amp;',
        '<': '&lt;',
        '>': '&gt;',
        "'": '&#39;',
        '"': '&quot;'
    })[character]);
}

// Drag & Drop Setup
function setupDragDrop() {
    const dropZone = document.getElementById('dropZone');

    dropZone.addEventListener('click', () => {
        document.getElementById('fileInput').click();
    });

    dropZone.addEventListener('dragover', (e) => {
        e.preventDefault();
        dropZone.classList.add('drag-over');
    });

    dropZone.addEventListener('dragleave', () => {
        dropZone.classList.remove('drag-over');
    });

    dropZone.addEventListener('drop', (e) => {
        e.preventDefault();
        dropZone.classList.remove('drag-over');

        const files = Array.from(e.dataTransfer.files).filter(f =>
            f.name.toLowerCase().endsWith('.pdf')
        );

        if (files.length > 0) {
            handleFiles(files);
        } else {
            showToast('Please drop PDF files only', 'warning');
        }
    });
}

function setupFileInput() {
    const fileInput = document.getElementById('fileInput');
    fileInput.addEventListener('change', (e) => {
        const files = Array.from(e.target.files);
        handleFiles(files);
    });
}

// File Handling
async function handleFiles(files) {
    if (files.length === 0) return;

    showProgress('Uploading files...', `Uploading ${files.length} file(s)`);

    const formData = new FormData();
    files.forEach(file => formData.append('files', file));

    try {
        const response = await fetch('/api/upload', {
            method: 'POST',
            body: formData
        });

        const data = await response.json();

        if (data.success) {
            uploadedFiles = uploadedFiles.concat(data.files);
            updateFileList();
            showToast(`Uploaded ${data.files.length} file(s)`, 'success');
        } else {
            showToast(data.error || 'Upload failed', 'error');
        }
    } catch (error) {
        showToast('Upload error: ' + error.message, 'error');
    } finally {
        hideProgress();
    }
}

function updateFileList() {
    const fileList = document.getElementById('fileList');
    const filesContainer = document.getElementById('files');
    const fileCount = document.getElementById('fileCount');

    if (uploadedFiles.length === 0) {
        fileList.style.display = 'none';
        return;
    }

    fileList.style.display = 'block';
    fileCount.textContent = uploadedFiles.length;

    filesContainer.innerHTML = uploadedFiles.map((file, index) => `
        <div class="file-item">
            <div class="file-info">
                <div class="file-icon">${iconMarkup('file-pdf')}</div>
                <div class="file-details">
                    <h4>${escapeHtml(file.filename)}</h4>
                    <div class="file-size">${formatBytes(file.size)}</div>
                </div>
            </div>
            <div class="file-actions">
                <button class="btn btn-danger" onclick="removeFile(${index})" aria-label="Remove ${escapeHtml(file.filename)}">${iconMarkup('ban')}Remove</button>
            </div>
        </div>
    `).join('');
}

function removeFile(index) {
    uploadedFiles.splice(index, 1);
    updateFileList();
}

function clearFiles() {
    if (confirm('Clear all uploaded files?')) {
        uploadedFiles = [];
        updateFileList();
    }
}

// Analysis
async function analyzeFiles() {
    if (uploadedFiles.length === 0) {
        showToast('No files to analyze', 'warning');
        return;
    }

    // Check settings
    const settings = await getSettings();
    if (!settings.has_api_key || !settings.ebooks_folder) {
        showToast('Please configure settings first', 'warning');
        showSettings();
        return;
    }

    showProgress('Analyzing PDFs...', 'This may take a moment');

    try {
        const response = await fetch('/api/analyze', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ files: uploadedFiles })
        });

        const data = await response.json();

        if (data.success) {
            analysisResults = data.results;
            showResults();
            showToast('Analysis complete!', 'success');
        } else {
            showToast(data.error || 'Analysis failed', 'error');
        }
    } catch (error) {
        showToast('Analysis error: ' + error.message, 'error');
    } finally {
        hideProgress();
    }
}

function showResults() {
    document.getElementById('uploadSection').style.display = 'none';
    document.getElementById('resultsSection').style.display = 'block';

    const resultsContainer = document.getElementById('results');

    resultsContainer.innerHTML = analysisResults.map((result, index) => `
        <div class="result-card ${result.approved ? 'approved' : ''}" id="result-${index}">
            <div class="result-header">
                <div class="result-filename">
                    ${iconMarkup('file-pdf')}${escapeHtml(result.filename)}
                    ${result.is_gibberish ? '<span class="gibberish-badge">Unclear filename</span>' : ''}
                </div>
                <div class="result-actions">
                    <button class="btn btn-success" onclick="approveResult(${index})">${iconMarkup('circle-check')}Approve</button>
                    <button class="btn btn-danger" onclick="rejectResult(${index})">${iconMarkup('ban')}Reject</button>
                </div>
            </div>
            <div class="result-body">
                <div class="result-field">
                    <span class="result-label">${iconMarkup('tag')}Category:</span>
                    <input type="text" class="input result-value" value="${escapeHtml(result.category)}"
                           onchange="updateCategory(${index}, this.value)">
                </div>
                ${result.rename ? `
                    <div class="result-field">
                        <span class="result-label">${iconMarkup('pencil')}Rename to:</span>
                        <input type="text" class="input result-value" value="${escapeHtml(result.rename)}"
                               onchange="updateRename(${index}, this.value)">
                    </div>
                ` : ''}
                <div class="result-field">
                    <span class="result-label">${iconMarkup('gauge')}Confidence:</span>
                    <span class="confidence-badge confidence-${result.confidence}">
                        ${result.confidence.toUpperCase()}
                    </span>
                </div>
            </div>
        </div>
    `).join('');
}

function approveResult(index) {
    analysisResults[index].approved = true;
    document.getElementById(`result-${index}`).classList.add('approved');
    showToast('Approved', 'success');
}

function rejectResult(index) {
    analysisResults[index].approved = false;
    document.getElementById(`result-${index}`).classList.remove('approved');
    document.getElementById(`result-${index}`).classList.add('rejected');
    showToast('Rejected', 'warning');
}

function approveAll() {
    analysisResults.forEach((_, index) => approveResult(index));
}

function rejectAll() {
    analysisResults.forEach((_, index) => rejectResult(index));
}

function updateCategory(index, value) {
    analysisResults[index].category = value;
}

function updateRename(index, value) {
    analysisResults[index].rename = value;
}

// Organize
async function organizeApproved() {
    const approved = analysisResults.filter(r => r.approved);

    if (approved.length === 0) {
        showToast('No files approved', 'warning');
        return;
    }

    if (!confirm(`Organize ${approved.length} approved file(s)?`)) {
        return;
    }

    showProgress('Organizing PDFs...', `Moving ${approved.length} file(s)`);

    try {
        const response = await fetch('/api/organize', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ files: approved })
        });

        const data = await response.json();

        if (data.success) {
            showToast(`Organized ${data.organized.length} file(s)!`, 'success');

            if (data.failed.length > 0) {
                showToast(`${data.failed.length} file(s) failed`, 'error');
            }

            // Reset
            uploadedFiles = [];
            analysisResults = [];
            showUpload();
        } else {
            showToast(data.error || 'Organization failed', 'error');
        }
    } catch (error) {
        showToast('Organization error: ' + error.message, 'error');
    } finally {
        hideProgress();
    }
}

// Settings
async function saveSettings() {
    const settings = {
        ebooks_folder: document.getElementById('ebooksFolder').value,
        provider: document.getElementById('provider').value,
        api_key: document.getElementById('apiKey').value,
        content_analysis: document.getElementById('contentAnalysis').checked
    };

    if (!settings.ebooks_folder || (!settings.api_key && !apiKeySaved)) {
        showToast('Please fill in all required fields', 'warning');
        return;
    }

    try {
        const response = await fetch('/api/settings', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(settings)
        });

        const data = await response.json();

        if (data.success) {
            apiKeySaved = apiKeySaved || Boolean(settings.api_key);
            document.getElementById('apiKey').value = '';
            showToast('Settings saved!', 'success');
            showUpload();
        } else {
            showToast(data.error || 'Failed to save settings', 'error');
        }
    } catch (error) {
        showToast('Error saving settings: ' + error.message, 'error');
    }
}

async function loadSettings() {
    try {
        const response = await fetch('/api/settings');
        const settings = await response.json();

        if (settings.ebooks_folder) {
            document.getElementById('ebooksFolder').value = settings.ebooks_folder;
        }
        if (settings.provider) {
            document.getElementById('provider').value = settings.provider;
        }
        document.getElementById('contentAnalysis').checked = Boolean(settings.content_analysis);
        apiKeySaved = Boolean(settings.has_api_key);
        document.getElementById('apiKey').placeholder = apiKeySaved
            ? 'Key saved - leave blank to keep it'
            : 'Enter your API key';
    } catch (error) {
        console.error('Failed to load settings:', error);
    }
}

async function getSettings() {
    const response = await fetch('/api/settings');
    return await response.json();
}

function updateAPIKeyLink() {
    const provider = document.getElementById('provider').value;
    const link = document.getElementById('apiKeyLink');

    const links = {
        'gemini': 'https://aistudio.google.com/app/apikey',
        'anthropic': 'https://console.anthropic.com/',
        'deepseek': 'https://platform.deepseek.com/'
    };

    link.href = links[provider];
    link.textContent = links[provider];
}

document.getElementById('provider').addEventListener('change', updateAPIKeyLink);

// Navigation
function showUpload() {
    hideAllSections();
    document.getElementById('uploadSection').style.display = 'block';
}

function showSettings() {
    hideAllSections();
    document.getElementById('settingsSection').style.display = 'block';
}

async function showBrowser() {
    hideAllSections();
    document.getElementById('browserSection').style.display = 'block';

    showProgress('Loading library...', '');

    try {
        const response = await fetch('/api/browse');
        const data = await response.json();

        if (data.success) {
            renderLibraryTree(data.tree, data.stats);
        } else {
            showToast(data.error || 'Failed to load library', 'error');
        }
    } catch (error) {
        showToast('Error loading library: ' + error.message, 'error');
    } finally {
        hideProgress();
    }
}

async function showStats() {
    hideAllSections();
    document.getElementById('statsSection').style.display = 'block';

    showProgress('Loading statistics...', '');

    try {
        const response = await fetch('/api/stats');
        const stats = await response.json();

        renderStats(stats);
    } catch (error) {
        showToast('Error loading stats: ' + error.message, 'error');
    } finally {
        hideProgress();
    }
}

function hideAllSections() {
    document.querySelectorAll('.section').forEach(section => {
        section.style.display = 'none';
    });
}

// Render Functions
function renderLibraryTree(tree, stats) {
    const statsBar = document.getElementById('libraryStats');
    statsBar.innerHTML = `
        <div>${iconMarkup('file-pdf')}<strong>Total PDFs:</strong> ${Number(stats.total_pdfs) || 0}</div>
        <div>${iconMarkup('folder-tree')}<strong>Folders:</strong> ${Number(stats.total_folders) || 0}</div>
        <div>${iconMarkup('map-pin')}<strong>Location:</strong> ${escapeHtml(stats.ebooks_folder || '')}</div>
    `;

    const treeContainer = document.getElementById('libraryTree');
    treeContainer.innerHTML = renderTreeItems(tree);
}

function renderTreeItems(items) {
    if (!items || items.length === 0) return `<p>${iconMarkup('folder')}No files found</p>`;

    return items.map(item => {
        if (item.type === 'folder') {
            return `
                <div class="folder-item">
                    ${iconMarkup('folder')} ${escapeHtml(item.name)} (${Number(item.pdf_count) || 0} PDFs)
                    <div class="folder-children">
                        ${renderTreeItems(item.children)}
                    </div>
                </div>
            `;
        } else {
            return `
                <div class="file-item-tree">
                    ${iconMarkup('file-pdf')} ${escapeHtml(item.name)} (${formatBytes(item.size)})
                </div>
            `;
        }
    }).join('');
}

function renderStats(stats) {
    const container = document.getElementById('statsContent');

    const categoryList = Object.entries(stats.categories || {})
        .sort((a, b) => b[1] - a[1])
        .map(([cat, count]) => `<div>${iconMarkup('tag')}<strong>${escapeHtml(cat)}:</strong> ${Number(count) || 0} PDFs</div>`)
        .join('');

    container.innerHTML = `
        <div class="stat-card">
            ${iconMarkup('archive-check')}
            <div class="stat-value">${stats.total_organized}</div>
            <div class="stat-label">Total Organized</div>
        </div>
        <div class="stat-card">
            ${iconMarkup('tags')}
            <div class="stat-value">${Object.keys(stats.categories || {}).length}</div>
            <div class="stat-label">Categories Used</div>
        </div>
        <div class="stat-card">
            ${iconMarkup('calendar-clock')}
            <div class="stat-value">${stats.last_run ? new Date(stats.last_run).toLocaleDateString() : 'Never'}</div>
            <div class="stat-label">Last Run</div>
        </div>
        <div class="section">
            <h3>Category Breakdown</h3>
            ${categoryList || '<p>No data yet</p>'}
        </div>
    `;
}

// UI Helpers
function showProgress(message, detail) {
    document.getElementById('progressMessage').textContent = message;
    document.getElementById('progressDetail').textContent = detail;
    document.getElementById('progressOverlay').style.display = 'flex';
}

function hideProgress() {
    document.getElementById('progressOverlay').style.display = 'none';
}

function showToast(message, type = 'info') {
    const container = document.getElementById('toastContainer');
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    const iconNames = {
        success: 'circle-check',
        error: 'triangle-alert',
        warning: 'triangle-alert',
        info: 'circle-info'
    };
    const icon = document.createElement('span');
    icon.className = `ui-icon icon-${iconNames[type] || iconNames.info}`;
    icon.setAttribute('aria-hidden', 'true');
    toast.append(icon, document.createTextNode(message));

    container.appendChild(toast);

    setTimeout(() => {
        toast.remove();
    }, 3000);
}

function formatBytes(bytes) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i];
}

// ========================================
// PDF SIGNATURE TOOL
// ========================================

let signatureConfig = {
    signatureImage: null,
    signatureImageName: '',
    signatureDimensions: null,
    pages: 'all',
    skipPages: '',
    position: 'bottom-left',
    scale: 0.25,
    xOffset: 0.5,
    yOffset: 0.5,
    opacity: 1.0,
    rotation: 0,
    pdfs: []
};

function showSignature() {
    hideAllSections();
    document.getElementById('signatureSection').style.display = 'block';
    setupSignatureDragDrop();
}

function setupSignatureDragDrop() {
    // Signature image drop zone
    const sigDropZone = document.getElementById('signatureDropZone');
    const sigInput = document.getElementById('signatureInput');

    sigInput.addEventListener('change', (e) => {
        if (e.target.files.length > 0) {
            uploadSignatureImage(e.target.files[0]);
        }
    });

    sigDropZone.addEventListener('dragover', (e) => {
        e.preventDefault();
        sigDropZone.classList.add('drag-over');
    });

    sigDropZone.addEventListener('dragleave', () => {
        sigDropZone.classList.remove('drag-over');
    });

    sigDropZone.addEventListener('drop', (e) => {
        e.preventDefault();
        sigDropZone.classList.remove('drag-over');

        const file = e.dataTransfer.files[0];
        if (file && file.name.toLowerCase().endsWith('.png')) {
            uploadSignatureImage(file);
        } else {
            showToast('Please upload a PNG image', 'warning');
        }
    });

    // PDF drop zone
    const pdfDropZone = document.getElementById('pdfSignDropZone');
    const pdfInput = document.getElementById('pdfSignInput');

    pdfInput.addEventListener('change', (e) => {
        if (e.target.files.length > 0) {
            uploadPdfsForSigning(Array.from(e.target.files));
        }
    });

    pdfDropZone.addEventListener('dragover', (e) => {
        e.preventDefault();
        pdfDropZone.classList.add('drag-over');
    });

    pdfDropZone.addEventListener('dragleave', () => {
        pdfDropZone.classList.remove('drag-over');
    });

    pdfDropZone.addEventListener('drop', (e) => {
        e.preventDefault();
        pdfDropZone.classList.remove('drag-over');

        const files = Array.from(e.dataTransfer.files).filter(f =>
            f.name.toLowerCase().endsWith('.pdf')
        );

        if (files.length > 0) {
            uploadPdfsForSigning(files);
        } else {
            showToast('Please drop PDF files only', 'warning');
        }
    });

    // Page selection handler
    document.getElementById('pagesSelect').addEventListener('change', (e) => {
        const rangeGroup = document.getElementById('pagesRangeGroup');
        if (e.target.value === 'range') {
            rangeGroup.style.display = 'block';
            signatureConfig.pages = document.getElementById('pagesRange').value || '1';
        } else {
            rangeGroup.style.display = 'none';
            signatureConfig.pages = e.target.value;
        }
        renderPreviewCanvas();
    });
}

async function uploadSignatureImage(file) {
    const formData = new FormData();
    formData.append('signature', file);

    try {
        showProgress('Uploading signature...', 'Processing image');

        const response = await fetch('/api/signature/upload-image', {
            method: 'POST',
            body: formData
        });

        const result = await response.json();

        if (result.success) {
            signatureConfig.signatureImageName = result.filename;
            signatureConfig.signatureDimensions = result.dimensions;

            // Show preview
            document.getElementById('signaturePreviewArea').style.display = 'block';
            document.getElementById('signatureFilename').textContent = result.filename;
            document.getElementById('signatureDimensions').textContent =
                `${result.dimensions.width} x ${result.dimensions.height} px`;

            // Show config step
            document.getElementById('signatureConfigStep').style.display = 'block';
            document.getElementById('signaturePdfStep').style.display = 'block';

            // Render preview
            renderPreviewCanvas();

            showToast('Signature uploaded successfully', 'success');
        } else {
            showToast('Error: ' + result.error, 'error');
        }
    } catch (error) {
        showToast('Upload failed: ' + error.message, 'error');
    } finally {
        hideProgress();
    }
}

async function uploadPdfsForSigning(files) {
    const formData = new FormData();
    files.forEach(file => formData.append('files', file));

    try {
        showProgress('Uploading PDFs...', `Uploading ${files.length} files`);

        const response = await fetch('/api/signature/upload-pdfs', {
            method: 'POST',
            body: formData
        });

        const result = await response.json();

        if (result.success) {
            signatureConfig.pdfs = result.files;

            // Update UI
            const pdfList = document.getElementById('signPdfList');
            const pdfFiles = document.getElementById('signPdfFiles');
            const pdfCount = document.getElementById('signPdfCount');

            pdfCount.textContent = result.files.length;
            pdfFiles.innerHTML = result.files.map(file => `
                <div class="file-card">
                    <div class="file-info">
                        ${iconMarkup('file-pdf')}<strong>${escapeHtml(file.filename)}</strong>
                        <small>${formatBytes(file.size)}</small>
                    </div>
                </div>
            `).join('');

            pdfList.style.display = 'block';

            showToast(`${result.files.length} PDFs ready to sign`, 'success');
        } else {
            showToast('Error: ' + result.error, 'error');
        }
    } catch (error) {
        showToast('Upload failed: ' + error.message, 'error');
    } finally {
        hideProgress();
    }
}

function selectPosition(position) {
    signatureConfig.position = position;

    // Update UI
    document.querySelectorAll('.position-btn').forEach(btn => {
        btn.classList.remove('active');
        if (btn.dataset.position === position) {
            btn.classList.add('active');
        }
    });

    renderPreviewCanvas();
}

function updateScale(value) {
    signatureConfig.scale = value / 100.0;
    document.getElementById('scaleValue').textContent = value;
    renderPreviewCanvas();
}

function updateXOffset(value) {
    signatureConfig.xOffset = parseFloat(value);
    document.getElementById('xOffsetValue').textContent = value;
    renderPreviewCanvas();
}

function updateYOffset(value) {
    signatureConfig.yOffset = parseFloat(value);
    document.getElementById('yOffsetValue').textContent = value;
    renderPreviewCanvas();
}

function updateOpacity(value) {
    signatureConfig.opacity = value / 100.0;
    document.getElementById('opacityValue').textContent = value;
    renderPreviewCanvas();
}

function updateRotation(value) {
    signatureConfig.rotation = parseInt(value);
    document.getElementById('rotationValue').textContent = value;
    renderPreviewCanvas();
}

function updateSignatureConfig() {
    const pagesSelect = document.getElementById('pagesSelect').value;
    if (pagesSelect === 'range') {
        signatureConfig.pages = document.getElementById('pagesRange').value || '1';
    } else {
        signatureConfig.pages = pagesSelect;
    }

    // Get skip pages value
    signatureConfig.skipPages = document.getElementById('skipPages').value.trim();

    renderPreviewCanvas();
}

function renderPreviewCanvas() {
    const canvas = document.getElementById('signaturePreviewCanvas');
    if (!canvas) return;

    const ctx = canvas.getContext('2d');
    const a4Ratio = 210 / 297;

    // Clear canvas
    ctx.fillStyle = '#f5f5f5';
    ctx.fillRect(0, 0, canvas.width, canvas.height);

    // Draw A4 portrait page outline
    const pageHeight = canvas.height - 20;
    const pageWidth = pageHeight * a4Ratio;
    const pageX = (canvas.width - pageWidth) / 2;
    const pageY = 10;

    ctx.strokeStyle = '#333';
    ctx.lineWidth = 2;
    ctx.strokeRect(pageX, pageY, pageWidth, pageHeight);

    // Draw page label
    ctx.fillStyle = '#666';
    ctx.font = '12px Arial';
    ctx.fillText('A4 Reference', pageX + 10, pageY + 20);

    // Calculate signature dimensions
    const sigWidth = pageWidth * signatureConfig.scale;
    const aspectRatio = signatureConfig.signatureDimensions
        ? signatureConfig.signatureDimensions.height / signatureConfig.signatureDimensions.width
        : 0.5;
    const sigHeight = sigWidth * aspectRatio;

    // Convert offsets to pixels
    const xOffsetPx = signatureConfig.xOffset * 20; // Rough conversion
    const yOffsetPx = signatureConfig.yOffset * 20;

    // Calculate position
    let x, y;
    if (signatureConfig.position === 'bottom-right') {
        x = pageX + pageWidth - sigWidth - xOffsetPx;
        y = pageY + pageHeight - sigHeight - yOffsetPx;
    } else if (signatureConfig.position === 'bottom-left') {
        x = pageX + xOffsetPx;
        y = pageY + pageHeight - sigHeight - yOffsetPx;
    } else if (signatureConfig.position === 'top-right') {
        x = pageX + pageWidth - sigWidth - xOffsetPx;
        y = pageY + yOffsetPx;
    } else if (signatureConfig.position === 'top-left') {
        x = pageX + xOffsetPx;
        y = pageY + yOffsetPx;
    }

    // Draw signature placeholder with rotation and opacity
    ctx.save();
    ctx.globalAlpha = signatureConfig.opacity;

    // Apply rotation
    if (signatureConfig.rotation !== 0) {
        const centerX = x + sigWidth / 2;
        const centerY = y + sigHeight / 2;
        ctx.translate(centerX, centerY);
        ctx.rotate((signatureConfig.rotation * Math.PI) / 180);
        ctx.translate(-centerX, -centerY);
    }

    ctx.fillStyle = '#4285f4';
    ctx.fillRect(x, y, sigWidth, sigHeight);

    ctx.fillStyle = 'white';
    ctx.font = 'bold 14px "Trebuchet MS"';
    ctx.textAlign = 'center';
    ctx.fillText('Signature', x + sigWidth / 2, y + sigHeight / 2 + 5);

    ctx.restore();
}

async function processSignature() {
    if (!signatureConfig.signatureImageName) {
        showToast('Please upload a signature image first', 'warning');
        return;
    }

    if (signatureConfig.pdfs.length === 0) {
        showToast('Please upload PDFs to sign', 'warning');
        return;
    }

    try {
        showProgress('Signing PDFs...', `Processing ${signatureConfig.pdfs.length} files`);

        const response = await fetch('/api/signature/process', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                files: signatureConfig.pdfs,
                config: {
                    pages: signatureConfig.pages,
                    skipPages: signatureConfig.skipPages,
                    position: signatureConfig.position,
                    scale: signatureConfig.scale,
                    xOffset: signatureConfig.xOffset,
                    yOffset: signatureConfig.yOffset,
                    opacity: signatureConfig.opacity,
                    rotation: signatureConfig.rotation
                }
            })
        });

        const result = await response.json();

        if (result.success) {
            // Show results
            const resultsDiv = document.getElementById('signatureResults');
            const filesList = document.getElementById('signedFilesList');

            filesList.innerHTML = `
                <div class="result-summary">
                    <p><strong>Successfully signed: ${result.signed.length} PDFs</strong></p>
                    ${result.failed.length > 0 ? `<p class="error">Failed: ${result.failed.length} PDFs</p>` : ''}
                </div>
                <div class="signed-files">
                    ${result.signed.map(file => `
                        <div class="file-card">
                            <div class="file-info">
                                ${iconMarkup('file-pdf')}<strong>${escapeHtml(file.filename)}</strong>
                                <small>Pages signed: ${file.pages_signed} / ${file.total_pages}</small>
                            </div>
                            <a href="/api/signature/download/${encodeURIComponent(file.filename)}" class="btn btn-sm btn-primary" download>
                                ${iconMarkup('download')}Download
                            </a>
                        </div>
                    `).join('')}
                    ${result.failed.length > 0 ? `
                        <div class="failed-files">
                            <h4>Failed Files:</h4>
                            ${result.failed.map(file => `
                                <div class="file-card error">
                                    ${iconMarkup('triangle-alert')}<strong>${escapeHtml(file.filename)}</strong>
                                    <small>${escapeHtml(file.error)}</small>
                                </div>
                            `).join('')}
                        </div>
                    ` : ''}
                </div>
            `;

            resultsDiv.style.display = 'block';
            document.getElementById('signaturePdfStep').style.display = 'none';

            showToast(`Successfully signed ${result.signed.length} PDFs`, 'success');
        } else {
            showToast('Error: ' + result.error, 'error');
        }
    } catch (error) {
        showToast('Processing failed: ' + error.message, 'error');
    } finally {
        hideProgress();
    }
}

function clearSignPdfs() {
    signatureConfig.pdfs = [];
    document.getElementById('signPdfList').style.display = 'none';
    document.getElementById('pdfSignInput').value = '';
}

function resetSignature() {
    signatureConfig = {
        signatureImage: null,
        signatureImageName: '',
        signatureDimensions: null,
        pages: 'all',
        position: 'bottom-left',
        scale: 0.25,
        xOffset: 0.5,
        yOffset: 0.5,
        opacity: 1.0,
        rotation: 0,
        pdfs: []
    };

    document.getElementById('signaturePreviewArea').style.display = 'none';
    document.getElementById('signatureConfigStep').style.display = 'none';
    document.getElementById('signaturePdfStep').style.display = 'none';
    document.getElementById('signatureResults').style.display = 'none';
    document.getElementById('signPdfList').style.display = 'none';

    document.getElementById('signatureInput').value = '';
    document.getElementById('pdfSignInput').value = '';

    // Reset sliders
    document.getElementById('scaleSlider').value = 25;
    document.getElementById('xOffsetSlider').value = 0.5;
    document.getElementById('yOffsetSlider').value = 0.5;
    document.getElementById('opacitySlider').value = 100;
    document.getElementById('rotationSlider').value = 0;

    updateScale(25);
    updateXOffset(0.5);
    updateYOffset(0.5);
    updateOpacity(100);
    updateRotation(0);
}
