import csv
import urllib.request
import urllib.parse
import os
import sys
import subprocess
import argparse
import numpy as np

def fetch_songs_from_sheet(sheet_id, sheet_name=None):
    """Fetch the song list from a public Google Spreadsheet."""
    if sheet_name:
        encoded_sheet_name = urllib.parse.quote(sheet_name)
        url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv&sheet={encoded_sheet_name}"
    else:
        url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv&gid=0"
    
    print(f"Fetching spreadsheet from: {url}")
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req) as response:
            content = response.read().decode('utf-8')
        
        reader = csv.reader(content.splitlines())
        rows = list(reader)
        return rows
    except Exception as e:
        print(f"Error fetching Google Sheet: {e}", file=sys.stderr)
        sys.exit(1)

def read_songs_from_local_csv(csv_path):
    """Read the song list from a local CSV file."""
    print(f"Reading local CSV file from: {csv_path}")
    try:
        with open(csv_path, mode='r', encoding='utf-8-sig') as f:
            reader = csv.reader(f)
            return list(reader)
    except Exception as e:
        print(f"Error reading local CSV file: {e}", file=sys.stderr)
        sys.exit(1)

def normalize_date(d_str):
    """Normalize date strings (e.g. M/D/YYYY or YYYY-MM-DD) to a comparable (YYYY, MM, DD) tuple."""
    if not d_str:
        return None
    d_str = d_str.strip().replace('-', '/')
    parts = d_str.split('/')
    if len(parts) != 3:
        return None
    try:
        if len(parts[0]) == 4:
            return int(parts[0]), int(parts[1]), int(parts[2])
        year = int(parts[2])
        if year < 100:
            year += 2000
        return year, int(parts[0]), int(parts[1])
    except ValueError:
        return None

def parse_song_list(rows, target_date=None):
    """Parse the rows from the spreadsheet to extract song names."""
    if not rows:
        return []
    
    headers = [h.strip().lower() for h in rows[0]]
    date_col = -1
    title_col = -1
    
    for i, h in enumerate(headers):
        if 'date' in h:
            date_col = i
            break
            
    for i, h in enumerate(headers):
        if h in ('name', 'title', 'song name', 'song title'):
            title_col = i
            break
            
    if title_col == -1:
        for i, h in enumerate(headers):
            if any(term in h for term in ('song', 'title', 'track', 'name')):
                if not any(exclude in h for exclude in ('#', 'num', 'index', 'rate', 'count')):
                    title_col = i
                    break
                    
    if title_col == -1:
        title_col = 0
        
    print(f"CSV Headers parsed. Date column index: {date_col}, Title column index: {title_col} (Name: '{headers[title_col]}')")
    
    songs = []
    
    if date_col != -1 and len(rows) > 1:
        date_groups = {}
        for row in rows[1:]:
            if len(row) > max(date_col, title_col):
                raw_date = row[date_col].strip()
                norm_date = normalize_date(raw_date)
                song_name = row[title_col].strip()
                if raw_date and norm_date and song_name:
                    if norm_date not in date_groups:
                        date_groups[norm_date] = []
                    date_groups[norm_date].append((raw_date, song_name))
        
        if target_date:
            norm_target = normalize_date(target_date)
            if norm_target in date_groups:
                orig_date = date_groups[norm_target][0][0]
                print(f"Target date '{target_date}' matched with sheet date '{orig_date}'")
                songs = [item[1] for item in date_groups[norm_target]]
            else:
                available_dates = sorted(list(date_groups.keys()))
                available_str = [f"{d[1]}/{d[2]}/{d[0]}" for d in available_dates[-5:]]
                print(f"Date '{target_date}' not found. Latest available dates in CSV: {available_str}", file=sys.stderr)
                sys.exit(1)
        else:
            available_dates = sorted(list(date_groups.keys()))
            if available_dates:
                latest_date = available_dates[-1]
                orig_date = date_groups[latest_date][0][0]
                print(f"No date specified. Using latest date chronologically: {orig_date}")
                songs = [item[1] for item in date_groups[latest_date]]
    else:
        start_row = 1 if len(rows) > 1 else 0
        for row in rows[start_row:]:
            if len(row) > title_col:
                t = row[title_col].strip()
                if t:
                    songs.append(t)
                    
    songs = [s for s in songs if s]
    print(f"Found {len(songs)} target songs in spreadsheet: {songs}")
    return songs

def format_time(seconds):
    """Format seconds into HH:MM:SS or MM:SS."""
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    s = int(seconds % 60)
    if h > 0:
        return f"{h:02d}:{m:02d}:{s:02d}"
    else:
        return f"{m:02d}:{s:02d}"

def extract_acoustic_features(video_path, sample_rate=22050, chunk_size_sec=1.0):
    """Stream audio from ffmpeg and extract RMS and ZCR features in chunks."""
    bytes_per_sec = sample_rate * 2
    bytes_per_chunk = int(bytes_per_sec * chunk_size_sec)
    frame_size = int(sample_rate * 0.05) # 50ms frames
    
    cmd = [
        "ffmpeg",
        "-i", video_path,
        "-vn",
        "-ac", "1",
        "-ar", str(sample_rate),
        "-f", "s16le",
        "-"
    ]
    
    print("Streaming audio from video file...")
    process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
    
    features = []
    timestamps = []
    
    chunk_index = 0
    while True:
        data = process.stdout.read(bytes_per_chunk)
        if not data:
            break
        samples = np.frombuffer(data, dtype=np.int16).astype(np.float32)
        if len(samples) < sample_rate * 0.5:
            break
            
        num_frames = len(samples) // frame_size
        if num_frames == 0:
            break
            
        rms_values = []
        zcr_values = []
        
        for f in range(num_frames):
            frame = samples[f * frame_size : (f + 1) * frame_size]
            rms = np.sqrt(np.mean(frame**2))
            rms_values.append(rms)
            zcr = np.sum(np.diff(frame > 0)) / len(frame)
            zcr_values.append(zcr)
            
        rms_values = np.array(rms_values)
        zcr_values = np.array(zcr_values)
        
        mean_rms = np.mean(rms_values)
        std_rms = np.std(rms_values)
        cv_rms = std_rms / (mean_rms + 1e-5)
        
        mean_zcr = np.mean(zcr_values)
        
        features.append([mean_rms, cv_rms, mean_zcr])
        timestamps.append(chunk_index * chunk_size_sec)
        
        chunk_index += 1
        if chunk_index % 100 == 0:
            print(f"  Processed {format_time(chunk_index * chunk_size_sec)} of audio...")
            
    process.terminate()
    return np.array(features), np.array(timestamps)

def smooth_predictions(is_music, window_size=7):
    """Apply a 1D majority-voting filter to smooth transitions and filter out transient noise."""
    smoothed = np.copy(is_music)
    half_w = window_size // 2
    for i in range(len(is_music)):
        start = max(0, i - half_w)
        end = min(len(is_music), i + half_w + 1)
        smoothed[i] = 1 if np.mean(is_music[start:end]) >= 0.5 else 0
    return smoothed

def bridge_gaps(is_music, gap_limit_sec, chunk_size_sec):
    """Bridge short non-music gaps (like brief tuning or sheet adjustments) within a song."""
    gap_limit_chunks = int(gap_limit_sec / chunk_size_sec)
    music_indices = np.where(is_music == 1)[0]
    if len(music_indices) <= 1:
        return is_music
        
    smoothed = np.copy(is_music)
    for idx in range(len(music_indices) - 1):
        curr_i = music_indices[idx]
        next_i = music_indices[idx + 1]
        gap = next_i - curr_i - 1
        if 0 < gap <= gap_limit_chunks:
            smoothed[curr_i + 1 : next_i] = 1
    return smoothed

def find_music_segments(is_music, timestamps, chunk_size_sec=1.0, min_duration=90.0):
    """Identify continuous segments of music longer than min_duration."""
    segments = []
    in_music = False
    start_time = 0
    
    for i, val in enumerate(is_music):
        t = timestamps[i]
        if val == 1 and not in_music:
            in_music = True
            start_time = t
        elif val == 0 and in_music:
            in_music = False
            duration = t - start_time
            if duration >= min_duration:
                segments.append({"start": start_time, "end": t, "duration": duration})
            
    if in_music:
        duration = timestamps[-1] + chunk_size_sec - start_time
        if duration >= min_duration:
            segments.append({"start": start_time, "end": timestamps[-1] + chunk_size_sec, "duration": duration})
        
    return segments

def get_song_starts(segments, num_songs):
    """Retrieve the 'num_songs' longest music segments sorted chronologically."""
    if len(segments) < num_songs:
        print(f"Warning: Only found {len(segments)} music blocks that meet the minimum duration, but expected {num_songs} songs from CSV.")
        selected = segments
    else:
        sorted_by_duration = sorted(segments, key=lambda x: x["duration"], reverse=True)
        selected = sorted_by_duration[:num_songs]
        
    selected = sorted(selected, key=lambda x: x["start"])
    return selected

def main():
    parser = argparse.ArgumentParser(description="Generate YouTube chapters from a Google Sheet (or CSV) and video recording.")
    parser.add_argument("video_path", help="Path to the video/audio file of the live stream.")
    
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--csv-path", help="Path to a local CSV file containing the songs.")
    group.add_argument("--sheet-id", help="Google Sheet ID.")
    
    parser.add_argument("--sheet-name", help="Name of the specific sheet/tab to read (Google Sheet only).")
    parser.add_argument("--date", help="Target show date in the spreadsheet (optional).")
    
    parser.add_argument("--method", choices=["silence", "kmeans"], default="silence", help="Method to detect music blocks (default: silence).")
    parser.add_argument("--chunk-size", type=float, default=1.0, help="Analysis chunk size in seconds (default: 1.0).")
    parser.add_argument("--min-duration", type=float, default=90.0, help="Minimum duration of a song block in seconds (default: 90.0).")
    parser.add_argument("--skip-start", type=float, default=0.0, help="Skip the first X seconds of the stream (default: 0.0).")
    parser.add_argument("--offset", type=float, default=0.0, help="Offset in seconds to add/subtract from the generated chapter timestamps (default: 0.0).")
    
    args = parser.parse_args()
    
    if not os.path.exists(args.video_path):
        print(f"Error: Video file not found: {args.video_path}", file=sys.stderr)
        sys.exit(1)
        
    if args.csv_path:
        rows = read_songs_from_local_csv(args.csv_path)
    else:
        rows = fetch_songs_from_sheet(args.sheet_id, args.sheet_name)
        
    target_songs = parse_song_list(rows, args.date)
    
    if not target_songs:
        print("Error: No songs found matching the criteria.", file=sys.stderr)
        sys.exit(1)
        
    print(f"\nAnalyzing audio spectrum and energy patterns (method={args.method}, chunk size={args.chunk_size}s)...")
    features, timestamps = extract_acoustic_features(args.video_path, chunk_size_sec=args.chunk_size)
    
    if len(features) < 10:
        print("Error: Audio is too short to analyze.", file=sys.stderr)
        sys.exit(1)
        
    # Noise Gate
    max_rms = np.max(features[:, 0])
    silence_threshold = max(30.0, 0.005 * max_rms)
    is_silent = features[:, 0] < silence_threshold
    
    if args.method == "silence":
        # Silence-based segmentation
        is_active = np.ones(len(features), dtype=int)
        silent_run = 0
        
        consecutive_limit = max(3, int(2.5 / args.chunk_size))
        for i in range(len(features)):
            if is_silent[i]:
                silent_run += 1
            else:
                silent_run = 0
            if silent_run >= consecutive_limit:
                is_active[i - silent_run + 1 : i + 1] = 0
                
        segments = []
        in_active = False
        start_time = 0
        
        for i, val in enumerate(is_active):
            t = timestamps[i]
            if val == 1 and not in_active:
                in_active = True
                start_time = t
            elif val == 0 and in_active:
                in_active = False
                duration = t - start_time
                if duration >= args.min_duration:
                    segments.append({"start": start_time, "end": t, "duration": duration})
                    
        if in_active:
            duration = timestamps[-1] + args.chunk_size - start_time
            if duration >= args.min_duration:
                segments.append({"start": start_time, "end": timestamps[-1] + args.chunk_size, "duration": duration})
                
    else:
        # K-Means method
        active_indices = np.where(~is_silent)[0]
        if len(active_indices) < 5:
            print("Error: Not enough active audio in recording.", file=sys.stderr)
            sys.exit(1)
            
        active_features = features[active_indices][:, 1:3]
        mean = active_features.mean(axis=0)
        std = active_features.std(axis=0) + 1e-5
        scaled_active = (active_features - mean) / std
        
        np.random.seed(42)
        k = 2
        centroids = scaled_active[np.random.choice(len(scaled_active), k, replace=False)]
        labels = np.zeros(len(scaled_active), dtype=int)
        
        for _ in range(50):
            distances = np.linalg.norm(scaled_active[:, np.newaxis, :] - centroids[np.newaxis, :, :], axis=2)
            new_labels = np.argmin(distances, axis=1)
            if np.array_equal(labels, new_labels):
                break
            labels = new_labels
            centroids = np.array([scaled_active[labels == i].mean(axis=0) if np.sum(labels == i) > 0 else centroids[i] for i in range(k)])
            
        unscaled_centroids = centroids * std + mean
        music_idx = np.argmin(unscaled_centroids[:, 0])
        
        final_labels = np.zeros(len(features), dtype=int)
        final_labels[is_silent] = 0
        active_labels = np.where(labels == music_idx, 2, 1)
        final_labels[active_indices] = active_labels
        
        is_music = (final_labels == 2).astype(int)
        smoothing_window = max(3, int(15.0 / args.chunk_size) | 1)
        smoothed_music = smooth_predictions(is_music, window_size=smoothing_window)
        smoothed_music = bridge_gaps(smoothed_music, gap_limit_sec=25.0, chunk_size_sec=args.chunk_size)
        
        segments = find_music_segments(smoothed_music, timestamps, chunk_size_sec=args.chunk_size, min_duration=args.min_duration)
        
        # Refine start times
        for seg in segments:
            t_detect = seg["start"]
            detect_idx = int(t_detect / args.chunk_size)
            search_limit = min(120, detect_idx)
            refined_start = t_detect
            for i in range(detect_idx, detect_idx - search_limit, -1):
                if i >= 3 and np.all(is_silent[i-3:i]):
                    refined_start = i * args.chunk_size
                    break
            seg["start"] = refined_start
            seg["duration"] = seg["end"] - refined_start
            
    # Apply skip_start filter to the segments (so it doesn't skew clustering)
    if args.skip_start > 0:
        print(f"Filtering out music blocks starting before {args.skip_start} seconds ({format_time(args.skip_start)})...")
        segments = [seg for seg in segments if seg["start"] >= args.skip_start]
        
    song_starts = get_song_starts(segments, len(target_songs))
    
    # Build chapters
    song_timestamps = {}
    song_timestamps["0:00"] = "Intro / Chat"
    song_offsets = []
    
    for idx, start_seg in enumerate(song_starts):
        chapter_time = max(0.0, start_seg["start"] + args.offset)
        formatted_start = format_time(chapter_time)
        raw_seconds = int(round(chapter_time))
        if idx < len(target_songs):
            name = target_songs[idx]
        else:
            name = f"Song {idx+1}"
            
        if formatted_start != "0:00":
            song_timestamps[formatted_start] = name
            song_offsets.append((name, raw_seconds, formatted_start))
            
    print("\nDetected Music Blocks (unadjusted for offset):")
    for idx, seg in enumerate(segments):
        is_selected = " [Selected as Song]" if seg in song_starts else " [Filtered/Skipped]"
        print(f"  Block {idx+1}: {format_time(seg['start'])} to {format_time(seg['end'])} - Duration: {format_time(seg['duration'])}{is_selected}")
        
    # Output chapter markers
    print("\n" + "="*40)
    print(" GENERATED YOUTUBE CHAPTERS")
    print("="*40)
    
    # Sort timestamps chronologically
    def timestamp_key(ts):
        parts = list(map(int, ts[0].split(':')))
        if len(parts) == 2:
            return parts[0] * 60 + parts[1]
        elif len(parts) == 3:
            return parts[0] * 3600 + parts[1] * 60 + parts[2]
        return 0
        
    sorted_chapters = sorted(song_timestamps.items(), key=timestamp_key)
    
    output_lines = []
    for ts, name in sorted_chapters:
        line = f"{ts} - {name}"
        output_lines.append(line)
        print(line)
        
    print("="*40)
    print("You can copy the lines above and paste them into your YouTube video description!")
    
    # Output copy-paste column for Google Sheets
    print("\n" + "="*40)
    print(" GOOGLE SHEETS COPY-PASTE COLUMN")
    print("="*40)
    print("Copy the numbers below and paste them directly into the 'Offset' column in Google Sheets:")
    print("----------------------------------------")
    for name, raw_sec, formatted in song_offsets:
        print(raw_sec)
    print("----------------------------------------")
    print("Verification mapping:")
    for name, raw_sec, formatted in song_offsets:
         print(f"  - {name}: {raw_sec}s ({formatted})")
    print("="*40)

if __name__ == "__main__":
    main()
