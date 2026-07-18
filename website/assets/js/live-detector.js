// Load YouTube IFrame Player API dynamically
var tag = document.createElement('script');
tag.src = "https://www.youtube.com/iframe_api";
var firstScriptTag = document.getElementsByTagName('script')[0];
if (firstScriptTag) {
  firstScriptTag.parentNode.insertBefore(tag, firstScriptTag);
} else {
  document.head.appendChild(tag);
}

var player;
window.onYouTubeIframeAPIReady = function() {
  var iframe = document.getElementById('live-stream-iframe');
  if (!iframe) return; // Exit if the live player is not on this page
  
  player = new YT.Player('live-stream-iframe', {
    events: {
      'onReady': onPlayerReady,
      'onError': onPlayerError
    }
  });
};

function onPlayerReady(event) {
  // If the video is unavailable, the player state stays as -1 (unstarted).
  // We check after 2.5s to allow for initial buffering, else fallback.
  setTimeout(function() {
    try {
      if (player.getPlayerState() === -1) {
        showFallback();
      }
    } catch (e) {
      showFallback();
    }
  }, 2500);
}

function onPlayerError(event) {
  showFallback();
}

function showFallback() {
  var card = document.getElementById('live-stream-card');
  var fallback = document.getElementById('live-stream-fallback');
  if (card && fallback) {
    card.style.display = 'none';
    fallback.style.display = 'block';
  }
}
