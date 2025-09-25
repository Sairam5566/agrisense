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
    
    // Feature cards - specifically target card content
    document.querySelectorAll('.feature-card h4:not([data-translate]), .feature-card p:not([data-translate]), .feature-card .btn:not([data-translate])')
      .forEach(el => nodes.push(el));
    
    // Common content selectors across pages (exclude elements already handled by static dictionary)
    document.querySelectorAll('h1:not([data-translate]), h2:not([data-translate]), h3:not([data-translate]), h4:not([data-translate]), h5:not([data-translate]), h6:not([data-translate]), p:not([data-translate]), li:not([data-translate]), td:not([data-translate]), th:not([data-translate]), span:not([data-translate]):not(.navbar-brand span), label:not([data-translate]), small:not([data-translate]), .lead:not([data-translate]), .btn:not([data-translate])')
      .forEach(el => nodes.push(el));
    
    // Specifically target button text content
    document.querySelectorAll('button:not([data-translate]), .btn:not([data-translate]), a.btn:not([data-translate])')
      .forEach(el => {
        // Only add buttons that have text content and aren't in header
        if (el.textContent.trim() && !el.closest('.app-navbar')) {
          nodes.push(el);
        }
      });
    
    // Do NOT translate header/nav containers; header is handled by changeLanguage()
    const isInHeader = (el) => !!el.closest('.app-navbar, .navbar');
    
    // Check if element has only text content or simple inline elements
    const isTranslatable = (el) => {
      // Skip elements that are purely icons or have no text
      const text = el.textContent.trim();
      if (!text) return false;
      
      // Skip elements that are just icons (common patterns)
      if (text.match(/^[\u{1F300}-\u{1F9FF}]$/u)) return false; // emoji only
      if (text.match(/^[<>←→↑↓▲▼◀▶]+$/)) return false; // arrow symbols only
      
      // Allow elements with mixed content but prioritize text
      return true;
    };
    
    // Avoid duplicates while preserving order
    const seen = new Set();
    const out = [];
    for (const n of nodes) {
      if (isInHeader(n)) continue;
      if (!isTranslatable(n)) continue;
      if (!seen.has(n)) { 
        seen.add(n); 
        out.push(n); 
      }
    }
    
    // Limit to a reasonable batch size to avoid quota spikes
    return out.slice(0, 300);
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
      if (n.dataset && n.dataset.origText) {
        n.innerText = n.dataset.origText;
      }
    });
  }

  // Clear all translations and restore to English
  function clearAllTranslations() {
    const allElements = document.querySelectorAll('[data-orig-text]');
    allElements.forEach(el => {
      if (el.dataset.origText) {
        el.innerText = el.dataset.origText;
      }
    });
  }

  // Force restore all elements to original English text
  function forceRestoreToEnglish() {
    const allElements = document.querySelectorAll('*');
    allElements.forEach(el => {
      if (el.dataset && el.dataset.origText) {
        el.innerText = el.dataset.origText;
        console.log(`Restored: "${el.dataset.origText}"`);
      }
    });
  }

  async function translateDynamicContent(lang){
    console.log(`Starting translation to: ${lang}`);
    
    const nodes = collectTargets();
    // Always store originals before any modification
    storeOriginals(nodes);
    
    // FORCE restore to English first - this is critical!
    console.log('Restoring to English first...');
    restoreOriginals(nodes);
    
    // Also force restore any elements that might have been missed
    forceRestoreToEnglish();
    
    if (!lang || lang === 'en') {
      console.log('Staying in English');
      return;
    }
    
    // Small delay to ensure DOM updates are complete
    await new Promise(resolve => setTimeout(resolve, 100));
    
    console.log(`Translating ${nodes.length} elements to ${lang}`);

    const texts = nodes.map(n => (n.innerText || '').trim());
    // Filter out empty strings and very short tokens
    const items = [];
    const mapping = [];
    texts.forEach((t, idx) => {
      // Enhanced text detection for multiple scripts and languages
      if (t && t.length > 1 && /[a-zA-Z\u0900-\u097F\u0980-\u09FF\u0A00-\u0A7F\u0A80-\u0AFF\u0B00-\u0B7F\u0B80-\u0BFF\u0C00-\u0C7F\u0C80-\u0CFF\u0D00-\u0D7F\u0D80-\u0DFF\u1C50-\u1C7F]/.test(t)) {
        // Covers: Latin, Devanagari, Bengali, Gurmukhi, Gujarati, Oriya, Tamil, Telugu, Kannada, Malayalam, Sinhala, Ol Chiki
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
          // Handle buttons and elements with icons specially
          if (el.tagName === 'BUTTON' || el.classList.contains('btn')) {
            // Preserve icons and update only text content
            const iconElements = el.querySelectorAll('i, .fas, .far, .fab');
            const hasIcons = iconElements.length > 0;
            
            if (hasIcons) {
              // Store icons
              const icons = Array.from(iconElements).map(icon => icon.outerHTML);
              // Update text while preserving structure
              const originalHTML = el.innerHTML;
              const textOnly = el.textContent.trim();
              const newHTML = originalHTML.replace(textOnly, translated);
              el.innerHTML = newHTML;
            } else {
              el.innerText = translated;
            }
          } else {
            el.innerText = translated;
          }
        }
      });
    } catch(err) {
      // swallow errors by default
      console.warn('Translation error:', err);
    }
  }

  // Expose for manual call
  window.translateDynamicContent = translateDynamicContent;
  
  // Expose manual translation trigger
  window.forceTranslation = function(lang) {
    if (!lang) lang = getPreferredLanguage();
    console.log('Force translating to:', lang);
    
    // Clear any existing translations first
    const allNodes = collectTargets();
    storeOriginals(allNodes);
    restoreOriginals(allNodes);
    
    // Then translate to target language
    setTimeout(() => translateDynamicContent(lang), 100);
  };

  // Complete page refresh translation
  window.refreshTranslation = function() {
    const currentLang = getPreferredLanguage();
    console.log('Refreshing translation for:', currentLang);
    
    // Force complete re-collection and translation
    setTimeout(() => {
      const nodes = collectTargets();
      storeOriginals(nodes);
      restoreOriginals(nodes);
      forceRestoreToEnglish();
      if (currentLang !== 'en') {
        setTimeout(() => translateDynamicContent(currentLang), 300);
      }
    }, 100);
  };

  // Reset everything to English
  window.resetToEnglish = function() {
    console.log('Resetting all content to English');
    forceRestoreToEnglish();
    setPreferredLanguage('en');
    
    // Update language selectors to English
    document.querySelectorAll('select[id*="lang"], select[id*="Lang"]').forEach(select => {
      select.value = 'en';
    });
  };
  
  // Debug function to see what elements would be translated
  window.debugTranslation = function() {
    const targets = collectTargets();
    console.log('Elements that will be translated:', targets);
    targets.forEach((el, i) => {
      console.log(`${i}: "${el.textContent.trim()}" (${el.tagName}.${el.className})`);
    });
    return targets;
  };

  // Wrap changeLanguage if present so dynamic text also updates
  function wrapChangeLanguage(){
    if (!window.changeLanguage || window.changeLanguage.__wrapped) return;
    const prev = window.changeLanguage;
    const wrapped = async function(lang){
      try { setPreferredLanguage(lang); } catch {}
      
      // Call original changeLanguage for header/static content
      if (typeof prev === 'function') {
        try {
          await prev(lang);
        } catch(e) {
          console.warn('Error in original changeLanguage:', e);
        }
      }
      
      // Immediately translate dynamic content so header and body update together
      // Use setTimeout to ensure DOM updates are complete
      setTimeout(async () => {
        try {
          await translateDynamicContent(lang);
          console.log('Dynamic content translated to:', lang);
        } catch(e) {
          console.warn('Error translating dynamic content:', e);
        }
      }, 100);
    };
    wrapped.__wrapped = true;
    window.changeLanguage = wrapped;
  }

  // Also listen for language selector changes directly
  function setupDirectLanguageListeners() {
    // Listen for changes on all language selectors
    document.addEventListener('change', function(e) {
      if (e.target && (e.target.id === 'langSelectPartial' || e.target.id === 'languageSelect')) {
        const selectedLang = e.target.value;
        console.log('Language selector changed to:', selectedLang);
        
        // Trigger translation with proper sequencing to avoid conflicts
        setTimeout(async () => {
          try {
            await translateDynamicContent(selectedLang);
            console.log(`Translation to ${selectedLang} completed`);
          } catch(error) {
            console.warn('Translation error:', error);
            // Retry once on error
            setTimeout(() => translateDynamicContent(selectedLang), 500);
          }
        }, 50);
      }
    });

    // Also listen for any select element changes that might be language selectors
    document.addEventListener('change', function(e) {
      if (e.target && e.target.tagName === 'SELECT' && e.target.options) {
        // Check if this looks like a language selector
        const hasLanguageCodes = Array.from(e.target.options).some(opt => 
          ['en', 'hi', 'ta', 'te', 'bn', 'gu', 'kn', 'ml', 'mr', 'pa', 'ur'].includes(opt.value)
        );
        
        if (hasLanguageCodes) {
          const selectedLang = e.target.value;
          console.log('Detected language selector change to:', selectedLang);
          
          // Same careful translation approach
          setTimeout(async () => {
            try {
              await translateDynamicContent(selectedLang);
              console.log(`Generic selector translation to ${selectedLang} completed`);
            } catch(error) {
              console.warn('Generic selector translation error:', error);
            }
          }, 50);
        }
      }
    });
  }

  // Init on readiness
  document.addEventListener('DOMContentLoaded', () => {
    // Try to wrap immediately and also after a short delay (in case base.js defines later)
    wrapChangeLanguage();
    setTimeout(wrapChangeLanguage, 200);
    
    // Setup direct language selector listeners
    setupDirectLanguageListeners();
    
    // Also setup listeners after a delay in case selectors are added dynamically
    setTimeout(setupDirectLanguageListeners, 500);

    const lang = getPreferredLanguage();
    console.log('Initial language:', lang);
    
    // Kick off translation for dynamic parts on load immediately to avoid staggered updates
    if (typeof requestAnimationFrame === 'function') {
      requestAnimationFrame(() => translateDynamicContent(lang));
    } else {
      translateDynamicContent(lang);
    }
  });

  // Also setup listeners when page is fully loaded (for dynamic content)
  window.addEventListener('load', () => {
    setTimeout(() => {
      setupDirectLanguageListeners();
      const lang = getPreferredLanguage();
      if (lang !== 'en') {
        translateDynamicContent(lang);
      }
    }, 1000);
  });
})();
