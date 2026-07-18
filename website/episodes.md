---
layout: default
title: "Episodes"
subtitle: "Chronological record of live performances. Click an episode to see its full setlist, tempos, styles, and timing details."
---

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
      {% if epi.theme and epi.theme != "" or epi.tip_jar and epi.tip_jar != "" %}
        <div class="episode-card-body">
          {% if epi.theme and epi.theme != "" %}
            <div class="episode-card-body-item">🎨 Theme: {{ epi.theme }}</div>
          {% endif %}
          {% if epi.tip_jar and epi.tip_jar != "" %}
            <div class="episode-card-body-item">❤️ Charity: {{ epi.tip_jar }}</div>
          {% endif %}
        </div>
      {% endif %}
      <div class="card-meta">
        {% if epi.rerun %}
          <span class="badge-style badge-style--rerun">Rerun</span>
        {% else %}
          <span class="badge-style">YouTube Stream</span>
        {% endif %}
        <span class="badge-count">{{ epi.song_count }} Songs</span>
      </div>
    </a>
  {% endfor %}
</div>
