# Watch Mode - Automatic PDF Organization

This guide documents a PDF-specific automation tool inside the Chwezi Document Suite.

## What is Watch Mode?

Watch Mode continuously monitors your Downloads folder and automatically organizes new PDFs as they arrive. Perfect for "set it and forget it" automation!

## Features

- **Automatic Detection**: Detects new PDFs instantly
- **Smart Batching**: Groups PDFs arriving within 10 seconds into ONE API call
- **Cost-Effective**: Uses the same batch processing as regular mode
- **Background Running**: Runs continuously until you stop it
- **Real-time Stats**: Shows processing statistics
- **Handles Multiple Files**: Processes multiple PDFs arriving at once

## Cost Comparison

### Watch Mode is JUST AS COST-EFFECTIVE as Batch Mode!

**How it works:**
- PDFs arriving within the batch delay (default 10 seconds) are processed together
- Multiple PDFs = ONE API call
- Cost depends on your provider's per-token pricing; batching keeps the number of calls low

**Examples:**

| Scenario | API calls |
|----------|-----------|
| 1 PDF arrives | 1 |
| 5 PDFs arrive within 10s | 1 |
| 50 PDFs arrive within 10s | 1 |
| 100 PDFs over 1 hour (in small groups) | One per group (for example 2-4) |

**The batch delay is key:**
- Longer delay (20-30s) = Better batching = Lower cost
- Shorter delay (5-10s) = Faster processing = Slightly higher cost

## Quick Start

### Option 1: Interactive Setup (Easiest)

```bash
python watch_setup.py
```

Follow the prompts to configure and start watch mode.

### Option 2: Direct Launch

```bash
python watch_organizer.py --ebooks F:/ebooks --provider gemini --api-key YOUR_KEY
```

### Option 3: Windows Batch File

```bash
START_WATCH_MODE.bat
```

## Configuration Options

```bash
python watch_organizer.py \
  --downloads ~/Downloads \          # Folder to watch (default: user's Downloads)
  --ebooks F:/ebooks \                # Where to organize PDFs
  --provider gemini \                 # AI provider (gemini/anthropic/deepseek)
  --api-key YOUR_KEY \                # Your API key
  --content-analysis \                # Optional: send text previews of unclear files (off by default)
  --delay 10                          # Batch delay in seconds (default: 10)
```

### Recommended Delay Settings

- **Fast organization**: `--delay 5` (5 seconds)
- **Balanced**: `--delay 10` (10 seconds) - DEFAULT
- **Maximum batching**: `--delay 30` (30 seconds)

## How It Works

1. **Watch Mode Starts**: Monitors your Downloads folder
2. **PDF Detected**: New PDF file is detected
3. **Batch Timer Starts**: Waits for the batch delay (default 10s)
4. **More PDFs?**: If more PDFs arrive, timer resets
5. **Process Batch**: After delay expires, ALL pending PDFs processed in ONE API call
6. **Organize**: PDFs are categorized and moved to ebooks folder
7. **Repeat**: Continues watching for more PDFs

Watch mode also detects browser downloads that finish by renaming (`.crdownload` or `.part` becoming `.pdf`), and ignores files inside the library folder. By default only filenames and PDF metadata (title and author) are sent to the AI provider; `--content-analysis` adds text previews of unclear files. AI-suggested folders and filenames are sanitised and confined to the library, and one failing file does not stop a batch.

## Examples

### Download 1 PDF every few minutes
```
PDF arrives → Wait 10s → Process (1 API call) → Continue watching
Cost: one API call per PDF
```

### Download 10 PDFs at once
```
10 PDFs arrive → Wait 10s → Process all 10 (1 API call) → Continue watching
Cost: one API call for all 10 PDFs
```

### Download PDFs throughout the day
```
Morning: 5 PDFs → 1 API call
Afternoon: 8 PDFs → 1 API call
Evening: 12 PDFs → 1 API call
Total: 25 PDFs organized in 3 API calls
```

## Stopping Watch Mode

Press **Ctrl+C** in the terminal to stop watch mode gracefully.

You'll see final statistics before it exits.

## Statistics Tracking

Watch mode tracks:
- Total PDFs processed
- Successful organizations
- Failed attempts
- Total runtime

## Running as a Background Service

### Windows

Create a scheduled task that runs on startup:

```powershell
# Create task
schtasks /create /tn "PDF Watch" /tr "python C:\path\to\watch_organizer.py --ebooks F:/ebooks --provider gemini --api-key YOUR_KEY" /sc onlogon
```

### Linux/Mac

Use systemd or launchd to run as a service.

## Troubleshooting

### Watch mode not detecting PDFs
- Check that the Downloads folder path is correct
- Ensure PDFs are actually being created (not moved from elsewhere)
- Try increasing the delay to give files time to finish writing

### High API costs
- Increase the batch delay (`--delay 30`)
- This groups more PDFs into fewer API calls

### PDFs being skipped
- Files might still be downloading/writing
- The system waits for file size to stabilize before processing
- Increase delay if needed

## Best Practices

1. **Set appropriate delay**: Balance speed vs. cost
2. **Run during active hours**: Only run when you're actively downloading PDFs
3. **Monitor statistics**: Check the stats periodically
4. **Test first**: Try with a few PDFs before leaving it running

## Comparison with Regular Batch Mode

| Feature | Watch Mode | Batch Mode |
|---------|-----------|------------|
| When to use | Continuous monitoring | One-time organization |
| Interaction | Set and forget | Manual trigger |
| Cost | Same batching efficiency | Same batching efficiency |
| Best for | Regular PDF downloads | Organizing existing PDFs |

## Advanced Usage

### Multiple Watch Folders

Run multiple instances with different folders:

```bash
# Terminal 1 - Watch Downloads
python watch_organizer.py --downloads ~/Downloads --ebooks ~/ebooks --provider gemini --api-key KEY1

# Terminal 2 - Watch Documents
python watch_organizer.py --downloads ~/Documents --ebooks ~/ebooks --provider gemini --api-key KEY1
```

### Different Providers for Different Times

```bash
# Daytime - Use fast provider
python watch_organizer.py --provider gemini --api-key KEY1

# Nighttime - Use cheaper provider
python watch_organizer.py --provider deepseek --api-key KEY2
```

## Support

If you encounter issues:
1. Check that all dependencies are installed: `python -m pip install -r requirements.txt` (or `python -m pip install -e ".[dev,extract]"`)
2. Verify your API key is correct
3. Ensure folders exist and have proper permissions
4. Check the console output for error messages

Enjoy automatic PDF organization! 🎉
