---
layout: default
title: "All Songs"
---

<style>
  .hero-section {
    text-align: center;
    margin-bottom: 4rem;
    padding: 3rem 1rem;
  }
  
  .hero-title {
    font-family: 'Outfit', sans-serif;
    font-weight: 800;
    font-size: 3.5rem;
    margin: 0 0 1rem 0;
    background: var(--accent-gradient);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    letter-spacing: -0.03em;
    line-height: 1.1;
  }
  
  .hero-subtitle {
    color: var(--text-secondary);
    font-size: 1.2rem;
    max-width: 600px;
    margin: 0 auto;
    font-weight: 400;
  }
  
  .grid-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 2rem;
    border-bottom: 1px solid var(--border-color);
    padding-bottom: 1rem;
  }
  
  .grid-title {
    font-family: 'Outfit', sans-serif;
    font-size: 1.6rem;
    font-weight: 600;
    margin: 0;
    letter-spacing: -0.01em;
  }
  
  .songs-list {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
    gap: 1.5rem;
  }
  
  .song-card {
    background: var(--card-bg);
    border: 1px solid var(--border-color);
    border-radius: 16px;
    padding: 1.6rem;
    text-decoration: none;
    color: var(--text-primary);
    transition: transform 0.2s cubic-bezier(0.16, 1, 0.3, 1), border-color 0.2s ease, box-shadow 0.2s ease;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
    min-height: 90px;
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
    backdrop-filter: blur(8px);
    -webkit-backdrop-filter: blur(8px);
  }
  
  .song-card:hover {
    transform: translateY(-5px);
    border-color: var(--accent-color);
    box-shadow: 0 10px 30px rgba(59, 130, 246, 0.15);
  }
  
  .card-top {
    margin-bottom: 1rem;
  }
  
  .card-title {
    font-family: 'Outfit', sans-serif;
    font-size: 1.3rem;
    font-weight: 600;
    margin: 0 0 0.4rem 0;
    letter-spacing: -0.01em;
    line-height: 1.25;
  }
  
  .card-composer {
    color: var(--text-secondary);
    font-size: 0.85rem;
  }
  
  .card-meta {
    color: var(--text-secondary);
    font-size: 0.85rem;
    display: flex;
    justify-content: space-between;
    align-items: center;
    border-top: 1px solid rgba(255, 255, 255, 0.04);
    padding-top: 0.8rem;
  }
  
  .badge-style {
    background-color: rgba(255, 255, 255, 0.04);
    padding: 0.2rem 0.6rem;
    border-radius: 6px;
    font-size: 0.75rem;
    text-transform: capitalize;
  }
  
  .badge-count {
    color: var(--accent-hover);
    font-weight: 600;
    font-size: 0.85rem;
  }
</style>

<div class="hero-section">
  <h1 class="hero-title">Songs</h1>
  <p class="hero-subtitle">Exploring all songs performed live by Bill Walker. Searchable log of show dates, styles, tempos, and performance notes.</p>
</div>

<div class="grid-header">
  <h2 class="grid-title">Regular Rotation Songs ({{ site.songs | size }})</h2>
</div>

<div class="songs-list">
  {% assign sorted_songs = site.songs | sort: "play_count" | reverse %}
  {% for song in sorted_songs %}
    <a href="{{ song.url | relative_url }}" class="song-card">
      <div class="card-top">
        <h3 class="card-title">{{ song.title }}</h3>
        {% if song.composer and song.composer != "" %}
          <span class="card-composer">by {{ song.composer }}</span>
        {% endif %}
      </div>
      <div class="card-meta">
        {% if song.style and song.style != "" %}
          <span class="badge-style">{{ song.style }}</span>
        {% else %}
          <span></span>
        {% endif %}
        <span class="badge-count">Played {{ song.play_count }}x</span>
      </div>
    </a>
  {% endfor %}
</div>

<div class="grid-header" style="margin-top: 4rem;">
  <h2 class="grid-title">One-Off Songs ({{ site.data.one_offs | size }})</h2>
  <a href="{{ '/one-offs.html' | relative_url }}" style="color: var(--accent-hover); text-decoration: none; font-size: 0.95rem; font-weight: 500; transition: color 0.2s ease;">View Full Table &rarr;</a>
</div>

<div class="songs-list">
  {% for song in site.data.one_offs %}
    <a href="{{ '/one-offs.html' | relative_url }}#{{ song.slug }}" class="song-card">
      <div class="card-top">
        <h3 class="card-title">{{ song.title }}</h3>
        {% if song.composer and song.composer != "" %}
          <span class="card-composer">by {{ song.composer }}</span>
        {% endif %}
      </div>
      <div class="card-meta">
        {% if song.style and song.style != "" %}
          <span class="badge-style">{{ song.style }}</span>
        {% else %}
          <span></span>
        {% endif %}
        <span class="badge-count">Played 1x</span>
      </div>
    </a>
  {% endfor %}
</div>


