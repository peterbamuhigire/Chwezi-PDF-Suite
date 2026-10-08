#!/usr/bin/env python3
"""
PDF Organizer - Web Interface
Modern web UI for PDF organization with drag & drop
"""

import contextlib
import json
import os
import secrets
import threading
import time
import uuid
import webbrowser
from io import BytesIO
from pathlib import Path
from urllib.parse import urlsplit

from flask import Flask, jsonify, render_template, request, send_from_directory, session
from werkzeug.utils import secure_filename

from organize_batch import BatchPDFOrganizer
from pdf_signature import PDFSignature

app = Flask(__name__)
app.secret_key = os.urandom(24)
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024  # 100MB max file size
app.config['UPLOAD_FOLDER'] = Path.home() / 'pdf_organizer_uploads'
app.config['UPLOAD_FOLDER'].mkdir(exist_ok=True)
app.config['SESSION_COOKIE_SAMESITE'] = 'Strict'

# Server-side state per browser session. API keys and file paths never reach the browser;
# the browser only ever holds opaque upload ids.
_server_state = {}
_state_lock = threading.Lock()
SESSION_IDLE_SECONDS = 12 * 60 * 60


def _evict_idle_sessions(now):
    """Forget idle sessions (and their keys) and delete uploads they never organised. Lock held."""
    for sid in [
        s for s, st in _server_state.items() if now - st['last_seen'] > SESSION_IDLE_SECONDS
    ]:
        stale = _server_state.pop(sid)
        for filepath in [*stale['uploads'].values(), *stale['sign_uploads'].values()]:
            with contextlib.suppress(OSError):  # a locked file must not fail another user's request
                filepath.unlink(missing_ok=True)


def _state():
    now = time.monotonic()
    with _state_lock:
        _evict_idle_sessions(now)
        sid = session.get('sid')
        if sid not in _server_state:
            sid = secrets.token_urlsafe(32)
            session['sid'] = sid
            _server_state[sid] = {'api_key': '', 'uploads': {}, 'sign_uploads': {}}
        _server_state[sid]['last_seen'] = now
        return _server_state[sid]


def _register_upload(registry, folder, file):
    name = secure_filename(file.filename or '')
    if not name.lower().endswith('.pdf'):
        name = 'document.pdf'
    file_id = uuid.uuid4().hex
    filepath = folder / f"{file_id}_{name}"
    file.save(filepath)
    registry[file_id] = filepath
    return {'id': file_id, 'filename': name, 'size': filepath.stat().st_size}


def _resolve_upload(registry, file_info):
    """Map a client-supplied upload id to a server-held path; client paths are ignored."""
    file_id = file_info.get('id') if isinstance(file_info, dict) else None
    filepath = registry.get(str(file_id))
    return filepath if filepath is not None and filepath.exists() else None


def _display_name(filepath):
    return filepath.name.split('_', 1)[-1]


LOCAL_HOSTNAMES = {'localhost', '127.0.0.1', '::1'}


@app.before_request
def reject_cross_origin_writes():
    """Stop other websites from driving this localhost API from the user's browser."""
    # A Host allowlist defeats DNS rebinding, where Origin and Host would otherwise match.
    if urlsplit(f"//{request.host}").hostname not in LOCAL_HOSTNAMES:
        return jsonify({'error': 'Unexpected Host header'}), 403
    if request.method in ('GET', 'HEAD', 'OPTIONS'):
        return None
    source = request.headers.get('Origin') or request.headers.get('Referer')
    if source and urlsplit(source).netloc != request.host:
        return jsonify({'error': 'Cross-origin request rejected'}), 403
    return None


@app.route('/')
def index():
    """Main page"""
    return render_template('index.html')


@app.route('/api/settings', methods=['GET', 'POST'])
def settings():
    """Get or update settings"""
    state = _state()
    if request.method == 'POST':
        data = request.get_json(silent=True) or {}
        session['ebooks_folder'] = data.get('ebooks_folder')
        session['provider'] = data.get('provider', 'gemini')
        session['batch_delay'] = data.get('batch_delay', 10)
        session['content_analysis'] = data.get('content_analysis') is True
        api_key = str(data.get('api_key') or '').strip()
        if api_key:
            state['api_key'] = api_key

        return jsonify({'success': True, 'message': 'Settings saved'})

    return jsonify({
        'ebooks_folder': session.get('ebooks_folder', ''),
        'provider': session.get('provider', 'gemini'),
        'has_api_key': bool(state['api_key']),
        'content_analysis': session.get('content_analysis', False),
        'batch_delay': session.get('batch_delay', 10)
    })


@app.route('/api/upload', methods=['POST'])
def upload_pdf():
    """Handle PDF upload"""
    if 'files' not in request.files:
        return jsonify({'error': 'No files provided'}), 400

    files = request.files.getlist('files')
    uploads = _state()['uploads']
    uploaded = []

    for file in files:
        if file and file.filename.lower().endswith('.pdf'):
            uploaded.append(_register_upload(uploads, app.config['UPLOAD_FOLDER'], file))

    return jsonify({
        'success': True,
        'files': uploaded
    })


@app.route('/api/analyze', methods=['POST'])
def analyze_pdfs():
    """Analyze uploaded PDFs and suggest categorization"""
    data = request.get_json(silent=True) or {}
    file_infos = data.get('files', [])
    state = _state()

    if not state['api_key']:
        return jsonify({'error': 'API key not configured'}), 400

    if not session.get('ebooks_folder'):
        return jsonify({'error': 'Ebooks folder not configured'}), 400

    try:
        # Create temporary organizer
        organizer = BatchPDFOrganizer(
            downloads_folder=app.config['UPLOAD_FOLDER'],
            ebooks_folder=session.get('ebooks_folder'),
            api_key=state['api_key'],
            provider=session.get('provider', 'gemini'),
            use_content_analysis=session.get('content_analysis', False)
        )

        # Get PDF info
        pdf_list = []
        for file_info in file_infos:
            pdf_path = _resolve_upload(state['uploads'], file_info)
            if pdf_path is not None:
                info = organizer.get_pdf_info(pdf_path)
                info['id'] = file_info['id']
                info['filename'] = _display_name(pdf_path)
                pdf_list.append(info)

        # Load categories
        categories = organizer.load_or_analyze_categories()

        # Batch categorize
        categorizations = organizer.batch_categorize_all(pdf_list, categories)

        # Match results
        results = []
        categorization_map = {cat['number']: cat for cat in categorizations}

        for i, pdf_info in enumerate(pdf_list, 1):
            cat_result = categorization_map.get(i, {
                'category': 'Uncategorized',
                'confidence': 'low',
                'rename': None
            })

            results.append({
                'id': pdf_info['id'],
                'filename': pdf_info['filename'],
                'category': cat_result.get('category', 'Uncategorized'),
                'confidence': cat_result.get('confidence', 'low'),
                'rename': cat_result.get('rename'),
                'is_gibberish': pdf_info.get('is_gibberish', False),
                'has_content': pdf_info.get('has_content', False),
                'approved': False  # User needs to approve
            })

        organizer.cleanup()

        return jsonify({
            'success': True,
            'results': results
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/organize', methods=['POST'])
def organize_pdfs():
    """Organize approved PDFs"""
    data = request.get_json(silent=True) or {}
    approved_files = data.get('files', [])
    state = _state()

    if not state['api_key']:
        return jsonify({'error': 'API key not configured'}), 400

    try:
        organizer = BatchPDFOrganizer(
            downloads_folder=app.config['UPLOAD_FOLDER'],
            ebooks_folder=session.get('ebooks_folder'),
            api_key=state['api_key'],
            provider=session.get('provider', 'gemini')
        )

        organized = []
        failed = []

        for file_info in approved_files:
            source = _resolve_upload(state['uploads'], file_info)
            if source is None:
                name = file_info.get('filename', '') if isinstance(file_info, dict) else ''
                failed.append({'filename': str(name), 'error': 'Upload not found'})
                continue
            filename = _display_name(source)
            try:
                result = {
                    'source': str(source),
                    'filename': filename,
                    'category': file_info.get('category'),
                    'rename_to': file_info.get('rename')
                }

                destination = organizer.move_pdf(result)
                organizer.log['organized_files'].append({**result, 'destination': str(destination)})
                organized.append(filename)
                state['uploads'].pop(file_info['id'], None)

            except Exception as e:
                failed.append({
                    'filename': filename,
                    'error': str(e)
                })

        organizer.save_log()
        organizer.cleanup()

        return jsonify({
            'success': True,
            'organized': organized,
            'failed': failed
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/browse')
def browse_library():
    """Browse organized PDF library"""
    ebooks_folder = session.get('ebooks_folder')

    if not ebooks_folder or not Path(ebooks_folder).exists():
        return jsonify({'error': 'Ebooks folder not configured or does not exist'}), 400

    ebooks_path = Path(ebooks_folder)

    # Build file tree
    def build_tree(path, max_depth=3, current_depth=0):
        if current_depth >= max_depth:
            return None

        items = []
        try:
            for item in sorted(path.iterdir()):
                if item.is_dir():
                    children = build_tree(item, max_depth, current_depth + 1)
                    pdf_count = len(list(item.rglob('*.pdf')))
                    items.append({
                        'name': item.name,
                        'type': 'folder',
                        'path': str(item.relative_to(ebooks_path)),
                        'pdf_count': pdf_count,
                        'children': children or []
                    })
                elif item.suffix.lower() == '.pdf':
                    items.append({
                        'name': item.name,
                        'type': 'file',
                        'path': str(item.relative_to(ebooks_path)),
                        'size': item.stat().st_size
                    })
        except PermissionError:
            pass

        return items

    tree = build_tree(ebooks_path)

    # Get statistics
    total_pdfs = len(list(ebooks_path.rglob('*.pdf')))
    total_folders = len([d for d in ebooks_path.rglob('*') if d.is_dir()])

    return jsonify({
        'success': True,
        'tree': tree,
        'stats': {
            'total_pdfs': total_pdfs,
            'total_folders': total_folders,
            'ebooks_folder': str(ebooks_path)
        }
    })


@app.route('/api/stats')
def get_stats():
    """Get organization statistics"""
    ebooks_folder = session.get('ebooks_folder')

    if not ebooks_folder:
        return jsonify({'error': 'Ebooks folder not configured'}), 400

    ebooks_path = Path(ebooks_folder)
    log_file = ebooks_path / 'organization_log.json'

    if not log_file.exists():
        return jsonify({
            'total_organized': 0,
            'last_run': None,
            'categories': {}
        })

    with open(log_file, encoding='utf-8') as f:
        log = json.load(f)

    # Count by category
    category_counts = {}
    for item in log.get('organized_files', []):
        cat = item.get('category', 'Uncategorized')
        category_counts[cat] = category_counts.get(cat, 0) + 1

    return jsonify({
        'total_organized': len(log.get('organized_files', [])),
        'last_run': log.get('last_run'),
        'categories': category_counts
    })


@app.route('/api/categories')
def get_categories():
    """Get available categories"""
    ebooks_folder = session.get('ebooks_folder')

    if not ebooks_folder:
        return jsonify([])

    try:
        organizer = BatchPDFOrganizer(
            downloads_folder=app.config['UPLOAD_FOLDER'],
            ebooks_folder=ebooks_folder,
            api_key='dummy',  # Not needed for category analysis
            provider='gemini'
        )

        categories = organizer.load_or_analyze_categories()

        category_list = [
            {
                'path': path,
                'count': info['count'],
                'depth': info['depth']
            }
            for path, info in sorted(categories.items())
        ]

        organizer.cleanup()

        return jsonify(category_list)

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/signature/upload-image', methods=['POST'])
def upload_signature_image():
    """Upload signature PNG image"""
    if 'signature' not in request.files:
        return jsonify({'error': 'No signature file provided'}), 400

    file = request.files['signature']

    if not file or not file.filename.lower().endswith('.png'):
        return jsonify({'error': 'File must be PNG format'}), 400

    try:
        from PIL import Image

        # Read file data once
        file_data = file.stream.read()

        # Validate it's a readable PNG
        img = Image.open(BytesIO(file_data))
        if img.format != 'PNG':
            return jsonify({'error': 'File must be PNG format'}), 400

        width, height = img.size
        img.close()

        # Save to uploads folder
        filename = secure_filename(file.filename)
        sig_folder = app.config['UPLOAD_FOLDER'] / 'signatures'
        sig_folder.mkdir(exist_ok=True)

        filepath = sig_folder / filename

        # Write file data
        with open(filepath, 'wb') as f:
            f.write(file_data)

        # Store in session
        session['signature_path'] = str(filepath)
        session['signature_filename'] = filename

        return jsonify({
            'success': True,
            'filename': filename,
            'dimensions': {'width': width, 'height': height}
        })

    except Exception as e:
        return jsonify({'error': f'Failed to process signature: {e!s}'}), 500


@app.route('/api/signature/upload-pdfs', methods=['POST'])
def upload_pdfs_for_signing():
    """Upload PDFs to be signed"""
    if 'files' not in request.files:
        return jsonify({'error': 'No files provided'}), 400

    files = request.files.getlist('files')
    sign_uploads = _state()['sign_uploads']
    pdf_folder = app.config['UPLOAD_FOLDER'] / 'sign_pdfs'
    pdf_folder.mkdir(exist_ok=True)
    uploaded = []

    for file in files:
        if file and file.filename.lower().endswith('.pdf'):
            uploaded.append(_register_upload(sign_uploads, pdf_folder, file))

    return jsonify({
        'success': True,
        'files': uploaded
    })


@app.route('/api/signature/process', methods=['POST'])
def process_signature():
    """Sign PDFs with configured signature"""
    data = request.get_json(silent=True) or {}
    sign_uploads = _state()['sign_uploads']

    signature_path = session.get('signature_path')
    if not signature_path or not Path(signature_path).exists():
        return jsonify({'error': 'Signature image not uploaded'}), 400

    pdf_files = data.get('files', [])
    if not pdf_files:
        return jsonify({'error': 'No PDF files to sign'}), 400

    # Get configuration
    config = data.get('config', {})
    position = config.get('position', 'bottom-right')
    scale = config.get('scale', 0.25)
    x_offset = config.get('xOffset', 0.5)
    y_offset = config.get('yOffset', 0.5)
    opacity = config.get('opacity', 1.0)
    rotation = config.get('rotation', 0)
    pages = config.get('pages', 'all')
    skip_pages = config.get('skipPages', '')

    try:
        # Create signer
        signer = PDFSignature(
            signature_image_path=signature_path,
            position=position,
            scale=scale,
            x_offset=x_offset,
            y_offset=y_offset,
            opacity=opacity,
            rotation=rotation,
            pages=pages,
            skip_pages=skip_pages
        )

        # Create output folder
        signed_folder = app.config['UPLOAD_FOLDER'] / 'signed'
        signed_folder.mkdir(exist_ok=True)

        signed_files = []
        failed_files = []

        # Process each PDF
        for pdf_info in pdf_files:
            pdf_path = _resolve_upload(sign_uploads, pdf_info)
            if pdf_path is None:
                failed_files.append({
                    'filename': (
                        str(pdf_info.get('filename', '')) if isinstance(pdf_info, dict) else ''
                    ),
                    'error': 'File not found'
                })
                continue
            pdf_info = {'filename': _display_name(pdf_path)}

            try:
                # Output path
                output_filename = f"{Path(pdf_info['filename']).stem}_signed.pdf"
                output_path = signed_folder / output_filename

                # Sign PDF
                result = signer.add_signature_to_pdf(str(pdf_path), str(output_path))

                if result['success']:
                    signed_files.append({
                        'filename': output_filename,
                        'total_pages': result['total_pages'],
                        'pages_signed': result['pages_signed']
                    })
                else:
                    failed_files.append({
                        'filename': pdf_info['filename'],
                        'error': result['error']
                    })

            except Exception as e:
                failed_files.append({
                    'filename': pdf_info['filename'],
                    'error': str(e)
                })

        return jsonify({
            'success': True,
            'signed': signed_files,
            'failed': failed_files
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/signature/download/<filename>')
def download_signed_pdf(filename):
    """Download signed PDF"""
    signed_folder = app.config['UPLOAD_FOLDER'] / 'signed'
    return send_from_directory(signed_folder, filename, as_attachment=True)


def open_browser():
    """Open browser after a short delay to ensure server is ready"""
    import time
    time.sleep(1.5)  # Wait for server to start
    webbrowser.open('http://localhost:5000')


def main():
    """Run the web interface"""
    print("="*70)
    print("  PDF Organizer - Web Interface")
    print("="*70)
    print()
    print("Starting web server...")
    print()
    print("Your browser will open automatically to:")
    print("  -> http://localhost:5000")
    print()
    print("Press Ctrl+C to stop the server")
    print("="*70)
    print()

    # Open browser in a separate thread
    threading.Thread(target=open_browser, daemon=True).start()

    # Run Flask app
    # This adapter is intentionally local-only. It has no remote authentication boundary.
    app.run(debug=False, host='127.0.0.1', port=5000, use_reloader=False)


if __name__ == '__main__':
    main()
