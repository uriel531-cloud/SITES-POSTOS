/* Roda dentro do <head>: aplica a paleta e o motion escolhidos antes da
   primeira pintura da tela, para o site não piscar com a cor errada. */
(function () {
  'use strict';
  var R = document.documentElement, P = window.POSTO, PAL = window.PALETAS, MO = window.MOTION_OPCOES;
  R.classList.add('js');
  var calmo = !!(window.matchMedia && matchMedia('(prefers-reduced-motion: reduce)').matches);
  if (calmo) R.classList.add('calmo');

  var CHAVE = 'pz:' + P.id;
  function ler() { try { return JSON.parse(localStorage.getItem(CHAVE)) || {}; } catch (e) { return {}; } }
  function salvar(dados) { try { localStorage.setItem(CHAVE, JSON.stringify(dados)); } catch (e) { /* janela anônima: segue sem salvar */ } }

  /* ---------- cores (mesma conta do gerar.py) ---------- */
  function hexRgb(h) { h = h.replace('#', ''); var n = parseInt(h, 16); return [n >> 16 & 255, n >> 8 & 255, n & 255]; }
  function rgbHex(c) {
    return '#' + c.map(function (v) { v = Math.round(Math.max(0, Math.min(255, v))); return (v < 16 ? '0' : '') + v.toString(16); }).join('').toUpperCase();
  }
  function lum(h) {
    var p = [0.2126, 0.7152, 0.0722];
    return hexRgb(h).reduce(function (s, v, i) { v /= 255; return s + p[i] * (v <= 0.03928 ? v / 12.92 : Math.pow((v + 0.055) / 1.055, 2.4)); }, 0);
  }
  function contraste(a, b) { var x = lum(a), y = lum(b); return (Math.max(x, y) + 0.05) / (Math.min(x, y) + 0.05); }
  function misturar(a, b, t) { var x = hexRgb(a), y = hexRgb(b); return rgbHex(x.map(function (v, i) { return v + (y[i] - v) * t; })); }
  function hexValido(h) { return /^#?[0-9a-f]{6}$/i.test(h || ''); }
  function hexLimpo(h) { return '#' + String(h).replace('#', '').toUpperCase(); }

  var BRANCO = '#FFFFFF', ESCURO = '#111418';
  function completar(c) {
    var o = {}; for (var k in c) o[k] = c[k];
    o['marca-texto'] = contraste(BRANCO, o.marca) >= contraste(ESCURO, o.marca) ? BRANCO : ESCURO;
    o['marca-esc'] = o['marca-texto'] === BRANCO ? misturar(o.marca, '#000000', 0.14) : misturar(o.marca, '#FFFFFF', 0.18);
    // marca-forte: a cor da marca ajustada para servir de TEXTO sobre os fundos (AA 4,5:1)
    var alvo = lum(o.fundo) > 0.4 ? '#000000' : '#FFFFFF', f = o.marca, n = 0;
    function pior(x) { return Math.min(contraste(x, o.fundo), contraste(x, o['fundo-2']), contraste(x, o.card)); }
    while (pior(f) < 4.5 && n < 30) { f = misturar(f, alvo, 0.08); n++; }
    o['marca-forte'] = f;
    return o;
  }

  /* ---------- estado: URL > localStorage > POSTO ---------- */
  var ids = PAL.map(function (p) { return p.id; });
  var guardado = ler(), q = new URLSearchParams(location.search);
  var cor = { paleta: P.paleta, cor: null, destaque: null };
  if (guardado.cores) { cor.paleta = guardado.cores.paleta; cor.cor = guardado.cores.cor; cor.destaque = guardado.cores.destaque; }
  if (q.get('paleta') && ids.indexOf(q.get('paleta')) > -1) { cor = { paleta: q.get('paleta'), cor: null, destaque: null }; }
  if (hexValido(q.get('cor'))) {
    cor.cor = hexLimpo(q.get('cor'));
    cor.destaque = hexValido(q.get('destaque')) ? hexLimpo(q.get('destaque')) : null;
  }
  if (ids.indexOf(cor.paleta) < 0) cor.paleta = ids[0];
  if (cor.cor && !hexValido(cor.cor)) cor.cor = null;
  if (cor.destaque && !hexValido(cor.destaque)) cor.destaque = null;

  var mot = {}, k;
  for (k in P.motion) mot[k] = P.motion[k];
  if (guardado.motion) for (k in guardado.motion) mot[k] = guardado.motion[k];
  if (q.get('m')) q.get('m').split(',').forEach(function (par) { var s = par.split('.'); if (s.length === 2) mot[s[0]] = s[1]; });
  MO.forEach(function (b) {
    var ok = b.opcoes.map(function (o) { return o[0]; });
    if (ok.indexOf(mot[b.id]) < 0) mot[b.id] = ok.indexOf(P.motion[b.id]) > -1 ? P.motion[b.id] : ok[0];
  });

  function coresAtuais() {
    var base = PAL.filter(function (p) { return p.id === cor.paleta; })[0] || PAL[0], c = {};
    for (var x in base.cores) c[x] = base.cores[x];
    if (cor.cor) { c.marca = cor.cor; if (cor.destaque) c.destaque = cor.destaque; }
    return completar(c);
  }
  function aplicarCores() {
    var c = coresAtuais();
    for (var x in c) R.style.setProperty('--' + x, c[x]);
    var meta = document.querySelector('meta[name="theme-color"]');
    if (meta) meta.setAttribute('content', c.fundo);
    var ic = document.querySelector('link[rel="icon"]');
    if (ic) {
      var svg = "<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 64 64'><rect width='64' height='64' rx='14' fill='" + c.marca +
        "'/><text x='32' y='44' font-family='Arial,Helvetica,sans-serif' font-size='34' font-weight='700' text-anchor='middle' fill='" +
        c['marca-texto'] + "'>" + (P.inicial || P.nome.replace(/^(auto\s+)?posto\s+(&\s+)?/i, '').charAt(0)) + '</text></svg>';
      ic.setAttribute('href', 'data:image/svg+xml,' + encodeURIComponent(svg));
    }
    return c;
  }
  var VEL = { suave: [1.4, 0.6], normal: [1, 1], intenso: [0.75, 1.3] };
  function aplicarMotion() {
    MO.forEach(function (b) { R.setAttribute('data-m-' + b.id, calmo ? b.parado : mot[b.id]); });
    var v = VEL[mot.vel] || VEL.normal;
    R.style.setProperty('--m-vel', v[0]);
    R.style.setProperty('--m-dist', v[1]);
  }

  /* ---------- estilo Apple (vidro): URL > localStorage > POSTO ---------- */
  var VO = window.VIDRO_OPCOES || [], VP = window.VIDRO_PRESETS || {}, vid = {};
  function preset(nome) {
    if (nome === 'sugestao') return P.vidroSugerido || {};
    return VP[nome] ? VP[nome].valores : null;
  }
  function validarVidro() {
    VO.forEach(function (b) {
      var ok = b.opcoes.map(function (o) { return o[0]; });
      if (ok.indexOf(vid[b.id]) < 0) vid[b.id] = (P.vidro && ok.indexOf(P.vidro[b.id]) > -1) ? P.vidro[b.id] : ok[0];
    });
  }
  if (P.vidro) for (k in P.vidro) vid[k] = P.vidro[k];
  if (guardado.vidro) for (k in guardado.vidro) vid[k] = guardado.vidro[k];
  if (q.get('g')) {
    var pg = preset(q.get('g'));
    if (pg) { VO.forEach(function (b) { vid[b.id] = pg[b.id] || 'original'; }); }
    else q.get('g').split(',').forEach(function (par) { var s = par.split('.'); if (s.length === 2) vid[s[0]] = s[1]; });
  }
  validarVidro();
  function aplicarVidro() { VO.forEach(function (b) { R.setAttribute('data-g-' + b.id, vid[b.id]); }); }

  aplicarCores();
  aplicarMotion();
  aplicarVidro();

  window.PZ = {
    calmo: calmo, cor: cor, mot: mot, vid: vid, salvar: salvar, completar: completar, contraste: contraste,
    misturar: misturar, hexValido: hexValido, hexLimpo: hexLimpo, coresAtuais: coresAtuais,
    aplicarCores: aplicarCores, aplicarMotion: aplicarMotion, aplicarVidro: aplicarVidro, presetVidro: preset,
    guardar: function () { salvar({ cores: cor, motion: mot, vidro: vid }); }
  };
})();
