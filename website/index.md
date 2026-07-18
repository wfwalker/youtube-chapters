---
layout: default
title: "friday jazz happy hour"
subtitle: "Hi! My name is Bill Walker. On March 20th, 2020 I started doing a weekly live streaming show from my back room during the COVID-19 shelter-in-place. I'm still doing it every Friday, please join us!"
---

<div class="live-stream-card">
  <h3 class="live-stream-header">
    <span class="live-indicator"></span>
    Upcoming / Live Show
  </h3>
  <div class="responsive-video-container">
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
    <span class="nav-card-action">View Episodes »</span>
  </a>

  <a href="{{ '/hall-of-fame.html' | relative_url }}" class="nav-card">
    <div class="nav-card-header">
      <span class="nav-card-icon">🎹</span>
      <span class="nav-card-stat">{{ site.songs | size }}</span>
    </div>
    <h3 class="nav-card-title">Hall of Fame</h3>
    <p class="nav-card-description">Browse the core catalog of jazz standards, pop tunes, and originals that form the repertoire on Fridays.</p>
    <span class="nav-card-action">View Hall of Fame »</span>
  </a>

  <a href="{{ '/one-off-songs.html' | relative_url }}" class="nav-card">
    <div class="nav-card-header">
      <span class="nav-card-icon">⚗️</span>
      <span class="nav-card-stat">{{ site.data.one_offs | size }}</span>
    </div>
    <h3 class="nav-card-title">One-Off Songs</h3>
    <p class="nav-card-description">Explore unique performances, modular synth improvisations, and special requests.</p>
    <span class="nav-card-action">View One-Offs »</span>
  </a>
</div>
