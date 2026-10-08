# Quick Fix Guide - "File Not Found" Error

## Problem

You're seeing this error:

```
python: can't open file 'C:\Windows\System32\organize_batch.py': 
[Errno 2] No such file or directory
```

## Why This Happens

The batch file is running from the wrong directory (System32 instead of where your files are).

## ✅ SOLUTION - Run from the project folder

**The easiest fix:** open a terminal in the project folder and launch the suite from there.

```
python index-app.py        # Chwezi Document Suite launcher
python organize_batch.py   # Organizer GUI / CLI
python web_interface.py    # Web interface (http://localhost:5000)
```

On Linux or macOS you can also run `./run_gui.sh`.

Running from the project folder guarantees Python finds the other files.

---

## Alternative Solutions

### Option 1: Run from Command Prompt (Recommended)

1. **Open File Explorer** and navigate to the folder with your PDF organiser files
2. **Type `cmd`** in the address bar and press Enter
3. **Run:** `python organize_batch.py`

This guarantees you're in the right directory.

### Option 2: Use the launcher script (Linux/macOS)

Run `./run_gui.sh` from the project folder. On Windows, use `python index-app.py` instead.

### Option 3: Create a Shortcut (Best for Desktop)

1. **Right-click** on `organize_batch.py`
2. Select **"Create shortcut"**
3. **Right-click** the shortcut → **Properties**
4. In **"Target"** field, change it to:

   ```
   python "C:\full\path\to\your\folder\organize_batch.py"
   ```

   (Replace with your actual path)
5. In **"Start in"** field, put:

   ```
   C:\full\path\to\your\folder
   ```

6. Click **OK**
7. Move the shortcut to your Desktop

### Option 4: Use PowerShell Installer

If nothing else works, use the PowerShell installer:

1. **Right-click** `install.ps1`
2. Select **"Run with PowerShell"**
3. It will set everything up correctly

---

## Where Should Your Files Be?

All these files must be in the **SAME FOLDER**:

- ✓ organize_batch.py
- ✓ organize_batch.py
- ✓ requirements.txt
- ✓ setup.py
- ✓ index-app.py (launcher)

**Good locations:**

- `C:\Users\YourName\Documents\PDF-Organizer\`
- `C:\PDF-Organizer\`
- `D:\Tools\PDF-Organizer\`

**Bad locations:**

- ❌ Desktop (can work but not ideal)
- ❌ Downloads (files might get mixed up)
- ❌ System folders (C:\Windows, C:\Program Files)

---

## Step-by-Step: Starting Fresh

If you want to start clean:

1. **Create a new folder:**

   ```
   C:\PDF-Organizer
   ```

2. **Move ALL these files** into that folder:
   - organize_batch.py
   - organize_batch.py
   - requirements.txt
   - setup.py
   - index-app.py
   - install.ps1
   - (all other .py, .ps1, .txt, .md files)

3. **Open Command Prompt in that folder:**
   - Navigate to `C:\PDF-Organizer` in File Explorer
   - Type `cmd` in the address bar
   - Press Enter

4. **Install dependencies:**

   ```
   python -m pip install -r requirements.txt
   ```

5. **Run the setup:**

   ```
   python setup.py
   ```

6. **Launch the GUI:**

   ```
   python organize_batch.py
   ```

Or just run `python index-app.py`!

---

## Still Not Working?

### Check Python Installation

Open Command Prompt anywhere and run:

```
python --version
```

If you see `'python' is not recognized`, then:

1. Python is not installed, OR
2. Python is not in your PATH

**Fix:**

- Reinstall Python from <https://www.python.org/>
- ✅ CHECK "Add Python to PATH" during installation

### Check Dependencies

```
python -m pip list
```

Look for:

- google-genai
- pdfplumber
- pypdf

If missing, install:

```
python -m pip install -r requirements.txt
```

---

## Quick Test

To verify everything works:

```
cd C:\PDF-Organizer
python -c "import google.genai; import pdfplumber; import pypdf; print('All good!')"
```

If you see "All good!" - you're ready to run the GUI!

```
python organize_batch.py
```

---

## Need More Help?

1. Read `INSTALLATION.md` for detailed setup instructions
2. Check error messages - they usually tell you what's wrong
3. Make sure you're running from the correct folder
4. Verify Python is installed and in PATH
