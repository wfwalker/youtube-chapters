# YouTube Chapter Generator

This tool automatically detects song start times in a YouTube live stream recording and generates YouTube-formatted chapter markers (e.g., `03:15 - Song Name`) using a song list from a Google Spreadsheet (local CSV or online Sheet).

## How It Works
1. **Song List**: The script reads your song list from a local CSV file or fetches it from a public Google Sheet. It parses the list to get the order of the songs for a specific show date (or defaults to the most recent show).
2. **Scan**: It scans through the video/audio file by extracting short audio clips at set intervals.
3. **Recognize**: It submits these clips to Shazam's recognition service to identify which song is playing.
4. **Refine**: Once a song matches, it performs a binary search (halving intervals) to pinpoint the exact transition timestamp within 10 seconds.
5. **Output**: It generates a formatted list of timestamps and titles ready to copy and paste directly into your YouTube description.

## Prerequisites

1. **Spreadsheet Format**:
   - The script assumes your spreadsheet has columns named **Date** and **Name** (or **Song**, **Title**, **Track**).
   - If there is a Date column, you can target a specific show using the `--date` option, or omit it to automatically use the latest date found in the sheet.

2. **FFmpeg & Python**:
   - Python 3.9+ and `ffmpeg` are required and already configured on your system.

---

## How to Run

1. Open your terminal and navigate to the project directory:
   ```bash
   cd /Users/walker/Dropbox/youtube-chapters
   ```

2. Activate the virtual environment:
   ```bash
   source .venv/bin/activate
   ```

3. Run the generator script:

   **Option A: Using the local CSV file (Recommended)**
   ```bash
   python3 chapter_generator.py "/path/to/livestream_recording.mp4" --csv-path "FJHH songs - Songs.csv"
   ```

   **Option B: Directly fetching from Google Sheets**
   *Note: First share your Google Sheet as "Anyone with the link can view (Viewer)", and copy the Sheet ID from the URL.*
   ```bash
   python3 chapter_generator.py "/path/to/livestream_recording.mp4" --sheet-id "YOUR_SPREADSHEET_ID"
   ```

   **Option C: For live original improvisations (Bypassing Shazam)**
   If you are doing original live improvisations or playing songs that cannot be recognized by Shazam, add the `--improv` flag. This uses a local machine learning (K-Means clustering) pipeline to distinguish talking/silence from continuous musical improvisation, automatically mapping the detected music segments to the song list:
   ```bash
   python3 chapter_generator.py "/path/to/livestream_recording.mp4" --csv-path "FJHH songs - Songs.csv" --improv
   ```

### Additional Options

* **Handle a Musical Intro at the Start (`--skip-start`)**:
  If you play a musical intro or warm up for the first few minutes, you can tell the script to skip analyzing the first $X$ seconds (e.g., skip the first 3 minutes = 180 seconds):
  ```bash
  python3 chapter_generator.py "/path/to/livestream_recording.mp4" --csv-path "FJHH songs - Songs.csv" --improv --skip-start 180
  ```

* **Filter Out Short Jams/Tuning (`--min-duration`)**:
  To ignore short music blocks (like a 30-second sound check or short jam) and only target actual songs, increase the minimum duration (in seconds) required for a block to be considered a song (default is 90 seconds):
  ```bash
  python3 chapter_generator.py "/path/to/livestream_recording.mp4" --csv-path "FJHH songs - Songs.csv" --improv --min-duration 120
  ```

* **Align Local Recording with YouTube Stream (`--offset`)**:
  Sometimes, the raw local video file has a pre-roll or extra recording buffer compared to the final trimmed stream published on YouTube. You can use `--offset` (in seconds) to shift all generated timestamps so they align perfectly with the YouTube video timeline:
  ```bash
  # Shift all timestamps back by 21 seconds
  python3 chapter_generator.py "/path/to/livestream_recording.mp4" --csv-path "FJHH songs - Songs.csv" --improv --offset -21.0
  ```

* **Select Improvisation Detection Method (`--improv-method`)**:
  By default, improvisation mode uses `silence` segmentation which detects the pauses between songs. You can also specify `kmeans` to use unsupervised machine learning features (Zero Crossing Rate and loudness variation):
  ```bash
  # Use K-Means clustering instead of silence boundary detection
  python3 chapter_generator.py "/path/to/livestream_recording.mp4" --csv-path "FJHH songs - Songs.csv" --improv --improv-method kmeans
  ```

* **Increase Start Time Accuracy (`--chunk-size`)**:
  By default, the script analyzes the video in 1-second chunks. To get sub-second precision (e.g. 0.5-second accuracy), specify a smaller chunk size:
  ```bash
  # Recommended for highest precision
  python3 chapter_generator.py "/path/to/livestream_recording.mp4" --csv-path "FJHH songs - Songs.csv" --improv --chunk-size 0.5
  ```

* **Specify a Show Date**:
  If your spreadsheet lists songs for multiple weeks, specify which date you want to extract songs for (otherwise, it will default to the last/most recent date in the sheet, e.g. `6/26/2026`):
  ```bash
  python3 chapter_generator.py "/path/to/livestream_recording.mp4" --csv-path "FJHH songs - Songs.csv" --date "6/26/2026"
  ```
  *(Note: You can input the date in either `M/D/YYYY` or `YYYY-MM-DD` formats; the script normalizes them automatically).*

* **Change Scan Interval (Shazam Mode Only)**:
  By default, in Shazam mode it checks the audio every 30 seconds to speed up scanning. If songs are shorter or you want to scan differently, you can change the interval (in seconds):
  ```bash
  python3 chapter_generator.py "/path/to/livestream_recording.mp4" --csv-path "FJHH songs - Songs.csv" --interval 15
  ```

* **Specify a Tab/Sheet Name (Google Sheets Only)**:
  If your songs are on a specific tab in the online workbook, use `--sheet-name`:
  ```bash
  python3 chapter_generator.py "/path/to/livestream_recording.mp4" --sheet-id "YOUR_ID" --sheet-name "Shows 2026"
  ```
