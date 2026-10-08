## 🌐 Web Interface Guide

# PDF Organiser - Web Interface

This guide documents the legacy PDF web interface inside the Chwezi Document Suite.

A modern, beautiful web interface for organizing PDFs with drag & drop functionality, real-time categorization, and library browsing.

## 🚀 Quick Start

### Launch the Web Interface

**Option 1: Batch File (Windows)**
```bash
START_WEB_INTERFACE.bat
```

**Option 2: Python Command**
```bash
python web_interface.py
```

**Option 3: Direct Python**
```python
from web_interface import app
app.run(host="127.0.0.1", port=5000)  # local only; do not bind to 0.0.0.0
```

Then open your browser and go to:
```
http://localhost:5000
```

## 📋 Features

### 1. **Drag & Drop Upload**
- Drag PDF files directly into the browser
- Or click to browse and select files
- Upload multiple PDFs at once
- Real-time upload progress

### 2. **AI-Powered Categorization**
- Automatic category suggestions
- Smart filename analysis
- Content-based classification
- Confidence scoring (High/Medium/Low)

### 3. **Interactive Review**
- See all suggestions before organizing
- Edit categories manually
- Edit suggested filenames
- Approve or reject individual files
- Batch approve/reject all

### 4. **Library Browser**
- Browse organized PDFs
- Hierarchical folder view
- File size information
- Category statistics

### 5. **Statistics Dashboard**
- Total PDFs organized
- Category breakdown
- Last run date
- Visual charts

### 6. **Provider Selection**
- Choose between Gemini, Anthropic, or DeepSeek
- Configure API keys
- Default models: `gemini-3.8-flash`, `claude-haiku-5-5`, `deepseek-flash` (override with `model_name` on `BatchPDFOrganizer`)
- Optional checkbox: **Send text previews of unclear files to the AI provider** (off by default)
- Set ebooks folder path

## 🎯 How to Use

### Step 1: Configure Settings

First time using the web interface:

1. Click **⚙️ Settings** button
2. Enter your **Ebooks Folder** path (e.g., `F:\ebooks`)
3. Select your **AI Provider** (Gemini, Anthropic, or DeepSeek)
4. Enter your **API Key**
5. Click **Save Settings**

### Step 2: Upload PDFs

1. **Drag & drop** PDFs into the upload area
   - OR click **Choose Files** to browse
2. See uploaded files listed with sizes
3. Click **🤖 Analyze & Categorize**

### Step 3: Review Suggestions

The AI will analyze each PDF and suggest:
- **Category**: Where to organize it
- **Rename**: Better filename (if current is gibberish)
- **Confidence**: How confident the AI is

For each PDF, you can:
- ✅ **Approve**: Include in organization
- ❌ **Reject**: Skip this file
- ✏️ **Edit**: Change category or filename
- Use **Approve All** or **Reject All** for batch actions

### Step 4: Organize

1. Review all suggestions
2. Click **📦 Organize Approved Files**
3. Confirm the action
4. Watch as PDFs are moved and renamed!

### Step 5: Browse Library

Click **📁 Browse Library** to:
- See your organized PDFs
- Navigate folder structure
- View statistics

## 📸 Interface Overview

### Main Upload Screen
```
┌─────────────────────────────────────────┐
│   📚 PDF organiser                      │
│   AI-Powered Library Management         │
│   [Settings] [Browse] [Statistics]      │
├─────────────────────────────────────────┤
│                                         │
│   ┌───────────────────────────────┐    │
│   │       📄                       │    │
│   │   Drag & Drop PDFs Here       │    │
│   │   or click to browse          │    │
│   │   [Choose Files]              │    │
│   └───────────────────────────────┘    │
│                                         │
└─────────────────────────────────────────┘
```

### Review Screen
```
┌─────────────────────────────────────────┐
│   📋 Categorization Results             │
│   [✓ Approve All] [✗ Reject All]       │
│   [📦 Organize Approved Files]          │
├─────────────────────────────────────────┤
│   ┌─────────────────────────────┐      │
│   │ Document.pdf  🔍 Gibberish   │      │
│   │ Category: Science/Biology    │      │
│   │ Rename: Study of Rabbits     │      │
│   │ Confidence: HIGH              │      │
│   │              [✓ Approve] [✗] │      │
│   └─────────────────────────────┘      │
│                                         │
│   ✅ APPROVED                           │
│   ┌─────────────────────────────┐      │
│   │ Python Guide.pdf             │      │
│   │ Category: Programming/Python │      │
│   │ Confidence: HIGH              │      │
│   └─────────────────────────────┘      │
└─────────────────────────────────────────┘
```

## 🎨 Visual Features

### Color Coding

- **Green border**: Approved files
- **Red opacity**: Rejected files
- **Blue badge**: Gibberish filename detected
- **Green badge**: High confidence
- **Yellow badge**: Medium confidence
- **Red badge**: Low confidence

### Real-time Updates

- Upload progress spinner
- Analysis loading indicator
- Organization progress overlay
- Toast notifications for all actions

## ⚙️ Configuration

### Settings Page

```javascript
{
  "ebooks_folder": "F:/ebooks",      // Where PDFs are organized
  "provider": "gemini",              // AI provider
  "use_content_analysis": false,      // text previews off by default
  "batch_delay": 10                  // Not used in web interface
}
```

### API Provider Links

- **Gemini**: https://aistudio.google.com/app/apikey
- **Anthropic**: https://console.anthropic.com/
- **DeepSeek**: https://platform.deepseek.com/

## 🔧 Advanced Usage

### Port and network access

The web interface is local-only. It always listens on `127.0.0.1:5000` and has no authentication, so do not bind it to `0.0.0.0`, forward the port, or run it behind a public WSGI server. Cross-origin requests from other web pages are rejected.

## 📊 API Endpoints

The web interface provides a RESTful API:

### GET `/`
Main page (HTML)

### GET/POST `/api/settings`
Get or update settings
- POST body: `{ ebooks_folder, provider, api_key, content_analysis }`; a blank `api_key` keeps the saved key
- GET returns `has_api_key` (true/false), never the key itself

### POST `/api/upload`
Upload PDF files
- Body: `FormData` with files
- Returns: `{ id, filename, size }` per file. Later calls refer to files only by `id`; any `path` sent by a client is ignored

### POST `/api/analyze`
Analyze PDFs and get categorization
- Body: `{ files: [...] }`
- Returns: Categorization results

### POST `/api/organize`
Move approved files to ebooks folder
- Body: `{ files: [...] }`
- Returns: Success/failure status

### GET `/api/browse`
Browse organized library
- Returns: File tree and statistics

### GET `/api/stats`
Get organization statistics
- Returns: Total organized, categories, last run

### GET `/api/categories`
Get available categories
- Returns: List of existing categories

### POST `/api/signature/upload-image`
Upload the PNG signature image (`FormData` field `signature`)

### POST `/api/signature/upload-pdfs`
Upload PDFs to sign; returns `{ id, filename, size }` per file

### POST `/api/signature/process`
Sign uploaded PDFs
- Body: `{ files: [{ id }], config: { position, scale, xOffset, yOffset, opacity, rotation, pages, skipPages } }`

### GET `/api/signature/download/<filename>`
Download a signed PDF

All POST endpoints reject requests whose `Origin` is not this local server.

## 🐛 Troubleshooting

### Port Already in Use

```
Error: Address already in use
```

**Solution**: Change the port:
```python
app.run(port=5001)  # Use different port
```

### Can't Access from Browser

1. Check firewall settings
2. Try `http://127.0.0.1:5000` instead of `localhost`
3. Make sure server is running

### Upload Fails

1. Check file size (max 100MB per file)
2. Ensure files are PDFs
3. Check browser console for errors

### Analysis Fails

1. Verify API key is correct
2. Check ebooks folder exists
3. Ensure API provider is selected

### Files Not Organizing

1. Make sure files are approved (green border)
2. Check ebooks folder permissions
3. Verify category paths are valid

## 💡 Tips & Best Practices

### Performance

- Upload in batches of 20-50 files for best results
- Large PDFs (>10MB) may take longer to process
- Analysis is batched - multiple PDFs = one API call

### Workflow

1. **Daily Use**: Leave web interface open, drag PDFs as they arrive
2. **Bulk Organization**: Upload many PDFs, review all at once
3. **Careful Review**: Always check suggestions before organizing

### Category Management

- Edit categories to match your structure
- Use existing categories when possible
- Create subcategories with `/` (e.g., `Science/Biology/Zoology`)

### Filename Editing

- AI suggests better names for gibberish files
- Edit names before organizing
- Keep names descriptive but concise

## 🔐 Security Notes

### Local use only

The web interface binds to `127.0.0.1:5000` and has no authentication. It is not designed for network exposure. Requests from other origins (other websites in your browser) are rejected.

### API key handling

- The API key you enter is kept on the server side only and is never returned to the browser.
- It is used only to call your chosen AI provider.
- Re-enter it after restarting the application.

### What is sent to the AI provider

PDFs are processed locally and are not uploaded to the provider. By default only filenames and PDF metadata (title and author) are sent. If you tick **Send text previews of unclear files to the AI provider** in Settings, a short text preview of files with unclear names is also sent.

## 📈 Future Enhancements

Potential improvements:
- [ ] User authentication
- [ ] Multiple user accounts
- [ ] Persistent settings storage
- [ ] OCR for scanned PDFs
- [ ] PDF preview thumbnails
- [ ] Advanced search
- [ ] Category templates
- [ ] Undo functionality
- [ ] Dark mode
- [ ] Mobile-responsive design
- [ ] Batch operations history

## 🆘 Support

Having issues? Check:

1. **Console Output**: Look for error messages in terminal
2. **Browser Console**: Check for JavaScript errors (F12)
3. **Network Tab**: Inspect API calls
4. **Log Files**: Check Flask logs

## 🎉 Enjoy!

The web interface makes PDF organization beautiful and intuitive. Drag, drop, review, organize!

Happy organizing! 📚✨
