/* Núcleo dos modelos de site de posto: dados, fotos, motion e painel Personalizar.
   Tudo em JS puro. Os dados do posto ficam no objeto POSTO, no <head>. */
(function () {
  'use strict';
  var D = document, R = D.documentElement, W = window;
  var P = W.POSTO, PAL = W.PALETAS, MO = W.MOTION_OPCOES, PZ = W.PZ;
  var calmo = PZ.calmo;
  var mouseFino = W.matchMedia('(pointer: fine)').matches;
  var temIO = 'IntersectionObserver' in W;
  function $(s, c) { return (c || D).querySelector(s); }
  function $$(s, c) { return Array.prototype.slice.call((c || D).querySelectorAll(s)); }
  function vel() { return parseFloat(getComputedStyle(R).getPropertyValue('--m-vel')) || 1; }
  function reflow(el) { return el.offsetWidth; }
  function ICONE(nome) { return '<svg class="ic" aria-hidden="true"><use href="#i-' + nome + '"/></svg>'; }

  /* =====================================================================
     1. DADOS DO POSTO (o HTML já vem preenchido; aqui só sobrescreve)
     ===================================================================== */
  function soDigitos(s) { return String(s || '').replace(/\D/g, ''); }
  function linkWhats(msg) { return 'https://wa.me/' + soDigitos(P.whatsapp) + '?text=' + encodeURIComponent(msg || P.mensagemWhats); }
  function linkMaps() { return 'https://www.google.com/maps/search/?api=1&query=' + encodeURIComponent(P.endereco); }
  function textoBandeira() { return /^bandeira branca$/i.test(P.bandeira) ? 'Posto bandeira branca' : 'Posto bandeira ' + P.bandeira; }
  function formatar(el, v) {
    var moeda = el.hasAttribute('data-moeda'), txt;
    var casas = el.hasAttribute('data-casas') ? +el.getAttribute('data-casas') : (moeda ? 3 : 0);
    var op = { minimumFractionDigits: casas, maximumFractionDigits: casas };
    if (moeda) { op.style = 'currency'; op.currency = 'BRL'; }
    txt = new Intl.NumberFormat('pt-BR', op).format(v);
    return (el.getAttribute('data-prefixo') || '') + txt + (el.getAttribute('data-sufixo') || '');
  }
  // escreve o número no elemento; em preço, o "R$" vai num <span class="cifra"> (fica menor no CSS)
  var CIFRA = /^R\$\s*/;
  function pintar(el, v) {
    var txt = formatar(el, v);
    if (el.hasAttribute('data-moeda') && CIFRA.test(txt)) el.innerHTML = '<span class="cifra">R$</span> ' + txt.replace(CIFRA, '');
    else el.textContent = txt;
  }

  function aplicarDados() {
    $$('[data-p]').forEach(function (el) { var k = el.getAttribute('data-p'); if (P[k] != null) el.textContent = P[k]; });
    $$('[data-p-bandeira]').forEach(function (el) { el.textContent = textoBandeira(); });
    $$('a[data-whats]').forEach(function (a) { a.href = linkWhats(a.getAttribute('data-msg')); });
    $$('a[data-tel]').forEach(function (a) { a.href = 'tel:+55' + soDigitos(P.telefone); });
    $$('a[data-maps]').forEach(function (a) { a.href = linkMaps(); });
    $$('a[data-insta]').forEach(function (a) {
      a.href = 'https://www.instagram.com/' + P.instagram + '/';
      var t = $('[data-insta-txt]', a); if (t) t.textContent = '@' + P.instagram;
    });
    $$('[data-atualizado]').forEach(function (el) { el.textContent = P.precos.atualizado; });
    $$('[data-ano]').forEach(function (el) { el.textContent = new Date().getFullYear(); });
    $$('[data-horario]').forEach(function (tb) {
      tb.innerHTML = '';
      P.horario.forEach(function (h) {
        var tr = D.createElement('tr'), th = D.createElement('th'), td = D.createElement('td');
        th.scope = 'row'; th.textContent = h[0]; td.textContent = h[1];
        tr.appendChild(th); tr.appendChild(td); tb.appendChild(tr);
      });
    });
    var maior = Math.max.apply(null, P.precos.itens.map(function (i) { return i[1]; }));
    $$('[data-preco]').forEach(function (el) {
      var it = P.precos.itens[+el.getAttribute('data-preco')];
      if (!it) { el.hidden = true; return; }
      var n = $('[data-pn]', el); if (n) n.textContent = it[0];
      var u = $('[data-pu]', el); if (u) u.textContent = it[2] || 'por litro';
      $$('[data-num]', el).forEach(function (v) { v.setAttribute('data-valor', it[1]); pintar(v, it[1]); });
      if (el.hasAttribute('data-barra')) el.style.setProperty('--v', (it[1] / maior).toFixed(3));
    });
    $$('[data-pacote]').forEach(function (el) {
      var it = (P.pacotes || [])[+el.getAttribute('data-pacote')];
      if (!it) { el.hidden = true; return; }
      var n = $('[data-pn]', el); if (n) n.textContent = it[0];
      var v = $('[data-num]', el); if (v) { v.setAttribute('data-valor', it[1]); pintar(v, it[1]); }
      var d = $('[data-pd]', el); if (d) d.textContent = it[2];
    });
    $$('[data-numero]').forEach(function (el) {
      var it = (P.numeros || [])[+el.getAttribute('data-numero')];
      if (!it) { el.hidden = true; return; }
      var v = $('[data-num]', el);
      if (v) { v.setAttribute('data-valor', it[0]); v.setAttribute('data-sufixo', it[1] || ''); pintar(v, it[0]); }
      var t = $('[data-nt]', el); if (t) t.textContent = it[2];
    });
    // JSON-LD sempre igual ao objeto POSTO
    var ld = D.getElementById('ld-posto');
    if (ld) {
      try {
        var j = JSON.parse(ld.textContent);
        j.name = P.nome; j.telephone = '+55 ' + P.telefone; j.address.streetAddress = P.endereco;
        ld.textContent = JSON.stringify(j);
      } catch (e) { /* mantém o original */ }
    }
  }

  /* =====================================================================
     2. VAGAS DE FOTO: mostra o quadro reservado e troca pela foto se existir
     ===================================================================== */
  var cache = {};
  function sondar(url) {
    if (!cache[url]) cache[url] = new Promise(function (ok) {
      var im = new Image();
      im.onload = function () { ok(true); };
      im.onerror = function () { ok(false); };
      im.src = url;
    });
    return cache[url];
  }
  function placeholder(fig) {
    if ($('.foto-ph', fig)) return;
    var marca = fig.classList.contains('vaga-marca');
    var ph = D.createElement('span');
    ph.className = 'foto-ph'; ph.setAttribute('aria-hidden', 'true');
    ph.innerHTML = ICONE(marca ? 'selo' : 'camera') + '<b></b><span class="ph-desc"></span><span class="ph-tam"></span>';
    $('b', ph).textContent = (marca ? 'LOGO: ' : 'FOTO: ') + fig.getAttribute('data-foto');
    $('.ph-desc', ph).textContent = fig.getAttribute('data-desc') || '';
    $('.ph-tam', ph).textContent = 'Tamanho ideal: ' + (fig.getAttribute('data-tamanho') || '');
    fig.insertBefore(ph, fig.firstChild);
  }
  function carregarFoto(fig) {
    var url = (fig.getAttribute('data-base') || 'img/') + fig.getAttribute('data-foto');
    sondar(url).then(function (ok) {
      if (!ok) return;
      var img = $('img', fig);
      if (img && img.getAttribute('src') !== url) img.setAttribute('src', url);
      fig.classList.add('tem-foto');
      var logo = fig.closest('.logo'); if (logo) logo.classList.add('tem-logo');
    });
  }
  var ioFoto = temIO ? new IntersectionObserver(function (es) {
    es.forEach(function (e) { if (e.isIntersecting) { ioFoto.unobserve(e.target); carregarFoto(e.target); } });
  }, { rootMargin: '600px 0px' }) : null;
  // Galeria horizontal e abas: carrega o grupo inteiro quando a seção se aproxima
  var ioGrupo = temIO ? new IntersectionObserver(function (es) {
    es.forEach(function (e) {
      if (!e.isIntersecting) return;
      ioGrupo.unobserve(e.target);
      $$('figure.foto[data-foto]', e.target).forEach(carregarFoto);
    });
  }, { rootMargin: '600px 0px' }) : null;
  function prepararFoto(fig) {
    var r = fig.getAttribute('data-proporcao');
    if (r && !fig.classList.contains('foto-fundo')) fig.style.aspectRatio = r;
    placeholder(fig);
    var grupo = fig.closest('.pilha, [data-abas]');
    if (fig.classList.contains('eager') || !ioFoto) carregarFoto(fig);
    else if (grupo) ioGrupo.observe(grupo);
    else ioFoto.observe(fig);
  }

  /* =====================================================================
     3. OBSERVADORES: aparecer ao rolar e pausar loops fora da tela
     ===================================================================== */
  var ioVer = temIO ? new IntersectionObserver(function (es) {
    es.forEach(function (e) {
      if (!e.isIntersecting) return;
      ioVer.unobserve(e.target);
      e.target.classList.add('visto');
      e.target.dispatchEvent(new CustomEvent('visto'));
    });
  }, { threshold: 0.15, rootMargin: '0px 0px -6% 0px' }) : null;
  function observar(el) {
    if (ioVer && !calmo) ioVer.observe(el);
    else { el.classList.add('visto'); el.dispatchEvent(new CustomEvent('visto')); }
  }
  var ioLoop = temIO ? new IntersectionObserver(function (es) {
    es.forEach(function (e) {
      e.target.classList.toggle('em-tela', e.isIntersecting);
      e.target.dispatchEvent(new CustomEvent(e.isIntersecting ? 'entrou' : 'saiu'));
    });
  }) : null;
  function vigiar(el) { if (ioLoop) ioLoop.observe(el); else el.classList.add('em-tela'); }
  D.addEventListener('visibilitychange', function () { R.classList.toggle('oculta', D.hidden); });

  function prepararStagger(raiz) {
    $$('[data-stagger]', raiz).forEach(function (g) {
      $$('.rv', g).forEach(function (el, i) { el.style.setProperty('--i', i % 8); });
    });
  }

  /* =====================================================================
     4. PEÇAS REUTILIZADAS PELO MOTION
     ===================================================================== */
  // M9: inclina com o mouse; devolve a função que desfaz
  function inclinar(el, max) {
    if (!mouseFino || calmo) return function () {};
    function mover(e) {
      var r = el.getBoundingClientRect();
      var x = (e.clientX - r.left) / r.width - 0.5, y = (e.clientY - r.top) / r.height - 0.5;
      el.style.transitionDelay = '0s';
      el.style.setProperty('--ry', (x * max).toFixed(2) + 'deg');
      el.style.setProperty('--rx', (-y * max * 0.75).toFixed(2) + 'deg');
    }
    function sair() { el.style.removeProperty('--rx'); el.style.removeProperty('--ry'); }
    el.addEventListener('mousemove', mover);
    el.addEventListener('mouseleave', sair);
    return function () { el.removeEventListener('mousemove', mover); el.removeEventListener('mouseleave', sair); sair(); el.style.transitionDelay = ''; };
  }

  // Números: contar do zero
  function contar(el) {
    var alvo = +el.getAttribute('data-valor'), t0 = performance.now(), dur = 1400 * vel(), id = 0;
    function passo(t) {
      var p = Math.min(1, (t - t0) / dur), s = 1 - Math.pow(1 - p, 3);
      pintar(el, alvo * s);
      if (p < 1) id = requestAnimationFrame(passo);
    }
    id = requestAnimationFrame(passo);
    return function () { cancelAnimationFrame(id); pintar(el, alvo); };
  }
  // Números: dígitos de bomba (cada dígito rola de 0 até o valor)
  function montarDigitos(el) {
    var final = formatar(el, +el.getAttribute('data-valor')), i = 0;
    el.setAttribute('aria-label', final);
    el.innerHTML = '';
    if (el.hasAttribute('data-moeda') && CIFRA.test(final)) {
      el.insertAdjacentHTML('beforeend', '<span class="cifra" aria-hidden="true">R$</span><span aria-hidden="true"> </span>');
      final = final.replace(CIFRA, '');
    }
    final.split('').forEach(function (ch) {
      if (/\d/.test(ch)) {
        var dg = D.createElement('span'), col = D.createElement('span'), h = '';
        dg.className = 'dg'; dg.setAttribute('aria-hidden', 'true');
        col.className = 'dg-col'; col.style.setProperty('--i', i++); col.setAttribute('data-d', ch);
        for (var n = 0; n <= 9; n++) h += '<span>' + n + '</span>';
        col.innerHTML = h; dg.appendChild(col); el.appendChild(dg);
      } else {
        var s = D.createElement('span'); s.setAttribute('aria-hidden', 'true'); s.textContent = ch; el.appendChild(s);
      }
    });
  }
  function rolarDigitos(el, mostrar) {
    $$('.dg-col', el).forEach(function (c) {
      c.style.transform = mostrar ? 'translate3d(0,' + (-1.15 * +c.getAttribute('data-d')) + 'em,0)' : '';
    });
  }
  function restaurarNumero(el) { el.removeAttribute('aria-label'); pintar(el, +el.getAttribute('data-valor')); }

  // M6: faixa infinita com cópia aria-hidden
  function montarFaixa(trilho, criarGrupo, larguraMin) {
    var faixa = D.createElement('div'); faixa.className = 'pf-faixa';
    var g1 = criarGrupo(); faixa.appendChild(g1); trilho.appendChild(faixa);
    var vezes = 0;
    while (g1.scrollWidth < larguraMin && vezes < 6) { $$(':scope > *', criarGrupo()).forEach(function (n) { g1.appendChild(n); }); vezes++; }
    var g2 = g1.cloneNode(true); g2.setAttribute('aria-hidden', 'true');
    $$('a,button', g2).forEach(function (n) { n.tabIndex = -1; });
    faixa.appendChild(g2);
    return faixa;
  }

  /* =====================================================================
     5. MÓDULOS DE MOTION (cada variação com iniciar e parar)
     ===================================================================== */
  var heroEl = $('.hero'), heroH1 = heroEl ? $('h1', heroEl) : null, h1Original = heroH1 ? heroH1.innerHTML : '';
  var parcPalco = $('.parc-palco');

  function parceirosLista() {
    return (P.parceiros || []).slice(0, 8).map(function (nome, i) { return { nome: nome, arq: 'parceiro-' + (i + 1) + '.png' }; });
  }
  function itemParceiro(p) {
    var d = D.createElement('div'); d.className = 'parc-item';
    d.innerHTML = '<figure class="foto vaga-marca" data-proporcao="5/2" data-tamanho="400 x 160"><img alt=""></figure>';
    var f = $('figure', d);
    f.setAttribute('data-foto', p.arq);
    f.setAttribute('data-desc', 'Logo: ' + p.nome + '. PNG com fundo transparente');
    $('img', f).alt = 'Logo ' + p.nome;
    prepararFoto(f);
    return d;
  }
  function grupoParceiros(lista, ordem) {
    var g = D.createElement('div'); g.className = 'pf-grupo';
    (ordem === 'rev' ? lista.slice().reverse() : lista).forEach(function (p) { g.appendChild(itemParceiro(p)); });
    return g;
  }
  function limparParceiros() { if (parcPalco) { parcPalco.innerHTML = ''; parcPalco.className = 'parc-palco'; } }

  var timers = {};
  var MOD = {
    hero: {
      palavras: {
        iniciar: function () {
          if (!heroH1) return;
          heroH1.setAttribute('aria-label', heroH1.textContent.replace(/\s+/g, ' ').trim());
          var w = 0;
          $$('.ln > span', heroH1).forEach(function (sp) {
            var html = '';
            sp.textContent.split(/(\s+)/).forEach(function (p) {
              if (!p) return;
              html += /^\s+$/.test(p) ? ' ' : '<span class="pw" aria-hidden="true" style="--w:' + (w++) + '">' + p.replace(/&/g, '&amp;').replace(/</g, '&lt;') + '</span>';
            });
            sp.innerHTML = html;
          });
        },
        parar: function () { if (heroH1) { heroH1.innerHTML = h1Original; heroH1.removeAttribute('aria-label'); } }
      }
    },
    foto: {
      parallax: {
        iniciar: function () {
          var img = heroEl && $('.hero-media img', heroEl); if (!img || calmo) return;
          var pend = 0;
          function rolar() {
            pend = 0;
            var r = heroEl.getBoundingClientRect();
            if (r.bottom < 0) return;
            heroEl.style.setProperty('--par', Math.min(r.height, -r.top) * 0.3 + 'px');
          }
          function aoRolar() { if (!pend) pend = requestAnimationFrame(rolar); }
          W.addEventListener('scroll', aoRolar, { passive: true }); rolar();
          timers.parallax = function () { W.removeEventListener('scroll', aoRolar); cancelAnimationFrame(pend); heroEl.style.removeProperty('--par'); };
        },
        parar: function () { if (timers.parallax) timers.parallax(); timers.parallax = null; }
      }
    },
    cards: {
      inclinar: {
        iniciar: function () { timers.cards = $$('.card').map(function (c) { c.classList.add('tilt-on'); return inclinar(c, 6); }); },
        parar: function () { (timers.cards || []).forEach(function (f) { f(); }); $$('.card.tilt-on').forEach(function (c) { c.classList.remove('tilt-on'); }); timers.cards = null; }
      }
    },
    bandeira: {
      virar: {
        iniciar: function () { var c = $('.selo-cartao'); if (c) { c.classList.add('tilt-on'); timers.selo = inclinar(c, 10); } },
        parar: function () { if (timers.selo) timers.selo(); timers.selo = null; var c = $('.selo-cartao'); if (c) c.classList.remove('tilt-on'); }
      },
      totem: {
        iniciar: function () {
          var t = $('.totem'); if (!t) return;
          var nums = $$('[data-num]', t);
          nums.forEach(montarDigitos);
          function rodar() { setTimeout(function () { nums.forEach(function (n) { rolarDigitos(n, true); }); }, 350 * vel()); }
          if (t.classList.contains('visto')) rodar(); else t.addEventListener('visto', rodar, { once: true });
          timers.totem = function () { t.removeEventListener('visto', rodar); nums.forEach(restaurarNumero); };
        },
        parar: function () { if (timers.totem) timers.totem(); timers.totem = null; }
      }
    },
    parceiros: {
      faixa: { iniciar: function () { montarTrilhos(1); }, parar: limparParceiros },
      'faixa-dupla': { iniciar: function () { montarTrilhos(2); }, parar: limparParceiros },
      colunas: {
        iniciar: function () {
          var lista = parceirosLista(); if (!parcPalco || !lista.length) return;
          parcPalco.classList.add('pc-colunas');
          for (var c = 0; c < 3; c++) {
            var col = D.createElement('div'); col.className = 'pc-col';
            var parte = lista.filter(function (_, i) { return i % 3 === c; });
            if (parte.length < 2) parte = lista.slice(c).concat(lista.slice(0, c));
            var faixa = D.createElement('div'); faixa.className = 'pf-faixa';
            var g1 = D.createElement('div'); g1.className = 'pf-grupo';
            while (g1.children.length < 5) parte.forEach(function (p) { g1.appendChild(itemParceiro(p)); });
            var g2 = g1.cloneNode(true); g2.setAttribute('aria-hidden', 'true');
            faixa.appendChild(g1); faixa.appendChild(g2); col.appendChild(faixa); parcPalco.appendChild(col);
            $$('figure', g2).forEach(carregarFoto);
          }
        },
        parar: limparParceiros
      },
      cascata: {
        iniciar: function () {
          if (!parcPalco) return;
          parcPalco.classList.add('parc-grade', 'parc-cascata');
          parceirosLista().forEach(function (p, i) { var it = itemParceiro(p); it.style.setProperty('--i', i); parcPalco.appendChild(it); observar(it); });
        },
        parar: limparParceiros
      },
      destaque: {
        iniciar: function () {
          var lista = parceirosLista(); if (!parcPalco || !lista.length) return;
          if (lista.length < 3) { MOD.parceiros.parado.iniciar(); return; }
          var vista = D.createElement('div'), trilho = D.createElement('div');
          vista.className = 'pd-vista'; trilho.className = 'pd-trilho';
          var todos = lista.concat(lista, lista);
          todos.forEach(function (p, i) { var it = itemParceiro(p); if (i >= lista.length) it.setAttribute('aria-hidden', 'true'); trilho.appendChild(it); });
          vista.appendChild(trilho); parcPalco.appendChild(vista);
          var itens = Array.prototype.slice.call(trilho.children), idx = lista.length, pausa = false, id = 0;
          function centrar(anim) {
            var it = itens[idx];
            trilho.style.transition = anim ? '' : 'none';
            trilho.style.transform = 'translate3d(' + (vista.clientWidth / 2 - (it.offsetLeft + it.offsetWidth / 2)) + 'px,0,0)';
            itens.forEach(function (x, k) { x.classList.toggle('centro', k === idx); });
            if (!anim) reflow(trilho);
          }
          function proximo() {
            if (pausa || D.hidden || !parcPalco.closest('[data-loop]').classList.contains('em-tela')) return;
            idx++;
            centrar(true);
            if (idx >= lista.length * 2) setTimeout(function () { idx -= lista.length; centrar(false); }, 850 * vel());
          }
          centrar(false);
          id = setInterval(proximo, 2500 * vel());
          var on = function () { pausa = true; }, off = function () { pausa = false; }, rs = function () { centrar(false); };
          vista.addEventListener('mouseenter', on); vista.addEventListener('mouseleave', off); W.addEventListener('resize', rs);
          timers.destaque = function () { clearInterval(id); W.removeEventListener('resize', rs); };
        },
        parar: function () { if (timers.destaque) timers.destaque(); timers.destaque = null; limparParceiros(); }
      },
      parado: {
        iniciar: function () {
          if (!parcPalco) return;
          parcPalco.classList.add('parc-grade');
          parceirosLista().forEach(function (p) { parcPalco.appendChild(itemParceiro(p)); });
        },
        parar: limparParceiros
      }
    },
    numeros: {
      contar: {
        iniciar: function () {
          timers.num = [];
          numerosAlvo().forEach(function (el) {
            pintar(el, 0);
            el.classList.remove('visto');
            var f = function () { timers.num.push(contar(el)); };
            el.addEventListener('visto', f, { once: true });
            timers.num.push(function () { el.removeEventListener('visto', f); });
            observar(el);
          });
        },
        parar: function () { (timers.num || []).forEach(function (f) { f(); }); timers.num = null; numerosAlvo().forEach(function (el) { if (ioVer) ioVer.unobserve(el); restaurarNumero(el); }); }
      },
      bomba: {
        iniciar: function () {
          timers.bomba = [];
          numerosAlvo().forEach(function (el) {
            montarDigitos(el); el.classList.remove('visto');
            var f = function () { requestAnimationFrame(function () { rolarDigitos(el, true); }); };
            el.addEventListener('visto', f, { once: true });
            timers.bomba.push(function () { el.removeEventListener('visto', f); });
            observar(el);
          });
        },
        parar: function () { (timers.bomba || []).forEach(function (f) { f(); }); timers.bomba = null; numerosAlvo().forEach(function (el) { if (ioVer) ioVer.unobserve(el); restaurarNumero(el); }); }
      }
    },
    fundo: {
      faiscas: {
        iniciar: function () { if (heroEl && mouseFino && !calmo) timers.faiscas = faiscas(heroEl); },
        parar: function () { if (timers.faiscas) timers.faiscas(); timers.faiscas = null; }
      }
    }
  };
  function numerosAlvo() { return $$('[data-num]').filter(function (el) { return !el.closest('.totem, .mq'); }); }

  function montarTrilhos(qtd) {
    var lista = parceirosLista(); if (!parcPalco || !lista.length) return;
    for (var k = 0; k < qtd; k++) {
      var tr = D.createElement('div'); tr.className = 'pf-trilho' + (k ? ' pf-rev' : '');
      parcPalco.appendChild(tr);
      var faixa = montarFaixa(tr, function () { return grupoParceiros(lista, k ? 'rev' : ''); }, Math.max(parcPalco.clientWidth, 900));
      $$('[aria-hidden] figure', faixa).forEach(carregarFoto);
    }
  }

  // M13: linhas e faíscas que nascem no cursor (canvas para sozinho sem movimento)
  function faiscas(sec) {
    var cv = D.createElement('canvas'); cv.className = 'hero-fx'; cv.setAttribute('aria-hidden', 'true');
    sec.appendChild(cv);
    var ctx = cv.getContext('2d'), Wd = 0, H = 0, dpr = Math.min(2, W.devicePixelRatio || 1);
    var linhas = [], pontos = [], raf = 0, mx = 0, my = 0, ultimo = 0, cor = '245,165,36', apagar = 0;
    function lerCor() {
      var h = getComputedStyle(R).getPropertyValue('--marca').trim().replace('#', '');
      if (h.length === 6) { var n = parseInt(h, 16); cor = (n >> 16 & 255) + ',' + (n >> 8 & 255) + ',' + (n & 255); }
    }
    function medir() { Wd = sec.clientWidth; H = sec.clientHeight; cv.width = Wd * dpr; cv.height = H * dpr; ctx.setTransform(dpr, 0, 0, dpr, 0, 0); }
    function quadro() {
      ctx.clearRect(0, 0, Wd, H);
      ctx.lineCap = 'round';
      linhas = linhas.filter(function (c) { return c.vida > 0; });
      linhas.forEach(function (c) {
        if (c.r < c.alvo) c.r += 0.6;
        c.a += c.giro; c.vida--;
        ctx.strokeStyle = 'rgba(' + cor + ',' + (c.vida / 110 * 0.7).toFixed(3) + ')';
        ctx.lineWidth = c.larg;
        ctx.beginPath(); ctx.moveTo(c.x, c.y); ctx.lineTo(c.x + Math.cos(c.a) * c.r, c.y + Math.sin(c.a) * c.r); ctx.stroke();
      });
      pontos = pontos.filter(function (s) { return s.vida > 0; });
      pontos.forEach(function (s) {
        s.x += s.vx; s.y += s.vy; s.vx *= 0.96; s.vy = s.vy * 0.96 + 0.03; s.vida--;
        ctx.fillStyle = 'rgba(' + cor + ',' + (s.vida / 70 * 0.85).toFixed(3) + ')';
        ctx.beginPath(); ctx.arc(s.x, s.y, s.tam, 0, Math.PI * 2); ctx.fill();
      });
      if (linhas.length || pontos.length) apagar = 30;
      raf = apagar-- > 0 ? requestAnimationFrame(quadro) : (ctx.clearRect(0, 0, Wd, H), 0);
    }
    function mover(e) {
      var b = sec.getBoundingClientRect(); mx = e.clientX - b.left; my = e.clientY - b.top;
      var t = performance.now();
      if (t - ultimo > 40) {
        ultimo = t;
        for (var i = 0; i < 2; i++) pontos.push({ x: mx, y: my, vx: (Math.random() - 0.5) * 3, vy: (Math.random() - 0.7) * 3, vida: 70, tam: Math.random() * 1.8 + 0.6 });
        if (Math.random() < 0.35) linhas.push({ x: mx + (Math.random() - 0.5) * 24, y: my + (Math.random() - 0.5) * 24, a: Math.random() * Math.PI * 2, giro: (Math.random() - 0.5) * 0.03, r: 0, alvo: Math.random() * 40 + 16, vida: 110, larg: Math.random() * 0.8 + 0.7 });
      }
      if (!raf) raf = requestAnimationFrame(quadro);
    }
    lerCor(); medir();
    sec.addEventListener('mousemove', mover);
    W.addEventListener('resize', medir);
    D.addEventListener('paleta:trocou', lerCor);
    return function () {
      sec.removeEventListener('mousemove', mover); W.removeEventListener('resize', medir); D.removeEventListener('paleta:trocou', lerCor);
      cancelAnimationFrame(raf); cv.remove();
    };
  }

  function iniciarBloco(b, v) {
    if (b === 'parceiros') limparParceiros();   // tira a grade estática do HTML antes de montar
    var m = MOD[b] && MOD[b][v]; if (m) m.iniciar();
  }
  function pararBloco(b, v) { var m = MOD[b] && MOD[b][v]; if (m) m.parar(); }
  function efetivo(b) { var bl = MO.filter(function (x) { return x.id === b; })[0]; return calmo ? bl.parado : PZ.mot[b]; }

  function trocarMotion(b, v) {
    var antes = efetivo(b);
    pararBloco(b, antes);
    PZ.mot[b] = v;
    PZ.aplicarMotion();
    iniciarBloco(b, efetivo(b));
    PZ.guardar();
    limparURL();
  }

  // "Ver de novo": repete a entrada do bloco
  function repetir(b) {
    var bl = MO.filter(function (x) { return x.id === b; })[0];
    var alvo = bl && bl.alvo ? $(bl.alvo) : null;
    if (alvo) alvo.scrollIntoView({ behavior: calmo ? 'auto' : 'smooth', block: 'center' });
    setTimeout(function () {
      if (b === 'hero' || b === 'foto') { heroEl.classList.remove('h-play'); reflow(heroEl); heroEl.classList.add('h-play'); }
      else if (b === 'cards') {
        var sec = alvo || D;
        $$('.rv', sec).forEach(function (el) { el.classList.remove('visto'); reflow(el); observar(el); });
      } else if (b === 'bandeira' || b === 'parceiros' || b === 'numeros') {
        var v = efetivo(b); pararBloco(b, v);
        if (b === 'bandeira') $$('.selo,.totem').forEach(function (el) { el.classList.remove('visto'); el.style.animation = 'none'; reflow(el); el.style.animation = ''; observar(el); });
        $$('.selo-cartao').forEach(function (el) { el.style.animation = 'none'; reflow(el); el.style.animation = ''; });
        iniciarBloco(b, v);
      } else if (b === 'fundo') {
        heroEl.classList.remove('h-play'); reflow(heroEl); heroEl.classList.add('h-play');
      }
    }, alvo ? 500 : 0);
  }

  /* =====================================================================
     6. MOTIONS FIXOS DE CADA MODELO
     ===================================================================== */
  // M3 cabeçalho
  var topo = $('.topo');
  function rolouTopo() { if (topo) topo.classList.toggle('rolou', W.scrollY > 40); }
  W.addEventListener('scroll', rolouTopo, { passive: true }); rolouTopo();

  // Menu do celular
  var burger = $('.burger'), menu = D.getElementById('menu');
  function fecharMenu(focar) { if (!topo) return; topo.classList.remove('aberto'); if (burger) burger.setAttribute('aria-expanded', 'false'); if (focar && burger) burger.focus(); }
  if (burger && menu) {
    burger.addEventListener('click', function () {
      var ab = !topo.classList.contains('aberto');
      topo.classList.toggle('aberto', ab); burger.setAttribute('aria-expanded', String(ab));
      if (ab) { var a = $('a', menu); if (a) a.focus(); }
    });
    $$('a', menu).forEach(function (a) { a.addEventListener('click', function () { fecharMenu(false); }); });
    D.addEventListener('keydown', function (e) { if (e.key === 'Escape' && topo.classList.contains('aberto')) fecharMenu(true); });
  }

  // M6 faixas fixas (pagamento, serviços, preços)
  $$('[data-marquee]').forEach(function (mq) {
    var fonte = $('.mq-grupo', mq); if (!fonte) return;
    var faixa = D.createElement('div'); faixa.className = 'mq-faixa';
    mq.insertBefore(faixa, fonte); faixa.appendChild(fonte);
    var n = 0, base = Array.prototype.slice.call(fonte.children);
    while (fonte.scrollWidth < Math.max(mq.clientWidth, 900) && n < 6) { base.forEach(function (x) { var c = x.cloneNode(true); c.setAttribute('aria-hidden', 'true'); fonte.appendChild(c); }); n++; }
    var copia = fonte.cloneNode(true); copia.setAttribute('aria-hidden', 'true');
    faixa.appendChild(copia);
    vigiar(mq);
  });

  // M7 rolagem horizontal fixa
  $$('[data-hscroll]').forEach(function (box) {
    var fixo = $('.hscroll-fixo', box), pilha = $('.pilha', box), itens = $$('.pilha-item', box), dist = 0, ativo = false, pend = 0;
    var mq = W.matchMedia('(min-width: 961px)');
    function medir() {
      ativo = mq.matches && !calmo;
      box.classList.toggle('motion', ativo);
      if (!ativo) { box.style.height = ''; pilha.style.transform = ''; return; }
      dist = Math.max(0, pilha.scrollWidth - fixo.clientWidth);
      box.style.height = (fixo.offsetHeight + dist) + 'px';
      rolar();
    }
    function rolar() {
      pend = 0; if (!ativo) return;
      var r = box.getBoundingClientRect(), topoPx = parseFloat(getComputedStyle(R).getPropertyValue('--topo')) || 72;
      var total = Math.max(1, box.offsetHeight - fixo.offsetHeight);
      var p = Math.min(1, Math.max(0, (topoPx - r.top) / total));
      pilha.style.transform = 'translate3d(' + (-p * dist).toFixed(1) + 'px,0,0)';
      itens.forEach(function (it) {
        var c = it.getBoundingClientRect();
        it.style.setProperty('--d', (((c.left + c.width / 2) - W.innerWidth / 2) / W.innerWidth).toFixed(3));
      });
    }
    W.addEventListener('scroll', function () { if (!pend) pend = requestAnimationFrame(rolar); }, { passive: true });
    W.addEventListener('resize', medir);
    if (mq.addEventListener) mq.addEventListener('change', medir);
    W.addEventListener('load', medir);
    medir();
  });

  // M8 abas com troca automática e barra de progresso
  $$('[data-abas]').forEach(function (box) {
    var tabs = $$('[role="tab"]', box), paineis = tabs.map(function (t) { return D.getElementById(t.getAttribute('aria-controls')); });
    var i = 0, timer = 0, visivel = false, pausa = false;
    function mostrar(n, foco) {
      i = (n + tabs.length) % tabs.length;
      tabs.forEach(function (t, k) { var s = k === i; t.setAttribute('aria-selected', String(s)); t.tabIndex = s ? 0 : -1; paineis[k].hidden = !s; });
      if (foco) tabs[i].focus();
      seguir();
    }
    function seguir() {
      clearTimeout(timer); box.classList.remove('tocando'); reflow(box);
      if (calmo || !visivel || pausa || D.hidden) return;
      box.classList.add('tocando');
      timer = setTimeout(function () { mostrar(i + 1); }, 5000 * vel());
    }
    tabs.forEach(function (t, k) {
      t.addEventListener('click', function () { mostrar(k); });
      t.addEventListener('keydown', function (e) {
        if (e.key === 'ArrowRight' || e.key === 'ArrowDown') { e.preventDefault(); mostrar(i + 1, true); }
        else if (e.key === 'ArrowLeft' || e.key === 'ArrowUp') { e.preventDefault(); mostrar(i - 1, true); }
        else if (e.key === 'Home') { e.preventDefault(); mostrar(0, true); }
        else if (e.key === 'End') { e.preventDefault(); mostrar(tabs.length - 1, true); }
      });
    });
    box.addEventListener('mouseenter', function () { pausa = true; seguir(); });
    box.addEventListener('mouseleave', function () { pausa = false; seguir(); });
    box.addEventListener('focusin', function () { pausa = true; seguir(); });
    box.addEventListener('focusout', function (e) { if (!box.contains(e.relatedTarget)) { pausa = false; seguir(); } });
    box.addEventListener('entrou', function () { visivel = true; seguir(); });
    box.addEventListener('saiu', function () { visivel = false; seguir(); });
    D.addEventListener('visibilitychange', seguir);
    box.setAttribute('data-loop', '');
    vigiar(box);
    mostrar(0);
  });

  // M9 inclinação fixa + parallax na rolagem
  $$('[data-tilt]').forEach(function (el) {
    if (calmo) return;
    var mq = W.matchMedia('(min-width: 961px)');
    if (mq.matches) inclinar(el, +el.getAttribute('data-tilt') || 12);
    var pend = 0, sec = el.closest('section') || el;
    function rolar() {
      pend = 0; if (!mq.matches) { el.style.removeProperty('--py'); return; }
      var r = sec.getBoundingClientRect(), meio = (r.top + r.height / 2 - W.innerHeight / 2) / W.innerHeight;
      el.style.setProperty('--py', (Math.max(-1, Math.min(1, meio)) * 36).toFixed(1) + 'px');
    }
    W.addEventListener('scroll', function () { if (!pend) pend = requestAnimationFrame(rolar); }, { passive: true });
    rolar();
  });

  // M12 barras crescem ao aparecer
  $$('[data-barras]').forEach(function (b) { $$('.barra i', b).forEach(function (i, k) { i.style.setProperty('--i', k); }); observar(b); });

  /* =====================================================================
     6b. ESTILO APPLE (Liquid Glass): barra inferior, aviso de preço, segmentado
     ===================================================================== */
  var VO = W.VIDRO_OPCOES || [], VP = W.VIDRO_PRESETS || {};
  var IC_SECAO = { precos: 'tag', combustivel: 'tag', servicos: 'bomba', autocenter: 'chave', pacotes: 'lavagem', parada: 'camera', galeria: 'camera',
    restaurante: 'restaurante', lanchonete: 'cafe', cafe: 'cafe', conveniencia: 'loja', localizacao: 'pin', contato: 'whats', historia: 'relogio', processo: 'relogio',
    energia: 'bomba', motorista: 'app', detalhes: 'chave', oficina: 'camera', roteiro: 'estrada', pagamento: 'cartao' };
  // ordem de preferência dos atalhos da barra (os 2 primeiros que existirem + "Como chegar")
  var PRIORIDADE = ['pacotes', 'precos', 'servicos', 'energia', 'motorista', 'conveniencia', 'restaurante', 'lanchonete', 'cafe', 'roteiro', 'detalhes', 'processo', 'historia', 'pagamento', 'parada', 'galeria', 'oficina'];

  // Barra de abas flutuante (como a tab bar do iPhone): 3 links do menu + WhatsApp em destaque
  var barra = null;
  function montarBarra() {
    var links = $$('.menu a:not(.btn)').filter(function (a) { return /^#/.test(a.getAttribute('href')); });
    var loc = links.filter(function (a) { return a.getAttribute('href') === '#localizacao'; })[0];
    function peso(a) { var i = PRIORIDADE.indexOf(a.getAttribute('href').slice(1)); return i < 0 ? 99 : i; }
    var escolhidos = links.filter(function (a) { return a !== loc; }).sort(function (x, y) { return peso(x) - peso(y); }).slice(0, loc ? 2 : 3);
    if (loc) escolhidos.push(loc);
    barra = D.createElement('nav'); barra.className = 'g-barra'; barra.setAttribute('aria-label', 'Atalhos');
    var html = '<span class="g-pilula" aria-hidden="true"></span>';
    escolhidos.forEach(function (a, i) {
      var id = a.getAttribute('href').slice(1);
      if (i === Math.min(2, escolhidos.length)) html += '<a class="g-whats" data-whats href="' + linkWhats() + '">' + ICONE('whats') + '<span>WhatsApp</span></a>';
      html += '<a href="#' + id + '" data-alvo="' + id + '">' + ICONE(IC_SECAO[id] || 'seta') + '<span>' + a.textContent.trim() + '</span></a>';
    });
    if (escolhidos.length < 2) html += '<a class="g-whats" data-whats href="' + linkWhats() + '">' + ICONE('whats') + '<span>WhatsApp</span></a>';
    barra.innerHTML = html;
    D.body.appendChild(barra);
    var pilula = $('.g-pilula', barra), itens = $$('a[data-alvo]', barra);
    var ultimo = null;
    function marcar(id) {
      ultimo = id; var at = null;
      itens.forEach(function (a) { var s = a.getAttribute('data-alvo') === id; a.classList.toggle('ativo', s); if (s) at = a; });
      pilula.classList.toggle('on', !!at);
      if (at) { pilula.style.left = at.offsetLeft + 'px'; pilula.style.width = at.offsetWidth + 'px'; }
    }
    barra._re = function () { marcar(ultimo); };
    W.addEventListener('resize', barra._re);
    if (temIO) {
      var io = new IntersectionObserver(function (es) {
        es.forEach(function (e) { if (e.isIntersecting) marcar(e.target.id); });
      }, { rootMargin: '-45% 0px -50% 0px' });
      itens.forEach(function (a) { var s = D.getElementById(a.getAttribute('data-alvo')); if (s) io.observe(s); });
      var ioTopo = $('#inicio');
      if (ioTopo) new IntersectionObserver(function (es) { if (es[0].isIntersecting) marcar(null); }, { rootMargin: '-45% 0px -50% 0px' }).observe(ioTopo);
    }
  }

  // Controle segmentado: polegar que desliza atrás da aba ativa
  function montarPolegares() {
    $$('[data-abas] .abas-lista').forEach(function (lista) {
      if ($('.g-polegar', lista)) return;
      var pol = D.createElement('span'); pol.className = 'g-polegar'; pol.setAttribute('aria-hidden', 'true');
      lista.insertBefore(pol, lista.firstChild);
      function mover() {
        var at = $('[aria-selected="true"]', lista); if (!at) return;
        pol.style.left = at.offsetLeft + 'px'; pol.style.width = at.offsetWidth + 'px';
      }
      new MutationObserver(mover).observe(lista, { attributes: true, subtree: true, attributeFilter: ['aria-selected'] });
      W.addEventListener('resize', mover);
      lista._mover = mover; mover();
    });
  }
  function moverPolegares() { $$('[data-abas] .abas-lista').forEach(function (l) { if (l._mover) l._mover(); }); }

  // Aviso no estilo notificação do iPhone, com o preço de hoje
  function mostrarAviso() {
    var velho = $('.g-aviso'); if (velho) velho.remove();
    var it = (P.precos && P.precos.itens || [])[0]; if (!it) return;
    var alvo = $('.precos-lista') ? ($('.precos-lista').closest('section') || {}).id : null;
    var a = D.createElement('div'); a.className = 'g-aviso'; a.setAttribute('role', 'status');
    a.innerHTML = '<span class="g-aviso-ic">' + ICONE('tag') + '</span><span class="g-aviso-txt"><span class="g-aviso-app"><span>' + P.nome +
      '</span><span>agora</span></span><b>' + it[0] + ' hoje: R$ ' + Number(it[1]).toFixed(2).replace('.', ',') + '</b><p>' +
      (alvo ? 'Toque para ver todos os preços.' : 'Atualizado em ' + P.precos.atualizado + '.') + '</p></span>' +
      '<button type="button" class="g-aviso-x" aria-label="Fechar aviso">' + ICONE('fechar') + '</button>';
    function sair() { a.classList.add('sair'); setTimeout(function () { a.remove(); }, 350); }
    a.addEventListener('click', function (e) {
      if (!e.target.closest('.g-aviso-x') && alvo) { var s = D.getElementById(alvo); if (s) s.scrollIntoView({ behavior: calmo ? 'auto' : 'smooth' }); }
      sair();
    });
    D.body.appendChild(a);
    setTimeout(function () { if (a.isConnected) sair(); }, 8000);
  }
  function avisoAutomatico() {
    if (PZ.vid.aviso !== 'preco') return;
    try { if (sessionStorage.getItem('g-aviso:' + P.id)) return; sessionStorage.setItem('g-aviso:' + P.id, '1'); } catch (e) { /* segue */ }
    setTimeout(mostrarAviso, 2600);
  }

  function trocarVidro(b, v) {
    PZ.vid[b] = v; PZ.aplicarVidro(); PZ.guardar(); limparURL();
    if (b === 'abas') setTimeout(moverPolegares, 30);
    if (b === 'aviso' && v === 'preco') mostrarAviso();
    if (b === 'flutuantes' && barra) setTimeout(barra._re, 60);
  }

  /* =====================================================================
     7. PAINEL PERSONALIZAR (aba Cores e aba Movimento)
     ===================================================================== */
  function copiar(txt, status) {
    function ok() { status.textContent = 'Copiado!'; setTimeout(function () { status.textContent = ''; }, 2200); }
    function velho() {
      var t = D.createElement('textarea'); t.value = txt; t.setAttribute('readonly', ''); t.style.position = 'fixed'; t.style.opacity = '0';
      D.body.appendChild(t); t.select();
      try { D.execCommand('copy'); ok(); } catch (e) { status.textContent = 'Não deu para copiar. Selecione e copie: ' + txt; }
      t.remove();
    }
    if (navigator.clipboard && W.isSecureContext) navigator.clipboard.writeText(txt).then(ok, velho); else velho();
  }
  function urlAtual() {
    var u = location.href.split('#')[0].split('?')[0], q = [];
    if (PZ.cor.cor) { q.push('cor=' + PZ.cor.cor.replace('#', '')); if (PZ.cor.destaque) q.push('destaque=' + PZ.cor.destaque.replace('#', '')); q.push('paleta=' + PZ.cor.paleta); }
    else q.push('paleta=' + PZ.cor.paleta);
    q.push('m=' + MO.map(function (b) { return b.id + '.' + PZ.mot[b.id]; }).join(','));
    if (VO.length) q.push('g=' + VO.map(function (b) { return b.id + '.' + PZ.vid[b.id]; }).join(','));
    return u + '?' + q.join('&');
  }
  function limparURL() { if (location.search && history.replaceState) history.replaceState(null, '', location.pathname + location.hash); }
  function textoConfig() {
    return 'motion: { ' + MO.map(function (b) { return b.id + ': "' + PZ.mot[b.id] + '"'; }).join(', ') + ' }';
  }
  function textoVidro() {
    return 'vidro: { ' + VO.map(function (b) { return b.id + ': "' + PZ.vid[b.id] + '"'; }).join(', ') + ' }';
  }
  function textoCores() {
    var c = PZ.coresAtuais(), l = [':root {'];
    for (var k in c) l.push('  --' + k + ': ' + c[k] + ';');
    l.push('}');
    return l.join('\n');
  }
  function radios(grupo, aoEscolher) {
    var ops = $$('[role="radio"]', grupo);
    function marcar(alvo, foco) {
      ops.forEach(function (o) { var s = o === alvo; o.setAttribute('aria-checked', String(s)); o.tabIndex = s ? 0 : -1; });
      if (foco) alvo.focus();
    }
    ops.forEach(function (o, k) {
      o.addEventListener('click', function () { marcar(o); aoEscolher(o.getAttribute('data-v')); });
      o.addEventListener('keydown', function (e) {
        var n = null;
        if (e.key === 'ArrowRight' || e.key === 'ArrowDown') n = ops[(k + 1) % ops.length];
        if (e.key === 'ArrowLeft' || e.key === 'ArrowUp') n = ops[(k - 1 + ops.length) % ops.length];
        if (n && !n.disabled) { e.preventDefault(); marcar(n, true); aoEscolher(n.getAttribute('data-v')); }
      });
    });
    return { marcar: function (v) { var o = ops.filter(function (x) { return x.getAttribute('data-v') === v; })[0]; marcar(o || null); } };
  }

  function montarPainel() {
    if (P.mostrarSeletor === false) return;
    var btn = D.createElement('button');
    btn.type = 'button'; btn.className = 'pz-botao';
    btn.setAttribute('aria-haspopup', 'dialog'); btn.setAttribute('aria-expanded', 'false'); btn.setAttribute('aria-controls', 'pz');
    btn.innerHTML = ICONE('paleta') + '<span>Personalizar</span>';

    var pz = D.createElement('div');
    pz.className = 'pz'; pz.id = 'pz'; pz.hidden = true;
    pz.setAttribute('role', 'dialog'); pz.setAttribute('aria-labelledby', 'pz-titulo');

    var swatches = PAL.map(function (p) {
      return '<button type="button" class="pz-paleta" role="radio" data-v="' + p.id + '" aria-label="' + p.nome + '" title="' + p.nome +
        '"><span style="background:linear-gradient(135deg,' + p.cores.fundo + ' 0 38%,' + p.cores.destaque + ' 38% 66%,' + p.cores.marca + ' 66% 100%)"></span></button>';
    }).join('');
    var linhas = MO.map(function (b) {
      var ops = b.opcoes.map(function (o) { return '<button type="button" class="pz-op" role="radio" data-v="' + o[0] + '">' + o[1] + '</button>'; }).join('');
      return '<div class="pz-linha"><div class="pz-linha-cab"><span id="pz-l-' + b.id + '">' + b.nome + '</span>' +
        (b.alvo ? '<button type="button" class="pz-ver" data-ver="' + b.id + '">▶ Ver de novo</button>' : '') +
        '</div><div class="pz-opcoes" role="radiogroup" aria-labelledby="pz-l-' + b.id + '" data-bloco="' + b.id + '">' + ops + '</div></div>';
    }).join('');
    // Estilo Apple: só mostra os blocos que existem neste modelo
    var blocosVidro = VO.filter(function (b) { return !b.requer || $(b.requer); });
    var linhasVidro = blocosVidro.map(function (b) {
      var ops = b.opcoes.map(function (o) { return '<button type="button" class="pz-op" role="radio" data-v="' + o[0] + '">' + o[1] + '</button>'; }).join('');
      return '<div class="pz-linha"><div class="pz-linha-cab"><span id="pz-g-' + b.id + '">' + b.nome + '</span>' +
        (b.id === 'aviso' ? '<button type="button" class="pz-ver" data-ver-aviso>▶ Ver aviso</button>' : '') +
        '</div>' + (b.dica ? '<p class="pz-dica">' + b.dica + '</p>' : '') +
        '<div class="pz-opcoes" role="radiogroup" aria-labelledby="pz-g-' + b.id + '" data-vidro="' + b.id + '">' + ops + '</div></div>';
    }).join('');
    var presets = Object.keys(VP).map(function (k) {
      return '<button type="button" class="pz-preset" data-preset="' + k + '">' + VP[k].nome + '<small>' + VP[k].desc + '</small></button>';
    }).join('') + (P.vidroSugerido ? '<button type="button" class="pz-preset sugestao" data-preset="sugestao">Sugestão do designer<small>O que mais combina com este modelo</small></button>' : '');

    pz.innerHTML =
      '<div class="pz-cab"><h2 id="pz-titulo">Personalizar</h2><button type="button" class="pz-fechar" aria-label="Fechar painel">' + ICONE('fechar') + '</button></div>' +
      '<div class="pz-abas" role="tablist" aria-label="Seções do painel">' +
        '<button type="button" class="pz-aba" role="tab" id="pz-t-cores" aria-controls="pz-p-cores" aria-selected="true">Cores</button>' +
        '<button type="button" class="pz-aba" role="tab" id="pz-t-mov" aria-controls="pz-p-mov" aria-selected="false" tabindex="-1">Movimento</button>' +
        (VO.length ? '<button type="button" class="pz-aba" role="tab" id="pz-t-vid" aria-controls="pz-p-vid" aria-selected="false" tabindex="-1">Estilo Apple</button>' : '') +
      '</div>' +
      '<div class="pz-corpo" role="tabpanel" id="pz-p-cores" aria-labelledby="pz-t-cores">' +
        '<div><h3 id="pz-h-pal">Paletas prontas</h3><div class="pz-paletas" role="radiogroup" aria-labelledby="pz-h-pal">' + swatches + '</div><p class="pz-nome" aria-live="polite"></p></div>' +
        '<div><h3>Cor da marca do posto</h3>' +
          '<label class="pz-cor"><input type="color" id="pz-cor"> <span>Cor principal (botões e destaques)</span></label>' +
          '<label class="pz-cor"><input type="color" id="pz-dest"> <span>Cor de apoio (opcional)</span></label>' +
          '<p class="pz-aviso" role="status"></p></div>' +
        '<div class="pz-botoes"><button type="button" class="pz-acao" data-acao="copiar-cores">Copiar cores</button>' +
          '<button type="button" class="pz-acao" data-acao="link">Copiar link desta paleta</button>' +
          '<button type="button" class="pz-acao" data-acao="padrao-cores">Voltar ao padrão</button></div>' +
      '</div>' +
      '<div class="pz-corpo" role="tabpanel" id="pz-p-mov" aria-labelledby="pz-t-mov" hidden>' +
        (calmo ? '<p class="pz-aviso">Seu computador está com "reduzir movimento" ligado, então as animações ficam desligadas.</p>' : '') +
        linhas +
        '<div class="pz-botoes"><button type="button" class="pz-acao" data-acao="config">Copiar configuração</button>' +
          '<button type="button" class="pz-acao" data-acao="link">Copiar link</button>' +
          '<button type="button" class="pz-acao" data-acao="padrao-mov">Voltar ao padrão</button></div>' +
      '</div>' +
      (VO.length ? '<div class="pz-corpo" role="tabpanel" id="pz-p-vid" aria-labelledby="pz-t-vid" hidden>' +
        '<div><h3>Combinações prontas</h3><div class="pz-presets">' + presets + '</div></div>' +
        linhasVidro +
        '<div class="pz-botoes"><button type="button" class="pz-acao" data-acao="config-vidro">Copiar configuração</button>' +
          '<button type="button" class="pz-acao" data-acao="link">Copiar link</button>' +
          '<button type="button" class="pz-acao" data-acao="padrao-vidro">Voltar ao original</button></div>' +
      '</div>' : '') +
      '<p class="pz-status pz-corpo" aria-live="polite" style="padding-top:0"></p>';

    D.body.appendChild(pz); D.body.appendChild(btn);
    var status = $('.pz-status', pz), aviso = $('.pz-aviso[role="status"]', pz), nome = $('.pz-nome', pz);
    var inCor = $('#pz-cor', pz), inDest = $('#pz-dest', pz);

    // abas do painel
    var abas = $$('.pz-aba', pz);
    function abaAtiva(k, foco) {
      abas.forEach(function (a, j) { var s = j === k; a.setAttribute('aria-selected', String(s)); a.tabIndex = s ? 0 : -1; D.getElementById(a.getAttribute('aria-controls')).hidden = !s; });
      if (foco) abas[k].focus();
    }
    abas.forEach(function (a, k) {
      a.addEventListener('click', function () { abaAtiva(k); });
      a.addEventListener('keydown', function (e) {
        if (e.key === 'ArrowRight') { e.preventDefault(); abaAtiva((k + 1) % abas.length, true); }
        if (e.key === 'ArrowLeft') { e.preventDefault(); abaAtiva((k - 1 + abas.length) % abas.length, true); }
      });
    });

    // cores
    function atualizarCoresUI() {
      var c = PZ.coresAtuais();
      inCor.value = c.marca.toLowerCase(); inDest.value = c.destaque.toLowerCase();
      var p = PAL.filter(function (x) { return x.id === PZ.cor.paleta; })[0];
      nome.textContent = PZ.cor.cor ? 'Cor personalizada sobre a paleta ' + p.nome : 'Paleta: ' + p.nome;
      var ct = PZ.contraste(c.marca, c.fundo);
      aviso.textContent = ct < 3 ? 'Pouco contraste com o fundo (' + ct.toFixed(1).replace('.', ',') + ':1). Experimente um tom ' + (PZ.contraste('#000000', c.fundo) > PZ.contraste('#FFFFFF', c.fundo) ? 'mais escuro' : 'mais claro') + ' da cor.' : '';
    }
    function aplicar() {
      if (!calmo) { R.classList.add('trocando'); clearTimeout(timers.troca); timers.troca = setTimeout(function () { R.classList.remove('trocando'); }, 450); }
      PZ.aplicarCores(); PZ.guardar(); limparURL(); atualizarCoresUI();
      D.dispatchEvent(new CustomEvent('paleta:trocou'));
    }
    var grupoPal = radios($('.pz-paletas', pz), function (id) { PZ.cor.paleta = id; PZ.cor.cor = null; PZ.cor.destaque = null; aplicar(); });
    grupoPal.marcar(PZ.cor.paleta);
    inCor.addEventListener('input', function () { PZ.cor.cor = PZ.hexLimpo(inCor.value); aplicar(); });
    inDest.addEventListener('input', function () { if (!PZ.cor.cor) PZ.cor.cor = PZ.coresAtuais().marca; PZ.cor.destaque = PZ.hexLimpo(inDest.value); aplicar(); });
    atualizarCoresUI();

    // movimento
    var grupos = {};
    $$('.pz-opcoes', pz).forEach(function (g) {
      var b = g.getAttribute('data-bloco');
      grupos[b] = radios(g, function (v) { trocarMotion(b, v); });
      grupos[b].marcar(PZ.mot[b]);
      if (calmo) $$('.pz-op', g).forEach(function (o) { o.disabled = true; });
    });
    $$('[data-ver]', pz).forEach(function (v) {
      if (calmo) v.disabled = true;
      v.addEventListener('click', function () { repetir(v.getAttribute('data-ver')); });
    });

    // estilo Apple
    var gruposVid = {};
    $$('[data-vidro]', pz).forEach(function (g) {
      var b = g.getAttribute('data-vidro');
      gruposVid[b] = radios(g, function (v) { trocarVidro(b, v); });
      gruposVid[b].marcar(PZ.vid[b]);
    });
    function aplicarPreset(nome) {
      var val = PZ.presetVidro(nome) || {};
      VO.forEach(function (b) { PZ.vid[b.id] = val[b.id] || 'original'; if (gruposVid[b.id]) gruposVid[b.id].marcar(PZ.vid[b.id]); });
      PZ.aplicarVidro(); PZ.guardar(); limparURL();
      setTimeout(moverPolegares, 30); if (barra) setTimeout(barra._re, 60);
      if (PZ.vid.aviso === 'preco') mostrarAviso();
    }
    $$('[data-preset]', pz).forEach(function (b) {
      b.addEventListener('click', function () {
        aplicarPreset(b.getAttribute('data-preset'));
        status.textContent = 'Aplicado: ' + b.firstChild.textContent + '.';
      });
    });
    $$('[data-ver-aviso]', pz).forEach(function (b) { b.addEventListener('click', mostrarAviso); });

    // ações
    $$('[data-acao]', pz).forEach(function (a) {
      a.addEventListener('click', function () {
        var ac = a.getAttribute('data-acao');
        if (ac === 'copiar-cores') copiar(textoCores(), status);
        if (ac === 'link') copiar(urlAtual(), status);
        if (ac === 'config') copiar(textoConfig(), status);
        if (ac === 'config-vidro') copiar(textoVidro(), status);
        if (ac === 'padrao-vidro') { aplicarPreset('__original'); status.textContent = 'Visual original do modelo aplicado.'; }
        if (ac === 'padrao-cores') { PZ.cor.paleta = P.paleta; PZ.cor.cor = null; PZ.cor.destaque = null; grupoPal.marcar(P.paleta); aplicar(); status.textContent = 'Cores do padrão aplicadas.'; }
        if (ac === 'padrao-mov') {
          MO.forEach(function (b) { if (PZ.mot[b.id] !== P.motion[b.id]) trocarMotion(b.id, P.motion[b.id]); grupos[b.id].marcar(P.motion[b.id]); });
          status.textContent = 'Movimento do padrão aplicado.';
        }
      });
    });

    // abrir e fechar
    function abrir() { pz.hidden = false; btn.setAttribute('aria-expanded', 'true'); var f = $('.pz-aba[aria-selected="true"]', pz); if (f) f.focus(); }
    function fechar(foco) { pz.hidden = true; btn.setAttribute('aria-expanded', 'false'); if (foco) btn.focus(); }
    btn.addEventListener('click', function () { if (pz.hidden) abrir(); else fechar(true); });
    $('.pz-fechar', pz).addEventListener('click', function () { fechar(true); });
    D.addEventListener('keydown', function (e) { if (e.key === 'Escape' && !pz.hidden) fechar(true); });
    D.addEventListener('pointerdown', function (e) { if (!pz.hidden && !pz.contains(e.target) && !btn.contains(e.target)) fechar(false); });
  }

  /* =====================================================================
     8. INÍCIO
     ===================================================================== */
  aplicarDados();
  $$('figure.foto[data-foto]').forEach(prepararFoto);
  prepararStagger(D);
  $$('.rv, .obs').forEach(observar);
  $$('[data-loop]').forEach(vigiar);
  MO.forEach(function (b) { iniciarBloco(b.id, efetivo(b.id)); });
  if (heroEl) heroEl.classList.add('h-play');
  if (VO.length) { montarBarra(); montarPolegares(); avisoAutomatico(); }
  montarPainel();
})();
