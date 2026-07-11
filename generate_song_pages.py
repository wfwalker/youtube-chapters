import csv
import os
import re

csv_path = "/Users/walker/Dropbox/youtube-chapters/FJHH songs - Songs.csv"
hof_csv_path = "/Users/walker/Dropbox/youtube-chapters/FJHH songs - Hall of Fame.csv"
output_dir = "/Users/walker/Dropbox/youtube-chapters/website/_songs"

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
        
        for row in reader:
            if not row or len(row) <= max(title_idx, ready_idx, style_idx):
                continue
            title = row[title_idx].strip()
            ready = row[ready_idx].strip()
            style = row[style_idx].strip()
            if title:
                slug = slugify(title)
                hof[slug] = {
                    "title": title,
                    "ready": ready,
                    "style": style
                }
    print(f"Loaded {len(hof)} songs from Hall of Fame.")
    return hof

def parse_csv(path):
    songs_data = {}
    epi_dates_map = {}
    
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
        
        rows = list(reader)
        
        # Pass 1: Gather all dates per episode number
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
                    
        # Pass 2: Build song data
        for row in rows:
            if not row or len(row) <= max(name_idx, date_idx):
                continue
                
            name = row[name_idx].strip()
            if not name:
                continue
                
            slug = slugify(name)
            if not slug:
                continue
                
            date = row[date_idx].strip()
            epi = row[epi_idx].strip()
            song_num = row[song_num_idx].strip()
            url = row[url_idx].strip()
            tempo = row[tempo_idx].strip()
            composer = row[composer_idx].strip()
            style = row[style_idx].strip()
            notes = row[notes_idx].strip()
            
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
            
    return songs_data, rerun_keys, canonical_dates

def get_episode_link(epi, date, rerun_keys, canonical_dates):
    if not date and epi in canonical_dates:
        date = canonical_dates[epi]
    if not date:
        return "#%s" % epi if epi else "Show"
        
    if epi:
        is_rerun = (epi, date) in rerun_keys
        if is_rerun:
            slug = f"episode-{slugify(epi)}-rerun-{slugify(date)}"
        else:
            slug = f"episode-{slugify(epi)}"
        return '<a href="{{ \'/episodes/\' | relative_url }}%s/">#%s</a>' % (slug, epi)
    else:
        slug = f"show-{slugify(date)}"
        return '<a href="{{ \'/episodes/\' | relative_url }}%s/">Show</a>' % slug

def generate_markdown(songs_data, hof, rerun_keys, canonical_dates, out_dir):
    # Clean out the songs directory to avoid orphan files
    if os.path.exists(out_dir):
        for f in os.listdir(out_dir):
            if f.endswith('.md'):
                os.remove(os.path.join(out_dir, f))
    else:
        os.makedirs(out_dir, exist_ok=True)
        
    one_offs_performances = []
    one_offs_meta = {} # slug -> {title, composer, style, count}
    multi_play_count = 0
    
    data_dir = "/Users/walker/Dropbox/youtube-chapters/website/_data"
    os.makedirs(data_dir, exist_ok=True)
    
    # Sort songs alphabetically by key
    for slug in sorted(songs_data.keys()):
        data = songs_data[slug]
        title = max(set(data["names"]), key=data["names"].count)
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
        
        # Check if song is in Hall of Fame
        if slug in hof:
            multi_play_count += 1
            hof_data = hof[slug]
            
            # Style override from Hall of Fame CSV
            if hof_data["style"]:
                style = hof_data["style"]
                
            ready_rating = hof_data["ready"] or "0"
            title_escaped = title.replace('"', '\\"')
            composer_escaped = composer.replace('"', '\\"')
            style_escaped = style.replace('"', '\\"')
            
            md_content = f"""---
layout: song
title: "{title_escaped}"
composer: "{composer_escaped}"
style: "{style_escaped}"
play_count: {count}
hall_of_fame: true
ready_rating: {ready_rating}
---

# {title}

Played **{count}** times in the live shows.

| Date | Episode | Tempo | Notes |
| --- | --- | --- | --- |
"""
            for perf in performances:
                date_link = f"[{perf['date']}]({perf['url']})" if perf['url'] else perf['date']
                epi_link = get_episode_link(perf['episode'], perf['date'], rerun_keys, canonical_dates)
                md_content += f"| {date_link} | {epi_link} | {perf['tempo']} | {perf['notes']} |\n"
                
            file_path = os.path.join(out_dir, f"{slug}.md")
            with open(file_path, mode='w', encoding='utf-8') as f:
                f.write(md_content)
        else:
            # Song is NOT in Hall of Fame: treat as one-off / non-regular-rotation
            if count > 1:
                print(f"Warning: Song '{title}' was played {count} times but is not in the Hall of Fame.")
                
            # Log all performances to list
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
                
            # Log song aggregate metadata for the homepage feed
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
    
    # 2. Write one-offs performances structured YAML feed
    one_offs_perf_path = os.path.join(data_dir, "one_offs_performances.yml")
    with open(one_offs_perf_path, mode='w', encoding='utf-8') as f:
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
            
    # 3. Generate website/_data/one_offs.yml summary feed for home page
    yaml_path = os.path.join(data_dir, "one_offs.yml")
    sorted_one_offs_meta = sorted(one_offs_meta.items(), key=lambda x: x[1]["title"].lower())
    with open(yaml_path, mode='w', encoding='utf-8') as f:
        for slug, meta in sorted_one_offs_meta:
            title_esc = meta["title"].replace('"', '\\"')
            comp_esc = meta["composer"].replace('"', '\\"')
            style_esc = meta["style"].replace('"', '\\"')
            f.write(f"- title: \"{title_esc}\"\n")
            f.write(f"  slug: \"{slug}\"\n")
            f.write(f"  composer: \"{comp_esc}\"\n")
            f.write(f"  style: \"{style_esc}\"\n")
            f.write(f"  play_count: {meta['play_count']}\n")
            
    print(f"Generated {multi_play_count} individual Hall of Fame song pages.")
    print(f"Consolidated {len(one_offs_performances)} performances of {len(one_offs_meta)} unique non-rotation songs into website/_data/one_offs_performances.yml and website/_data/one_offs.yml.")

if __name__ == "__main__":
    hof = read_hall_of_fame(hof_csv_path)
    songs_data, rerun_keys, canonical_dates = parse_csv(csv_path)
    generate_markdown(songs_data, hof, rerun_keys, canonical_dates, output_dir)
