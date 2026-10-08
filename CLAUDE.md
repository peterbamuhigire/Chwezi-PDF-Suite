# CLAUDE.md

AI coding assistant guidance for the Chwezi Document Suite (repository: Chwezi-PDF-Suite; formerly pyPDFLibrarianSort).

## Project Overview

**AI-powered PDF library organizer** with three AI provider options (Gemini, Anthropic, DeepSeek), featuring batch processing for 98% cost savings, automated watch mode, modern web interface, and intelligent content analysis.

**Key Innovation**: Batch processing - up to 150 PDFs per API call (`DEFAULT_CHUNK_SIZE`) instead of one call per PDF; actual cost depends on the provider's per-token pricing.

## Documentation Structure

**Follow the documentation organization rule:**
All detailed documentation lives in `docs/` with semantic subdirectories. Root README.md is a landing page that points to docs/.

```
docs/
├── guides/          # User guides (setup, usage)
├── features/        # Feature documentation
├── overview/        # Project summaries
└── reference/       # Technical reference
```

## Available Skills

The `skills/` directory contains reusable development skills for Claude Code:

- **`update-claude-documentation/`** - Systematic documentation update workflow
- **`skill-writing/`** (skill-creator) - Guide for creating effective skills
- **`doc-architect/`** - Generate Triple-Layer AGENTS.md documentation

**When to use skills:**
- Reference skills explicitly when needed: "Using update-claude-documentation, update all docs"
- Skills loaded only when mentioned (saves tokens)
- See `skills/CLAUDE.md` and `skills/README.md` for complete skill documentation

## Core Architecture

### Four Processing Modes

**1. Web Interface (`web_interface.py`)** - Recommended for most users
- Modern Flask-based web UI with drag & drop
- Real-time categorization preview
- Visual approval/rejection workflow
- Browse organized library
- PDF signature tool integrated
- Runs on http://localhost:5000

**2. PDF Signature (`pdf_signature.py`)** - No AI credits required
- Add PNG signatures to PDFs
- 4 corner positions, adjustable size and margins
- Page selection (all, first, last, odd, even, ranges)
- Opacity control (10-100%)
- Rotation (0-360 degrees)
- Batch processing support
- Web interface + CLI tools
- Pure PDF manipulation, no API calls

**3. Watch Mode (`watch_organizer.py`)** - Set and forget
- Monitors Downloads folder 24/7
- Auto-organizes PDFs as they arrive
- Smart batching (groups PDFs within delay window)
- Background operation with statistics tracking

**4. Organizer (`organize_batch.py`)** - Canonical organizer
- Single organizer implementation for GUI and CLI
- Batch categorization with low-cost bulk processing
- Automatic chunking for large libraries

### Key Components

**Main Classes:**

- `BatchPDFOrganizer` (organize_batch.py) - Canonical organizer backend

**Interactive Launchers:**

- `web_interface.py` - Modern web UI with drag & drop (RECOMMENDED)
- `sign_setup.py` - Interactive PDF signature setup (no AI credits)
- `watch_setup.py` - Interactive setup for watch mode (auto-organize)
- `organize_batch.py` - Canonical organizer entrypoint with GUI and CLI

**Core Processing Engines:**

- `PDFSignature` (pdf_signature.py) - PDF signature placement engine (no AI)
- `BatchPDFOrganizer` (organize_batch.py) - Canonical organizer backend
- `PDFWatcher` (watch_organizer.py) - File system monitoring for auto-organization
- Flask app (web_interface.py) - Web interface with RESTful API

**Category System:**

- `category_template.json` - Pre-generated hierarchical category structure
- `fetch-categories.py` - Generates category template from existing ebooks folder
- Both organizers analyze existing folder structure and preserve deep hierarchies (up to 3+ levels)

**Content Analysis:**

- `pdf_content_analyzer.py` - Detects gibberish filenames, extracts PDF content
- `PDFContentAnalyzer` class - Analyzes first 3 pages for better categorization

**Support Tools:**

- `test_basic.py` - Interactive API smoke check (prompts for provider and key)
- `test_signature.py` - PDF signature unit tests
- `setup.py` - Setup wizard
- `fetch-categories.py` - Category template generator
- `pdf_signature.py` - Canonical PDF signing tool

**Templates & Static Files:**

- `templates/` - HTML templates for web interface
  - `index.html` - Main template with signature section
- `static/` - CSS, JavaScript for web UI
  - `static/css/style.css` - Includes signature tool styling
  - `static/js/app.js` - Includes signature tool JavaScript

### Data Flow

1. **Discovery**: Recursively find PDFs in Downloads folder
2. **Content Analysis**:
   - Extract PDF metadata (title, author, subject)
   - Detect gibberish filenames (PDFContentAnalyzer)
   - Read first 3 pages of content for gibberish files
3. **Structure Analysis**: Scan existing ebooks folder hierarchy OR load category_template.json
4. **AI Categorization**:
   - Send batch of filenames + metadata + content previews + category structure
   - Supports Gemini, Anthropic, or DeepSeek
   - Returns JSON with category paths and suggested filenames
5. **Response Parsing**: Parse JSON, validate categories
6. **User Review** (web interface): Preview and approve/reject suggestions
7. **File Operations**: Move PDFs to appropriate folders with smart renaming
8. **Logging**: Record all operations in organization_log.json

### Category Template System

The organizers can use a pre-generated category template (`category_template.json`) to avoid scanning large ebooks folders every time:

```json
{
  "generated_at": "2026-01-11T10:00:00",
  "ebooks_root": "F:/ebooks",
  "category_count": 47,
  "categories": [
    {"path": "Computer & ICT/Programming/Python", "depth": 3, "count": 34},
    {"path": "Business/Finance", "depth": 2, "count": 45}
  ]
}
```

To generate from an existing ebooks folder:

```bash
cd /path/to/ebooks
python /path/to/Chwezi-PDF-Suite/fetch-categories.py
```

`BatchPDFOrganizer` supports the `category_template` parameter.

### Smart Content Analysis

The system includes intelligent gibberish filename detection:

**Detection Criteria** (2+ triggers = gibberish):
- Too short (< 5 characters)
- Mostly numbers (> 60% digits)
- All numbers
- Random case mixing
- Temp file patterns (temp*, tmp*, download*)
- No vowels

**When gibberish detected:**
1. Extract PDF metadata (title, author)
2. Read first 3 pages of content
3. Send content preview to AI (max 1000 chars for batch mode)
4. AI suggests better filename based on content

**Example:**
```
Input: SAJSABC4345.pdf
Metadata: "A Study of Eastern Rabbits"
Content: "This research paper examines behavioral patterns..."
→ Output: Science/Biology/Zoology/A Study of Eastern Rabbits.pdf
```

## Common Commands

### Development

```bash
# Install dependencies
pip install -r requirements.txt

# Run the automated test suite (tests/ directory, from repo root)
python -m pytest

# Interactive API smoke check (prompts for provider/key)
python test_basic.py

# System diagnostics
python diagnose.py

# Setup wizard
python setup.py
```

### Usage

```bash
# Suite launcher
python index-app.py

# Web interface (recommended, then open http://localhost:5000)
python web_interface.py

# Batch mode (one-time organization; GUI / CLI)
python organize_batch.py
# Direct invocation
python organize_batch.py --downloads /path/to/downloads --ebooks /path/to/ebooks --api-key <key>

# Watch mode (continuous auto-organization)
python watch_setup.py
# Or directly:
python watch_organizer.py --ebooks F:/ebooks --provider gemini --api-key YOUR_KEY
```

### Windows desktop suite

The canonical package definition is `packaging/desktop-suite.toml`. Regenerate checked-in build
files after changing it, then build only from the lock file:

```powershell
python C:\wamp64\www\chwezi-dev-engine\skills\languages\python-modern-standards\scripts\desktop_suite_packager.py generate --config packaging\desktop-suite.toml
.\scripts\build-desktop-suite.ps1 -UnsignedDevelopmentBuild -SkipInstaller
```

The frozen launcher opens sibling executables; source mode opens sibling Python scripts. Public
builds must omit `-UnsignedDevelopmentBuild` and satisfy the licence, Authenticode, and Inno Setup
gates described in `docs/guides/DESKTOP_DISTRIBUTION.md`.

### Generate category template

```bash
# From your ebooks folder
cd F:/ebooks
python C:/path/to/Chwezi-PDF-Suite/fetch-categories.py
# Creates category_template.json in current directory

# Copy to project root for use by organizers
copy category_template.json C:/path/to/Chwezi-PDF-Suite/
```

## Important Implementation Details

### API Key Management

- Supports three AI providers: Gemini, Anthropic (Claude), and DeepSeek
- Interactive launchers prompt for provider selection and corresponding API key
- Can be passed as parameter: `BatchPDFOrganizer(downloads, ebooks, api_key="...", provider="gemini")`
- Can optionally be stored in `~/.pdf_organizer_settings.json` (by setup.py)
- The web interface never returns the stored key to the browser.
- Default models: gemini -> `gemini-3.8-flash`, anthropic -> `claude-haiku-5-5`, deepseek -> `deepseek-flash`; override with the `model_name` parameter.
- Provider-specific API key URLs:
  - Gemini: https://aistudio.google.com/app/apikey
  - Anthropic: https://console.anthropic.com/
  - DeepSeek: https://platform.deepseek.com/

### File Operations

- All operations are local - PDFs never uploaded to API
- Only filenames and metadata sent to AI provider (Gemini, Anthropic, or DeepSeek)
- Uses `shutil.move()` for file operations
- Maintains `organization_log.json` in ebooks folder for tracking
- Dry-run mode available: `BatchPDFOrganizer(..., dry_run=True)`

### Category Hierarchy

- Preserves multi-level folder structures (e.g., "Computer & ICT/Programming/Python")
- AI receives complete existing structure to maintain consistency
- Creates new categories when appropriate
- Falls back to "Uncategorized" for unclear PDFs

### Error Handling

- PDFs that fail to read skip gracefully
- API errors reported but don't stop batch processing
- Validation ensures required folders exist before processing
- Comprehensive error messages for common issues

## Testing

```bash
# Automated suite (tests/ directory, run from repo root)
python -m pytest

# Interactive API smoke check (prompts for provider and key)
python test_basic.py

# Test with dry-run (no files moved)
python -c "from organize_batch import BatchPDFOrganizer; o = BatchPDFOrganizer('downloads', 'ebooks', api_key='key', dry_run=True); o.organize_pdfs()"
```

## Dependencies

`pyproject.toml` is the canonical dependency definition (core dependencies plus extras such as `ai`, `sign`, `watch`, `extract`, `suite`). `requirements.txt` is the legacy flat list used by the standalone apps:

- `customtkinter>=5.2.0` - desktop GUI
- `anthropic>=0.36.0` - Anthropic (Claude) client
- `google-genai>=1.73.1` - Gemini client
- `pypdf>=6.13.3,<7` - PDF metadata extraction
- `openai>=1.0.0` - OpenAI-compatible client (DeepSeek)
- `watchdog>=3.0.0` - file system monitoring (watch mode)
- `flask>=3.0.0`, `flask-cors>=4.0.0` - web interface
- `pillow>=12.3,<13`, `reportlab>=4.0.0` - PDF signature tool
- `python-pptx>=1.0.2`, `pdfplumber>=0.11.0` - document extraction

## Documentation Maintenance

**When making significant changes**, use the `update-claude-documentation` skill to systematically update all docs:

```
Using update-claude-documentation skill, update all documentation for [change description]
```

**Documentation files to update:**
- `PROJECT_BRIEF.md` - 30-second overview (update for major features)
- `README.md` - Landing page (keep concise, point to docs/)
- `CLAUDE.md` - This file (update for architecture/pattern changes)
- `docs/guides/` - User guides (update for feature changes)
- `docs/features/FEATURES_SUMMARY.md` - Feature list
- `docs/reference/` - Technical references

**Documentation organization principle:**
- Root README.md = Landing page with links
- Detailed docs = `docs/` subdirectories
- AI guidance = `CLAUDE.md`
- Skills = `skills/` directory

## Working with Skills

The `skills/` directory contains development skills for Claude Code. To use them:

**Available skills:**
- `update-claude-documentation` - Systematic doc updates
- `skill-writing` - Creating new skills
- `doc-architect` - Generate AGENTS.md files

**Usage pattern:**
```
Using [skill-name], [task description]
```

See `skills/README.md` for complete skill documentation.

## Configuration Files

- `requirements.txt` - Python package dependencies
- `setup.py` - Interactive setup wizard
- `category_template.json` - Pre-generated category hierarchy (optional)
- `~/.pdf_organizer_settings.json` - User settings (created by setup.py)
- `organization_log.json` - Created in ebooks folder, tracks organized files

## Platform Support

- Cross-platform: Windows, macOS, Linux
- Windows: `install.ps1` installer and the `python index-app.py` launcher
- Unix: `install.sh` installer and `run_gui.sh` launcher
