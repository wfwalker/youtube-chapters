---
layout: default
title: "Friday Jazz Happy Hour Archive"
---

<style>
  .dashboard-hero {
    text-align: center;
    margin: 3rem auto 3.5rem auto;
    padding: 3rem 1.5rem;
    max-width: 800px;
  }
  
  .dashboard-title {
    font-family: var(--font-title);
    font-weight: var(--font-title-weight);
    font-size: 4rem;
    margin: 0 0 1rem 0;
    background: var(--accent-gradient);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    line-height: 1.1;
  }
  
  .dashboard-subtitle {
    color: var(--text-secondary);
    font-size: 1.25rem;
    line-height: 1.6;
    font-weight: 400;
  }

  .navigation-grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 1.5rem;
    margin-bottom: 5rem;
  }

  .nav-card {
    background: var(--card-bg);
    border: 1px solid var(--border-color);
    border-radius: 20px;
    padding: 2.2rem;
    text-decoration: none;
    color: var(--text-primary);
    transition: transform 0.25s cubic-bezier(0.16, 1, 0.3, 1), border-color 0.25s ease, box-shadow 0.25s ease;
    display: flex;
    flex-direction: column;
    height: 100%;
    box-sizing: border-box;
    backdrop-filter: blur(12px);
    -webkit-backdrop-filter: blur(12px);
    box-shadow: 0 4px 30px rgba(0, 0, 0, 0.15);
  }

  .nav-card:hover {
    transform: translateY(-6px);
    border-color: var(--accent-color);
    box-shadow: 0 12px 40px rgba(59, 130, 246, 0.18);
  }

  .nav-card-header {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    margin-bottom: 1.2rem;
  }

  .nav-card-icon {
    font-size: 2.2rem;
    margin: 0;
    line-height: 1;
    display: inline-block;
  }

  .nav-card-stat {
    font-family: var(--font-title);
    font-size: 2.6rem;
    font-weight: var(--font-title-weight);
    line-height: 1;
    background: linear-gradient(135deg, #ffffff, #a1a1aa);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
  }

  .nav-card-title {
    font-family: var(--font-title);
    font-size: 1.45rem;
    font-weight: var(--font-title-weight);
    margin: 0 0 0.8rem 0;
    line-height: 1.25;
  }

  .nav-card-description {
    color: var(--text-secondary);
    font-size: 0.95rem;
    line-height: 1.5;
    margin: 0 0 1.5rem 0;
    flex-grow: 1;
  }

  .nav-card-action {
    color: var(--accent-hover);
    font-size: 0.9rem;
    font-weight: 600;
    display: flex;
    align-items: center;
    gap: 0.25rem;
    transition: gap 0.2s ease;
  }

  .nav-card:hover .nav-card-action {
    gap: 0.5rem;
  }

  @media (max-width: 800px) {
    .navigation-grid {
      grid-template-columns: 1fr;
      gap: 1.2rem;
    }
    
    .dashboard-title {
      font-size: 2.8rem;
    }
  }

  .live-stream-card {
    background: var(--card-bg);
    border: 1px solid var(--border-color);
    border-radius: 20px;
    padding: 2rem;
    margin: 0 auto 3.5rem auto;
    max-width: 700px;
    text-align: center;
    backdrop-filter: blur(12px);
    -webkit-backdrop-filter: blur(12px);
    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.15);
  }
  
  .live-stream-header {
    font-family: var(--font-title);
    font-weight: var(--font-title-weight);
    font-size: 1.5rem;
    margin-top: 0;
    margin-bottom: 1.2rem;
    color: var(--text-primary);
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 0.6rem;
  }
  
  .live-indicator {
    display: inline-block;
    width: 10px;
    height: 10px;
    background-color: #ef4444;
    border-radius: 50%;
    box-shadow: 0 0 0 0 rgba(239, 68, 68, 0.7);
    animation: pulse-live 1.5s infinite;
  }
  
  @keyframes pulse-live {
    0% {
      transform: scale(0.95);
      box-shadow: 0 0 0 0 rgba(239, 68, 68, 0.7);
    }
    70% {
      transform: scale(1);
      box-shadow: 0 0 0 8px rgba(239, 68, 68, 0);
    }
    100% {
      transform: scale(0.95);
      box-shadow: 0 0 0 0 rgba(239, 68, 68, 0);
    }
  }

  .video-responsive {
    position: relative;
    padding-bottom: 56.25%; /* 16:9 ratio */
    height: 0;
    overflow: hidden;
    border-radius: 12px;
    border: 1px solid var(--border-color);
  }
  
  .video-responsive iframe {
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
  }
</style>

<div class="dashboard-hero">
  <h1 class="dashboard-title">Friday Jazz Happy Hour</h1>
  <p class="dashboard-subtitle">Hi! My name is Bill Walker. On March 20th, 2020 I started doing a weekly live streaming show from my back room during the COVID-19 shelter-in-place. I'm still doing it every Friday, please join us!
</p>
</div>

<div class="live-stream-card">
  <h3 class="live-stream-header">
    <span class="live-indicator"></span>
    Upcoming / Live Show
  </h3>
  <div class="video-responsive">
    <iframe src="https://www.youtube.com/embed/live_stream?channel=UCsfG2kMhKa8QfTGdo9zawNg" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" allowfullscreen></iframe>
  </div>
</div>

<div class="navigation-grid">
  <a href="{{ '/episodes.html' | relative_url }}" class="nav-card">
    <div class="nav-card-header">
      <span class="nav-card-icon">📅</span>
      <span class="nav-card-stat">{{ site.episodes | size }}</span>
    </div>
    <h3 class="nav-card-title">Episodes</h3>
    <p class="nav-card-description">Scan the chronological history of all our shows with setlists and charity links.</p>
    <span class="nav-card-action">View Episodes &rarr;</span>
  </a>

  <a href="{{ '/hall-of-fame.html' | relative_url }}" class="nav-card">
    <div class="nav-card-header">
      <span class="nav-card-icon">🎹</span>
      <span class="nav-card-stat">{{ site.songs | size }}</span>
    </div>
    <h3 class="nav-card-title">Hall of Fame</h3>
    <p class="nav-card-description">Browse the core catalog of jazz standards, pop tunes, and originals that form the repertoire on Fridays.</p>
    <span class="nav-card-action">View Hall of Fame &rarr;</span>
  </a>

  <a href="{{ '/one-off-songs.html' | relative_url }}" class="nav-card">
    <div class="nav-card-header">
      <span class="nav-card-icon">⚗️</span>
      <span class="nav-card-stat">{{ site.data.one_offs | size }}</span>
    </div>
    <h3 class="nav-card-title">One-Off Songs</h3>
    <p class="nav-card-description">Explore unique performances, modular synth improvisations, and special requests.</p>
    <span class="nav-card-action">View One-Offs &rarr;</span>
  </a>
</div>
