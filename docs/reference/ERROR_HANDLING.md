# Error Handling & Troubleshooting

## Common Errors and Solutions

### ❌ "unsupported operand type(s) for /: 'WindowsPath' and 'NoneType'"

**What it means:** The AI failed to provide a category path, or returned None/empty.

**Why it happens:**

- API connection issue
- AI response was malformed
- API rate limit hit
- Invalid API key

**Solutions:**

1. **Check your API key:**

   ```bash
   # Keys are NOT read from environment variables.
   # Enter the key in the GUI or pass --api-key.
   ```

2. **Check internet connection:**
   - Make sure you're connected
   - Try: `ping generativelanguage.googleapis.com`

3. **Try again:**
   - Tool now has fallback to "Uncategorized" if this happens
   - Re-run to process remaining files

4. **Check API limits:**
   - Make sure you haven't hit rate limits
   - Check your Google AI Studio: <https://aistudio.google.com/app/apikey>

**Fixed in latest version:** Tool now automatically uses "Uncategorized" category if AI fails.

---

### ❌ "No module named 'pdfplumber'"

**What it means:** Dependencies not installed

**Solution:**

```bash
# Run the dependency installer
INSTALL_DEPENDENCIES.bat

# Or manually:
python -m pip install -r requirements.txt
```

---

### ❌ "Python is not recognized..."

**What it means:** Python not in PATH

**Solution:**

1. Reinstall Python from <https://python.org>
2. ✅ CHECK "Add Python to PATH" during installation
3. Restart computer
4. Try again

---

### ❌ "Could not extract text from [file].pdf"

**What it means:** PDF is image-based (scanned) or encrypted

**Solutions:**

1. **For scanned PDFs:**
   - PDF contains images, not text
   - Tool will skip these files
   - Consider using OCR separately

2. **For encrypted PDFs:**
   - PDF is password protected
   - Unlock the PDF first
   - Then run organizer

3. **For corrupted PDFs:**
   - PDF file may be damaged
   - Try opening in PDF reader
   - Re-download if needed

---

### ❌ "Permission denied" when moving files

**What it means:** File in use or no write permission

**Solutions:**

1. **Close PDF readers:**
   - Close Adobe Reader, Chrome, Edge
   - Make sure no PDFs are open

2. **Check permissions:**
   - Ensure you have write access to ebooks folder
   - Try running as administrator (right-click → Run as Administrator)

3. **Check antivirus:**
   - Temporarily disable if it's blocking
   - Add folder to exclusions

---

### ❌ "API key not found"

**What it means:** No API key was supplied (keys are not read from environment variables)

**Solutions:**

1. **Enter it in the GUI:**
   - Just type it in the API Key field
   - It is saved to your user settings only if you choose to save settings

2. **Or pass as argument:**

   ```bash
   python organize_batch.py --ebooks "F:\ebooks" --api-key "your-key"
   ```

---

### ❌ "Categorization error: 401 Unauthorized"

**What it means:** Invalid API key

**Solutions:**

1. **Verify API key:**
   - Check at <https://aistudio.google.com/app/apikey>
   - Make sure it's active
   - Create new key if needed

2. **Update key:**
   - Delete old key from settings
   - Enter new key

---

### ⚠️ "Warning: AI response missing category_path"

**What it means:** AI returned incomplete response

**What happens:**

- File automatically goes to "Uncategorized" folder
- Process continues with other files

**Solutions:**

1. **Manual categorization:**
   - Check "Uncategorized" folder
   - Manually move files to correct categories

2. **Re-run on specific file:**
   - Move file back to Downloads
   - Run organizer again

---

### ❌ "Could not parse AI response as JSON"

**What it means:** AI returned malformed JSON

**What happens:**

- File goes to "Uncategorized"
- Error is logged
- Process continues

**Solutions:**

1. **Check API status:**
   - Visit <https://status.cloud.google.com/>
   - May be temporary API issue

2. **Try again later:**
   - Wait a few minutes
   - Re-run organizer

3. **Check output:**
   - Tool shows what AI returned
   - Can help debug issue

---

## Error Recovery Features

### Automatic Fallbacks

The tool now includes automatic error recovery:

1. **Missing category_path** → Uses "Uncategorized"
2. **JSON parse error** → Uses "Uncategorized"
3. **File move fails** → Logs error, continues with next file
4. **Duplicate filename** → Adds "_1", "_2", etc.
5. **Invalid characters** → Automatically cleaned from filenames

### Logs

All operations are logged to:

```
F:\ebooks\organization_log.json
```

Check this file to see:

- Which files were processed
- What categories were assigned
- Any errors that occurred
- Timestamps of operations

---

## Prevention Tips

### Before Running

1. ✅ **Dry run first:**

   ```bash
   python organize_batch.py --ebooks "F:\ebooks" --api-key "your-key" --dry-run
   ```

2. ✅ **Close all PDFs:**
   - Exit PDF readers
   - Close browsers with PDFs open

3. ✅ **Check API key:**
   - Verify it's set and valid
   - Test with a small batch first

4. ✅ **Backup important files:**
   - Just in case!
   - Or use dry-run mode

### During Operation

1. 📊 **Watch for warnings:**
   - Yellow warnings are informational
   - Red errors need attention

2. 🔄 **Don't interrupt:**
   - Let it finish processing
   - Ctrl+C if you need to stop

3. 📝 **Review summary:**
   - Check categorizations before confirming
   - Verify renames look correct

### After Running

1. ✅ **Verify results:**
   - Spot-check a few categorized files
   - Make sure they're in right places

2. 📋 **Check log:**
   - Review organization_log.json
   - Look for any errors

3. 🗂️ **Manual adjustments:**
   - Move any mis-categorized files
   - Update structure if needed

---

## Debug Mode

For detailed error information:

```bash
# Run with verbose output
python organize_batch.py --ebooks "F:\ebooks" --api-key "your-key" --dry-run 2>&1 | tee debug.log
```

This saves all output to `debug.log` for troubleshooting.

---

## Getting Help

If you encounter persistent errors:

1. **Check this guide first**
2. **Review error message carefully** - it usually explains the issue
3. **Check the log file** - `organization_log.json`
4. **Try dry-run mode** - see what happens without making changes
5. **Test with single file** - move one PDF to Downloads and test

### Useful Diagnostic Commands

```bash
# Check Python
python --version

# Check packages
pip list | grep generativeai
pip list | grep pdfplumber
pip list | grep pypdf

# Test PDF reading
python -c "from pypdf import PdfReader; print('PDF library works')"

# Test imports
python -c "import google.genai, pdfplumber, pypdf; print('All imports OK')"
```

---

## Error Codes Reference

| Error | Meaning | Solution |
|-------|---------|----------|
| ModuleNotFoundError | Package not installed | Run INSTALL_DEPENDENCIES.bat |
| FileNotFoundError | File/folder doesn't exist | Check paths |
| PermissionError | No write access | Close files, check permissions |
| JSONDecodeError | AI response invalid | Retry, check API status |
| ConnectionError | No internet | Check connection |
| 401 Unauthorized | Invalid API key | Verify key at your AI provider console (for Gemini: aistudio.google.com) |
| 429 Too Many Requests | Rate limit hit | Wait and retry |
| WindowsPath/NoneType | AI returned no category | Fixed in latest version |

---

**Remember:** The tool now has robust error handling and will continue processing even if individual files fail! Check the "Uncategorized" folder for any files that couldn't be categorized automatically.

---

## Run behaviour

- One failing file no longer stops an organiser run; the remaining files are still processed.
- The command-line organiser exits with a non-zero status if any file failed, so scripts can detect partial failures.
- AI-suggested folders and filenames are sanitised and confined to the library folder.
