/* =====================================================================
   KIT LIQUID GLASS — comportamentos (sem dependências)
   Coloque no fim do <body>: <script src="glass.js"></script>
   API: LG.init(raiz?)  LG.open('#id')  LG.close(el)  LG.notify({...})
   ===================================================================== */
(function () {
  const $ = (s, r = document) => r.querySelector(s);
  const $$ = (s, r = document) => [...r.querySelectorAll(s)];
  const LG = {};

  /* --- brilho especular que segue o ponteiro --- */
  function shine(root) {
    $$('.lg-glass, .lg-btn--glass, .lg-btn--glass-prominent', root).forEach(el => {
      if (el._lgShine) return; el._lgShine = 1;
      el.addEventListener('pointermove', e => {
        const r = el.getBoundingClientRect();
        el.style.setProperty('--lg-x', ((e.clientX - r.left) / r.width * 100).toFixed(1) + '%');
        el.style.setProperty('--lg-y', ((e.clientY - r.top) / r.height * 100).toFixed(1) + '%');
      });
      el.addEventListener('pointerleave', () => { el.style.removeProperty('--lg-x'); el.style.removeProperty('--lg-y'); });
    });
  }

  /* --- indicador deslizante: [data-lg-pill] (segmentado, tab bar) --- */
  function pills(root) {
    $$('[data-lg-pill]', root).forEach(group => {
      if (group._lgPill) return; group._lgPill = 1;
      const ind = document.createElement('span'); ind.className = 'lg-pill-indicator'; ind.setAttribute('aria-hidden', 'true');
      group.prepend(ind);
      const items = () => $$(':scope > button, :scope > a', group);
      const place = () => {
        const a = items().find(b => b.classList.contains('is-active')) || items()[0]; if (!a) return;
        ind.style.left = a.offsetLeft + 'px'; ind.style.width = a.offsetWidth + 'px';
      };
      items().forEach(b => b.addEventListener('click', () => {
        items().forEach(x => { x.classList.toggle('is-active', x === b); x.setAttribute('aria-selected', x === b); });
        place();
        // painéis: botão com data-panel="id" dentro de [data-lg-tabview]
        const view = group.closest('[data-lg-tabview]');
        if (view && b.dataset.panel) $$('[data-lg-panel]', view).forEach(p => p.hidden = p.dataset.lgPanel !== b.dataset.panel);
        group.dispatchEvent(new CustomEvent('lg:change', { detail: { value: b.dataset.value || b.textContent.trim() } }));
      }));
      place(); new ResizeObserver(place).observe(group);
    });
  }

  /* --- slider: preenche a trilha --- */
  function sliders(root) {
    $$('input.lg-slider', root).forEach(s => {
      const f = () => s.style.setProperty('--val', ((s.value - (s.min || 0)) / ((s.max || 100) - (s.min || 0)) * 100) + '%');
      if (!s._lg) { s._lg = 1; s.addEventListener('input', f); } f();
    });
  }

  /* --- stepper: <div class="lg-stepper" data-lg-stepper data-min data-max> --- */
  function steppers(root) {
    $$('[data-lg-stepper]', root).forEach(st => {
      if (st._lg) return; st._lg = 1;
      const out = $('output', st), min = +(st.dataset.min ?? -Infinity), max = +(st.dataset.max ?? Infinity);
      $$('[data-step]', st).forEach(b => b.addEventListener('click', () => {
        out.value = out.textContent = Math.min(max, Math.max(min, (+out.textContent || 0) + +b.dataset.step));
      }));
    });
  }

  /* --- avaliação --- */
  function ratings(root) {
    $$('.lg-rating[data-lg-rating]', root).forEach(r => {
      if (r._lg) return; r._lg = 1;
      const bs = $$('button', r), set = n => bs.forEach((b, i) => b.classList.toggle('is-on', i < n));
      set(+r.dataset.lgRating || 0);
      bs.forEach((b, i) => b.addEventListener('click', () => { r.dataset.lgRating = i + 1; set(i + 1); }));
    });
  }

  /* --- diálogos animados (alerta, sheet, action sheet) --- */
  LG.open = sel => {
    const d = typeof sel === 'string' ? $(sel) : sel; if (!d) return;
    if (d.tagName === 'DIALOG') { if (!d.open) d.showModal(); requestAnimationFrame(() => requestAnimationFrame(() => d.classList.add('is-open'))); }
    else d.classList.add('is-open');
  };
  LG.close = d => {
    if (!d) return; d.classList.remove('is-open');
    if (d.tagName === 'DIALOG') setTimeout(() => d.open && d.close(), 380);
  };
  function dialogs(root) {
    $$('dialog.lg-alert, dialog.lg-sheet, dialog.lg-actionsheet', root).forEach(d => {
      if (d._lg) return; d._lg = 1;
      d.addEventListener('click', e => { if (e.target === d) LG.close(d); });        // clique no fundo
      d.addEventListener('cancel', e => { e.preventDefault(); LG.close(d); });       // tecla Esc
    });
  }

  /* --- notificações: LG.notify({app, title, text, color, icon, time}) --- */
  LG.notify = (o = {}) => {
    let box = $('.lg-toasts'); if (!box) { box = document.createElement('div'); box.className = 'lg-toasts'; box.setAttribute('aria-live', 'polite'); document.body.append(box); }
    const n = document.createElement('div'); n.className = 'lg-notification lg-glass'; n.setAttribute('role', 'status');
    n.innerHTML = `<div class="lg-notification__icon" style="--c:${o.color || 'var(--lg-accent)'}">${o.icon || ''}</div>
      <div style="flex:1;min-width:0"><div class="lg-notification__app"><span>${o.app || ''}</span><span>${o.time || 'agora'}</span></div>
      <p class="lg-notification__title">${o.title || ''}</p><p class="lg-notification__text">${o.text || ''}</p></div>`;
    box.append(n); shine(n);
    const bye = () => { n.classList.add('is-leaving'); setTimeout(() => n.remove(), 300); };
    n.addEventListener('click', bye); setTimeout(bye, o.duration || 4200);
  };

  /* --- carrossel + indicador de página: <div data-lg-carousel="#dots"> --- */
  function carousels(root) {
    $$('[data-lg-carousel]', root).forEach(c => {
      if (c._lg) return; c._lg = 1;
      const dots = $(c.dataset.lgCarousel); if (!dots) return;
      const slides = [...c.children];
      dots.innerHTML = slides.map((_, i) => `<button aria-label="Página ${i + 1}"></button>`).join('');
      const bs = $$('button', dots);
      const upd = () => { const i = Math.round(c.scrollLeft / c.clientWidth); bs.forEach((b, j) => b.classList.toggle('is-active', i === j)); };
      bs.forEach((b, i) => b.addEventListener('click', () => c.scrollTo({ left: i * c.clientWidth, behavior: 'smooth' })));
      c.addEventListener('scroll', upd, { passive: true }); upd();
    });
  }

  /* --- cliques delegados: abrir/fechar, menus, tema, ilha, notificação, tokens --- */
  document.addEventListener('click', e => {
    const t = e.target;
    const op = t.closest('[data-lg-open]'); if (op) { e.preventDefault(); LG.open(op.dataset.lgOpen); return; }
    const cl = t.closest('[data-lg-close]'); if (cl) { LG.close(cl.closest('dialog, .is-open')); return; }

    const mt = t.closest('[data-lg-menu]');           // botão dentro de .lg-menu-wrap
    const openWraps = $$('.lg-menu-wrap.is-open');
    if (mt) { const w = mt.closest('.lg-menu-wrap'); openWraps.forEach(x => x !== w && x.classList.remove('is-open')); w.classList.toggle('is-open'); mt.setAttribute('aria-expanded', w.classList.contains('is-open')); return; }
    if (!t.closest('.lg-menu, .lg-popover')) openWraps.forEach(x => x.classList.remove('is-open'));
    else if (t.closest('.lg-menu button, .lg-menu a')) openWraps.forEach(x => x.classList.remove('is-open'));
    $$('.lg-menu--context.is-open').forEach(m => m.classList.remove('is-open'));

    if (t.closest('[data-lg-theme-toggle]')) {
      const h = document.documentElement, dark = h.dataset.theme ? h.dataset.theme === 'dark' : matchMedia('(prefers-color-scheme: dark)').matches;
      h.dataset.theme = dark ? 'light' : 'dark'; try { localStorage.setItem('lg-theme', h.dataset.theme); } catch (_) {}
      $$('[data-lg-pill]').forEach(g => g.dispatchEvent(new Event('resize')));
    }
    const isl = t.closest('[data-lg-island]'); if (isl) isl.classList.toggle('is-expanded');

    const nt = t.closest('[data-lg-notify]');
    if (nt) LG.notify({ app: nt.dataset.app, title: nt.dataset.title, text: nt.dataset.text, color: nt.dataset.color,
      icon: '<svg class="lg-i" viewBox="0 0 24 24"><path d="M6 8a6 6 0 1 1 12 0c0 7 3 9 3 9H3s3-2 3-9M10.3 21a1.9 1.9 0 0 0 3.4 0"/></svg>' });

    const rm = t.closest('.lg-token button'); if (rm) rm.closest('.lg-token').remove();
  });

  /* menu de contexto: elemento com data-lg-context="#menu" */
  document.addEventListener('contextmenu', e => {
    const z = e.target.closest('[data-lg-context]'); if (!z) return;
    e.preventDefault(); const m = $(z.dataset.lgContext); if (!m) return;
    m.style.left = Math.min(e.clientX, innerWidth - 240) + 'px'; m.style.top = Math.min(e.clientY, innerHeight - m.offsetHeight - 10) + 'px';
    m.classList.add('is-open');
  });
  document.addEventListener('keydown', e => {
    const isl = e.target.closest && e.target.closest('[data-lg-island]');
    if (isl && (e.key === 'Enter' || e.key === ' ')) { e.preventDefault(); isl.classList.toggle('is-expanded'); }
  });
  document.addEventListener('keydown', e => { if (e.key === 'Escape') $$('.lg-menu-wrap.is-open, .lg-menu--context.is-open').forEach(x => x.classList.remove('is-open')); });

  /* campo de tokens: Enter cria chip */
  document.addEventListener('keydown', e => {
    const inp = e.target.closest('.lg-tokens input'); if (!inp || e.key !== 'Enter' || !inp.value.trim()) return;
    e.preventDefault();
    const tk = document.createElement('span'); tk.className = 'lg-token';
    tk.innerHTML = `${inp.value.trim().replace(/[<>&]/g, '')} <button aria-label="Remover"><svg class="lg-i" viewBox="0 0 24 24"><path d="M6 6l12 12M18 6 6 18"/></svg></button>`;
    inp.before(tk); inp.value = '';
  });

  LG.init = (root = document) => { shine(root); pills(root); sliders(root); steppers(root); ratings(root); dialogs(root); carousels(root); };

  try { const t = localStorage.getItem('lg-theme'); if (t) document.documentElement.dataset.theme = t; } catch (_) {}
  window.LG = LG;
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', () => LG.init()); else LG.init();
})();
