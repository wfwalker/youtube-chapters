---
layout: default
title: "All Episodes"
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
  
  .episodes-list {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
    gap: 1.5rem;
  }
  
  .episode-card {
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
  
  .episode-card:hover {
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
  
  .card-date {
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
  <h1 class="hero-title">Episodes</h1>
  <p class="hero-subtitle">Chronological record of live performances. Click an episode to see its full setlist, tempos, styles, and timing details.</p>
</div>

<div class="grid-header">
  <h2 class="grid-title">All Shows ({{ site.episodes | size }})</h2>
</div>

<div class="episodes-list">
  {% assign sorted_episodes = site.episodes | sort: "date" | reverse %}
  {% for epi in sorted_episodes %}
    <a href="{{ epi.url | relative_url }}" class="episode-card">
      <div class="card-top">
        <h3 class="card-title">
          {% if epi.episode_number and epi.episode_number != "" %}
            Episode #{{ epi.episode_number }}
          {% else %}
            Live Stream Show
          {% endif %}
        </h3>
        <span class="card-date">{{ epi.date_string }}</span>
      </div>
      <div class="card-meta">
        {% if epi.rerun %}
          <span class="badge-style" style="background-color: rgba(239, 68, 68, 0.15); color: #f87171; border: 1px solid rgba(239, 68, 68, 0.25);">Rerun</span>
        {% else %}
          <span class="badge-style">YouTube Stream</span>
        {% endif %}
        <span class="badge-count">{{ epi.song_count }} Songs</span>
      </div>
    </a>
  {% endfor %}
</div>
