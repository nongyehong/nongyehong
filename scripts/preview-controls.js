// Preview controls only. Published animations live inside the SVG images.
const preference = matchMedia('(prefers-reduced-motion: reduce)');
const status = document.querySelector('#motion-status');
let replays = 0;

function showStatus() {
  status.textContent = preference.matches
    ? 'Reduced motion is enabled. Entrance animations respect this preference.'
    : `Entrance animations are enabled${replays ? ` · Replayed ${replays} time${replays === 1 ? '' : 's'}` : ''}. Use the button above to replay.`;
}

document.querySelector('#replay-motion').addEventListener('click', () => {
  const token = crypto.randomUUID();
  const position = {left: window.scrollX, top: window.scrollY};
  // Keep every replaced image's layout box while its new SVG timeline loads.
  // Otherwise intrinsic-size loss can shrink the page and clamp scrollY.
  for (const image of document.querySelectorAll('article img')) {
    if (!image.naturalWidth || !image.naturalHeight) continue;
    image.style.aspectRatio = `${image.naturalWidth} / ${image.naturalHeight}`;
    if (!image.hasAttribute('width')) image.style.width = `${image.naturalWidth}px`;
  }
  for (const element of document.querySelectorAll('article img[src]')) {
    const url = new URL(element.getAttribute('src'), location.href);
    url.searchParams.set('preview', token);
    element.setAttribute('src', url.pathname + url.search + url.hash);
  }
  replays += 1;
  showStatus();
  requestAnimationFrame(() => window.scrollTo({...position, behavior:'instant'}));
});
preference.addEventListener('change', showStatus);
showStatus();
