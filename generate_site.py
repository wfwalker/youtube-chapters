import csv
import os
import re
import datetime

# Configuration Paths
script_dir = os.path.dirname(os.path.abspath(__file__))
songs_csv_path = os.path.join(script_dir, "FJHH songs - Songs.csv")
hof_csv_path = os.path.join(script_dir, "FJHH songs - Hall of Fame.csv")
episodes_csv_path = os.path.join(script_dir, "FJHH songs - Episodes.csv")

songs_output_dir = os.path.join(script_dir, "website", "_songs")
episodes_output_dir = os.path.join(script_dir, "website", "_episodes")
data_output_dir = os.path.join(script_dir, "website", "_data")

# Utility Helpers
def slugify(text):
    text = text.lower().strip()
    text = re.sub(r'[^a-z0-9\s-]', '', text)
    text = re.sub(r'[\s-]+', '-', text)
    return text.strip('-')

def parse_date_key(date_str):
    parts = date_str.split('/')
    if len(parts) == 3:
        try:
            return int(parts[2]), int(parts[0]), int(parts[1])
        except ValueError:
            pass
    return (0, 0, 0)

def normalize_date_str(date_str):
    if not date_str:
        return ""
    parts = date_str.strip().replace('-', '/').split('/')
    if len(parts) == 3:
        try:
            return f"{int(parts[2]):04d}-{int(parts[0]):02d}-{int(parts[1]):02d}"
        except ValueError:
            pass
    return date_str.strip()

def format_long_date(date_str):
    if not date_str:
        return ""
    parts = date_str.split('/')
    if len(parts) == 3:
        try:
            m, d, y = int(parts[0]), int(parts[1]), int(parts[2])
            month_name = datetime.date(y, m, 1).strftime("%B")
            return f"{month_name} {d}, {y}"
        except ValueError:
            pass
    return date_str

def format_offset_time(seconds_str):
    try:
        seconds = int(seconds_str)
        m, s = divmod(seconds, 60)
        h, m = divmod(m, 60)
        if h > 0:
            return f"{h:02d}:{m:02d}:{s:02d}"
        else:
            return f"{m:02d}:{s:02d}"
    except ValueError:
        return seconds_str
# Data Loading Functions
def read_hall_of_fame(path):
    """Read the Hall of Fame CSV and map slugified titles to metadata."""
    hof = {}
    if not os.path.exists(path):
        print(f"Warning: Hall of Fame CSV not found at {path}")
        return hof
        
    print(f"Reading Hall of Fame CSV from: {path}")
    with open(path, mode='r', encoding='utf-8-sig') as f:
        reader = csv.reader(f)
        header = next(reader)
        header = [h.strip().lower() for h in header]
        
        title_idx = header.index('title') if 'title' in header else 1
        ready_idx = header.index('ready') if 'ready' in header else 2
        style_idx = header.index('style') if 'style' in header else 6
        composer_idx = header.index('composer') if 'composer' in header else (7 if len(header) > 7 else -1)
        
        for row in reader:
            limit_idx = max(title_idx, ready_idx, style_idx, composer_idx)
            if not row or len(row) <= limit_idx:
                continue
            title = row[title_idx].strip()
            ready = row[ready_idx].strip()
            style = row[style_idx].strip()
            composer = row[composer_idx].strip() if composer_idx != -1 else ""
            if title:
                slug = slugify(title)
                hof[slug] = {
                    "title": title,
                    "ready": ready,
                    "style": style,
                    "composer": composer
                }
    print(f"Loaded {len(hof)} songs from Hall of Fame.")
    return hof

def read_episodes_metadata(path):
    """Read the Episodes metadata CSV and map (episode_number, date) to its attributes."""
    metadata = {}
    if not os.path.exists(path):
        print(f"Warning: Episodes metadata CSV not found at {path}")
        return metadata
        
    print(f"Reading Episodes metadata CSV from: {path}")
    with open(path, mode='r', encoding='utf-8-sig') as f:
        reader = csv.reader(f)
        header = next(reader)
        header = [h.strip().lower() for h in header]
        
        # Determine column indices
        date_idx = 0 # First column is date
        epi_idx = header.index('episode #') if 'episode #' in header else 1
        url_idx = header.index('url') if 'url' in header else 4
        tip_jar_idx = header.index('tip jar') if 'tip jar' in header else 7
        theme_idx = header.index('theme') if 'theme' in header else 8
        shirt_idx = header.index('shirt') if 'shirt' in header else 9
        notes_idx = header.index('notes') if 'notes' in header else 10
        
        for row in reader:
            if not row or len(row) <= max(epi_idx, url_idx):
                continue
            date = row[date_idx].strip()
            epi = row[epi_idx].strip()
            url = row[url_idx].strip()
            tip_jar = row[tip_jar_idx].strip() if len(row) > tip_jar_idx else ""
            theme = row[theme_idx].strip() if len(row) > theme_idx else ""
            shirt = row[shirt_idx].strip() if len(row) > shirt_idx else ""
            notes = row[notes_idx].strip() if len(row) > notes_idx else ""
            
            norm_date = normalize_date_str(date)
            
            metadata[(epi, norm_date)] = {
                "url": url,
                "tip_jar": tip_jar,
                "theme": theme,
                "shirt": shirt,
                "notes": notes
            }
            
    print(f"Loaded metadata for {len(metadata)} episode entries.")
    return metadata

def read_songs_metadata(path):
    """Parses Songs.csv once and extracts counts, date maps, episode groups, and song metadata."""
    songs_data = {}
    song_counts = {}
    epi_dates_map = {}
    episode_rows = []
    
    with open(path, mode='r', encoding='utf-8-sig') as f:
        reader = csv.reader(f)
        header = next(reader)
        header = [h.strip().lower() for h in header]
        
        date_idx = header.index('date') if 'date' in header else 0
        epi_idx = header.index('epi #') if 'epi #' in header else 1
        song_num_idx = header.index('song #') if 'song #' in header else 2
        url_idx = header.index('url') if 'url' in header else 4
        name_idx = header.index('name') if 'name' in header else 6
        tempo_idx = header.index('tempo') if 'tempo' in header else 9
        composer_idx = header.index('composer') if 'composer' in header else 10
        style_idx = header.index('style') if 'style' in header else 11
        notes_idx = header.index('notes') if 'notes' in header else 15
        offset_idx = header.index('offset') if 'offset' in header else 3
        
        rows = list(reader)
        
        # Pass 1: Gather dates per episode
        for row in rows:
            if not row or len(row) <= name_idx:
                continue
            date = row[date_idx].strip()
            epi = row[epi_idx].strip()
            if epi and date:
                if epi not in epi_dates_map:
                    epi_dates_map[epi] = set()
                epi_dates_map[epi].add(date)
                
        # Resolve canonical dates and rerun dates
        canonical_dates = {}
        for epi, dates in epi_dates_map.items():
            dates_list = list(dates)
            canonical_dates[epi] = max(dates_list, key=lambda d: dates_list.count(d))
            
        rerun_keys = set()
        for epi, dates in epi_dates_map.items():
            if len(dates) > 1:
                sorted_dates = sorted(list(dates), key=parse_date_key)
                for rerun_date in sorted_dates[1:]:
                    rerun_keys.add((epi, rerun_date))
                    
        # Pass 2: Populate song aggregates and episode setlist rows
        for row in rows:
            if not row or len(row) <= max(name_idx, date_idx):
                continue
                
            name = row[name_idx].strip()
            if not name:
                continue
                
            slug = slugify(name)
            song_counts[slug] = song_counts.get(slug, 0) + 1
            
            date = row[date_idx].strip()
            epi = row[epi_idx].strip()
            song_num = row[song_num_idx].strip()
            url = row[url_idx].strip()
            tempo = row[tempo_idx].strip()
            composer = row[composer_idx].strip()
            style = row[style_idx].strip()
            notes = row[notes_idx].strip()
            offset = row[offset_idx].strip()
            
            # Populate songs aggregate
            if slug not in songs_data:
                songs_data[slug] = {
                    "names": [],
                    "composer": None,
                    "style": None,
                    "performances": []
                }
                
            songs_data[slug]["names"].append(name)
            if composer and not songs_data[slug]["composer"]:
                songs_data[slug]["composer"] = composer
            if style and not songs_data[slug]["style"]:
                songs_data[slug]["style"] = style
                
            songs_data[slug]["performances"].append({
                "date": date,
                "episode": epi,
                "song_num": song_num,
                "url": url,
                "tempo": tempo,
                "notes": notes
            })
            
            # Populate raw row list for episode setlist aggregation
            episode_rows.append({
                "date": date,
                "epi": epi,
                "song_num": song_num,
                "url": url,
                "name": name,
                "slug": slug,
                "tempo": tempo,
                "composer": composer,
                "style": style,
                "notes": notes,
                "offset": offset
            })
            
    # Group rows by show instance (epi, date)
    episodes_data = {}
    for item in episode_rows:
        epi = item["epi"]
        date = item["date"]
        
        # Impute missing date if needed
        if not date and epi in canonical_dates:
            date = canonical_dates[epi]
            
        show_key = (epi, date)
        if show_key not in episodes_data:
            episodes_data[show_key] = {
                "episode": epi,
                "date": date,
                "youtube_url": None,
                "setlist": []
            }
            
        if item["url"] and not episodes_data[show_key]["youtube_url"]:
            # Format stream URL to base parameterless URL
            base_url = re.sub(r'\?t=\d+', '', item["url"])
            base_url = re.sub(r'&t=\d+s', '', base_url)
            episodes_data[show_key]["youtube_url"] = base_url
            
        episodes_data[show_key]["setlist"].append(item)
        
    return song_counts, songs_data, episodes_data, rerun_keys, canonical_dates

# Page Generation Sub-functions
def write_single_song_page(slug, title, composer, style, count, ready_rating, performances, rerun_keys, canonical_dates, out_dir):
    title_escaped = title.replace('"', '\\"')
    composer_escaped = composer.replace('"', '\\"')
    style_escaped = style.replace('"', '\\"')
    
    # Build YAML performances front-matter
    perf_fm = ""
    if performances:
        perf_fm += "\nperformances:"
        for perf in performances:
            # Calculate episode slug and rerun flag
            epi = perf["episode"]
            date = perf["date"]
            if not date and epi in canonical_dates:
                date = canonical_dates[epi]
                
            is_rerun = False
            epi_slug = ""
            if date:
                if epi:
                    is_rerun = (epi, date) in rerun_keys
                    if is_rerun:
                        epi_slug = f"episode-{slugify(epi)}-rerun-{slugify(date)}"
                    else:
                        epi_slug = f"episode-{slugify(epi)}"
                else:
                    epi_slug = f"show-{slugify(date)}"
                    
            notes_esc = perf["notes"].replace('"', '\\"') if perf["notes"] else ""
            
            perf_fm += f"\n  - date: \"{perf['date']}\""
            perf_fm += f"\n    url: \"{perf['url']}\""
            perf_fm += f"\n    episode: \"{epi}\""
            perf_fm += f"\n    episode_slug: \"{epi_slug}\""
            perf_fm += f"\n    tempo: \"{perf['tempo']}\""
            perf_fm += f"\n    notes: \"{notes_esc}\""
            perf_fm += f"\n    rerun: {str(is_rerun).lower()}"

    md_content = f"""---
layout: song
title: "{title_escaped}"
composer: "{composer_escaped}"
style: "{style_escaped}"
play_count: {count}
hall_of_fame: true
ready_rating: {ready_rating}{perf_fm}
---
"""
    file_path = os.path.join(out_dir, f"{slug}.md")
    with open(file_path, mode='w', encoding='utf-8') as f:
        f.write(md_content)

def write_one_offs_performances_feed(one_offs_performances, canonical_dates, rerun_keys, path):
    with open(path, mode='w', encoding='utf-8') as f:
        for song in one_offs_performances:
            title_esc = song["title"].replace('"', '\\"')
            comp_esc = song["composer"].replace('"', '\\"')
            style_esc = song["style"].replace('"', '\\"')
            notes_esc = song["notes"].replace('"', '\\"')
            
            # Calculate episode slug and title properties
            epi = song["episode"]
            date = song["date"]
            if not date and epi in canonical_dates:
                date = canonical_dates[epi]
                
            epi_title = "Show"
            epi_slug = ""
            if date:
                if epi:
                    is_rerun = (epi, date) in rerun_keys
                    if is_rerun:
                        epi_slug = f"episode-{slugify(epi)}-rerun-{slugify(date)}"
                        epi_title = f"#{epi} (Rerun)"
                    else:
                        epi_slug = f"episode-{slugify(epi)}"
                        epi_title = f"#{epi}"
                else:
                    epi_slug = f"show-{slugify(date)}"
                    epi_title = "Show"
            elif epi:
                epi_title = f"#{epi}"
                
            f.write(f"- title: \"{title_esc}\"\n")
            f.write(f"  slug: \"{song['slug']}\"\n")
            f.write(f"  composer: \"{comp_esc}\"\n")
            f.write(f"  style: \"{style_esc}\"\n")
            f.write(f"  date: \"{date}\"\n")
            f.write(f"  url: \"{song['url']}\"\n")
            f.write(f"  episode: \"{epi}\"\n")
            f.write(f"  episode_slug: \"{epi_slug}\"\n")
            f.write(f"  episode_title: \"{epi_title}\"\n")
            f.write(f"  tempo: \"{song['tempo']}\"\n")
            f.write(f"  notes: \"{notes_esc}\"\n")

def write_one_offs_summary_feed(sorted_one_offs_meta, path):
    with open(path, mode='w', encoding='utf-8') as f:
        for slug, meta in sorted_one_offs_meta:
            title_esc = meta["title"].replace('"', '\\"')
            comp_esc = meta["composer"].replace('"', '\\"')
            style_esc = meta["style"].replace('"', '\\"')
            f.write(f"- title: \"{title_esc}\"\n")
            f.write(f"  slug: \"{slug}\"\n")
            f.write(f"  composer: \"{comp_esc}\"\n")
            f.write(f"  style: \"{style_esc}\"\n")
            f.write(f"  play_count: {meta['play_count']}\n")

def generate_songs_and_data_feeds(songs_data, hof, rerun_keys, canonical_dates, out_dir):
    """Generates individual HOF song files and outputs consolidated one-off data files."""
    if os.path.exists(out_dir):
        for f in os.listdir(out_dir):
            if f.endswith('.md'):
                os.remove(os.path.join(out_dir, f))
    else:
        os.makedirs(out_dir, exist_ok=True)
        
    one_offs_performances = []
    one_offs_meta = {}
    multi_play_count = 0
    
    # Sort songs alphabetically by key
    for slug in sorted(songs_data.keys()):
        data = songs_data[slug]
        title = max(sorted(list(set(data["names"]))), key=data["names"].count)
        composer = data["composer"] or ""
        style = data["style"] or ""
        performances = data["performances"]
        
        # Sort performances by date
        def parse_perf_date_key(perf):
            parts = perf["date"].split('/')
            if len(parts) == 3:
                try:
                    return int(parts[2]), int(parts[0]), int(parts[1])
                except ValueError:
                    pass
            return (0, 0, 0)
            
        performances.sort(key=parse_perf_date_key)
        count = len(performances)
        
        if slug in hof:
            multi_play_count += 1
            hof_data = hof[slug]
            
            # Prefer HOF CSV values
            if hof_data["style"]:
                style = hof_data["style"]
            if hof_data["composer"]:
                composer = hof_data["composer"]
                
            ready_rating = hof_data["ready"] or "0"
            write_single_song_page(slug, title, composer, style, count, ready_rating, performances, rerun_keys, canonical_dates, out_dir)
        else:
            if count > 1:
                print(f"Warning: Song '{title}' was played {count} times but is not in the Hall of Fame.")
                
            for perf in performances:
                one_offs_performances.append({
                    "slug": slug,
                    "title": title,
                    "composer": composer,
                    "style": style,
                    "date": perf["date"],
                    "episode": perf["episode"],
                    "song_num": perf["song_num"],
                    "url": perf["url"],
                    "tempo": perf["tempo"],
                    "notes": perf["notes"]
                })
                
            if slug not in one_offs_meta:
                one_offs_meta[slug] = {
                    "title": title,
                    "composer": composer,
                    "style": style,
                    "play_count": count
                }
                
    # Sort one-off performances alphabetically by song title, then by date
    def parse_one_off_key(x):
        return x["title"].lower(), parse_perf_date_key(x)
    one_offs_performances.sort(key=parse_one_off_key)
    
    # Write one-offs performances structured YAML feed
    one_offs_perf_path = os.path.join(data_output_dir, "one_offs_performances.yml")
    write_one_offs_performances_feed(one_offs_performances, canonical_dates, rerun_keys, one_offs_perf_path)
            
    # Generate website/_data/one_offs.yml summary feed
    yaml_path = os.path.join(data_output_dir, "one_offs.yml")
    sorted_one_offs_meta = sorted(one_offs_meta.items(), key=lambda x: x[1]["title"].lower())
    write_one_offs_summary_feed(sorted_one_offs_meta, yaml_path)
            
    print(f"Generated {multi_play_count} individual Hall of Fame song pages.")
    print(f"Consolidated {len(one_offs_performances)} performances of {len(one_offs_meta)} unique non-rotation songs into website/_data/one_offs_performances.yml and website/_data/one_offs.yml.")

def write_single_episode_page(epi, date, data, rerun_keys, canonical_dates, metadata, hof_data, out_dir):
    setlist = data["setlist"]
    
    # Sort setlist by Song #
    def parse_song_num(item):
        try:
            return int(item["song_num"])
        except ValueError:
            return 999
    setlist.sort(key=parse_song_num)
    
    # Format date for Jekyll front-matter sorting
    date_formatted = ""
    norm_date = normalize_date_str(date)
    if date:
        parts = date.split('/')
        if len(parts) == 3:
            try:
                date_formatted = f"{int(parts[2]):04d}-{int(parts[0]):02d}-{int(parts[1]):02d}"
            except ValueError:
                pass
    if not date_formatted:
        date_formatted = "2000-01-01"
        
    is_rerun = (epi, date) in rerun_keys
    
    # Retrieve rich metadata from Episodes.csv
    meta_entry = metadata.get((epi, norm_date), {})
    if not meta_entry:
        meta_entry = metadata.get(("", norm_date), {})
        
    yt_url = meta_entry.get("url") or data["youtube_url"] or ""
    theme = meta_entry.get("theme") or ""
    shirt = meta_entry.get("shirt") or ""
    tip_jar = meta_entry.get("tip_jar") or ""
    notes = meta_entry.get("notes") or ""
    
    # Generate slug and title with long date formatting
    long_date = format_long_date(date)
    if epi:
        if is_rerun:
            slug = f"episode-{slugify(epi)}-rerun-{slugify(date)}"
            title = f"Episode {epi} ({long_date}) (Rerun)"
        else:
            slug = f"episode-{slugify(epi)}"
            title = f"Episode {epi} ({long_date})"
    else:
        slug = f"show-{slugify(date)}"
        title = f"Show ({long_date})"
        
    # Check if title slide image exists
    image_url = None
    for ext in ["jpg", "png", "jpeg"]:
        img_rel_path = f"assets/images/title-slides/{slug}.{ext}"
        img_abs_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "website", img_rel_path)
        if os.path.exists(img_abs_path):
            image_url = f"/{img_rel_path}"
            break
            
    title_escaped = title.replace('"', '\\"')
    theme_escaped = theme.replace('"', '\\"')
    shirt_escaped = shirt.replace('"', '\\"')
    tip_jar_escaped = tip_jar.replace('"', '\\"')
    notes_escaped = notes.replace('"', '\\"')
    image_fm = f'\nimage: "{image_url}"' if image_url else ""
    
    # Build YAML setlist front-matter
    setlist_fm = ""
    if setlist:
        setlist_fm += "\nsetlist:"
        for item in setlist:
            slug_song = item["slug"]
            is_hof = slug_song in hof_data
            if is_hof:
                style_val = hof_data[slug_song] if hof_data[slug_song] else item["style"]
            else:
                style_val = item["style"]
                
            time_str = format_offset_time(item["offset"])
            
            # Escape strings for YAML
            name_esc = item["name"].replace('"', '\\"')
            style_esc = style_val.replace('"', '\\"') if style_val else ""
            comp_esc = item["composer"].replace('"', '\\"') if item["composer"] else ""
            notes_esc = item["notes"].replace('"', '\\"') if item["notes"] else ""
            
            setlist_fm += f"\n  - song_num: \"{item['song_num']}\""
            setlist_fm += f"\n    name: \"{name_esc}\""
            setlist_fm += f"\n    slug: \"{slug_song}\""
            setlist_fm += f"\n    url: \"{item['url']}\""
            setlist_fm += f"\n    time: \"{time_str}\""
            setlist_fm += f"\n    style: \"{style_esc}\""
            setlist_fm += f"\n    composer: \"{comp_esc}\""
            setlist_fm += f"\n    notes: \"{notes_esc}\""
            setlist_fm += f"\n    hof: {str(is_hof).lower()}"

    md_content = f"""---
layout: episode
title: "{title_escaped}"
episode_number: "{epi}"
date_string: "{date}"
date: {date_formatted}
song_count: {len(setlist)}
rerun: {str(is_rerun).lower()}
theme: "{theme_escaped}"
shirt: "{shirt_escaped}"
tip_jar: "{tip_jar_escaped}"
notes: "{notes_escaped}"
youtube_url: "{yt_url}"{image_fm}{setlist_fm}
---
"""
    file_path = os.path.join(out_dir, f"{slug}.md")
    with open(file_path, mode='w', encoding='utf-8') as f:
        f.write(md_content)

def generate_episode_pages(episodes_data, rerun_keys, canonical_dates, metadata, out_dir):
    """Generates individual episode setlist markdown files."""
    if os.path.exists(out_dir):
        for f in os.listdir(out_dir):
            if f.endswith('.md'):
                os.remove(os.path.join(out_dir, f))
    else:
        os.makedirs(out_dir, exist_ok=True)
        
    # Load Hall of Fame CSV styles and slugs for layout lookup
    hof_data = {}
    if os.path.exists(hof_csv_path):
        with open(hof_csv_path, mode='r', encoding='utf-8-sig') as hf:
            r = csv.reader(hf)
            header = next(r)
            header = [h.strip().lower() for h in header]
            title_idx = header.index('title') if 'title' in header else 1
            style_idx = header.index('style') if 'style' in header else 6
            for r_row in r:
                if len(r_row) > max(title_idx, style_idx):
                    title = r_row[title_idx].strip()
                    style = r_row[style_idx].strip()
                    if title:
                        hof_data[slugify(title)] = style
                        
    for (epi, date), data in episodes_data.items():
        write_single_episode_page(epi, date, data, rerun_keys, canonical_dates, metadata, hof_data, out_dir)
            
    print(f"Generated {len(episodes_data)} episode files.")

def main():
    print("🚀 Starting Unified Friday Jazz Happy Hour Site Generator...")
    
    # 1. Read metadata
    metadata = read_episodes_metadata(episodes_csv_path)
    hof = read_hall_of_fame(hof_csv_path)
    
    # 2. Parse Songs CSV once
    song_counts, songs_data, episodes_data, rerun_keys, canonical_dates = read_songs_metadata(songs_csv_path)
    
    # 3. Generate Song pages and data feeds
    generate_songs_and_data_feeds(songs_data, hof, rerun_keys, canonical_dates, songs_output_dir)
    
    # 4. Generate Episode pages
    generate_episode_pages(episodes_data, rerun_keys, canonical_dates, metadata, episodes_output_dir)
    
    print("✅ Site generation successfully complete!")

if __name__ == "__main__":
    main()
