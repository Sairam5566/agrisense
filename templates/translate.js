(function(){
  const ENDPOINT = '/api/translate/batch';
  const DEFAULT_SOURCE = 'en';

  // Cache original text so we can restore when switching back to English
  const ORIGINAL_KEY = '__orig_text__';

  function getPreferredLanguage(){
    try {
      const v = localStorage.getItem('preferred_language') || 'en';
      return v;
    } catch { return 'en'; }
  }

  function setPreferredLanguage(lang){
    try { localStorage.setItem('preferred_language', lang); } catch {}
  }

  function collectTargets(){
    const nodes = [];
    // Generic dynamic markers
    document.querySelectorAll('[data-translate-dynamic], [data-translate-auto]')
      .forEach(el => nodes.push(el));
    // News page specific
    document.querySelectorAll('.news-title, .news-description')
      .forEach(el => nodes.push(el));
    // Common content selectors across pages (exclude elements already handled by static dictionary)
    document.querySelectorAll('h1:not([data-translate]), h2:not([data-translate]), h3:not([data-translate]), h4:not([data-translate]), h5:not([data-translate]), h6:not([data-translate]), p:not([data-translate]), li:not([data-translate]), td:not([data-translate]), th:not([data-translate]), span:not([data-translate]), label:not([data-translate]), small:not([data-translate]), .lead:not([data-translate])')
      .forEach(el => nodes.push(el));
    // Do NOT translate header/nav containers; header is handled by changeLanguage()
    const isInHeader = (el) => !!el.closest('.app-navbar');
    // Only translate leaf nodes (no element children) to avoid wiping icons/markup
    const isLeaf = (el) => !el.children || el.children.length === 0;
    // Avoid duplicates while preserving order
    const seen = new Set();
    const out = [];
    for (const n of nodes) {
      if (isInHeader(n)) continue;
      if (!isLeaf(n)) continue;
      if (!seen.has(n)) { seen.add(n); out.push(n); }
    }
    // Limit to a reasonable batch size to avoid quota spikes
    return out.slice(0, 200);
  }

  function storeOriginals(nodes){
    nodes.forEach(n => {
      if (!n.dataset) return;
      if (!n.dataset.origText) {
        const t = (n.innerText || '').trim();
        // Only store once; avoid huge memory
        if (t) n.dataset.origText = t;
      }
    });
  }

  function restoreOriginals(nodes){
    nodes.forEach(n => {
      if (n.dataset && typeof n.dataset.origText !== 'undefined') {
        n.innerText = n.dataset.origText;
      }
    });
  }

  async function translateDynamicContent(lang){
    const nodes = collectTargets();
    // Always store originals before any modification
    storeOriginals(nodes);
    if (!lang || lang === 'en') {
      // Restore original English text
      restoreOriginals(nodes);
      return;
    }

    const texts = nodes.map(n => (n.innerText || '').trim());
    // Filter out empty strings and very short tokens
    const items = [];
    const mapping = [];
    texts.forEach((t, idx) => {
      if (t && /[a-zA-Z\u0900-\u097F]/.test(t)) { // simple alpha or Devanagari check
        items.push(t);
        mapping.push(idx);
      }
    });
    if (!items.length) return;

    try {
      const res = await fetch(ENDPOINT, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ texts: items, target: lang, source: DEFAULT_SOURCE })
      });
      if (!res.ok) {
        // Silently fail to avoid blocking UI
        return;
      }
      const data = await res.json();
      const out = data.translations || [];
      // Use the same collected nodes order
      mapping.forEach((origIdx, i) => {
        const el = nodes[origIdx];
        if (!el) return;
        const translated = out[i];
        if (translated && typeof translated === 'string') {
          el.innerText = translated;
        }
      });
    } catch(err) {
      // swallow errors by default
      console.warn('Translation error:', err);
    }
  }

  // Expose for manual call
  window.translateDynamicContent = translateDynamicContent;

  // Wrap changeLanguage if present so dynamic text also updates
  function wrapChangeLanguage(){
    if (!window.changeLanguage || window.changeLanguage.__wrapped) return;
    const prev = window.changeLanguage;
    const wrapped = async function(lang){
      try { setPreferredLanguage(lang); } catch {}
      if (typeof prev === 'function') await prev(lang);
      // Immediately translate dynamic content so header and body update together
      // Run in requestAnimationFrame to ensure any synchronous DOM updates from prev() have applied
      if (typeof requestAnimationFrame === 'function') {
        requestAnimationFrame(() => translateDynamicContent(lang));
      } else {
        translateDynamicContent(lang);
      }
    };
    wrapped.__wrapped = true;
    window.changeLanguage = wrapped;
  }

  // Init on readiness
  document.addEventListener('DOMContentLoaded', () => {
    // Try to wrap immediately and also after a short delay (in case base.js defines later)
    wrapChangeLanguage();
    setTimeout(wrapChangeLanguage, 200);

    const lang = getPreferredLanguage();
    // Kick off translation for dynamic parts on load immediately to avoid staggered updates
    if (typeof requestAnimationFrame === 'function') {
      requestAnimationFrame(() => translateDynamicContent(lang));
    } else {
      translateDynamicContent(lang);
    }
  });
})();
