/* Gemeinsam für alle Seiten: Service Worker anmelden und Verweise innerhalb der App im selben Fenster öffnen. */
(() => {
  const root = new URL('../', document.currentScript.src);

  if ('serviceWorker' in navigator) {
    addEventListener('load', () => {
      navigator.serviceWorker.register(new URL('sw.js', root)).catch(() => {});
    });
  }

  // Die Trainer öffnen Querverweise mit target="_blank". Innerhalb der App
  // würde das im installierten Modus den Browser starten – deshalb hier abfangen.
  document.addEventListener('click', e => {
    const a = e.target.closest && e.target.closest('a[target="_blank"]');
    if (!a || a.origin !== location.origin || e.defaultPrevented) return;
    if (e.button !== 0 || e.metaKey || e.ctrlKey || e.shiftKey || e.altKey) return;
    e.preventDefault();
    location.href = a.href;
  });
})();
