(function () {
  var CONTENT_SEL = '#viki-content, .viki-content';
  var BR_RE = /<br\s*\/?>/gi;
  var debounceTimer;

  function contentRoot() {
    return document.querySelector(CONTENT_SEL);
  }

  function shouldSkipParagraph(p) {
    if (p.closest('li') || p.closest('blockquote') || p.closest('td') || p.closest('th')) {
      return true;
    }
    if (p.classList.contains('viki-cn-para-split')) {
      return true;
    }
    return false;
  }

  function splitParagraph(p) {
    var html = p.innerHTML;
    if (!BR_RE.test(html)) {
      return;
    }
    var parts = html.split(BR_RE);
    if (parts.length < 2) {
      return;
    }
    p.classList.add('viki-cn-para-split');
    p.innerHTML = parts
      .map(function (seg) {
        return seg.trim();
      })
      .filter(Boolean)
      .map(function (seg) {
        return '<span class="viki-cn-para-line">' + seg + '</span>';
      })
      .join('');
    if (typeof MathJax !== 'undefined' && MathJax.Hub) {
      MathJax.Hub.Queue(['Typeset', MathJax.Hub, p]);
    }
  }

  function processContent() {
    var root = contentRoot();
    if (!root) {
      return;
    }
    var ps = root.querySelectorAll('p');
    for (var i = 0; i < ps.length; i++) {
      if (shouldSkipParagraph(ps[i])) {
        continue;
      }
      splitParagraph(ps[i]);
    }
  }

  function scheduleProcess() {
    clearTimeout(debounceTimer);
    debounceTimer = setTimeout(processContent, 0);
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', scheduleProcess);
  } else {
    scheduleProcess();
  }

  function startObserver() {
    var el = contentRoot();
    if (!el) {
      setTimeout(startObserver, 50);
      return;
    }
    var mo = new MutationObserver(scheduleProcess);
    mo.observe(el, { childList: true, subtree: true });
  }

  startObserver();
})();
