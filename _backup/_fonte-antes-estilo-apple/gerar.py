# -*- coding: utf-8 -*-
"""
Gera os 5 modelos de site de posto (pastas "posto 1" a "posto 5") e a página índice.
Cada site sai num único index.html (CSS e JS embutidos), pronto para abrir com dois cliques.

Uso:  python gerar.py
Depois de mudar textos, cores ou o núcleo (core.css, core.js, pre.js), rode de novo.
"""
import html, json, os, re, sys

AQUI = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.dirname(AQUI)

def ler(nome):
    with open(os.path.join(AQUI, nome), encoding='utf-8') as f:
        return f.read()

def esc(s):
    return html.escape(str(s), quote=True)

# ---------------------------------------------------------------------------
# Cores: mesma conta do pre.js (para o :root inicial e a tabela de contraste)
# ---------------------------------------------------------------------------
def hex_rgb(h):
    h = h.lstrip('#'); n = int(h, 16); return [n >> 16 & 255, n >> 8 & 255, n & 255]

def js_round(v):
    # Math.round do JS (meio sempre para cima)
    import math
    return int(math.floor(v + 0.5))

def rgb_hex(c):
    return '#' + ''.join('%02X' % js_round(max(0, min(255, v))) for v in c)

def lum(h):
    p = [0.2126, 0.7152, 0.0722]; s = 0
    for i, v in enumerate(hex_rgb(h)):
        v /= 255; s += p[i] * (v / 12.92 if v <= 0.03928 else ((v + 0.055) / 1.055) ** 2.4)
    return s

def contraste(a, b):
    x, y = lum(a), lum(b); return (max(x, y) + 0.05) / (min(x, y) + 0.05)

def misturar(a, b, t):
    x, y = hex_rgb(a), hex_rgb(b); return rgb_hex([v + (y[i] - v) * t for i, v in enumerate(x)])

BRANCO, ESCURO = '#FFFFFF', '#111418'

def completar(c):
    o = dict(c)
    o['marca-texto'] = BRANCO if contraste(BRANCO, o['marca']) >= contraste(ESCURO, o['marca']) else ESCURO
    o['marca-esc'] = misturar(o['marca'], '#000000', 0.14) if o['marca-texto'] == BRANCO else misturar(o['marca'], '#FFFFFF', 0.18)
    alvo = '#000000' if lum(o['fundo']) > 0.4 else '#FFFFFF'
    f, n = o['marca'], 0
    def pior(x): return min(contraste(x, o['fundo']), contraste(x, o['fundo-2']), contraste(x, o['card']))
    while pior(f) < 4.5 and n < 30:
        f = misturar(f, alvo, 0.08); n += 1
    o['marca-forte'] = f
    return o

NEUTROS = {
    'escuro':  {'fundo': '#111317', 'fundo-2': '#171A1F', 'card': '#1D2128', 'texto': '#F2F4F7', 'suave': '#A8B0BB', 'linha': 'rgba(255,255,255,.10)'},
    'claro':   {'fundo': '#FFFFFF', 'fundo-2': '#F3F5F7', 'card': '#FFFFFF', 'texto': '#121820', 'suave': '#505A67', 'linha': 'rgba(16,24,40,.11)'},
    'creme':   {'fundo': '#FBF6EC', 'fundo-2': '#F3EADA', 'card': '#FFFDF8', 'texto': '#2A2419', 'suave': '#625744', 'linha': 'rgba(60,45,20,.14)'},
    'marinho': {'fundo': '#0D1626', 'fundo-2': '#121E33', 'card': '#18273F', 'texto': '#EEF3FA', 'suave': '#A3B1C6', 'linha': 'rgba(255,255,255,.10)'},
    'branco-forte': {'fundo': '#FFFFFF', 'fundo-2': '#F4F4F4', 'card': '#FFFFFF', 'texto': '#101010', 'suave': '#4D4D4D', 'linha': 'rgba(0,0,0,.12)'},
}

def paleta(id_, nome, marca, destaque, neutro):
    c = dict(NEUTROS[neutro]); c['marca'] = marca; c['destaque'] = destaque
    return {'id': id_, 'nome': nome, 'cores': c}

def paleta3(id_, nome, base, normal, vibrante):
    """Paleta de 3 cores: base (fundo escuro), normal (cor de apoio) e vibrante (botões e destaques).
    Os tons de fundo, cards e textos saem da base, com um toque da cor normal."""
    fundo = base
    fundo2 = misturar(misturar(base, normal, 0.05), '#FFFFFF', 0.02)
    card = misturar(misturar(base, normal, 0.08), '#FFFFFF', 0.05)
    texto = misturar('#FFFFFF', normal, 0.06)
    suave, n = misturar(misturar('#FFFFFF', normal, 0.25), base, 0.3), 0
    while min(contraste(suave, x) for x in (fundo, fundo2, card)) < 5 and n < 20:
        suave = misturar(suave, '#FFFFFF', 0.08); n += 1
    c = {'fundo': fundo, 'fundo-2': fundo2, 'card': card, 'texto': texto, 'suave': suave,
         'linha': 'rgba(255,255,255,.10)', 'marca': vibrante, 'destaque': normal}
    return {'id': id_, 'nome': nome, 'cores': c}

MOTION_OPCOES = [
    {'id': 'bandeira', 'nome': 'Bandeira', 'alvo': '#bandeira', 'parado': 'parado', 'opcoes': [['brilho', 'Brilho passando'], ['virar', 'Virar 3D'], ['totem', 'Totem'], ['pulsar', 'Luz pulsando'], ['flutuar', 'Flutuar'], ['parado', 'Parado']]},
    {'id': 'parceiros', 'nome': 'Parceiros', 'alvo': '#bandeira', 'parado': 'parado', 'opcoes': [['faixa', 'Faixa contínua'], ['faixa-dupla', 'Faixa dupla'], ['colunas', 'Colunas subindo'], ['cascata', 'Grade em cascata'], ['destaque', 'Carrossel com destaque'], ['parado', 'Parado']]},
    {'id': 'hero', 'nome': 'Entrada do topo', 'alvo': '#inicio', 'parado': 'parado', 'opcoes': [['cascata', 'Cascata'], ['mascara', 'Revelar por máscara'], ['palavras', 'Palavra por palavra'], ['foco', 'Desfoque para nítido'], ['parado', 'Parado']]},
    {'id': 'foto', 'nome': 'Foto do topo', 'alvo': '#inicio', 'parado': 'parado', 'opcoes': [['zoom', 'Zoom lento'], ['parallax', 'Parallax'], ['cortina', 'Cortina'], ['parado', 'Parado']]},
    {'id': 'cards', 'nome': 'Cards e blocos', 'alvo': '#servicos', 'parado': 'parado', 'opcoes': [['subir', 'Subir'], ['escala', 'Crescer'], ['inclinar', 'Inclinar com o mouse'], ['parado', 'Parado']]},
    {'id': 'numeros', 'nome': 'Preços e números', 'alvo': '#precos', 'parado': 'parado', 'opcoes': [['contar', 'Contar'], ['bomba', 'Dígitos de bomba'], ['parado', 'Parado']]},
    {'id': 'fundo', 'nome': 'Fundo do topo', 'alvo': '#inicio', 'parado': 'nenhum', 'opcoes': [['faiscas', 'Faíscas no mouse'], ['linhas', 'Linhas de estrada'], ['nenhum', 'Nenhum']]},
    {'id': 'vel', 'nome': 'Velocidade geral', 'alvo': None, 'parado': 'normal', 'opcoes': [['suave', 'Suave'], ['normal', 'Normal'], ['intenso', 'Intensa']]},
]

# ---------------------------------------------------------------------------
# Ícones (SVG em linha, cor = currentColor)
# ---------------------------------------------------------------------------
ICONES = {
    'camera': '<path d="M3 8.5A2.5 2.5 0 0 1 5.5 6h1.8l1.4-2h6.6l1.4 2h1.8A2.5 2.5 0 0 1 21 8.5v9a2.5 2.5 0 0 1-2.5 2.5h-13A2.5 2.5 0 0 1 3 17.5z"/><circle cx="12" cy="13" r="3.6"/>',
    'selo': '<circle cx="12" cy="9.5" r="6"/><path d="M8.6 14.6 7 22l5-3 5 3-1.6-7.4"/><path d="M9.5 9.5l1.8 1.8 3.2-3.4"/>',
    'paleta': '<path d="M12 3a9 9 0 1 0 0 18c1.4 0 2-1 2-2 0-1.4-1.2-1.8-1.2-3 0-1 .8-1.8 1.8-1.8H17a4 4 0 0 0 4-4C21 6.4 17 3 12 3z"/><circle cx="7.5" cy="11" r="1"/><circle cx="10" cy="7" r="1"/><circle cx="14.5" cy="7" r="1"/>',
    'fechar': '<path d="M6 6l12 12M18 6 6 18"/>',
    'whats': '<path d="M20 11.5a8 8 0 0 1-11.8 7L4 20l1.5-4A8 8 0 1 1 20 11.5z"/><path d="M9.2 8.6c.2 2.6 2.4 4.9 5 5.2l1.1-1.2 1.8.9-.4 1.6c-3.8.3-7.4-3.2-7.1-7.1l1.6-.4.8 1.8z"/>',
    'bomba': '<path d="M4 21V5a2 2 0 0 1 2-2h6a2 2 0 0 1 2 2v16M3 21h12M6.5 7h5v4h-5z"/><path d="M14 9h2a2 2 0 0 1 2 2v5a1.5 1.5 0 0 0 3 0V8l-3-3"/>',
    'loja': '<path d="M4 9.5V20h16V9.5M3 4h18l-1 5.5H4z"/><path d="M9 20v-5h6v5"/>',
    'oleo': '<path d="M12 3s5 5.6 5 9.5a5 5 0 0 1-10 0C7 8.6 12 3 12 3z"/><path d="M10 13.5a2 2 0 0 0 2 2"/>',
    'lavagem': '<path d="M5 17h14M4 17v-3.5l2-4.5h12l2 4.5V17M4 17v2h3v-2M17 17v2h3v-2"/><circle cx="7.5" cy="14" r=".8"/><circle cx="16.5" cy="14" r=".8"/><path d="M9 2.5s-1.2 1.5-1.2 2.3a1.2 1.2 0 0 0 2.4 0C10.2 4 9 2.5 9 2.5zM15 2.5s-1.2 1.5-1.2 2.3a1.2 1.2 0 0 0 2.4 0c0-.8-1.2-2.3-1.2-2.3z"/>',
    'calibragem': '<path d="M4.5 17a8.5 8.5 0 1 1 15 0"/><path d="M12 13l4-4"/><circle cx="12" cy="13" r="1.3"/>',
    'ducha': '<path d="M4 20V7a3 3 0 0 1 3-3h1a3 3 0 0 1 3 3"/><path d="M8.5 9h6l-1-2h-4z"/><path d="M10 12v1.5M12.5 12v2.5M15 12v1.5M11 16v1.5M14 16v1.5"/>',
    'arla': '<path d="M9 3h6v3l2 2v12a1 1 0 0 1-1 1H8a1 1 0 0 1-1-1V8l2-2z"/><path d="M9.5 17l2.5-6.5 2.5 6.5M10.3 15h3.4"/>',
    'banheiro': '<circle cx="7" cy="4.5" r="1.5"/><circle cx="17" cy="4.5" r="1.5"/><path d="M5 21v-6H4l1.2-6.5h3.6L10 15H9v6M15 21v-7h-1V9.5A1.5 1.5 0 0 1 15.5 8h3A1.5 1.5 0 0 1 20 9.5V14h-1v7M12 3v18"/>',
    'wifi': '<path d="M2.5 9a14 14 0 0 1 19 0M5.5 12.5a9.5 9.5 0 0 1 13 0M8.5 16a5 5 0 0 1 7 0"/><circle cx="12" cy="19" r=".9"/>',
    'estacionamento': '<rect x="3.5" y="3.5" width="17" height="17" rx="3"/><path d="M9.5 17V7h3.5a3 3 0 0 1 0 6H9.5"/>',
    'cafe': '<path d="M4 9h13v5a5 5 0 0 1-5 5H9a5 5 0 0 1-5-5z"/><path d="M17 10.5h1.5a2.5 2.5 0 0 1 0 5H17M8 3.5c-.6.8-.6 1.7 0 2.5M12 3.5c-.6.8-.6 1.7 0 2.5M3 21h15"/>',
    'pix': '<rect x="3.5" y="3.5" width="7" height="7" rx="1"/><rect x="13.5" y="3.5" width="7" height="7" rx="1"/><rect x="3.5" y="13.5" width="7" height="7" rx="1"/><path d="M14 14h2.5v2.5H14zM18 18h2.5v2.5H18zM18 14h2.5M14 18v2.5"/>',
    'cartao': '<rect x="2.5" y="5" width="19" height="14" rx="2.5"/><path d="M2.5 10h19M6 15h4"/>',
    'aproximacao': '<path d="M7 8.5a5 5 0 0 1 0 7M10.5 6a9 9 0 0 1 0 12M14 3.5a12.5 12.5 0 0 1 0 17"/>',
    'dinheiro': '<rect x="2.5" y="6" width="19" height="12" rx="2"/><circle cx="12" cy="12" r="2.8"/><path d="M6 9.5v5M18 9.5v5"/>',
    'caminhao': '<path d="M2.5 6h11v10h-11zM13.5 9.5h4l3 3.5V16h-7"/><circle cx="6.5" cy="17.5" r="1.8"/><circle cx="17" cy="17.5" r="1.8"/>',
    'relogio': '<circle cx="12" cy="12" r="9"/><path d="M12 7v5l3.5 2"/>',
    'pin': '<path d="M12 21s-7-6.2-7-11.5a7 7 0 0 1 14 0C19 14.8 12 21 12 21z"/><circle cx="12" cy="9.5" r="2.5"/>',
    'telefone': '<path d="M5 4h3.5l1.5 4.5-2 1.5a11 11 0 0 0 6 6l1.5-2 4.5 1.5V19a2 2 0 0 1-2 2A16 16 0 0 1 3 6a2 2 0 0 1 2-2z"/>',
    'insta': '<rect x="3.5" y="3.5" width="17" height="17" rx="5"/><circle cx="12" cy="12" r="4"/><circle cx="17" cy="7" r=".8"/>',
    'check': '<path d="M5 12.5l4.5 4.5L19 7.5"/>',
    'restaurante': '<path d="M7 3v8M5 3v5a2 2 0 0 0 4 0V3M7 11v10M16 3c-2 0-3 2.5-3 6h3M16 3v18"/>',
    'pneu': '<circle cx="12" cy="12" r="9"/><circle cx="12" cy="12" r="4"/><path d="M12 3v5M12 16v5M3 12h5M16 12h5"/>',
    'bateria': '<rect x="3" y="7" width="18" height="12" rx="2"/><path d="M7 7V5h3v2M14 7V5h3v2M7 13h3M15.5 11.5v3M14 13h3"/>',
    'alinhamento': '<path d="M12 3v18"/><rect x="4" y="5" width="5" height="6" rx="1"/><rect x="15" y="5" width="5" height="6" rx="1"/><rect x="4" y="13" width="5" height="6" rx="1"/><rect x="15" y="13" width="5" height="6" rx="1"/>',
    'chave': '<path d="M15 4a5 5 0 0 0-4.6 6.9L3.5 17.8a1.9 1.9 0 0 0 2.7 2.7l6.9-6.9A5 5 0 0 0 20 9l-3 1-2-2 1-3z"/>',
    'app': '<rect x="6.5" y="2.5" width="11" height="19" rx="2.5"/><path d="M10.5 18.5h3"/>',
    'seta': '<path d="M5 12h14M13 6l6 6-6 6"/>',
    'cama': '<path d="M3 18V6M3 13h18v5M21 13a3 3 0 0 0-3-3h-7v3"/><circle cx="7" cy="10" r="1.8"/>',
    'pao': '<path d="M4 11a4 4 0 0 1 2-7h12a4 4 0 0 1 2 7v8a1 1 0 0 1-1 1H5a1 1 0 0 1-1-1z"/><path d="M9 8v3M12 8v3M15 8v3"/>',
    'coracao': '<path d="M12 20s-7.5-4.6-7.5-10A4.3 4.3 0 0 1 12 7.4 4.3 4.3 0 0 1 19.5 10c0 5.4-7.5 10-7.5 10z"/>',
    'tag': '<path d="M3.5 12.5v-8a1 1 0 0 1 1-1h8l8 8-9 9z"/><circle cx="8" cy="8" r="1.4"/>',
    'calendario': '<rect x="3.5" y="5" width="17" height="15.5" rx="2"/><path d="M3.5 10h17M8 3v4M16 3v4"/>',
    'escudo': '<path d="M12 3l7.5 3v5.5c0 4.6-3.2 8.4-7.5 9.5-4.3-1.1-7.5-4.9-7.5-9.5V6z"/><path d="M8.5 12l2.5 2.5 4.5-5"/>',
    'pessoas': '<circle cx="9" cy="8" r="3.2"/><path d="M3 20a6 6 0 0 1 12 0"/><circle cx="17" cy="9" r="2.5"/><path d="M15.5 14.2A5 5 0 0 1 21 19"/>',
    'gota': '<path d="M12 3s6 6.4 6 11a6 6 0 0 1-12 0c0-4.6 6-11 6-11z"/>',
    'estrada': '<path d="M8 3 4 21M16 3l4 18M12 4v2.5M12 10v3M12 17v3"/>',
}

def sprite():
    s = ''.join('<symbol id="i-%s" viewBox="0 0 24 24">%s</symbol>' % (k, v) for k, v in ICONES.items())
    return '<svg width="0" height="0" style="position:absolute" aria-hidden="true" focusable="false">%s</svg>' % s

def ic(nome, cls='ic'):
    return '<svg class="%s" aria-hidden="true"><use href="#i-%s"/></svg>' % (cls, nome)

# ---------------------------------------------------------------------------
# Peças comuns de HTML
# ---------------------------------------------------------------------------
class Site:
    def __init__(self, d):
        self.d = d
        self.fotos = []          # vagas usadas (para o LEIA-ME-FOTOS.txt)

    def __getattr__(self, k):
        return self.d[k]

    def foto(self, arq, prop, desc, tam, alt, cls='', eager=False):
        if arq not in [f[0] for f in self.fotos]:
            self.fotos.append((arq, desc, tam))
        estilo = '' if 'foto-fundo' in cls or not prop else ' style="aspect-ratio:%s"' % prop
        carga = ' fetchpriority="high"' if eager else ' loading="lazy"'
        classes = ('foto ' + cls + (' eager' if eager else '')).strip()
        return ('<figure class="%s" data-foto="%s" data-proporcao="%s" data-desc="%s" data-tamanho="%s"%s>'
                '<img alt="%s"%s decoding="async"></figure>') % (classes, arq, prop, esc(desc), tam, estilo, esc(alt), carga)

    def wa(self, msg=None):
        from urllib.parse import quote
        return 'https://wa.me/%s?text=%s' % (self.whatsapp, quote(msg or self.mensagemWhats))

    def maps(self):
        from urllib.parse import quote
        return 'https://www.google.com/maps/search/?api=1&query=' + quote(self.endereco)

    def tel(self):
        return 'tel:+55' + re.sub(r'\D', '', self.telefone)

    def texto_bandeira(self):
        return 'Posto bandeira branca' if self.bandeira.lower() == 'bandeira branca' else 'Posto bandeira ' + self.bandeira


def preco_txt(v, casas=3):
    return 'R$ ' + (('%.' + str(casas) + 'f') % v).replace('.', ',')

def num_txt(v, casas=0):
    s = ('{:,.%df}' % casas).format(v)
    return s.replace(',', 'X').replace('.', ',').replace('X', '.')

def topo(s, links, sobre_foto):
    itens = ''.join('<li><a href="#%s">%s</a></li>' % (i, t) for i, t in links)
    return '''
<a class="pular" href="#conteudo">Pular para o conteúdo</a>
<header class="topo">
  <div class="wrap">
    <a class="logo" href="#inicio" aria-label="%(nome)s, voltar ao início">
      %(logo)s<span class="logo-nome" data-p="nome">%(nome)s</span>
    </a>
    <nav aria-label="Principal">
      <ul class="menu" id="menu">%(itens)s<li><a class="btn btn-prim" data-whats href="%(wa)s">%(icw)s Chamar no WhatsApp</a></li></ul>
    </nav>
    <a class="btn btn-prim btn-topo" data-whats href="%(wa)s">%(icw)s WhatsApp</a>
    <button class="burger" type="button" aria-expanded="false" aria-controls="menu" aria-label="Menu"><span></span></button>
  </div>
</header>''' % dict(nome=esc(s.nome), itens=itens, wa=esc(s.wa()), icw=ic('whats'),
                    logo=s.foto('logo.png', '', 'Logo do posto em PNG com fundo transparente', '600 x 200', 'Logo ' + s.nome, cls='vaga-logo', eager=True))

def lista_precos(s, cls_item='preco card rv', extra=''):
    out = []
    for i, item in enumerate(s.precos['itens']):
        nome, v = item[0], item[1]
        un = item[2] if len(item) > 2 else 'por litro'
        out.append('<li class="%s" data-preco="%d"%s><span class="preco-nome" data-pn>%s</span>'
                   '<strong class="preco-valor" data-num data-moeda data-valor="%s">%s</strong><span class="preco-un" data-pu>%s</span></li>'
                   % (cls_item, i, extra, esc(nome), v, preco_txt(v), un))
    return ''.join(out)

def nota_precos():
    return ('<p class="nota preco-nota">Preços atualizados em <span data-atualizado></span>. '
            'Preços sujeitos a alteração sem aviso.</p>')

def servicos(lista, cls='card rv servico'):
    return ''.join('<li class="%s">%s<h3>%s</h3><p>%s</p></li>' % (cls, ic(i, 'ic ic-servico'), esc(t), esc(d)) for i, t, d in lista)

PAGAMENTOS = [('pix', 'Pix', 'Na pista e na loja, com QR Code na hora.'),
              ('aproximacao', 'Aproximação', 'Cartão, celular ou relógio, sem inserir o cartão.'),
              ('cartao', 'Débito e crédito', 'Principais bandeiras aceitas.'),
              ('caminhao', 'Cartão frota', 'Para empresas, com controle por veículo.'),
              ('dinheiro', 'Dinheiro', 'Com troco na pista e na loja.')]

def pagamentos(cls='card rv pag'):
    return ''.join('<li class="%s">%s<div><h3>%s</h3><p>%s</p></div></li>' % (cls, ic(i, 'ic ic-pag'), t, d) for i, t, d in PAGAMENTOS)

def secao_bandeira(s, titulo, texto, totem_idx, cls=''):
    totem_linhas = ''.join(
        '<div class="totem-linha" data-preco="%d"><span data-pn>%s</span><span data-num data-moeda data-valor="%s">%s</span></div>'
        % (i, esc(s.precos['itens'][i][0]), s.precos['itens'][i][1], preco_txt(s.precos['itens'][i][1])) for i in totem_idx)
    parc = ''.join('<div class="parc-item">%s</div>' % s.foto(
        'parceiro-%d.png' % (i + 1), '5/2', 'Logo: %s. PNG com fundo transparente' % n, '400 x 160', 'Logo ' + n, cls='vaga-marca')
        for i, n in enumerate(s.parceiros[:8]))
    selo_desc = 'Selo da bandeira do posto em PNG com fundo transparente'
    return '''
<section id="bandeira" class="secao bandeira %(cls)s" data-loop aria-labelledby="t-bandeira">
  <div class="wrap band-grid">
    <div class="band-txt rv">
      <p class="rotulo">Bandeira e parceiros</p>
      <h2 id="t-bandeira">%(titulo)s</h2>
      <p class="sub">%(texto)s</p>
    </div>
    <div class="bandeira-area">
      <div class="selo-palco"><div class="selo obs"><div class="selo-cartao">%(selo)s<p data-p-bandeira>%(band)s</p></div></div></div>
      <div class="totem obs">
        <div class="totem-placa">%(selo2)s<p class="totem-band" data-p-bandeira>%(band)s</p>%(linhas)s</div>
        <div class="totem-poste"></div><div class="totem-base"></div>
      </div>
    </div>
  </div>
  <div class="wrap parc-wrap">
    <h3 class="parc-titulo">Parceiros do posto</h3>
    <div class="parc-palco parc-grade">%(parc)s</div>
  </div>
</section>''' % dict(cls=cls, titulo=titulo, texto=texto, band=esc(s.texto_bandeira()), linhas=totem_linhas, parc=parc,
                     selo=s.foto('bandeira.png', '1/1', selo_desc, '600 x 600', 'Selo da bandeira do posto', cls='vaga-marca'),
                     selo2=s.foto('bandeira.png', '1/1', selo_desc, '600 x 600', 'Selo da bandeira do posto', cls='vaga-marca'))

def secao_depoimentos(s, textos, cls=''):
    cards = ''.join('''<li class="card rv depo"><span class="depo-selo">Exemplo de depoimento</span>
      <blockquote><p>%s</p></blockquote><p class="depo-autor">Cliente de exemplo, %s</p></li>''' % (esc(t), esc(s.cidade_uf)) for t in textos)
    return '''
<section id="depoimentos" class="secao depoimentos %s" aria-labelledby="t-depo">
  <div class="wrap">
    <div class="cab rv"><p class="rotulo">Quem abastece aqui</p><h2 id="t-depo">O que os clientes dizem</h2>
      <p class="sub">Os depoimentos abaixo são exemplos. No site do posto, entram frases reais de clientes, com autorização.</p></div>
    <ul class="depo-lista" data-stagger>%s</ul>
  </div>
</section>''' % (cls, cards)

def secao_local(s, titulo, cls=''):
    linhas = ''.join('<tr><th scope="row">%s</th><td>%s</td></tr>' % (esc(a), esc(b)) for a, b in s.horario)
    return '''
<section id="localizacao" class="secao local %(cls)s" aria-labelledby="t-local">
  <div class="wrap local-grid">
    <div class="local-info rv">
      <p class="rotulo">Horário e localização</p>
      <h2 id="t-local">%(titulo)s</h2>
      <table class="horario"><caption class="sr">Horário de funcionamento</caption><tbody data-horario>%(linhas)s</tbody></table>
      <p class="endereco">%(icpin)s<span data-p="endereco">%(end)s</span></p>
      <div class="acoes"><a class="btn btn-prim" data-maps href="%(maps)s" target="_blank" rel="noopener">%(icseta)s Abrir no Google Maps</a>
        <a class="btn btn-sec" data-tel href="%(tel)s">%(ictel)s <span data-p="telefone">%(telt)s</span></a></div>
    </div>
    <div class="local-mapa rv">%(mapa)s</div>
  </div>
</section>''' % dict(cls=cls, titulo=titulo, linhas=linhas, icpin=ic('pin'), end=esc(s.endereco), maps=esc(s.maps()), icseta=ic('pin'),
                     tel=s.tel(), ictel=ic('telefone'), telt=esc(s.telefone),
                     mapa=s.foto('mapa.jpg', '16/9', 'Print do mapa ou substituir pelo iframe do Google Maps', '1280 x 720', 'Mapa de localização do posto'))

def secao_final(s, titulo, texto, cls=''):
    return '''
<section id="contato" class="secao final %s" aria-labelledby="t-final">
  <div class="wrap final-box rv">
    <h2 id="t-final">%s</h2>
    <p class="sub">%s</p>
    <div class="acoes"><a class="btn btn-prim" data-whats href="%s">%s Chamar no WhatsApp</a>
      <a class="btn btn-sec" data-maps href="%s" target="_blank" rel="noopener">%s Como chegar</a></div>
  </div>
</section>''' % (cls, titulo, texto, esc(s.wa()), ic('whats'), esc(s.maps()), ic('pin'))

def rodape(s, cls=''):
    return '''
</main>
<footer class="rodape %(cls)s">
  <div class="wrap">
    <div class="rod-grid">
      <div>
        <a class="logo" href="#inicio" aria-label="%(nome)s, voltar ao início">%(logo)s<span class="logo-nome" data-p="nome">%(nome)s</span></a>
        <p class="rod-slogan" data-p="slogan">%(slogan)s</p>
      </div>
      <div>
        <h2 class="rod-tit">Contato</h2>
        <ul class="rod-lista">
          <li><a data-whats href="%(wa)s">%(icw)s WhatsApp</a></li>
          <li><a data-tel href="%(tel)s">%(ict)s <span data-p="telefone">%(telt)s</span></a></li>
          <li><a data-insta href="https://www.instagram.com/%(insta)s/" target="_blank" rel="noopener">%(ici)s <span data-insta-txt>@%(insta)s</span></a></li>
        </ul>
      </div>
      <div>
        <h2 class="rod-tit">Endereço e horário</h2>
        <ul class="rod-lista">
          <li>%(icp)s <span data-p="endereco">%(end)s</span></li>
          <li>%(icr)s <span>%(hor)s</span></li>
          <li>CNPJ <span data-p="cnpj">%(cnpj)s</span></li>
        </ul>
      </div>
    </div>
    <p class="aviso-modelo">Modelo de demonstração. Textos, preços e imagens serão substituídos pelos do posto. &copy; <span data-ano>2026</span> <span data-p="nome">%(nome)s</span>.</p>
  </div>
</footer>
<a class="whats-flutua" data-whats href="%(wa)s" aria-label="Conversar com o posto pelo WhatsApp">%(icw2)s</a>''' % dict(
        cls=cls, nome=esc(s.nome), slogan=esc(s.slogan), wa=esc(s.wa()), icw=ic('whats'), icw2=ic('whats'), tel=s.tel(), ict=ic('telefone'),
        telt=esc(s.telefone), insta=s.instagram, ici=ic('insta'), icp=ic('pin'), end=esc(s.endereco), icr=ic('relogio'),
        hor=esc(s.horario[0][0] + ': ' + s.horario[0][1]), cnpj=s.cnpj,
        logo=s.foto('logo.png', '', 'Logo do posto em PNG com fundo transparente', '600 x 200', 'Logo ' + s.nome, cls='vaga-logo'))

def titulo_linhas(linhas):
    return ''.join('<span class="ln"><span style="--l:%d">%s</span></span>' % (i, l) for i, l in enumerate(linhas))

def selos_hero(lista):
    return ''.join('<li>%s<span>%s</span></li>' % (ic(i), esc(t)) for i, t in lista)

def stats(s, cls='stat card rv'):
    return ''.join('<li class="%s" data-numero="%d"><strong data-num data-valor="%s" data-sufixo="%s">%s%s</strong><span data-nt>%s</span></li>'
                   % (cls, i, v, suf, num_txt(v), suf, esc(t)) for i, (v, suf, t) in enumerate(s.numeros))

# ---------------------------------------------------------------------------
# HEAD
# ---------------------------------------------------------------------------
def json_ld(s):
    horas = [{'@type': 'OpeningHoursSpecification', 'dayOfWeek': dias, 'opens': a, 'closes': f} for dias, a, f in s.ld_horas]
    return json.dumps({
        '@context': 'https://schema.org', '@type': 'GasStation', 'name': s.nome, 'description': s.descricao,
        'telephone': '+55 ' + s.telefone, 'image': 'img/og.jpg',
        'address': {'@type': 'PostalAddress', 'streetAddress': s.endereco, 'addressLocality': s.cidade, 'addressRegion': s.uf, 'addressCountry': 'BR'},
        'openingHoursSpecification': horas,
        'paymentAccepted': 'Pix, cartão de débito, cartão de crédito, cartão frota, dinheiro',
    }, ensure_ascii=False)

def dados_js(s):
    chaves = ['id', 'nome', 'inicial', 'slogan', 'whatsapp', 'telefone', 'endereco', 'cidade', 'cnpj', 'instagram', 'horario', 'precos',
              'numeros', 'pacotes', 'bandeira', 'parceiros', 'mensagemWhats', 'paleta', 'motion', 'mostrarSeletor']
    linhas = []
    for k in chaves:
        v = s.d.get(k, [] if k in ('numeros', 'pacotes') else None)
        linhas.append('  %s: %s' % (k, json.dumps(v, ensure_ascii=False)))
    return ('/* ===== DADOS DO POSTO: troque aqui nome, contatos, horário e preços ===== */\n'
            'window.POSTO = {\n' + ',\n'.join(linhas) + '\n};\n'
            '/* Paletas do seletor de cores (a primeira é a do conceito) */\n'
            'window.PALETAS = ' + json.dumps(s.paletas, ensure_ascii=False) + ';\n'
            'window.MOTION_OPCOES = ' + json.dumps(MOTION_OPCOES, ensure_ascii=False) + ';\n')

def root_css(s):
    pal = [p for p in s.paletas if p['id'] == s.paleta][0]
    c = completar(pal['cores'])
    vars_ = ''.join('--%s:%s;' % (k, v) for k, v in c.items())
    return (':root{%s--sobre-foto:#FFFFFF;--veu:rgba(6,8,12,.62);--topo:76px;--m-vel:1;--m-dist:1;--titulo:%s;--corpo:%s}'
            % (vars_, s.fonte_titulo, s.fonte_corpo))

def favicon(s):
    pal = [p for p in s.paletas if p['id'] == s.paleta][0]
    c = completar(pal['cores'])
    from urllib.parse import quote
    svg = ("<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 64 64'><rect width='64' height='64' rx='14' fill='%s'/>"
           "<text x='32' y='44' font-family='Arial,Helvetica,sans-serif' font-size='34' font-weight='700' text-anchor='middle' fill='%s'>%s</text></svg>"
           % (c['marca'], c['marca-texto'], s.inicial))
    return 'data:image/svg+xml,' + quote(svg)

def head(s, css_site):
    pal = [p for p in s.paletas if p['id'] == s.paleta][0]
    attrs = ' '.join('data-m-%s="%s"' % (k, v) for k, v in s.motion.items())
    return '''<!doctype html>
<html lang="pt-BR" %(attrs)s>
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>%(title)s</title>
<meta name="description" content="%(desc)s">
<!-- MODELO: remover a linha abaixo quando for publicar o site real do posto -->
<meta name="robots" content="noindex">
<meta name="theme-color" content="%(tc)s">
<meta property="og:type" content="website">
<meta property="og:title" content="%(title)s">
<meta property="og:description" content="%(desc)s">
<meta property="og:image" content="img/og.jpg">
<meta property="og:locale" content="pt_BR">
<link rel="icon" type="image/svg+xml" href="%(fav)s">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="%(fontes)s">
<link rel="preload" as="image" href="img/hero.jpg" fetchpriority="high">
<style>
%(root)s
%(core)s
/* ==================== ESTILO DESTE MODELO ==================== */
%(site)s
</style>
<script>
%(dados)s
</script>
<script>
%(pre)s
</script>
<script type="application/ld+json" id="ld-posto">%(ld)s</script>
</head>''' % dict(attrs=attrs, title=esc(s.titulo), desc=esc(s.descricao), tc=pal['cores']['fundo'], fav=favicon(s),
                  fontes=esc(s.fontes_url), root=root_css(s), core=ler('core.css'), site=css_site, dados=dados_js(s),
                  pre=ler('pre.js'), ld=json_ld(s))

def fim(s):
    return '''
<script>
%s
</script>
</body>
</html>
''' % ler('core.js')

# ---------------------------------------------------------------------------
# DADOS DOS 5 POSTOS
# ---------------------------------------------------------------------------
TODOS_DIAS = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
SEG_SAB = TODOS_DIAS[:6]

POSTOS = [
  dict(id='posto-1', pasta='posto 1', conceito='Rodovia', nome='Posto Estrada Real', inicial='E',
       titulo='Posto Estrada Real | Diesel S10, Arla 32 e parada 24h na BR',
       descricao='Posto de rodovia aberto 24 horas, com diesel S10, Arla 32, pátio para carretas, banho e restaurante. Modelo de demonstração.',
       slogan='Parada completa para quem vive na estrada.',
       whatsapp='5535900000000', telefone='(35) 0000-0000', endereco='Rodovia BR-000, km 000, Cidade - UF', cidade='Cidade', uf='UF', cidade_uf='Cidade - UF',
       cnpj='00.000.000/0000-00', instagram='postoexemplo',
       horario=[['Pista e conveniência', '24 horas, todos os dias'], ['Restaurante', '6h às 22h'], ['Banho', '24 horas']],
       ld_horas=[(TODOS_DIAS, '00:00', '23:59')],
       precos={'atualizado': '22/11/2026', 'itens': [['Diesel S10', 6.09], ['Diesel S500', 5.99], ['Gasolina comum', 6.29], ['Etanol', 4.39], ['Arla 32', 3.49]]},
       numeros=[[24, 'h', 'de portas abertas, todos os dias'], [60, '', 'vagas no pátio para carreta'], [8, '', 'bicos de diesel S10 na pista']],
       bandeira='Nome da Bandeira', parceiros=['Distribuidora', 'Cartão frota', 'App de frete', 'Lubrificante', 'Rastreamento', 'Seguradora'],
       mensagemWhats='Olá! Vim pelo site do Posto Estrada Real e gostaria de mais informações.',
       paleta='padrao', mostrarSeletor=True,
       motion={'bandeira': 'brilho', 'parceiros': 'faixa', 'hero': 'mascara', 'foto': 'zoom', 'cards': 'subir', 'numeros': 'contar', 'fundo': 'faiscas', 'vel': 'normal'},
       paletas=[paleta('padrao', 'Grafite e âmbar', '#F5A524', '#FF6B2C', 'escuro'),
                paleta('vermelho', 'Vermelho e grafite', '#D7263D', '#F5A524', 'escuro'),
                paleta('azul', 'Azul e amarelo', '#3D8BFD', '#F5C518', 'escuro'),
                paleta('verde', 'Verde e grafite', '#22B55F', '#C8E64A', 'escuro'),
                paleta('laranja', 'Laranja e grafite', '#FF7A1A', '#FFD166', 'escuro'),
                # paletas de 3 cores: base + cor normal + cor vibrante
                paleta3('petroleo', 'Petróleo, areia e laranja vibrante', '#0F1E24', '#C9B79C', '#FF6A13'),
                paleta3('marinho', 'Marinho, aço e amarelo neon', '#0E1628', '#8FA3B8', '#FFD60A'),
                paleta3('oliva', 'Grafite, oliva e verde-limão', '#15171A', '#8A9A5B', '#A3E635'),
                paleta3('vinho', 'Vinho, rosé e vermelho vibrante', '#1E1215', '#B8A0A4', '#FF2E4D'),
                paleta3('cobre', 'Carvão, cobre e ciano elétrico', '#121417', '#C07A3E', '#00E5FF')],
       fontes_url='https://fonts.googleapis.com/css2?family=Barlow+Condensed:wght@600;700;800&family=Inter:wght@400;500;600;700&display=swap',
       fonte_titulo="'Barlow Condensed', 'Arial Narrow', sans-serif", fonte_corpo="'Inter', system-ui, sans-serif",
       totem=[0, 2, 3], css='posto1.css', apoio_icones=True),
  dict(id='posto-2', pasta='posto 2', conceito='Urbano premium', nome='Posto Avenida', inicial='A',
       titulo='Posto Avenida | Combustível, conveniência e café na cidade',
       descricao='Posto urbano com gasolina aditivada, loja de conveniência, café, Pix e pagamento por aproximação. Modelo de demonstração.',
       slogan='Abasteça, pegue um café e siga o seu dia.',
       whatsapp='5535900000000', telefone='(35) 0000-0000', endereco='Avenida Exemplo, 000, Centro, Cidade - UF', cidade='Cidade', uf='UF', cidade_uf='Cidade - UF',
       cnpj='00.000.000/0000-00', instagram='postoexemplo',
       horario=[['Segunda a sábado', '6h à meia-noite'], ['Domingo e feriados', '7h às 22h'], ['Café', '7h às 21h']],
       ld_horas=[(SEG_SAB, '06:00', '23:59'), (['Sunday'], '07:00', '22:00')],
       precos={'atualizado': '22/11/2026', 'itens': [['Gasolina comum', 6.29], ['Gasolina aditivada', 6.59], ['Etanol', 4.39], ['Diesel S10', 6.19]]},
       numeros=[],
       bandeira='Nome da Bandeira', parceiros=['Distribuidora', 'App de fidelidade', 'Cafeteria', 'Marca de bebidas', 'Carteira digital', 'Cartão de benefícios'],
       mensagemWhats='Olá! Vim pelo site do Posto Avenida e gostaria de mais informações.',
       paleta='padrao', mostrarSeletor=True,
       motion={'bandeira': 'flutuar', 'parceiros': 'destaque', 'hero': 'foco', 'foto': 'cortina', 'cards': 'escala', 'numeros': 'contar', 'fundo': 'nenhum', 'vel': 'suave'},
       paletas=[paleta('padrao', 'Branco e azul-petróleo', '#0E6B78', '#2DD4BF', 'claro'),
                paleta('vermelho', 'Vermelho e branco', '#C8102E', '#FF8A80', 'claro'),
                paleta('azul', 'Azul e amarelo', '#1D4ED8', '#FACC15', 'claro'),
                paleta('verde', 'Verde e branco', '#15803D', '#86EFAC', 'claro'),
                paleta('laranja', 'Laranja e branco', '#C2410C', '#FDBA74', 'claro')],
       fontes_url='https://fonts.googleapis.com/css2?family=Manrope:wght@400;500;600;700;800&display=swap',
       fonte_titulo="'Manrope', system-ui, sans-serif", fonte_corpo="'Manrope', system-ui, sans-serif",
       totem=[0, 1, 2], css='posto2.css'),
  dict(id='posto-3', pasta='posto 3', conceito='Família, cidade pequena', nome='Auto Posto Bom Jesus', inicial='B',
       titulo='Auto Posto Bom Jesus | O posto da cidade desde 1986',
       descricao='Posto de família na cidade, com atendimento pelo nome, lavagem, calibragem e lanchonete. Modelo de demonstração.',
       slogan='O posto da cidade, atendendo pelo nome desde 1986.',
       whatsapp='5535900000000', telefone='(35) 0000-0000', endereco='Rua Exemplo, 000, Centro, Cidade - UF', cidade='Cidade', uf='UF', cidade_uf='Cidade - UF',
       cnpj='00.000.000/0000-00', instagram='postoexemplo', desde=1986,
       horario=[['Segunda a sábado', '6h às 22h'], ['Domingo', '7h às 20h'], ['Lanchonete', '6h às 20h']],
       ld_horas=[(SEG_SAB, '06:00', '22:00'), (['Sunday'], '07:00', '20:00')],
       precos={'atualizado': '22/11/2026', 'itens': [['Gasolina comum', 6.29], ['Gasolina aditivada', 6.49], ['Etanol', 4.39], ['Diesel S10', 6.09]]},
       numeros=[[40, '', 'anos atendendo a cidade'], [3, '', 'gerações da mesma família'], [12, '', 'pessoas na nossa equipe']],
       bandeira='Nome da Bandeira', parceiros=['Distribuidora', 'Padaria parceira', 'Cooperativa', 'Lubrificante', 'Seguradora', 'Cartão de benefícios'],
       mensagemWhats='Olá! Vim pelo site do Auto Posto Bom Jesus e gostaria de mais informações.',
       paleta='padrao', mostrarSeletor=True,
       motion={'bandeira': 'virar', 'parceiros': 'cascata', 'hero': 'palavras', 'foto': 'zoom', 'cards': 'subir', 'numeros': 'contar', 'fundo': 'nenhum', 'vel': 'suave'},
       paletas=[paleta('padrao', 'Creme, verde e laranja', '#2F6B3F', '#E8833A', 'creme'),
                paleta('vermelho', 'Vermelho e creme', '#A4262C', '#E8A33A', 'creme'),
                paleta('azul', 'Azul e creme', '#1F4E8C', '#E8B43A', 'creme'),
                paleta('verde', 'Verde-oliva e mostarda', '#55652A', '#D9A21B', 'creme'),
                paleta('laranja', 'Terracota e creme', '#A84B24', '#6B8F4E', 'creme')],
       fontes_url='https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,600;9..144,700&family=Nunito+Sans:wght@400;600;700;800&display=swap',
       fonte_titulo="'Fraunces', Georgia, serif", fonte_corpo="'Nunito Sans', system-ui, sans-serif",
       totem=[0, 2, 3], css='posto3.css'),
  dict(id='posto-4', pasta='posto 4', conceito='Econômico', nome='Posto Preço Justo', inicial='P',
       titulo='Posto Preço Justo | Preço na placa e formas de pagamento',
       descricao='Posto bandeira branca com tabela de preços sempre à vista, Pix, cartão e horário estendido. Modelo de demonstração.',
       slogan='Preço na placa, atendimento rápido e sem surpresa.',
       whatsapp='5535900000000', telefone='(35) 0000-0000', endereco='Avenida Exemplo, 000, Bairro Exemplo, Cidade - UF', cidade='Cidade', uf='UF', cidade_uf='Cidade - UF',
       cnpj='00.000.000/0000-00', instagram='postoexemplo',
       horario=[['Todos os dias', '6h às 23h'], ['Loja', '6h às 23h']],
       ld_horas=[(TODOS_DIAS, '06:00', '23:00')],
       precos={'atualizado': '22/11/2026', 'itens': [['Gasolina comum', 6.09], ['Gasolina aditivada', 6.29], ['Etanol', 4.19], ['Diesel S10', 5.89], ['Diesel S500', 5.79]]},
       numeros=[],
       bandeira='Bandeira branca', parceiros=['Distribuidora', 'Cartão de benefícios', 'Carteira digital', 'Clube de descontos', 'Cartão frota', 'Marca de bebidas'],
       mensagemWhats='Olá! Vim pelo site do Posto Preço Justo e gostaria de mais informações.',
       paleta='padrao', mostrarSeletor=True,
       motion={'bandeira': 'pulsar', 'parceiros': 'faixa-dupla', 'hero': 'cascata', 'foto': 'parallax', 'cards': 'escala', 'numeros': 'bomba', 'fundo': 'nenhum', 'vel': 'intenso'},
       paletas=[paleta('padrao', 'Vermelho, preto e branco', '#D90429', '#111111', 'branco-forte'),
                paleta('azul', 'Azul e amarelo', '#0050C8', '#FFC300', 'branco-forte'),
                paleta('verde', 'Verde e amarelo', '#0A7F38', '#FFD000', 'branco-forte'),
                paleta('laranja', 'Laranja e preto', '#E85D04', '#111111', 'branco-forte'),
                paleta('amarelo', 'Preto e amarelo', '#161616', '#FFC300', 'branco-forte')],
       fontes_url='https://fonts.googleapis.com/css2?family=Archivo:wght@400;500;600;700;800;900&display=swap',
       fonte_titulo="'Archivo', 'Arial Black', sans-serif", fonte_corpo="'Archivo', system-ui, sans-serif",
       totem=[0, 2, 3], css='posto4.css'),
  dict(id='posto-5', pasta='posto 5', conceito='Autocenter', nome='Posto & Autocenter Central', inicial='C',
       titulo='Posto & Autocenter Central | Troca de óleo, pneus, alinhamento e lavagem',
       descricao='Posto com autocenter: troca de óleo, pneus, alinhamento, balanceamento, bateria e lavagem, com agendamento pelo WhatsApp. Modelo de demonstração.',
       slogan='Abastece, revisa e lava no mesmo lugar.',
       whatsapp='5535900000000', telefone='(35) 0000-0000', endereco='Avenida Exemplo, 000, Centro, Cidade - UF', cidade='Cidade', uf='UF', cidade_uf='Cidade - UF',
       cnpj='00.000.000/0000-00', instagram='postoexemplo',
       horario=[['Pista: todos os dias', '6h às 22h'], ['Autocenter: segunda a sexta', '8h às 18h'], ['Autocenter: sábado', '8h às 13h']],
       ld_horas=[(TODOS_DIAS, '06:00', '22:00')],
       precos={'atualizado': '22/11/2026', 'itens': [['Gasolina comum', 6.29], ['Gasolina aditivada', 6.49], ['Etanol', 4.39], ['Diesel S10', 6.09]]},
       numeros=[],
       bandeira='Nome da Bandeira', parceiros=['Distribuidora', 'Marca de pneus', 'Marca de lubrificante', 'Marca de baterias', 'Peças automotivas', 'Seguradora'],
       mensagemWhats='Olá! Vim pelo site do Posto & Autocenter Central e gostaria de agendar um serviço.',
       paleta='padrao', mostrarSeletor=True,
       motion={'bandeira': 'totem', 'parceiros': 'colunas', 'hero': 'mascara', 'foto': 'parallax', 'cards': 'inclinar', 'numeros': 'contar', 'fundo': 'linhas', 'vel': 'normal'},
       paletas=[paleta('padrao', 'Azul-marinho e laranja', '#FF7A1A', '#3B82F6', 'marinho'),
                paleta('vermelho', 'Vermelho e marinho', '#F0484A', '#FACC15', 'marinho'),
                paleta('verde', 'Verde e marinho', '#22C55E', '#38BDF8', 'marinho'),
                paleta('amarelo', 'Amarelo e marinho', '#FACC15', '#FF7A1A', 'marinho'),
                paleta('claro', 'Laranja e branco', '#C2410C', '#1D4ED8', 'claro')],
       fontes_url='https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@500;600;700&family=IBM+Plex+Sans:wght@400;500;600;700&display=swap',
       fonte_titulo="'Space Grotesk', system-ui, sans-serif", fonte_corpo="'IBM Plex Sans', system-ui, sans-serif",
       totem=[0, 2, 3], css='posto5.css'),
]

# ---------------------------------------------------------------------------
# CORPO DE CADA SITE
# ---------------------------------------------------------------------------
def corpo_1(s):
    serv = [('bomba', 'Diesel S10 e S500', 'Bicos dedicados para carreta, com vazão alta.'),
            ('arla', 'Arla 32 na bomba', 'Abasteça o Arla junto com o diesel, sem descer galão.'),
            ('ducha', 'Banho quente', 'Chuveiros limpos, toalha e sabonete na conveniência.'),
            ('restaurante', 'Restaurante', 'Comida caseira no almoço e no jantar.'),
            ('estacionamento', 'Pátio iluminado', 'Vagas para carreta com iluminação e câmeras.'),
            ('loja', 'Conveniência 24h', 'Bebidas, lanches e itens de viagem a qualquer hora.'),
            ('wifi', 'Wi-Fi', 'Internet gratuita no restaurante e na loja.'),
            ('banheiro', 'Banheiros', 'Limpos e abertos dia e noite.')]
    parada = [('Pista de diesel', 'Bicos de diesel S10 e S500 e Arla 32 na bomba, com espaço para manobra.', 'Carreta na pista de diesel, de frente, com o posto ao fundo'),
              ('Na estrada com você', 'Na beira da BR, com entrada e saída fáceis para veículo pesado.', 'Caminhão na rodovia em frente ao posto'),
              ('Pátio para carretas', 'Vagas amplas, iluminadas e com câmeras para descansar com calma.', 'Pátio com carretas estacionadas ao entardecer'),
              ('Pernoite tranquilo', 'Banho, comida e um lugar seguro para dormir antes de seguir.', 'Pátio à noite com carretas paradas'),
              ('Hora de seguir', 'Tanque cheio, Arla em dia e a próxima entrega no horário.', 'Caminhão saindo do posto para a estrada'),
              ('Abastecimento rápido', 'Frentistas na pista o dia todo para você perder menos tempo.', 'Frentista abastecendo, mão no bico')]
    pilha = ''.join('''<article class="pilha-item">%s<div class="pilha-texto"><h3>%s</h3><p>%s</p></div></article>'''
                    % (s.foto('galeria-%d.jpg' % (i + 1), '4/3', d, '1200 x 900', t), t, x) for i, (t, x, d) in enumerate(parada))
    return '''
<body class="topo-sobre-foto m1">
%(sprite)s
%(topo)s
<main id="conteudo">
<section class="hero" id="inicio" aria-labelledby="t-hero">
  <div class="hero-media hero-cheio">%(hero)s</div>
  <div class="hero-veu"></div>
  <div class="hero-linhas" aria-hidden="true"><i></i><i></i><i></i></div>
  <div class="wrap hero-txt">
    <p class="km h-in" style="--i:0">%(icpin)s <span data-p="endereco">%(end)s</span></p>
    <h1 id="t-hero" class="h-in" style="--i:1">%(h1)s</h1>
    <p class="lead h-in" style="--i:2">Diesel S10, Arla 32 na bomba, banho quente, restaurante e pátio iluminado para a sua carreta. Aberto 24 horas, todos os dias.</p>
    <div class="acoes h-in" style="--i:3"><a class="btn btn-prim" data-maps href="%(maps)s" target="_blank" rel="noopener">%(icpin)s Como chegar</a>
      <a class="btn btn-foto" data-whats href="%(wa)s">%(icw)s WhatsApp</a></div>
    <ul class="selos h-in" style="--i:4">%(selos)s</ul>
  </div>
</section>

<section class="faixa-num" aria-label="O posto em números">
  <ul class="wrap nums" data-stagger>%(stats)s</ul>
</section>

<section id="precos" class="secao precos" aria-labelledby="t-precos">
  <div class="wrap">
    <div class="cab rv"><p class="rotulo">Preços de hoje</p><h2 id="t-precos">Combustível com preço à vista na placa</h2>
      <p class="sub">Confira antes de sair da estrada. Para frotas, fale com a gente sobre condições no cartão frota.</p></div>
    <ul class="precos-lista" data-stagger>%(precos)s</ul>
    %(nota)s
  </div>
</section>

<section id="servicos" class="secao servicos alt" aria-labelledby="t-serv">
  <div class="wrap">
    <div class="cab rv"><p class="rotulo">Estrutura</p><h2 id="t-serv">Tudo o que a parada precisa ter</h2>
      <p class="sub">Do bico de diesel ao chuveiro, a estrutura foi pensada para quem passa o dia na estrada.</p></div>
    <ul class="serv-grid" data-stagger>%(serv)s</ul>
  </div>
</section>

<section id="parada" class="parada" aria-labelledby="t-parada">
  <div class="hscroll" data-hscroll>
    <div class="hscroll-fixo">
      <div class="wrap cab-h"><p class="rotulo">Galeria</p><h2 id="t-parada">Conheça a parada</h2></div>
      <div class="pilha">%(pilha)s</div>
    </div>
  </div>
</section>

<section id="restaurante" class="secao restaurante" aria-labelledby="t-rest">
  <div class="wrap rest-grid">
    <div class="rest-foto rv">%(destaque)s</div>
    <div class="rest-txt rv">
      <p class="rotulo">Restaurante</p>
      <h2 id="t-rest">Comida de verdade antes de pegar a estrada</h2>
      <p class="sub">Prato feito, marmitex e café passado na hora. Abre às 6h e fecha às 22h, com mesa para descansar e Wi-Fi.</p>
      <ol class="fluxo">
        <li>%(icb)s<span>Abasteça</span></li><li class="tracejado" aria-hidden="true"></li>
        <li>%(icc)s<span>Descanse</span></li><li class="tracejado" aria-hidden="true"></li>
        <li>%(ice)s<span>Siga viagem</span></li>
      </ol>
    </div>
  </div>
</section>
%(bandeira)s
<section id="pagamento" class="secao pagamento alt" aria-labelledby="t-pag">
  <div class="wrap">
    <div class="cab rv"><p class="rotulo">Formas de pagamento</p><h2 id="t-pag">Pague do jeito que a sua empresa usa</h2>
      <p class="sub">Cartão frota com controle por placa, Pix com comprovante na hora e nota fiscal para o seu acerto de viagem.</p></div>
    <ul class="pag-grid" data-stagger>%(pag)s</ul>
  </div>
</section>
%(depo)s
%(local)s
%(final)s
%(rodape)s
''' % dict(sprite=sprite(), topo=topo(s, [('precos', 'Preços'), ('servicos', 'Estrutura'), ('parada', 'Galeria'), ('restaurante', 'Restaurante'), ('localizacao', 'Como chegar')], True),
           hero=s.foto('hero.jpg', '16/9', 'Fachada do posto à noite, com a cobertura e as bombas iluminadas', '1920 x 1080', 'Posto Estrada Real iluminado à noite', cls='foto-fundo', eager=True),
           icpin=ic('pin'), end=esc(s.endereco), h1=titulo_linhas(['Abasteça, descanse', 'e siga viagem', 'com tranquilidade.']),
           maps=esc(s.maps()), wa=esc(s.wa()), icw=ic('whats'),
           selos=selos_hero([('relogio', 'Aberto 24h'), ('arla', 'Diesel S10 e Arla 32'), ('caminhao', 'Pátio para carretas')]),
           stats=stats(s), precos=lista_precos(s), nota=nota_precos(), serv=servicos(serv), pilha=pilha,
           destaque=s.foto('destaque.jpg', '4/3', 'Prato do restaurante servido na mesa, de cima, com boa luz', '1200 x 900', 'Prato feito do restaurante do posto'),
           icb=ic('bomba'), icc=ic('cama'), ice=ic('estrada'),
           bandeira=secao_bandeira(s, 'Combustível de origem garantida', 'O selo da bandeira e as marcas que trabalham com a gente. As logos entram quando o posto enviar os arquivos.', s.totem),
           pag=pagamentos(), depo=secao_depoimentos(s, ['Parada certa na minha rota. Diesel bom, banho limpo e comida no capricho.',
                                                         'Pátio iluminado e seguro para dormir. Faço questão de parar aqui.',
                                                         'Arla na bomba e cartão frota sem burocracia. Rápido para seguir viagem.']),
           local=secao_local(s, 'Na beira da BR, aberto o tempo todo'),
           final=secao_final(s, 'Vai passar pela região?', 'Chame no WhatsApp para saber o preço do diesel, reservar vaga no pátio ou combinar o abastecimento da frota.'),
           rodape=rodape(s))


def corpo_2(s):
    serv = [('bomba', 'Gasolina aditivada', 'Para quem quer cuidar do motor no dia a dia.'),
            ('cafe', 'Café na hora', 'Expresso, cappuccino e pão de queijo quentinho.'),
            ('loja', 'Conveniência', 'Bebidas geladas, lanches e o básico da casa.'),
            ('aproximacao', 'Pague por aproximação', 'Cartão, celular ou relógio direto na bomba.'),
            ('calibragem', 'Calibragem', 'Calibrador digital à disposição, sem custo.'),
            ('lavagem', 'Ducha rápida', 'Tire a poeira do carro em poucos minutos.'),
            ('wifi', 'Wi-Fi no café', 'Para responder aquele e-mail enquanto o café sai.'),
            ('app', 'App de fidelidade', 'Junte pontos a cada abastecimento.')]
    galeria = ''.join('<li class="rv">%s</li>' % s.foto('galeria-%d.jpg' % i, '4/3', d, '1200 x 900', a) for i, d, a in [
        (3, 'Xícara de café com arte no leite, no balcão do café', 'Café com arte no leite servido no balcão'),
        (4, 'Cliente pagando pelo celular na maquininha', 'Pagamento por aproximação com o celular'),
        (5, 'Máquina de café expresso do posto, com o barista trabalhando', 'Máquina de café expresso do posto'),
        (6, 'Pagamento com cartão na maquininha, de perto', 'Pagamento com cartão por aproximação')])
    abas = [('pista', 'Pista', 'Atendimento rápido na pista', 'Frentistas treinados, gasolina aditivada e pagamento por aproximação direto na bomba. Você nem precisa sair do carro.',
             s.foto('galeria-1.jpg', '4/3', 'Cliente abastecendo o carro na pista, de lado, com luz do dia', '1200 x 900', 'Cliente abastecendo o carro na pista')),
            ('conveniencia', 'Conveniência', 'Tudo à mão, na hora que precisar', 'Geladeiras cheias, lanches e o básico da casa. Passe no caixa com Pix, cartão ou celular.',
             s.foto('galeria-2.jpg', '4/3', 'Geladeiras e prateleiras da conveniência, bem organizadas', '1200 x 900', 'Geladeiras da loja de conveniência')),
            ('cafe', 'Café', 'Um café de verdade no meio do caminho', 'Grãos selecionados, expresso tirado na hora e mesas para uma pausa rápida. Abre às 7h.',
             s.foto('destaque.jpg', '4/3', 'Balcão do café com a máquina de expresso e os doces', '1200 x 900', 'Balcão do café do posto')),
            ('fidelidade', 'Fidelidade', 'Abasteceu, ganhou ponto', 'Cadastre o CPF no caixa e junte pontos para trocar por café, lavagem e descontos na loja.', None)]
    lista = ''.join('<button type="button" class="aba" role="tab" id="aba-%s" aria-controls="painel-%s" aria-selected="%s"%s>%s</button>'
                    % (i, i, 'true' if k == 0 else 'false', '' if k == 0 else ' tabindex="-1"', n) for k, (i, n, _, _, _) in enumerate(abas))
    app = '''<div class="app-card" data-tilt="12"><div class="app-topo">%s<span>Fidelidade</span></div>
      <p class="app-saldo"><small>Seus pontos</small><strong>1.250</strong></p>
      <div class="app-barra"><i style="--v:.62"></i></div><p class="app-meta">Faltam 750 pontos para uma lavagem</p>
      <ul class="app-lista"><li><span>Abastecimento</span><b>+120</b></li><li><span>Café</span><b>+15</b></li><li><span>Conveniência</span><b>+40</b></li></ul>
      <p class="app-nota">Tela ilustrativa</p></div>''' % ic('app')
    paineis = ''.join('<div class="aba-painel" role="tabpanel" id="painel-%s" aria-labelledby="aba-%s"%s><div class="aba-grid"><div class="aba-txt"><h3>%s</h3><p>%s</p>'
                      '<a class="btn btn-prim" data-whats href="%s">%s Falar com o posto</a></div><div class="aba-media">%s</div></div></div>'
                      % (i, i, '' if k == 0 else ' hidden', t, x, esc(s.wa()), ic('whats'), f if f else app) for k, (i, n, t, x, f) in enumerate(abas))
    pag_chips = ''.join('<span class="chip">%s %s</span>' % (ic(i), t) for i, t, _ in PAGAMENTOS)
    return '''
<body class="m2">
%(sprite)s
%(topo)s
<main id="conteudo">
<section class="hero" id="inicio" aria-labelledby="t-hero">
  <div class="wrap hero-grid">
    <div class="hero-txt">
      <p class="rotulo h-in" style="--i:0">Posto e café na <span data-p="cidade">%(cidade)s</span></p>
      <h1 id="t-hero" class="h-in" style="--i:1">%(h1)s</h1>
      <p class="lead h-in" style="--i:2">Gasolina aditivada, conveniência completa e café de verdade. Pague com Pix, cartão ou por aproximação, direto na bomba.</p>
      <div class="acoes h-in" style="--i:3"><a class="btn btn-prim" data-maps href="%(maps)s" target="_blank" rel="noopener">%(icpin)s Como chegar</a>
        <a class="btn btn-sec" data-whats href="%(wa)s">%(icw)s WhatsApp</a></div>
      <ul class="selos h-in" style="--i:4">%(selos)s</ul>
    </div>
    <div class="hero-visual h-in" style="--i:2">
      <div class="hero-media">%(hero)s</div>
      <div class="pix-badge" data-flutuar>%(icpix)s<div><strong>Pix e aproximação</strong><span>direto na bomba</span></div></div>
    </div>
  </div>
</section>

<section id="precos" class="secao precos" aria-labelledby="t-precos">
  <div class="wrap">
    <div class="cab rv"><p class="rotulo">Preços</p><h2 id="t-precos">Preços de hoje</h2></div>
    <ul class="precos-lista" data-stagger>%(precos)s</ul>
    %(nota)s
  </div>
</section>

<section id="conveniencia" class="secao experiencia alt" aria-labelledby="t-exp">
  <div class="wrap">
    <div class="cab rv"><p class="rotulo">Por dentro do posto</p><h2 id="t-exp">Uma parada que resolve o seu dia</h2></div>
    <div class="abas rv" data-abas>
      <div class="abas-lista" role="tablist" aria-label="Áreas do posto">%(lista)s</div>
      %(paineis)s
    </div>
  </div>
</section>

<section id="servicos" class="secao servicos" aria-labelledby="t-serv">
  <div class="wrap">
    <div class="cab rv"><p class="rotulo">Serviços</p><h2 id="t-serv">Pensado para a rotina da cidade</h2></div>
    <ul class="serv-grid" data-stagger>%(serv)s</ul>
  </div>
</section>

<section id="galeria" class="secao galeria alt" aria-labelledby="t-gal">
  <div class="wrap">
    <div class="cab rv"><p class="rotulo">Galeria</p><h2 id="t-gal">O clima do Posto Avenida</h2></div>
    <ul class="gal-grid" data-stagger>%(galeria)s</ul>
  </div>
</section>

<section id="pagamento" class="secao pagamento" data-loop aria-labelledby="t-pag">
  <div class="wrap">
    <div class="cab rv centro"><p class="rotulo">Formas de pagamento</p><h2 id="t-pag">Pague como preferir</h2>
      <p class="sub">Na bomba ou no caixa, do jeito mais rápido para você.</p></div>
  </div>
  <div class="mq" data-marquee style="--mq-dur:30s;--mq-gap:16px"><div class="mq-grupo">%(chips)s</div></div>
</section>
%(bandeira)s
%(depo)s
%(local)s
%(final)s
%(rodape)s
''' % dict(sprite=sprite(), topo=topo(s, [('precos', 'Preços'), ('conveniencia', 'Conveniência'), ('servicos', 'Serviços'), ('galeria', 'Galeria'), ('localizacao', 'Como chegar')], False),
           cidade=esc(s.cidade), h1=titulo_linhas(['Abasteça,', 'pegue um café', 'e siga o seu dia.']), maps=esc(s.maps()), icpin=ic('pin'), wa=esc(s.wa()), icw=ic('whats'),
           selos=selos_hero([('cafe', 'Café a partir das 7h'), ('pix', 'Pix na bomba'), ('app', 'Fidelidade')]),
           hero=s.foto('hero.jpg', '16/9', 'Carro sendo abastecido com o bico na mão, de perto, luz do dia', '1920 x 1080', 'Carro sendo abastecido no Posto Avenida', eager=True),
           icpix=ic('aproximacao'), precos=lista_precos(s), nota=nota_precos(), lista=lista, paineis=paineis, serv=servicos(serv), galeria=galeria, chips=pag_chips,
           bandeira=secao_bandeira(s, 'Qualidade que você reconhece', 'A bandeira do posto e as marcas parceiras da pista, da loja e do café.', s.totem),
           depo=secao_depoimentos(s, ['Abasteço e já levo o café. Atendimento rápido e sempre educado.',
                                     'Gosto de pagar por aproximação na bomba. Não perco tempo no caixa.',
                                     'Loja organizada e limpa. Virou parada fixa no caminho do trabalho.']),
           local=secao_local(s, 'Fácil de chegar, no caminho do seu dia'),
           final=secao_final(s, 'Passa aqui hoje?', 'Fale com a gente pelo WhatsApp para saber o preço do dia, encomendar no café ou tirar dúvidas.'),
           rodape=rodape(s))


def corpo_3(s):
    serv = [('bomba', 'Abastecimento com frentista', 'Atendimento na pista, do jeito de sempre.'),
            ('lavagem', 'Lavagem', 'Lavagem simples e completa, com hora marcada.'),
            ('calibragem', 'Calibragem', 'Pneus calibrados enquanto você abastece.'),
            ('oleo', 'Troca de óleo', 'Óleo e filtro com registro da próxima troca.'),
            ('pao', 'Lanchonete', 'Pão de queijo, salgados e café coado.'),
            ('loja', 'Conveniência', 'O que faltou em casa, sem precisar ir ao centro.')]
    faixa = ''.join('<span class="mq-item">%s %s</span>' % (ic(i), esc(t)) for i, t, _ in serv)
    linha = [('1986', 'A primeira bomba', 'O posto abre com duas bombas e muita vontade de atender bem a cidade.'),
             ('1998', 'Lanchonete e lavagem', 'Chegam a lanchonete, o lava-rápido e o café coado que virou tradição.'),
             ('2010', 'A segunda geração', 'Os filhos assumem o balcão e o atendimento continua pelo nome.'),
             ('Hoje', 'O mesmo posto de sempre', 'Pista renovada, Pix e cartão, e a mesma família cuidando de tudo.')]
    tempo = ''.join('<li class="rv"><span class="t-ano">%s</span><div><h3>%s</h3><p>%s</p></div></li>' % (a, t, x) for a, t, x in linha)
    fotos = [(1, 'Balcão da lanchonete com o café e as louças', 'Balcão da lanchonete'),
             (2, 'Vitrine com os pães e quitandas do dia', 'Pães e quitandas na vitrine'),
             (3, 'Carro na lavagem, com espuma, de lado', 'Carro na lavagem do posto'),
             (4, 'Frentista calibrando o pneu do carro', 'Calibragem do pneu'),
             (5, 'Vista da cidade a partir do posto, no fim da tarde', 'Vista da cidade'),
             (6, 'Mão do frentista no bico abastecendo o carro', 'Frentista abastecendo o carro')]
    galeria = ''.join('<li class="polaroid rv"><div class="polaroid-in">%s<p>%s</p></div></li>' % (s.foto('galeria-%d.jpg' % i, '1/1', d, '1200 x 1200', a), esc(a)) for i, d, a in fotos)
    return '''
<body class="m3">
%(sprite)s
%(topo)s
<main id="conteudo">
<section class="hero" id="inicio" aria-labelledby="t-hero">
  <div class="wrap hero-grid">
    <div class="hero-txt">
      <p class="rotulo h-in" style="--i:0">Desde %(desde)s na <span data-p="cidade">%(cidade)s</span></p>
      <h1 id="t-hero" class="h-in" style="--i:1">%(h1)s</h1>
      <p class="lead h-in" style="--i:2">Somos o posto da família que conhece você pelo nome. Combustível, lavagem, calibragem e o café coado da nossa lanchonete.</p>
      <div class="acoes h-in" style="--i:3"><a class="btn btn-prim" data-whats href="%(wa)s">%(icw)s Fale com a gente</a>
        <a class="btn btn-sec" data-maps href="%(maps)s" target="_blank" rel="noopener">%(icpin)s Como chegar</a></div>
    </div>
    <div class="hero-visual h-in" style="--i:2">
      <div class="hero-media arco">%(hero)s</div>
      <div class="carimbo"><span>desde</span><strong>%(desde)s</strong><span>família</span></div>
    </div>
  </div>
</section>

<div class="faixa-serv" data-loop aria-label="Serviços do posto">
  <div class="mq" data-marquee style="--mq-dur:46s;--mq-gap:44px"><div class="mq-grupo">%(faixa)s</div></div>
</div>

<section id="precos" class="secao precos" aria-labelledby="t-precos">
  <div class="wrap precos-grid">
    <div class="cab rv"><p class="rotulo">Preços</p><h2 id="t-precos">O preço de hoje, do jeito que está na placa</h2>
      <p class="sub">Atualizamos sempre que o preço muda. Se preferir, pergunte pelo WhatsApp antes de sair de casa.</p></div>
    <div class="quadro rv"><ul class="precos-lista">%(precos)s</ul>%(nota)s</div>
  </div>
</section>

<section id="historia" class="secao historia alt" aria-labelledby="t-hist">
  <div class="wrap hist-grid">
    <div class="hist-foto rv">%(equipe)s</div>
    <div>
      <div class="cab rv"><p class="rotulo">Nossa história</p><h2 id="t-hist">Uma família cuidando do posto da cidade</h2></div>
      <ol class="linha-tempo"><li class="tracejado-v" aria-hidden="true"></li>%(tempo)s</ol>
    </div>
  </div>
  <div class="wrap"><ul class="nums" data-stagger>%(stats)s</ul></div>
</section>

<section id="servicos" class="secao servicos" aria-labelledby="t-serv">
  <div class="wrap">
    <div class="cab rv centro"><p class="rotulo">Serviços</p><h2 id="t-serv">Tudo para o seu carro, sem sair do bairro</h2></div>
    <ul class="serv-grid" data-stagger>%(serv)s</ul>
  </div>
</section>

<section id="lanchonete" class="secao lanchonete alt" aria-labelledby="t-lanche">
  <div class="wrap lanche-grid">
    <div class="rv"><p class="rotulo">Lanchonete</p><h2 id="t-lanche">Café coado, pão de queijo e prosa boa</h2>
      <p class="sub">Desde cedo com quitandas fresquinhas, salgados do dia e aquele café que muita gente vem buscar antes do trabalho.</p>
      <ul class="lanche-lista"><li>%(icc)s Café coado na hora</li><li>%(icp)s Pão de queijo e quitandas</li><li>%(icr)s Aberta das 6h às 20h</li></ul></div>
    <div class="lanche-foto rv">%(destaque)s</div>
  </div>
</section>

<section id="galeria" class="secao galeria" aria-labelledby="t-gal">
  <div class="wrap">
    <div class="cab rv centro"><p class="rotulo">Galeria</p><h2 id="t-gal">O nosso dia a dia</h2></div>
    <ul class="gal-polaroid" data-stagger>%(galeria)s</ul>
  </div>
</section>
%(bandeira)s
<section id="pagamento" class="secao pagamento alt" aria-labelledby="t-pag">
  <div class="wrap">
    <div class="cab rv centro"><p class="rotulo">Formas de pagamento</p><h2 id="t-pag">Pague como for melhor para você</h2></div>
    <ul class="pag-grid" data-stagger>%(pag)s</ul>
  </div>
</section>
%(depo)s
%(local)s
%(final)s
%(rodape)s
''' % dict(sprite=sprite(), topo=topo(s, [('precos', 'Preços'), ('historia', 'Nossa história'), ('servicos', 'Serviços'), ('lanchonete', 'Lanchonete'), ('localizacao', 'Onde estamos')], False),
           desde=s.desde, cidade=esc(s.cidade), h1=titulo_linhas(['O posto da cidade,', 'atendendo pelo nome.']),
           wa=esc(s.wa()), icw=ic('whats'), maps=esc(s.maps()), icpin=ic('pin'),
           hero=s.foto('hero.jpg', '16/9', 'Cliente abastecendo o carro na pista do posto, luz do dia', '1920 x 1080', 'Cliente abastecendo no Auto Posto Bom Jesus', eager=True),
           faixa=faixa, precos=lista_precos(s, 'preco rv'), nota=nota_precos(), tempo=tempo, stats=stats(s),
           equipe=s.foto('equipe.jpg', '3/2', 'Equipe do posto reunida na frente da loja, sorrindo', '1500 x 1000', 'Equipe do Auto Posto Bom Jesus'),
           serv=servicos(serv), icc=ic('cafe'), icp=ic('pao'), icr=ic('relogio'),
           destaque=s.foto('destaque.jpg', '4/3', 'Vitrine da lanchonete com pães e quitandas', '1200 x 900', 'Vitrine da lanchonete do posto'),
           galeria=galeria,
           bandeira=secao_bandeira(s, 'A bandeira e os parceiros de sempre', 'Quem trabalha com a gente há anos e ajuda a manter a qualidade do posto.', s.totem),
           pag=pagamentos(), depo=secao_depoimentos(s, ['Abasteço aqui desde menino. Atendimento de família, como era antigamente.',
                                                         'O café da lanchonete é sagrado de manhã. E a calibragem sai junto.',
                                                         'Gente honesta e prestativa. Indico para todo mundo da cidade.']),
           local=secao_local(s, 'No centro, pertinho de você'),
           final=secao_final(s, 'Precisa de alguma coisa?', 'Chame no WhatsApp para marcar a lavagem, perguntar o preço ou encomendar na lanchonete.'),
           rodape=rodape(s))


def corpo_4(s):
    letreiro = ''.join('<span class="let-item" data-preco="%d"><span data-pn>%s</span> <b data-num data-moeda data-valor="%s">%s</b></span>'
                       % (i, esc(n), v, preco_txt(v)) for i, (n, v) in enumerate(s.precos['itens']))
    barras = ''.join('<li data-preco="%d" data-barra style="--v:%.3f"><span class="b-nome" data-pn>%s</span><div class="barra"><i></i></div>'
                     '<span class="b-valor" data-num data-moeda data-valor="%s">%s</span></li>'
                     % (i, v / max(x[1] for x in s.precos['itens']), esc(n), v, preco_txt(v)) for i, (n, v) in enumerate(s.precos['itens']))
    serv = [('bomba', 'Abastecimento rápido', 'Várias bombas e fila andando.'),
            ('loja', 'Loja', 'Bebidas e lanches com preço na etiqueta.'),
            ('calibragem', 'Calibragem', 'Grátis, na entrada da pista.'),
            ('oleo', 'Troca de óleo', 'Óleo e filtro com preço combinado antes.'),
            ('banheiro', 'Banheiros', 'Limpos e abertos no horário do posto.'),
            ('estacionamento', 'Estacionamento', 'Vagas para quem vai à loja.')]
    fotos = [(1, 'Mão abastecendo o carro com o bico, de perto', 'Mão abastecendo o carro'),
             (2, 'Bico verde no tanque do carro, de perto', 'Bico de combustível no tanque'),
             (3, 'Cliente abastecendo com o porta-malas aberto', 'Cliente abastecendo o carro'),
             (4, 'Pagamento com cartão na maquininha, de perto', 'Pagamento com cartão'),
             (5, 'Pista do posto com a cobertura e a loja ao fundo', 'Pista do posto com a loja ao fundo'),
             (6, 'Cliente pagando no caixa da loja', 'Pagamento no caixa da loja')]
    galeria = ''.join('<li class="rv">%s</li>' % s.foto('galeria-%d.jpg' % i, '1/1', d, '1200 x 1200', a) for i, d, a in fotos)
    return '''
<body class="m4">
%(sprite)s
%(topo)s
<main id="conteudo">
<div class="letreiro" data-loop aria-label="Preços de hoje">
  <div class="mq" data-marquee style="--mq-dur:26s;--mq-gap:48px"><div class="mq-grupo">%(letreiro)s</div></div>
</div>
<section class="hero" id="inicio" aria-labelledby="t-hero">
  <div class="wrap hero-grid">
    <div class="hero-txt">
      <p class="tarja h-in" style="--i:0">%(ictag)s Bandeira branca</p>
      <h1 id="t-hero" class="h-in" style="--i:1">%(h1)s</h1>
      <p class="lead h-in" style="--i:2">Preço sempre à vista, atendimento rápido e todas as formas de pagamento. Aberto todos os dias, das 6h às 23h.</p>
      <div class="acoes h-in" style="--i:3"><a class="btn btn-prim" href="#precos">%(ictag)s Ver preços de hoje</a>
        <a class="btn btn-sec" data-maps href="%(maps)s" target="_blank" rel="noopener">%(icpin)s Como chegar</a></div>
    </div>
    <div class="hero-visual h-in" style="--i:2">
      <div class="hero-media">%(hero)s</div>
      <div class="placa">
        <span class="placa-tit" data-preco="0"><span data-pn>%(p0n)s</span></span>
        <strong data-preco="0"><span data-num data-moeda data-valor="%(p0v)s">%(p0)s</span></strong>
        <span class="placa-nota">por litro, hoje</span>
      </div>
    </div>
  </div>
</section>

<section id="precos" class="secao precos" aria-labelledby="t-precos">
  <div class="wrap">
    <div class="cab rv"><p class="rotulo">Tabela de preços</p><h2 id="t-precos">Todos os combustíveis, preço por litro</h2></div>
    <ul class="precos-lista" data-stagger>%(precos)s</ul>
    %(nota)s
    <div class="comparar rv" data-barras>
      <h3>Compare os combustíveis do posto</h3>
      <ul class="barras">%(barras)s</ul>
      <p class="nota">Comparação só entre os preços deste posto, para ajudar na escolha.</p>
    </div>
  </div>
</section>

<section id="pagamento" class="secao pagamento alt" aria-labelledby="t-pag">
  <div class="wrap">
    <div class="cab rv"><p class="rotulo">Formas de pagamento</p><h2 id="t-pag">Paga como quiser, sem complicação</h2></div>
    <ul class="pag-grid" data-stagger>%(pag)s</ul>
  </div>
</section>

<section id="servicos" class="secao servicos" aria-labelledby="t-serv">
  <div class="wrap">
    <div class="cab rv"><p class="rotulo">Serviços</p><h2 id="t-serv">O essencial, bem feito</h2></div>
    <ul class="serv-grid" data-stagger>%(serv)s</ul>
  </div>
</section>

<section id="galeria" class="secao galeria alt" aria-labelledby="t-gal">
  <div class="wrap">
    <div class="cab rv"><p class="rotulo">Galeria</p><h2 id="t-gal">O posto</h2></div>
    <ul class="gal-grid" data-stagger>%(galeria)s</ul>
  </div>
</section>
%(bandeira)s
%(depo)s
%(local)s
%(final)s
%(rodape)s
''' % dict(sprite=sprite(), topo=topo(s, [('precos', 'Preços'), ('pagamento', 'Pagamento'), ('servicos', 'Serviços'), ('localizacao', 'Como chegar')], False),
           letreiro=letreiro, ictag=ic('tag'), h1=titulo_linhas(['Preço na placa,', 'sem surpresa', 'na bomba.']),
           maps=esc(s.maps()), icpin=ic('pin'),
           hero=s.foto('hero.jpg', '16/9', 'Bicos de combustível coloridos na bomba, de perto', '1920 x 1080', 'Bicos de combustível na bomba do posto', eager=True),
           p0n=esc(s.precos['itens'][0][0]), p0v=s.precos['itens'][0][1], p0=preco_txt(s.precos['itens'][0][1]),
           precos=lista_precos(s), nota=nota_precos(), barras=barras, pag=pagamentos(), serv=servicos(serv), galeria=galeria,
           bandeira=secao_bandeira(s, 'Bandeira branca, com origem conferida', 'Bandeira branca quer dizer que o posto compra de distribuidoras autorizadas e repassa o preço para você. As logos dos parceiros entram aqui.', s.totem),
           depo=secao_depoimentos(s, ['O preço que está na placa é o que eu pago. Simples assim.',
                                     'Atendimento rápido, mesmo no horário de pico. Abasteço e sigo.',
                                     'Aceita tudo: Pix, cartão e aproximação. Muito prático.']),
           local=secao_local(s, 'Aberto todos os dias'),
           final=secao_final(s, 'Quer saber o preço antes de sair?', 'Chame no WhatsApp e confirme o preço do dia ou tire suas dúvidas.'),
           rodape=rodape(s))


def corpo_5(s):
    serv = [('oleo', 'Troca de óleo', 'Óleo e filtro conforme o manual do seu carro.'),
            ('pneu', 'Pneus', 'Venda, montagem e conserto de pneus.'),
            ('alinhamento', 'Alinhamento', 'Alinhamento computadorizado.'),
            ('calibragem', 'Balanceamento', 'Rodas balanceadas para rodar sem vibração.'),
            ('bateria', 'Bateria', 'Teste grátis e troca na hora.'),
            ('lavagem', 'Lavagem', 'Simples, completa e higienização.'),
            ('chave', 'Revisão rápida', 'Freios, suspensão e fluidos.'),
            ('bomba', 'Abastecimento', 'Pista aberta das 6h às 22h.')]
    abas = [('oleo', 'Óleo', 'Troca de óleo sem enrolação', 'Óleo e filtro conforme o manual do fabricante, com etiqueta da próxima troca no para-brisa. Você acompanha o serviço.',
             s.foto('destaque.jpg', '4/3', 'Mecânico conferindo o óleo no motor do carro', '1200 x 900', 'Mecânico conferindo o nível de óleo')),
            ('pneus', 'Pneus', 'Pneus, montagem e conserto', 'Trabalhamos com várias medidas e fazemos montagem, rodízio e conserto de furo no mesmo dia.',
             s.foto('galeria-1.jpg', '4/3', 'Mecânico trocando o pneu do carro na oficina', '1200 x 900', 'Mecânico trocando o pneu')),
            ('alinhamento', 'Alinhamento', 'Alinhamento e balanceamento', 'Carro puxando para o lado ou volante tremendo? A gente alinha e balanceia com equipamento computadorizado.',
             s.foto('galeria-2.jpg', '4/3', 'Carro no elevador da oficina, visto de lado', '1200 x 900', 'Carro no elevador da oficina')),
            ('lavagem', 'Lavagem', 'Lavagem enquanto você resolve o resto', 'Lavagem simples, completa e higienização interna. Deixe o carro e pegue pronto.',
             s.foto('galeria-3.jpg', '4/3', 'Carro sendo lavado com espuma no box de lavagem', '1200 x 900', 'Carro na lavagem'))]
    lista = ''.join('<button type="button" class="aba" role="tab" id="aba-%s" aria-controls="painel-%s" aria-selected="%s"%s>%s</button>'
                    % (i, i, 'true' if k == 0 else 'false', '' if k == 0 else ' tabindex="-1"', n) for k, (i, n, _, _, _) in enumerate(abas))
    paineis = ''.join('<div class="aba-painel" role="tabpanel" id="painel-%s" aria-labelledby="aba-%s"%s><div class="aba-grid"><div class="aba-media">%s</div><div class="aba-txt"><h3>%s</h3><p>%s</p>'
                      '<a class="btn btn-prim" data-whats href="%s" data-msg="%s">%s Agendar pelo WhatsApp</a></div></div></div>'
                      % (i, i, '' if k == 0 else ' hidden', f, t, x, esc(s.wa('Olá! Quero agendar: ' + n.lower() + '.')), esc('Olá! Quero agendar: ' + n.lower() + '.'), ic('whats'))
                      for k, (i, n, t, x, f) in enumerate(abas))
    checklist = [('Óleo e filtro', 1), ('Pneus e calibragem', 1), ('Freios', 1), ('Bateria', 1), ('Luzes e palhetas', 1)]
    barras = ''.join('<li><span>%s</span><div class="barra"><i style="--v:%s"></i></div><b>%s conferido</b></li>' % (n, v, ic('check')) for n, v in checklist)
    dentro = [(4, 'Motor revisado', 'Diagnóstico e manutenção com peças de qualidade.', 'Mecânico de luvas mexendo no motor, de perto'),
              (5, 'Bateria testada', 'Teste e troca de bateria sem precisar marcar.', 'Teste de bateria com os cabos ligados'),
              (6, 'Acabamento da lavagem', 'Espuma, enxágue e secagem com cuidado.', 'Roda do carro coberta de espuma na lavagem')]
    pilha = ''.join('<article class="pilha-item">%s<div class="pilha-texto"><h3>%s</h3><p>%s</p></div></article>'
                    % (s.foto('galeria-%d.jpg' % i, '4/3', d, '1200 x 900', t), t, x) for i, t, x, d in dentro)
    pilha += '<article class="pilha-item">%s<div class="pilha-texto"><h3>%s</h3><p>%s</p></div></article>' % (
        s.foto('equipe.jpg', '4/3', 'Equipe da oficina trabalhando, de preferência com o uniforme do posto', '1200 x 900', 'Mecânico trabalhando no elevador'),
        'Equipe na oficina', 'Mecânicos experientes cuidando do seu carro do começo ao fim.')
    return '''
<body class="m5">
%(sprite)s
%(topo)s
<main id="conteudo">
<section class="hero" id="inicio" aria-labelledby="t-hero">
  <div class="hero-media hero-diag">%(hero)s</div>
  <div class="hero-veu"></div>
  <div class="hero-linhas" aria-hidden="true"><i></i><i></i><i></i></div>
  <div class="wrap hero-txt">
    <p class="rotulo h-in" style="--i:0">Posto + autocenter</p>
    <h1 id="t-hero" class="h-in" style="--i:1">%(h1)s</h1>
    <p class="lead h-in" style="--i:2">Troca de óleo, pneus, alinhamento, bateria e lavagem no mesmo lugar onde você abastece. Agende pelo WhatsApp e acompanhe o serviço.</p>
    <div class="acoes h-in" style="--i:3"><a class="btn btn-prim" data-whats href="%(wa)s" data-msg="Olá! Quero agendar um serviço no autocenter.">%(icw)s Agendar serviço</a>
      <a class="btn btn-foto" href="#servicos">%(icc)s Ver serviços</a></div>
    <ul class="selos h-in" style="--i:4">%(selos)s</ul>
  </div>
</section>

<section id="servicos" class="secao servicos" aria-labelledby="t-serv">
  <div class="wrap">
    <div class="cab rv"><p class="rotulo">Autocenter</p><h2 id="t-serv">Serviços para o seu carro</h2>
      <p class="sub">Tudo com orçamento antes de começar. Você aprova e acompanha.</p></div>
    <ul class="serv-grid" data-stagger>%(serv)s</ul>
  </div>
</section>

<section id="detalhes" class="secao detalhes alt" aria-labelledby="t-det">
  <div class="wrap">
    <div class="cab rv"><p class="rotulo">Como fazemos</p><h2 id="t-det">Cada serviço, explicado</h2></div>
    <div class="abas rv" data-abas>
      <div class="abas-lista" role="tablist" aria-label="Serviços do autocenter">%(lista)s</div>
      %(paineis)s
    </div>
  </div>
</section>

<section id="checklist" class="secao checklist" aria-labelledby="t-check">
  <div class="wrap check-grid">
    <div class="rv" data-barras>
      <p class="rotulo">Na sua visita</p><h2 id="t-check">O que a gente confere no seu carro</h2>
      <p class="sub">Enquanto você abastece ou espera o serviço, nossa equipe faz uma conferência visual destes itens e avisa se algo precisar de atenção.</p>
      <ul class="check-lista">%(barras)s</ul>
    </div>
    <div class="agenda-card" data-tilt="10">
      %(iccal)s
      <h3>Agende pelo WhatsApp</h3>
      <p>Escolha o serviço, o dia e o horário. A gente confirma na hora e avisa quando o carro estiver pronto.</p>
      <a class="btn btn-prim" data-whats href="%(wa2)s" data-msg="Olá! Quero agendar um serviço no autocenter.">%(icw)s Agendar agora</a>
    </div>
  </div>
</section>

<section id="precos" class="secao precos alt" aria-labelledby="t-precos">
  <div class="wrap">
    <div class="cab rv"><p class="rotulo">Pista</p><h2 id="t-precos">Preços de hoje na pista</h2></div>
    <ul class="precos-lista" data-stagger>%(precos)s</ul>
    %(nota)s
  </div>
</section>

<section id="oficina" class="oficina" aria-labelledby="t-ofi">
  <div class="hscroll" data-hscroll>
    <div class="hscroll-fixo">
      <div class="wrap cab-h"><p class="rotulo">Galeria</p><h2 id="t-ofi">Por dentro do autocenter</h2></div>
      <div class="pilha">%(pilha)s</div>
    </div>
  </div>
</section>
%(bandeira)s
<section id="pagamento" class="secao pagamento" aria-labelledby="t-pag">
  <div class="wrap">
    <div class="cab rv"><p class="rotulo">Formas de pagamento</p><h2 id="t-pag">Pague à vista ou no cartão</h2>
      <p class="sub">Serviços do autocenter no Pix, débito ou crédito. Consulte as condições de parcelamento.</p></div>
    <ul class="pag-grid" data-stagger>%(pag)s</ul>
  </div>
</section>
%(depo)s
%(local)s
%(final)s
%(rodape)s
''' % dict(sprite=sprite(), topo=topo(s, [('servicos', 'Serviços'), ('detalhes', 'Como fazemos'), ('precos', 'Preços'), ('oficina', 'Galeria'), ('localizacao', 'Onde estamos')], True),
           hero=s.foto('hero.jpg', '16/9', 'Carro no elevador da oficina, com a oficina iluminada ao fundo', '1920 x 1080', 'Carro no elevador do autocenter', cls='foto-fundo', eager=True),
           h1=titulo_linhas(['Abastece, revisa', 'e lava no mesmo', 'lugar.']), wa=esc(s.wa('Olá! Quero agendar um serviço no autocenter.')), wa2=esc(s.wa('Olá! Quero agendar um serviço no autocenter.')),
           icw=ic('whats'), icc=ic('chave'), iccal=ic('calendario', 'ic ic-grande'),
           selos=selos_hero([('relogio', 'Seg. a sáb.'), ('escudo', 'Orçamento antes'), ('whats', 'Agenda no WhatsApp')]),
           serv=servicos(serv), lista=lista, paineis=paineis, barras=barras, precos=lista_precos(s), nota=nota_precos(), pilha=pilha,
           bandeira=secao_bandeira(s, 'Marcas que trabalham com a gente', 'Bandeira do posto e as marcas de pneus, lubrificantes e baterias do autocenter.', s.totem),
           pag=pagamentos(), depo=secao_depoimentos(s, ['Troquei o óleo enquanto abastecia. Rápido e com tudo explicado.',
                                                         'Fizeram o alinhamento e me mostraram o antes e o depois. Gostei da transparência.',
                                                         'Agendei pelo WhatsApp e o carro ficou pronto no horário combinado.']),
           local=secao_local(s, 'Pista e autocenter no mesmo endereço'),
           final=secao_final(s, 'Seu carro precisa de algum cuidado?', 'Chame no WhatsApp, conte o que precisa e receba o orçamento antes de começar.'),
           rodape=rodape(s))

CORPOS = [corpo_1, corpo_2, corpo_3, corpo_4, corpo_5]

# ---------------------------------------------------------------------------
# MODELOS 6 A 10
#   6, 7 e 8: variações do modelo 1 (mesmo estilo de rodovia, outro layout)
#   9 e 10: conceitos novos
# ---------------------------------------------------------------------------
PAL_RODOVIA = POSTOS[0]['paletas']
BASE_RODOVIA = dict(
    whatsapp='5535900000000', telefone='(35) 0000-0000', cidade='Cidade', uf='UF', cidade_uf='Cidade - UF',
    cnpj='00.000.000/0000-00', instagram='postoexemplo', mostrarSeletor=True, paletas=PAL_RODOVIA,
    fontes_url=POSTOS[0]['fontes_url'], fonte_titulo=POSTOS[0]['fonte_titulo'], fonte_corpo=POSTOS[0]['fonte_corpo'],
    apoio_icones=True, bandeira='Nome da Bandeira')

POSTOS += [
  dict(BASE_RODOVIA, id='posto-6', pasta='posto 6', conceito='Rodovia de serra (variação do 1)', nome='Posto Serra Azul', inicial='S',
       titulo='Posto Serra Azul | Diesel S10 e parada antes da serra',
       descricao='Posto de rodovia no pé da serra, com diesel S10, Arla 32, café da manhã, pátio e banho. Modelo de demonstração.',
       slogan='A última parada antes da serra.',
       endereco='Rodovia BR-000, km 000, Cidade - UF',
       horario=[['Pista e conveniência', '24 horas, todos os dias'], ['Café da manhã', '5h às 11h'], ['Restaurante', '11h às 22h']],
       ld_horas=[(TODOS_DIAS, '00:00', '23:59')],
       precos={'atualizado': '22/11/2026', 'itens': [['Diesel S10', 6.09], ['Diesel S500', 5.99], ['Arla 32', 3.49], ['Gasolina comum', 6.29], ['Etanol', 4.39]]},
       numeros=[], parceiros=['Distribuidora', 'Cartão frota', 'Rastreamento', 'Lubrificante', 'Seguradora', 'App de frete'],
       mensagemWhats='Olá! Vim pelo site do Posto Serra Azul e gostaria de mais informações.',
       paleta='petroleo',
       motion={'bandeira': 'totem', 'parceiros': 'faixa-dupla', 'hero': 'foco', 'foto': 'parallax', 'cards': 'subir', 'numeros': 'bomba', 'fundo': 'linhas', 'vel': 'normal'},
       totem=[0, 2, 3], css=['posto1.css', 'posto6.css']),
  dict(BASE_RODOVIA, id='posto-7', pasta='posto 7', conceito='Rodovia à noite (variação do 1)', nome='Posto Rota Sul', inicial='R',
       titulo='Posto Rota Sul | Aberto a noite toda na rodovia',
       descricao='Posto de rodovia aberto 24 horas, com pista iluminada, diesel S10, banho, restaurante e pátio vigiado. Modelo de demonstração.',
       slogan='Luz acesa a noite toda para quem está na estrada.',
       endereco='Rodovia BR-000, km 000, Cidade - UF',
       horario=[['Pista e conveniência', '24 horas, todos os dias'], ['Restaurante', '24 horas'], ['Banho', '24 horas']],
       ld_horas=[(TODOS_DIAS, '00:00', '23:59')],
       precos={'atualizado': '22/11/2026', 'itens': [['Diesel S10', 6.09], ['Diesel S500', 5.99], ['Gasolina comum', 6.29], ['Etanol', 4.39], ['Arla 32', 3.49]]},
       numeros=[], parceiros=['Distribuidora', 'Cartão frota', 'Pedágio eletrônico', 'Rastreamento', 'Lubrificante', 'Seguradora'],
       mensagemWhats='Olá! Vim pelo site do Posto Rota Sul e gostaria de mais informações.',
       paleta='marinho',
       motion={'bandeira': 'pulsar', 'parceiros': 'colunas', 'hero': 'palavras', 'foto': 'zoom', 'cards': 'escala', 'numeros': 'contar', 'fundo': 'faiscas', 'vel': 'normal'},
       totem=[0, 2, 3], css=['posto1.css', 'posto7.css']),
  dict(BASE_RODOVIA, id='posto-8', pasta='posto 8', conceito='Parada de viagem (variação do 1)', nome='Posto Parada Certa', inicial='P',
       titulo='Posto Parada Certa | A parada da viagem de carro',
       descricao='Posto de estrada para quem viaja de carro: banheiro limpo, café, lanches, calibragem e espaço para esticar as pernas. Modelo de demonstração.',
       slogan='Banheiro limpo, café quente e estrada livre.',
       endereco='Rodovia SP-000, km 000, Cidade - UF',
       horario=[['Pista e loja', '24 horas, todos os dias'], ['Café e lanches', '6h às 23h']],
       ld_horas=[(TODOS_DIAS, '00:00', '23:59')],
       precos={'atualizado': '22/11/2026', 'itens': [['Gasolina comum', 6.29], ['Gasolina aditivada', 6.49], ['Etanol', 4.39], ['Diesel S10', 6.09]]},
       numeros=[[24, 'h', 'de loja e banheiro abertos'], [40, '', 'vagas para carro e van'], [5, ' min', 'da pista até a mesa do café']],
       parceiros=['Distribuidora', 'Cafeteria', 'Marca de bebidas', 'App de fidelidade', 'Carteira digital', 'Seguradora'],
       mensagemWhats='Olá! Vim pelo site do Posto Parada Certa e gostaria de mais informações.',
       paleta='cobre',
       motion={'bandeira': 'virar', 'parceiros': 'destaque', 'hero': 'cascata', 'foto': 'cortina', 'cards': 'subir', 'numeros': 'contar', 'fundo': 'nenhum', 'vel': 'suave'},
       totem=[0, 2, 3], css=['posto1.css', 'posto8.css']),
  dict(id='posto-9', pasta='posto 9', conceito='Urbano: GNV, recarga e app', nome='Posto Via Expressa', inicial='V',
       titulo='Posto Via Expressa | GNV, recarga elétrica e parada para motorista de app',
       descricao='Posto urbano com GNV, recarga para carro elétrico, café 24 horas e vantagens para motoristas de aplicativo. Modelo de demonstração.',
       slogan='Abastece, carrega e volta pra corrida.',
       whatsapp='5535900000000', telefone='(35) 0000-0000', endereco='Avenida Exemplo, 000, Centro, Cidade - UF', cidade='Cidade', uf='UF', cidade_uf='Cidade - UF',
       cnpj='00.000.000/0000-00', instagram='postoexemplo',
       horario=[['Pista, GNV e recarga', '24 horas, todos os dias'], ['Café', '24 horas']],
       ld_horas=[(TODOS_DIAS, '00:00', '23:59')],
       precos={'atualizado': '22/11/2026', 'itens': [['Gasolina comum', 6.29], ['Etanol', 4.39], ['GNV', 4.79, 'por m³'], ['Recarga elétrica', 1.99, 'por kWh']]},
       numeros=[], bandeira='Nome da Bandeira',
       parceiros=['Distribuidora', 'Rede de recarga', 'App de corrida', 'Carteira digital', 'Cafeteria', 'Seguradora'],
       mensagemWhats='Olá! Vim pelo site do Posto Via Expressa e gostaria de mais informações.',
       paleta='padrao', mostrarSeletor=True,
       motion={'bandeira': 'flutuar', 'parceiros': 'faixa', 'hero': 'mascara', 'foto': 'cortina', 'cards': 'escala', 'numeros': 'contar', 'fundo': 'nenhum', 'vel': 'normal'},
       paletas=[paleta('padrao', 'Violeta e limão', '#6D28D9', '#A3E635', 'claro'),
                paleta('azul', 'Azul elétrico e ciano', '#1D4ED8', '#22D3EE', 'claro'),
                paleta('verde', 'Verde GNV e amarelo', '#047857', '#FACC15', 'claro'),
                paleta('rosa', 'Magenta e laranja', '#BE185D', '#FB923C', 'claro'),
                paleta('grafite', 'Grafite e verde neon', '#1F2937', '#4ADE80', 'claro')],
       fontes_url='https://fonts.googleapis.com/css2?family=Sora:wght@500;600;700;800&family=Inter:wght@400;500;600;700&display=swap',
       fonte_titulo="'Sora', system-ui, sans-serif", fonte_corpo="'Inter', system-ui, sans-serif",
       totem=[0, 2, 3], css='posto9.css'),
  dict(id='posto-10', pasta='posto 10', conceito='Estética automotiva premium', nome='Posto Brilho Total', inicial='B',
       titulo='Posto Brilho Total | Combustível e estética automotiva',
       descricao='Posto com centro de estética automotiva: lavagem técnica, polimento, higienização e proteção da pintura. Modelo de demonstração.',
       slogan='Abasteça enquanto o seu carro ganha outro brilho.',
       whatsapp='5535900000000', telefone='(35) 0000-0000', endereco='Avenida Exemplo, 000, Jardim Exemplo, Cidade - UF', cidade='Cidade', uf='UF', cidade_uf='Cidade - UF',
       cnpj='00.000.000/0000-00', instagram='postoexemplo',
       horario=[['Pista: todos os dias', '6h às 23h'], ['Estética: segunda a sábado', '8h às 19h']],
       ld_horas=[(TODOS_DIAS, '06:00', '23:00')],
       precos={'atualizado': '22/11/2026', 'itens': [['Gasolina comum', 6.29], ['Gasolina aditivada', 6.59], ['Etanol', 4.39], ['Diesel S10', 6.19]]},
       pacotes=[['Lavagem completa', 79.9, 'Lavagem externa técnica, aspiração, painel e vidros.'],
                ['Higienização interna', 249.9, 'Bancos, carpete e teto limpos a fundo, com secagem.'],
                ['Polimento e proteção', 590.0, 'Polimento técnico da pintura e camada de proteção.']],
       numeros=[], bandeira='Nome da Bandeira',
       parceiros=['Distribuidora', 'Marca de ceras', 'Marca de polidores', 'Película automotiva', 'Seguradora', 'Cartão de benefícios'],
       mensagemWhats='Olá! Vim pelo site do Posto Brilho Total e gostaria de agendar um serviço de estética.',
       paleta='padrao', mostrarSeletor=True, apoio_icones=True,
       motion={'bandeira': 'brilho', 'parceiros': 'cascata', 'hero': 'foco', 'foto': 'zoom', 'cards': 'subir', 'numeros': 'contar', 'fundo': 'nenhum', 'vel': 'suave'},
       paletas=[paleta3('padrao', 'Preto, grafite e dourado', '#0B0B0C', '#9A9AA0', '#D4AF37'),
                paleta3('ingles', 'Verde-inglês, creme e dourado', '#0E1A15', '#CFC6B0', '#E0B84C'),
                paleta3('noite', 'Azul-noite, prata e champanhe', '#0B1220', '#A9B4C2', '#E8C98A'),
                paleta3('vinho', 'Vinho, rosé e cobre', '#1A0E12', '#C9A9A6', '#E08A4F'),
                paleta3('gelo', 'Grafite, pérola e azul-gelo', '#141518', '#D9D6CF', '#7DD3FC')],
       fontes_url='https://fonts.googleapis.com/css2?family=Playfair+Display:wght@600;700&family=Manrope:wght@400;500;600;700;800&display=swap',
       fonte_titulo="'Playfair Display', Georgia, serif", fonte_corpo="'Manrope', system-ui, sans-serif",
       totem=[0, 2, 3], css='posto10.css'),
]

SERV_RODOVIA = [('bomba', 'Diesel S10 e S500', 'Bicos de alta vazão para carreta e caminhão.'),
                ('arla', 'Arla 32 na bomba', 'Sem descer galão, junto com o diesel.'),
                ('ducha', 'Banho quente', 'Chuveiros limpos e toalha na conveniência.'),
                ('restaurante', 'Restaurante', 'Comida caseira e café passado na hora.'),
                ('estacionamento', 'Pátio vigiado', 'Iluminação e câmeras a noite toda.'),
                ('loja', 'Conveniência 24h', 'Lanches, bebidas e itens de viagem.'),
                ('wifi', 'Wi-Fi grátis', 'No restaurante e na loja.'),
                ('banheiro', 'Banheiros', 'Limpos e abertos dia e noite.')]

def preco_hero(s, idx):
    return ''.join('<li data-preco="%d"><span data-pn>%s</span><strong data-num data-moeda data-valor="%s">%s</strong></li>'
                   % (i, esc(s.precos['itens'][i][0]), s.precos['itens'][i][1], preco_txt(s.precos['itens'][i][1])) for i in idx)

def secoes_finais(s, band_tit, band_txt, depo, local_tit, final_tit, final_txt, pag_tit, pag_txt):
    return (secao_bandeira(s, band_tit, band_txt, s.totem) + '''
<section id="pagamento" class="secao pagamento alt" aria-labelledby="t-pag">
  <div class="wrap">
    <div class="cab rv"><p class="rotulo">Formas de pagamento</p><h2 id="t-pag">%s</h2><p class="sub">%s</p></div>
    <ul class="pag-grid" data-stagger>%s</ul>
  </div>
</section>''' % (pag_tit, pag_txt, pagamentos()) + secao_depoimentos(s, depo) + secao_local(s, local_tit) + secao_final(s, final_tit, final_txt) + rodape(s))


def corpo_6(s):
    fotos = [(1, 'Estrada de serra em curvas com caminhões subindo', 'Caminhões na estrada da serra'),
             (2, 'Caminhão na estrada com a serra ao fundo', 'Caminhão com a serra ao fundo'),
             (3, 'Carreta vermelha chegando pela rodovia', 'Carreta chegando pela rodovia'),
             (4, 'Caminhão em reta longa, de frente', 'Caminhão em reta longa'),
             (5, 'Vista do alto da rodovia cortando a mata', 'Rodovia cortando a mata'),
             (6, 'Motorista descansando na cabine, visto pela janela', 'Motorista descansando na cabine')]
    mosaico = ''.join('<li class="rv mos-%d">%s<p>%s</p></li>' % (i, s.foto('galeria-%d.jpg' % i, '4/3', d, '1200 x 900', a), esc(a)) for i, d, a in fotos)
    lista = ''.join('<li class="card rv linha-serv">%s<div><h3>%s</h3><p>%s</p></div></li>' % (ic(i, 'ic ic-servico'), esc(t), esc(d)) for i, t, d in SERV_RODOVIA)
    return '''
<body class="topo-sobre-foto m1 m6">
%(sprite)s
%(topo)s
<main id="conteudo">
<section class="hero" id="inicio" aria-labelledby="t-hero">
  <div class="hero-media hero-cheio">%(hero)s</div>
  <div class="hero-veu"></div>
  <div class="hero-linhas" aria-hidden="true"><i></i><i></i><i></i></div>
  <div class="wrap hero-grid6">
    <div class="hero-txt">
      <p class="km h-in" style="--i:0">%(icpin)s <span data-p="endereco">%(end)s</span></p>
      <h1 id="t-hero" class="h-in" style="--i:1">%(h1)s</h1>
      <p class="lead h-in" style="--i:2">Abasteça com calma antes da subida. Diesel S10, Arla 32 na bomba, café da manhã a partir das 5h e pátio para descansar.</p>
      <div class="acoes h-in" style="--i:3"><a class="btn btn-prim" data-maps href="%(maps)s" target="_blank" rel="noopener">%(icpin)s Como chegar</a>
        <a class="btn btn-foto" data-whats href="%(wa)s">%(icw)s WhatsApp</a></div>
    </div>
    <aside class="painel-diesel h-in" style="--i:3" aria-label="Preços de hoje">
      <p class="painel-tit">%(icb)s Preço de hoje</p>
      <ul>%(ph)s</ul>
      <a class="painel-link" href="#precos">Ver todos os preços %(ics)s</a>
    </aside>
  </div>
</section>

<section id="servicos" class="secao servicos" aria-labelledby="t-serv">
  <div class="wrap serv6">
    <div class="cab rv"><p class="rotulo">Estrutura</p><h2 id="t-serv">Pare uma vez e resolva tudo</h2>
      <p class="sub">Antes de encarar a serra, o caminhoneiro encontra aqui tudo o que precisa num lugar só.</p>
      <a class="btn btn-prim" data-whats href="%(wa)s">%(icw)s Falar com o posto</a></div>
    <ul class="lista6" data-stagger>%(lista)s</ul>
  </div>
</section>

<section id="galeria" class="secao galeria alt" aria-labelledby="t-gal">
  <div class="wrap">
    <div class="cab rv"><p class="rotulo">Galeria</p><h2 id="t-gal">A estrada que passa por aqui</h2></div>
    <ul class="mosaico" data-stagger>%(mosaico)s</ul>
  </div>
</section>

<section id="precos" class="secao precos" aria-labelledby="t-precos">
  <div class="wrap">
    <div class="cab rv"><p class="rotulo">Tabela completa</p><h2 id="t-precos">Todos os preços de hoje</h2></div>
    <ul class="precos-lista" data-stagger>%(precos)s</ul>
    %(nota)s
  </div>
</section>

<section id="cafe" class="secao restaurante alt" aria-labelledby="t-cafe">
  <div class="wrap rest-grid">
    <div class="rest-txt rv">
      <p class="rotulo">Café da manhã</p>
      <h2 id="t-cafe">Café reforçado antes da subida</h2>
      <p class="sub">A partir das 5h: ovos, pão na chapa, frios e café passado. Depois das 11h, almoço caseiro até as 22h.</p>
      <ol class="fluxo">
        <li>%(icb)s<span>Abasteça</span></li><li class="tracejado" aria-hidden="true"></li>
        <li>%(icc)s<span>Café</span></li><li class="tracejado" aria-hidden="true"></li>
        <li>%(ice)s<span>Serra</span></li>
      </ol>
    </div>
    <div class="rest-foto rv">%(destaque)s</div>
  </div>
</section>
%(fim)s''' % dict(sprite=sprite(), topo=topo(s, [('servicos', 'Estrutura'), ('galeria', 'Galeria'), ('precos', 'Preços'), ('cafe', 'Café'), ('localizacao', 'Como chegar')], True),
           hero=s.foto('hero.jpg', '16/9', 'Vista do alto da estrada chegando ao posto, de preferência ao entardecer', '1920 x 1080', 'Estrada de serra vista do alto', cls='foto-fundo', eager=True),
           icpin=ic('pin'), end=esc(s.endereco), h1=titulo_linhas(['A última', 'parada antes', 'da serra.']), maps=esc(s.maps()), wa=esc(s.wa()), icw=ic('whats'),
           icb=ic('bomba'), ics=ic('seta'), icc=ic('cafe'), ice=ic('estrada'), ph=preco_hero(s, [0, 1, 2]), lista=lista, mosaico=mosaico,
           precos=lista_precos(s), nota=nota_precos(),
           destaque=s.foto('destaque.jpg', '4/3', 'Café da manhã servido na mesa do restaurante', '1200 x 900', 'Café da manhã do restaurante'),
           fim=secoes_finais(s, 'Origem garantida e parceiros de estrada', 'A bandeira do posto e as marcas que rodam com a gente. As logos entram quando o posto mandar os arquivos.',
                             ['Parada obrigatória antes da serra. Diesel bom e café caprichado.', 'Pátio tranquilo para dormir e banho sempre limpo.', 'Arla na bomba e cartão frota sem enrolação.'],
                             'No pé da serra, aberto o tempo todo', 'Vai subir a serra hoje?', 'Chame no WhatsApp para saber o preço do diesel ou combinar o abastecimento da frota.',
                             'Pague do jeito da sua empresa', 'Cartão frota com controle por placa, Pix e nota fiscal na hora.'))


def corpo_7(s):
    tiles = [('relogio', '24 horas', 'Pista, loja e restaurante'), ('bomba', 'Diesel S10', 'Bicos de alta vazão'),
             ('estacionamento', 'Pátio vigiado', 'Câmeras e iluminação'), ('ducha', 'Banho quente', 'A qualquer hora')]
    tiles_html = ''.join('<li>%s<div><strong>%s</strong><span>%s</span></div></li>' % (ic(i), esc(t), esc(d)) for i, t, d in tiles)
    faixa = ''.join('<span class="mq-item">%s %s</span>' % (ic(i), esc(t)) for i, t, _ in SERV_RODOVIA)
    numerados = ''.join('<li class="card rv num7"><span class="n7">%02d</span>%s<h3>%s</h3><p>%s</p></li>' % (k + 1, ic(i, 'ic ic-servico'), esc(t), esc(d))
                        for k, (i, t, d) in enumerate(SERV_RODOVIA))
    parada = [('Rodovia à noite', 'A pista fica acesa a noite toda, com frentista e conveniência abertos.', 'Rodovia à noite com o movimento dos faróis'),
              ('Fila de carretas', 'Espaço de sobra para manobrar e aguardar a vez com segurança.', 'Fila de carretas na rodovia vista do alto'),
              ('Praça de pedágio', 'Ponto de referência a poucos quilômetros do posto.', 'Praça de pedágio vista do alto'),
              ('Motorista na cabine', 'Quem roda a noite toda sabe onde encontrar uma parada de confiança.', 'Motorista sorrindo na cabine do caminhão'),
              ('Estrada em linha reta', 'Saída fácil para a pista principal depois do descanso.', 'Rodovia vista do alto em linha reta'),
              ('Descanso na cabine', 'Pátio vigiado para dormir com tranquilidade.', 'Motorista descansando na cabine')]
    pilha = ''.join('<article class="pilha-item">%s<div class="pilha-texto"><h3>%s</h3><p>%s</p></div></article>'
                    % (s.foto('galeria-%d.jpg' % (k + 1), '4/3', d, '1200 x 900', t), t, x) for k, (t, x, d) in enumerate(parada))
    return '''
<body class="topo-sobre-foto m1 m7">
%(sprite)s
%(topo)s
<main id="conteudo">
<section class="hero" id="inicio" aria-labelledby="t-hero">
  <div class="hero-media hero-cheio">%(hero)s</div>
  <div class="hero-veu"></div>
  <div class="hero-linhas" aria-hidden="true"><i></i><i></i><i></i></div>
  <div class="wrap hero-txt hero-centro">
    <p class="km h-in" style="--i:0">%(icpin)s <span data-p="endereco">%(end)s</span></p>
    <h1 id="t-hero" class="h-in" style="--i:1">%(h1)s</h1>
    <p class="lead h-in" style="--i:2">Pista iluminada, restaurante aberto e pátio vigiado a noite inteira. Quando o sono bater, a Rota Sul está acesa.</p>
    <div class="acoes h-in" style="--i:3"><a class="btn btn-prim" data-maps href="%(maps)s" target="_blank" rel="noopener">%(icpin)s Como chegar</a>
      <a class="btn btn-foto" data-whats href="%(wa)s">%(icw)s WhatsApp</a></div>
  </div>
  <ul class="wrap tiles7 h-in" style="--i:4">%(tiles)s</ul>
</section>

<div class="faixa7" data-loop aria-label="Serviços do posto">
  <div class="mq" data-marquee style="--mq-dur:40s;--mq-gap:44px"><div class="mq-grupo">%(faixa)s</div></div>
</div>

<section id="precos" class="secao precos" aria-labelledby="t-precos">
  <div class="wrap">
    <div class="cab rv"><p class="rotulo">Painel de preços</p><h2 id="t-precos">Preço aceso como a pista</h2></div>
    <ul class="painel7 rv">%(precos)s</ul>
    %(nota)s
  </div>
</section>

<section id="servicos" class="secao servicos alt" aria-labelledby="t-serv">
  <div class="wrap">
    <div class="cab rv"><p class="rotulo">Estrutura</p><h2 id="t-serv">Oito motivos para parar aqui</h2></div>
    <ul class="grade7" data-stagger>%(numerados)s</ul>
  </div>
</section>

<section id="parada" class="parada" aria-labelledby="t-parada">
  <div class="hscroll" data-hscroll>
    <div class="hscroll-fixo">
      <div class="wrap cab-h"><p class="rotulo">Galeria</p><h2 id="t-parada">A noite na Rota Sul</h2></div>
      <div class="pilha">%(pilha)s</div>
    </div>
  </div>
</section>

<section id="restaurante" class="secao restaurante" aria-labelledby="t-rest">
  <div class="wrap rest-grid">
    <div class="rest-foto rv">%(destaque)s</div>
    <div class="rest-txt rv">
      <p class="rotulo">Restaurante 24h</p>
      <h2 id="t-rest">Prato quente a qualquer hora</h2>
      <p class="sub">De madrugada também tem comida feita na hora, café forte e mesa para descansar antes de seguir.</p>
      <ol class="fluxo">
        <li>%(icb)s<span>Abasteça</span></li><li class="tracejado" aria-hidden="true"></li>
        <li>%(icr)s<span>Coma bem</span></li><li class="tracejado" aria-hidden="true"></li>
        <li>%(icc)s<span>Descanse</span></li>
      </ol>
    </div>
  </div>
</section>
%(fim)s''' % dict(sprite=sprite(), topo=topo(s, [('precos', 'Preços'), ('servicos', 'Estrutura'), ('parada', 'Galeria'), ('restaurante', 'Restaurante'), ('localizacao', 'Como chegar')], True),
           hero=s.foto('hero.jpg', '16/9', 'Rodovia em frente ao posto à noite, com os faróis riscando a pista', '1920 x 1080', 'Rodovia à noite com o rastro dos faróis', cls='foto-fundo', eager=True),
           icpin=ic('pin'), end=esc(s.endereco), h1=titulo_linhas(['Aberto quando', 'a estrada pede.']), maps=esc(s.maps()), wa=esc(s.wa()), icw=ic('whats'),
           tiles=tiles_html, faixa=faixa, precos=lista_precos(s, 'preco rv'), nota=nota_precos(), numerados=numerados, pilha=pilha,
           icb=ic('bomba'), icr=ic('restaurante'), icc=ic('cama'),
           destaque=s.foto('destaque.jpg', '4/3', 'Prato servido no restaurante do posto, com café', '1200 x 900', 'Prato servido no restaurante'),
           fim=secoes_finais(s, 'Bandeira e parceiros da estrada', 'O selo da bandeira e as marcas que trabalham com a Rota Sul. As logos entram quando o posto enviar os arquivos.',
                             ['Parada certa na madrugada. Tudo aberto e gente atenciosa.', 'Pátio vigiado de verdade. Durmo tranquilo aqui.', 'Comida quente às três da manhã. Não tem preço.'],
                             'Aberto 24 horas na rodovia', 'Rodando de madrugada?', 'Chame no WhatsApp para confirmar o preço do diesel ou avisar que está chegando com a frota.',
                             'Pague como a sua frota paga', 'Cartão frota, Pix e cartões, com nota fiscal na hora.'))


def corpo_8(s):
    roteiro = [('bomba', 'Abasteça', 'Frentista na pista e calibragem grátis.'),
               ('banheiro', 'Banheiro limpo', 'Limpeza a cada hora, fraldário e acessibilidade.'),
               ('cafe', 'Café e lanche', 'Pão de queijo, salgados e café coado.'),
               ('estrada', 'Siga viagem', 'Saída direta para a rodovia.')]
    rot = ''.join(('<li class="tracejado" aria-hidden="true"></li>' if k else '') + '<li class="rv">%s<h3>%s</h3><p>%s</p></li>' % (ic(i), esc(t), esc(d))
                  for k, (i, t, d) in enumerate(roteiro))
    serv = [('banheiro', 'Banheiros e fraldário', 'Limpos, cheirosos e com acessibilidade.'),
            ('cafe', 'Café e lanches', 'Para quem tem pressa e para quem quer sentar.'),
            ('calibragem', 'Calibragem', 'Calibrador digital à vontade.'),
            ('loja', 'Loja de estrada', 'Água, lanches, carregador e itens de viagem.'),
            ('estacionamento', 'Vagas amplas', 'Para carro, van e motorhome.'),
            ('wifi', 'Wi-Fi grátis', 'Na loja e nas mesas.')]
    fotos = [(1, 'Estrada vista de dentro do carro, com a serra ao fundo', 'Estrada vista de dentro do carro'),
             (2, 'Estrada de montanha vista pelo para-brisa', 'Estrada de montanha pelo para-brisa'),
             (3, 'Mesa do café com xícaras e lanches', 'Mesa do café'),
             (4, 'Café da manhã servido na mesa, visto de cima', 'Café da manhã servido'),
             (5, 'Motorista usando o GPS do celular na estrada', 'Motorista usando o GPS'),
             (6, 'Viajante dirigindo com o celular no suporte', 'Viajante dirigindo')]
    galeria = ''.join('<li class="rv">%s</li>' % s.foto('galeria-%d.jpg' % i, '4/3', d, '1200 x 900', a) for i, d, a in fotos)
    return '''
<body class="m1 m8">
%(sprite)s
%(topo)s
<main id="conteudo">
<section class="hero" id="inicio" aria-labelledby="t-hero">
  <div class="wrap hero-grid8">
    <div class="hero-txt">
      <p class="km h-in" style="--i:0">%(icpin)s <span data-p="endereco">%(end)s</span></p>
      <h1 id="t-hero" class="h-in" style="--i:1">%(h1)s</h1>
      <p class="lead h-in" style="--i:2">Para quem viaja de carro com a família: banheiro limpo de verdade, café quente, lanche rápido e calibragem. Em 15 minutos você está de volta à estrada.</p>
      <div class="acoes h-in" style="--i:3"><a class="btn btn-prim" data-maps href="%(maps)s" target="_blank" rel="noopener">%(icpin)s Como chegar</a>
        <a class="btn btn-sec" data-whats href="%(wa)s">%(icw)s WhatsApp</a></div>
    </div>
    <div class="hero-visual8 h-in" style="--i:2"><div class="hero-media">%(hero)s</div>
      <p class="etiqueta8">%(icr)s Loja e banheiro abertos 24h</p></div>
  </div>
</section>

<section id="roteiro" class="secao roteiro8 alt" aria-labelledby="t-rot">
  <div class="wrap">
    <div class="cab rv centro"><p class="rotulo">Roteiro da parada</p><h2 id="t-rot">Quatro passos e pé na estrada</h2></div>
    <ol class="rota8">%(rot)s</ol>
  </div>
</section>

<section id="precos" class="secao precos" aria-labelledby="t-precos">
  <div class="wrap">
    <div class="cab rv"><p class="rotulo">Preços de hoje</p><h2 id="t-precos">Encha o tanque sem surpresa</h2></div>
    <ul class="precos-lista" data-stagger>%(precos)s</ul>
    %(nota)s
  </div>
</section>

<section id="servicos" class="secao servicos alt" aria-labelledby="t-serv">
  <div class="wrap">
    <div class="cab rv"><p class="rotulo">Estrutura</p><h2 id="t-serv">Feito para a família na estrada</h2></div>
    <ul class="serv-grid" data-stagger>%(serv)s</ul>
    <ul class="wrap nums8" data-stagger>%(stats)s</ul>
  </div>
</section>

<section id="galeria" class="secao galeria" aria-labelledby="t-gal">
  <div class="wrap">
    <div class="cab rv"><p class="rotulo">Galeria</p><h2 id="t-gal">No meio do caminho tinha um café</h2></div>
    <ul class="gal-grid gal8" data-stagger>%(galeria)s</ul>
  </div>
</section>

<section id="cafe" class="secao restaurante alt" aria-labelledby="t-cafe">
  <div class="wrap rest-grid">
    <div class="rest-txt rv">
      <p class="rotulo">Café da estrada</p>
      <h2 id="t-cafe">Uma pausa gostosa no meio da viagem</h2>
      <p class="sub">Café coado, pão de queijo saindo do forno, sucos e lanches naturais. Mesas para sentar e esticar as pernas antes de seguir.</p>
    </div>
    <div class="rest-foto rv">%(destaque)s</div>
  </div>
</section>
%(fim)s''' % dict(sprite=sprite(), topo=topo(s, [('roteiro', 'A parada'), ('precos', 'Preços'), ('servicos', 'Estrutura'), ('galeria', 'Galeria'), ('localizacao', 'Como chegar')], False),
           hero=s.foto('hero.jpg', '16/9', 'Estrada vista pelo para-brisa, com o posto à frente', '1920 x 1080', 'Estrada vista de dentro do carro', eager=True),
           icpin=ic('pin'), end=esc(s.endereco), h1=titulo_linhas(['Banheiro limpo,', 'café quente,', 'estrada livre.']), maps=esc(s.maps()), wa=esc(s.wa()), icw=ic('whats'),
           icr=ic('relogio'), rot=rot, precos=lista_precos(s), nota=nota_precos(), serv=servicos(serv), stats=stats(s, 'stat rv'), galeria=galeria,
           destaque=s.foto('destaque.jpg', '4/3', 'Mesa do café do posto com xícaras e lanches', '1200 x 900', 'Mesa do café do posto'),
           fim=secoes_finais(s, 'A bandeira e os parceiros da parada', 'A bandeira do posto e as marcas da pista, da loja e do café.',
                             ['Banheiro limpo de verdade, coisa rara na estrada. Paramos sempre.', 'As crianças amam o pão de queijo. Parada certa na viagem de férias.', 'Rápido para abastecer e calibrar. Em dez minutos voltamos para a estrada.'],
                             'Na rodovia, aberto 24 horas', 'Vai pegar a estrada?', 'Chame no WhatsApp para saber o preço do combustível ou tirar dúvidas sobre a parada.',
                             'Pague como preferir', 'Pix, aproximação, débito e crédito na pista e na loja.'))


def corpo_9(s):
    chips = [('bomba', 'GNV'), ('aproximacao', 'Recarga elétrica'), ('app', 'Motorista de app'), ('cafe', 'Café 24h')]
    chips_html = ''.join('<span class="chip9 c9-%d" data-flutuar style="animation-delay:-%ds">%s %s</span>' % (k, k * 2, ic(i), esc(t)) for k, (i, t) in enumerate(chips))
    abas = [('gnv', 'GNV', 'GNV com fila andando', 'Bombas de GNV dedicadas, pressão conferida e atendimento rápido para quem roda o dia inteiro.',
             s.foto('galeria-1.jpg', '4/3', 'Motorista no carro com o celular, pronto para rodar', '1200 x 900', 'Motorista no carro com o celular')),
            ('recarga', 'Recarga elétrica', 'Carregue enquanto toma um café', 'Carregadores rápidos para carro elétrico. Pague pelo app ou no caixa, por kWh.',
             s.foto('destaque.jpg', '4/3', 'Carregador ligado no carro elétrico, de perto', '1200 x 900', 'Carro elétrico carregando')),
            ('app', 'Motorista de app', 'Vantagens para quem dirige por app', 'Cadastre-se no programa Motorista Parceiro e ganhe café, ducha e pontos a cada abastecimento.',
             s.foto('galeria-2.jpg', '4/3', 'Celular com o mapa de navegação no painel do carro', '1200 x 900', 'Celular com navegação no painel')),
            ('cafe', 'Café 24h', 'Pausa entre uma corrida e outra', 'Café expresso, lanches e banheiro limpo a qualquer hora, com tomada para carregar o celular.',
             s.foto('galeria-3.jpg', '4/3', 'Copos de café no balcão da loja', '1200 x 900', 'Copos de café no balcão'))]
    lista = ''.join('<button type="button" class="aba" role="tab" id="aba-%s" aria-controls="painel-%s" aria-selected="%s"%s>%s</button>'
                    % (i, i, 'true' if k == 0 else 'false', '' if k == 0 else ' tabindex="-1"', n) for k, (i, n, _, _, _) in enumerate(abas))
    paineis = ''.join('<div class="aba-painel" role="tabpanel" id="painel-%s" aria-labelledby="aba-%s"%s><div class="aba-grid"><div class="aba-txt"><h3>%s</h3><p>%s</p>'
                      '<a class="btn btn-prim" data-whats href="%s">%s Falar com o posto</a></div><div class="aba-media">%s</div></div></div>'
                      % (i, i, '' if k == 0 else ' hidden', t, x, esc(s.wa()), ic('whats'), f) for k, (i, n, t, x, f) in enumerate(abas))
    bento = [('bomba', 'GNV', 'Bombas dedicadas e atendimento ágil.', 'b-largo'),
             ('aproximacao', 'Recarga rápida', 'Para carros elétricos e híbridos plug-in.', ''),
             ('cafe', 'Café 24h', 'Expresso e lanche a qualquer hora.', ''),
             ('lavagem', 'Ducha express', 'Carro limpo para a próxima corrida.', ''),
             ('calibragem', 'Calibragem', 'Pneu certo gasta menos.', ''),
             ('wifi', 'Wi-Fi e tomadas', 'Carregue o celular na pausa.', 'b-largo')]
    bento_html = ''.join('<li class="card rv bento %s">%s<h3>%s</h3><p>%s</p></li>' % (c, ic(i, 'ic ic-servico'), esc(t), esc(d)) for i, t, d, c in bento)
    gal = ''.join('<li class="rv">%s</li>' % s.foto('galeria-%d.jpg' % i, '4/3', d, '1200 x 900', a) for i, d, a in [
        (4, 'Vista da cidade à noite a partir do posto', 'Cidade à noite'),
        (5, 'Celular no suporte do carro com o mapa aberto', 'Celular no suporte do carro'),
        (6, 'Avenida movimentada à noite, perto do posto', 'Avenida movimentada à noite')])
    chips_pag = ''.join('<span class="chip">%s %s</span>' % (ic(i), t) for i, t, _ in PAGAMENTOS)
    app = '''<div class="app9" data-tilt="12"><div class="app9-topo">%s<span>Motorista Parceiro</span></div>
      <p class="app9-nome">Olá, motorista!</p>
      <div class="app9-linha"><span>Abastecimentos no mês</span><b>18</b></div>
      <div class="app9-linha"><span>Cafés grátis disponíveis</span><b>2</b></div>
      <div class="barra"><i style="--v:.72"></i></div>
      <p class="app9-meta">Faltam 7 abastecimentos para a próxima ducha grátis</p>
      <p class="app-nota">Tela ilustrativa</p></div>''' % ic('app')
    return '''
<body class="m9">
%(sprite)s
%(topo)s
<main id="conteudo">
<section class="hero" id="inicio" aria-labelledby="t-hero">
  <div class="wrap hero-grid9">
    <div class="hero-txt">
      <p class="rotulo h-in" style="--i:0">GNV · Recarga · Café 24h</p>
      <h1 id="t-hero" class="h-in" style="--i:1">%(h1)s</h1>
      <p class="lead h-in" style="--i:2">GNV, recarga para carro elétrico, café 24 horas e vantagens para motorista de aplicativo. Tudo rápido, porque o seu tempo é dinheiro.</p>
      <div class="acoes h-in" style="--i:3"><a class="btn btn-prim" data-maps href="%(maps)s" target="_blank" rel="noopener">%(icpin)s Como chegar</a>
        <a class="btn btn-sec" data-whats href="%(wa)s">%(icw)s WhatsApp</a></div>
    </div>
    <div class="hero-visual9 h-in" style="--i:2"><div class="hero-media">%(hero)s</div>%(chips)s</div>
  </div>
</section>

<section id="precos" class="secao precos" aria-labelledby="t-precos">
  <div class="wrap">
    <div class="cab rv"><p class="rotulo">Preços de hoje</p><h2 id="t-precos">Gasolina, etanol, GNV e recarga</h2></div>
    <ul class="precos-lista" data-stagger>%(precos)s</ul>
    %(nota)s
  </div>
</section>

<section id="energia" class="secao experiencia alt" aria-labelledby="t-exp">
  <div class="wrap">
    <div class="cab rv"><p class="rotulo">Do jeito que você roda</p><h2 id="t-exp">Um posto para cada tipo de motor</h2></div>
    <div class="abas rv" data-abas>
      <div class="abas-lista" role="tablist" aria-label="Serviços do posto">%(lista)s</div>
      %(paineis)s
    </div>
  </div>
</section>

<section id="servicos" class="secao servicos" aria-labelledby="t-serv">
  <div class="wrap">
    <div class="cab rv"><p class="rotulo">Serviços</p><h2 id="t-serv">Rápido de entrar, rápido de sair</h2></div>
    <ul class="bento9" data-stagger>%(bento)s</ul>
  </div>
</section>

<section id="motorista" class="secao motorista9 alt" aria-labelledby="t-mot">
  <div class="wrap mot-grid">
    <div class="rv"><p class="rotulo">Motorista Parceiro</p><h2 id="t-mot">Quem roda por app ganha mais aqui</h2>
      <p class="sub">Cadastre o CPF no caixa e acompanhe tudo pelo celular. A cada abastecimento você junta pontos para café, ducha e descontos.</p>
      <ul class="lanche-lista"><li>%(icc)s Café grátis a cada 10 abastecimentos</li><li>%(icl)s Ducha express com desconto</li><li>%(ica)s Tomada e Wi-Fi na pausa</li></ul>
      <a class="btn btn-prim" data-whats href="%(wa)s">%(icw)s Quero me cadastrar</a></div>
    %(app)s
  </div>
</section>

<section id="galeria" class="secao galeria" aria-labelledby="t-gal">
  <div class="wrap">
    <div class="cab rv"><p class="rotulo">Galeria</p><h2 id="t-gal">A cidade não para. Nem a gente.</h2></div>
    <ul class="gal-grid gal9" data-stagger>%(gal)s</ul>
  </div>
</section>

<section id="pagamento" class="secao pagamento alt" data-loop aria-labelledby="t-pag">
  <div class="wrap"><div class="cab rv centro"><p class="rotulo">Formas de pagamento</p><h2 id="t-pag">Pague sem parar o motor</h2>
    <p class="sub">Pix, aproximação e cartão direto na bomba de GNV e no carregador.</p></div></div>
  <div class="mq" data-marquee style="--mq-dur:30s;--mq-gap:16px"><div class="mq-grupo">%(chipspag)s</div></div>
</section>
%(band)s%(depo)s%(local)s%(final)s%(rod)s''' % dict(sprite=sprite(), topo=topo(s, [('precos', 'Preços'), ('energia', 'GNV e recarga'), ('motorista', 'Motorista'), ('galeria', 'Galeria'), ('localizacao', 'Como chegar')], False),
           h1=titulo_linhas(['Abastece,', 'carrega e volta', 'pra corrida.']), maps=esc(s.maps()), icpin=ic('pin'), wa=esc(s.wa()), icw=ic('whats'),
           hero=s.foto('hero.jpg', '16/9', 'Avenida em frente ao posto à noite, com o movimento dos carros', '1920 x 1080', 'Avenida à noite com o rastro dos faróis', eager=True),
           chips=chips_html, precos=lista_precos(s), nota=nota_precos(), lista=lista, paineis=paineis, bento=bento_html, app=app,
           icc=ic('cafe'), icl=ic('lavagem'), ica=ic('wifi'), gal=gal, chipspag=chips_pag,
           band=secao_bandeira(s, 'Bandeira e parceiros', 'A bandeira do posto, a rede de recarga e os apps que trabalham com a gente.', s.totem),
           depo=secao_depoimentos(s, ['GNV rápido e café de madrugada. Virou meu ponto entre as corridas.', 'Carrego o elétrico enquanto tomo um café. Muito prático.', 'O programa para motorista de app vale a pena. Já ganhei várias duchas.']),
           local=secao_local(s, 'Na avenida, aberto 24 horas'),
           final=secao_final(s, 'Vai rodar hoje?', 'Chame no WhatsApp para saber o preço do GNV, a disponibilidade dos carregadores ou se cadastrar no programa.'),
           rod=rodape(s))


def corpo_10(s):
    pacotes = ''.join('''<li class="card rv pacote%s" data-pacote="%d"><p class="pac-tit" data-pn>%s</p><p class="pac-de">a partir de</p>
      <strong data-num data-moeda data-casas="2" data-valor="%s">%s</strong><p class="pac-desc" data-pd>%s</p>
      <a class="btn %s" data-whats href="%s" data-msg="%s">%s Agendar</a></li>'''
                      % (' destaque10' if k == 1 else '', k, esc(n), v, preco_txt(v, 2), esc(d), 'btn-prim' if k == 1 else 'btn-sec',
                         esc(s.wa('Olá! Quero agendar: ' + n.lower() + '.')), esc('Olá! Quero agendar: ' + n.lower() + '.'), ic('calendario'))
                      for k, (n, v, d) in enumerate(s.pacotes))
    passos = [('gota', 'Pré-lavagem', 'Espuma ativa para soltar a sujeira sem riscar.'),
              ('lavagem', 'Lavagem técnica', 'Luvas de microfibra e produtos neutros.'),
              ('ducha', 'Secagem', 'Toalhas macias e ar nos detalhes.'),
              ('selo', 'Acabamento', 'Pneus, vidros e plásticos tratados.')]
    proc = ''.join(('<li class="tracejado" aria-hidden="true"></li>' if k else '') + '<li class="rv"><span class="p10">%02d</span>%s<h3>%s</h3><p>%s</p></li>' % (k + 1, ic(i), esc(t), esc(d))
                   for k, (i, t, d) in enumerate(passos))
    fotos = [(1, 'Vidro do carro sendo lavado com esponja e espuma', 'Vidro sendo lavado com espuma'),
             (2, 'Esponja com espuma ao lado do carro escuro', 'Esponja com espuma'),
             (3, 'Aspiração do carro branco por dentro', 'Aspiração do carro'),
             (4, 'Limpeza profunda do carpete do carro', 'Limpeza do carpete'),
             (5, 'Higienização do banco do carro', 'Higienização do banco'),
             (6, 'Roda sendo lavada com esponja', 'Roda sendo lavada')]
    galeria = ''.join('<li class="rv m10-%d">%s</li>' % (i, s.foto('galeria-%d.jpg' % i, '4/3', d, '1200 x 900', a)) for i, d, a in fotos)
    serv = [('lavagem', 'Lavagem técnica', 'Externa e interna, com produtos neutros.'),
            ('gota', 'Higienização', 'Bancos, carpetes e teto.'),
            ('selo', 'Polimento', 'Remove riscos leves e devolve o brilho.'),
            ('escudo', 'Proteção da pintura', 'Cera e selante para durar mais.'),
            ('bomba', 'Combustível', 'Abasteça enquanto o carro fica pronto.'),
            ('cafe', 'Lounge com café', 'Espere com conforto e Wi-Fi.')]
    return '''
<body class="topo-sobre-foto m10">
%(sprite)s
%(topo)s
<main id="conteudo">
<section class="hero" id="inicio" aria-labelledby="t-hero">
  <div class="hero-media hero-cheio">%(hero)s</div>
  <div class="hero-veu"></div>
  <div class="wrap hero-txt hero10">
    <p class="rotulo h-in" style="--i:0">Posto e estética automotiva</p>
    <h1 id="t-hero" class="h-in" style="--i:1">%(h1)s</h1>
    <p class="lead h-in" style="--i:2">Lavagem técnica, higienização, polimento e proteção da pintura, com café no lounge enquanto você espera.</p>
    <div class="acoes h-in" style="--i:3"><a class="btn btn-prim" data-whats href="%(wa)s">%(icc)s Agendar horário</a>
      <a class="btn btn-foto" href="#pacotes">Ver pacotes</a></div>
  </div>
</section>

<section id="pacotes" class="secao pacotes10" aria-labelledby="t-pac">
  <div class="wrap">
    <div class="cab rv centro"><p class="rotulo">Pacotes</p><h2 id="t-pac">Escolha o cuidado do seu carro</h2>
      <p class="sub">Valores de referência para carro de passeio. O orçamento final depende do tamanho e do estado do veículo.</p></div>
    <ul class="pac-grid" data-stagger>%(pacotes)s</ul>
  </div>
</section>

<section id="processo" class="secao processo10 alt" aria-labelledby="t-proc">
  <div class="wrap">
    <div class="cab rv"><p class="rotulo">Como fazemos</p><h2 id="t-proc">Cuidado em cada etapa</h2></div>
    <ol class="rota10">%(proc)s</ol>
  </div>
</section>

<section id="polimento" class="secao restaurante" aria-labelledby="t-pol">
  <div class="wrap rest-grid">
    <div class="rest-foto rv">%(destaque)s</div>
    <div class="rest-txt rv">
      <p class="rotulo">Polimento e proteção</p>
      <h2 id="t-pol">Brilho de carro novo, de novo</h2>
      <p class="sub">Polimento técnico para tirar riscos leves e manchas, com camada de proteção para a pintura durar mais bonita.</p>
      <a class="btn btn-prim" data-whats href="%(wa)s">%(icc)s Pedir orçamento</a>
    </div>
  </div>
</section>

<section id="servicos" class="secao servicos alt" aria-labelledby="t-serv">
  <div class="wrap">
    <div class="cab rv"><p class="rotulo">Serviços</p><h2 id="t-serv">Tudo no mesmo endereço</h2></div>
    <ul class="serv-grid" data-stagger>%(serv)s</ul>
  </div>
</section>

<section id="galeria" class="secao galeria" aria-labelledby="t-gal">
  <div class="wrap">
    <div class="cab rv"><p class="rotulo">Galeria</p><h2 id="t-gal">Detalhe por detalhe</h2></div>
    <ul class="gal10" data-stagger>%(galeria)s</ul>
  </div>
</section>

<section id="precos" class="secao precos alt" aria-labelledby="t-precos">
  <div class="wrap">
    <div class="cab rv"><p class="rotulo">Pista</p><h2 id="t-precos">Combustível com preço à vista</h2></div>
    <ul class="precos-lista" data-stagger>%(precos)s</ul>
    %(nota)s
  </div>
</section>
%(band)s%(depo)s%(local)s%(final)s%(rod)s''' % dict(sprite=sprite(), topo=topo(s, [('pacotes', 'Pacotes'), ('processo', 'Como fazemos'), ('galeria', 'Galeria'), ('precos', 'Combustível'), ('localizacao', 'Onde estamos')], True),
           hero=s.foto('hero.jpg', '16/9', 'Carro claro coberto de espuma sendo lavado à mão no box', '1920 x 1080', 'Carro sendo lavado à mão com espuma', cls='foto-fundo', eager=True),
           h1=titulo_linhas(['O brilho que', 'o seu carro merece.']), wa=esc(s.wa()), icc=ic('calendario'), pacotes=pacotes, proc=proc,
           destaque=s.foto('destaque.jpg', '4/3', 'Polimento da pintura com a politriz, de perto', '1200 x 900', 'Polimento da pintura com politriz'),
           serv=servicos(serv), galeria=galeria, precos=lista_precos(s), nota=nota_precos(),
           band=secao_bandeira(s, 'Bandeira e marcas parceiras', 'A bandeira do posto e as marcas de produtos que usamos na estética.', s.totem),
           depo=secao_depoimentos(s, ['O carro saiu melhor do que quando comprei. Atendimento impecável.', 'Abasteço e faço a higienização no mesmo lugar. Prático demais.', 'O polimento tirou todos os riscos leves. Recomendo.']),
           local=secao_local(s, 'Pista e estética no mesmo endereço'),
           final=secao_final(s, 'Seu carro merece esse cuidado', 'Chame no WhatsApp, escolha o pacote e agende o melhor horário para você.'),
           rod=rodape(s))

CORPOS += [corpo_6, corpo_7, corpo_8, corpo_9, corpo_10]

# ---------------------------------------------------------------------------
# PÁGINA ÍNDICE
# ---------------------------------------------------------------------------
def indice(sites):
    cards = []
    for k, s in enumerate(sites):
        bolas = ''.join('<button type="button" class="bola" data-pal="%s" aria-pressed="%s" aria-label="Abrir com a paleta %s" title="%s" '
                        'style="background:linear-gradient(135deg,%s 0 38%%,%s 38%% 66%%,%s 66%% 100%%)"></button>'
                        % (p['id'], 'true' if p['id'] == s.paleta else 'false', esc(p['nome']), esc(p['nome']), p['cores']['fundo'], p['cores']['destaque'], p['cores']['marca'])
                        for p in s.paletas)
        cards.append('''<li class="modelo rv" style="--i:%(i)d">
  <figure class="foto" data-foto="hero.jpg" data-base="%(pasta)s/img/" data-proporcao="16/10" data-desc="Foto principal do modelo %(n)d" data-tamanho="1920 x 1080" style="aspect-ratio:16/10"><img alt="Prévia do modelo %(nome)s" loading="lazy"></figure>
  <div class="modelo-txt">
    <p class="modelo-num">Modelo %(n)d · %(conc)s</p>
    <h2>%(nome)s</h2>
    <p>%(desc)s</p>
    <div class="bolas" role="group" aria-label="Paletas do modelo %(n)d">%(bolas)s</div>
    <a class="btn btn-prim abrir" href="%(href)s/index.html" data-href="%(href)s/index.html">Abrir modelo</a>
  </div>
</li>''' % dict(i=k, pasta=esc(s.pasta), n=k + 1, nome=esc(s.nome), conc=esc(s.conceito), desc=esc(s.descricao.replace(' Modelo de demonstração.', '')),
                bolas=bolas, href=s.pasta.replace(' ', '%20')))
    c = completar(NEUTROS['escuro'] | {'marca': '#F5A524', 'destaque': '#FF6B2C'})
    vars_ = ''.join('--%s:%s;' % (k, v) for k, v in c.items())
    return '''<!doctype html>
<html lang="pt-BR" data-m-cards="subir">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Modelos de site para posto</title>
<meta name="description" content="Cinco modelos de site para posto de combustível, com seletor de cores e de animações.">
<meta name="robots" content="noindex">
<meta name="theme-color" content="%(fundo)s">
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap">
<style>
:root{%(vars)s--sobre-foto:#FFFFFF;--topo:0px;--m-vel:1;--m-dist:1;--titulo:'Inter',system-ui,sans-serif;--corpo:'Inter',system-ui,sans-serif}
%(core)s
.ind-topo{padding:clamp(56px,9vw,96px) 0 32px}
.ind-topo h1{font-size:clamp(34px,6vw,60px);letter-spacing:-.03em;max-width:16ch}
.modelos{display:grid;grid-template-columns:repeat(auto-fill,minmax(min(100%%,340px),1fr));gap:24px;padding-bottom:96px}
.modelo{background:var(--card);border:1px solid var(--linha);border-radius:20px;overflow:hidden;display:flex;flex-direction:column}
.modelo .foto{border-radius:0;border-width:0 0 1.5px}
.modelo-txt{padding:22px;display:grid;gap:12px;flex:1;align-content:start}
.modelo-num{font-size:13px;font-weight:700;letter-spacing:.08em;text-transform:uppercase;color:var(--marca-forte)}
.modelo h2{font-size:26px}
.modelo-txt>p:not(.modelo-num){color:var(--suave);font-size:15px}
.bolas{display:flex;gap:8px;flex-wrap:wrap}
.bola{width:44px;height:44px;border-radius:50%%;border:2px solid var(--linha)}
.bola[aria-pressed="true"]{border-color:var(--texto);box-shadow:0 0 0 2px var(--card),0 0 0 4px var(--marca-forte)!important}
.abrir{justify-self:start;margin-top:4px}
</style>
<script>document.documentElement.classList.add('js');if(matchMedia('(prefers-reduced-motion: reduce)').matches)document.documentElement.classList.add('calmo');</script>
</head>
<body>
%(sprite)s
<main class="wrap">
  <header class="ind-topo">
    <p class="rotulo">Modelos de demonstração</p>
    <h1>Cinco sites para posto de combustível</h1>
    <p class="sub">Cada modelo tem o botão <b>Personalizar</b> no canto inferior esquerdo, para trocar as cores e as animações na hora. Clique numa bolinha para abrir o modelo já com aquela paleta.</p>
  </header>
  <ul class="modelos">%(cards)s</ul>
</main>
<script>
(function(){
  var io='IntersectionObserver' in window&&!document.documentElement.classList.contains('calmo')?new IntersectionObserver(function(es){es.forEach(function(e){if(e.isIntersecting){e.target.classList.add('visto');io.unobserve(e.target);}});},{threshold:.1}):null;
  document.querySelectorAll('.rv').forEach(function(el){if(io)io.observe(el);else el.classList.add('visto');});
  document.querySelectorAll('figure.foto').forEach(function(f){
    var ph=document.createElement('span');ph.className='foto-ph';ph.setAttribute('aria-hidden','true');
    ph.innerHTML='<svg class="ic" aria-hidden="true"><use href="#i-camera"/></svg><b></b><span class="ph-tam"></span>';
    ph.querySelector('b').textContent='FOTO: '+f.getAttribute('data-foto');ph.querySelector('.ph-tam').textContent='Tamanho ideal: '+f.getAttribute('data-tamanho');
    f.insertBefore(ph,f.firstChild);
    var url=f.getAttribute('data-base')+f.getAttribute('data-foto'),im=new Image();
    im.onload=function(){f.querySelector('img').src=url;f.classList.add('tem-foto');};im.src=url;
  });
  document.querySelectorAll('.modelo').forEach(function(m){
    var a=m.querySelector('.abrir'),bs=m.querySelectorAll('.bola');
    bs.forEach(function(b){b.addEventListener('click',function(){
      bs.forEach(function(x){x.setAttribute('aria-pressed',String(x===b));});
      a.href=a.getAttribute('data-href')+'?paleta='+b.getAttribute('data-pal');
    });});
  });
})();
</script>
</body>
</html>
''' % dict(fundo=c['fundo'], vars=vars_, core=ler('core.css'), sprite=sprite(), cards=''.join(cards))

# ---------------------------------------------------------------------------
# LEIA-ME DE FOTOS DE CADA SITE
# ---------------------------------------------------------------------------
def leia_fotos(s):
    l = ['FOTOS DO SITE: %s (%s)' % (s.nome, s.pasta), '=' * 60, '',
         'Salve cada foto nesta pasta (img) com o NOME EXATO da lista.',
         'A foto aparece sozinha no site, sem mexer no código.',
         'Se apagar uma foto, o site mostra um quadro dizendo o que fotografar.', '',
         'Dicas: celular na horizontal, boa luz, sem pessoas de rosto aparente',
         'sem autorização. Logos sempre em PNG com fundo transparente.', '']
    for arq, desc, tam in s.fotos:
        l.append('%-18s %s' % (arq, desc))
        l.append('%-18s Tamanho ideal: %s' % ('', tam))
        l.append('')
    l.append('og.jpg             Imagem que aparece ao compartilhar o link no WhatsApp')
    l.append('                   Tamanho ideal: 1200 x 630')
    return '\n'.join(l) + '\n'

# ---------------------------------------------------------------------------
# CONFERÊNCIA DE CONTRASTE (WCAG AA)
# ---------------------------------------------------------------------------
def tabela_contraste(sites):
    linhas, falhas = [], 0
    for s in sites:
        for p in s.paletas:
            c = completar(p['cores'])
            t = [('texto/fundo', contraste(c['texto'], c['fundo']), 4.5),
                 ('texto/card', contraste(c['texto'], c['card']), 4.5),
                 ('suave/fundo', contraste(c['suave'], c['fundo']), 4.5),
                 ('suave/fundo-2', contraste(c['suave'], c['fundo-2']), 4.5),
                 ('botão texto', contraste(c['marca-texto'], c['marca']), 4.5),
                 ('botão hover', contraste(c['marca-texto'], c['marca-esc']), 4.5),
                 ('rótulo (marca-forte)', min(contraste(c['marca-forte'], c[x]) for x in ('fundo', 'fundo-2', 'card')), 4.5),
                 ('marca/fundo (ícones)', contraste(c['marca'], c['fundo']), 3.0)]
            if s.d.get('apoio_icones'):   # nestes modelos a cor de apoio também pinta ícones
                t.append(('apoio/fundo (ícones)', min(contraste(c['destaque'], c[x]) for x in ('fundo', 'fundo-2', 'card')), 3.0))
            ok = all(v >= m for _, v, m in t)
            if not ok: falhas += 1
            linhas.append((s.pasta, p['nome'], t, ok))
    return linhas, falhas

def main():
    sites = []
    for d, corpo in zip(POSTOS, CORPOS):
        s = Site(d)
        body = corpo(s)
        css = ''.join(ler(x) for x in (s.css if isinstance(s.css, list) else [s.css]))
        html_ = head(s, css) + body + fim(s)
        pasta = os.path.join(RAIZ, s.pasta)
        os.makedirs(os.path.join(pasta, 'img'), exist_ok=True)
        with open(os.path.join(pasta, 'index.html'), 'w', encoding='utf-8', newline='\n') as f:
            f.write(html_)
        with open(os.path.join(pasta, 'img', 'LEIA-ME-FOTOS.txt'), 'w', encoding='utf-8', newline='\r\n') as f:
            f.write(leia_fotos(s))
        sites.append(s)
        print('ok  %-8s %-28s %6.1f KB' % (s.pasta, s.nome, len(html_.encode('utf-8')) / 1024))
    with open(os.path.join(RAIZ, 'index.html'), 'w', encoding='utf-8', newline='\n') as f:
        f.write(indice(sites))
    print('ok  index.html')
    linhas, falhas = tabela_contraste(sites)
    out = ['CONTRASTE DAS PALETAS (WCAG AA: texto 4,5:1, ícones e botões 3:1)', '']
    for pasta, nome, t, ok in linhas:
        out.append('%s | %-26s | %s | %s' % (pasta, nome, '  '.join('%s %.1f' % (a, v) for a, v, _ in t), 'OK' if ok else 'FALHOU'))
    with open(os.path.join(AQUI, 'contraste.txt'), 'w', encoding='utf-8', newline='\r\n') as f:
        f.write('\n'.join(out) + '\n')
    print('contraste: %d paletas, %d falhas' % (len(linhas), falhas))
    for pasta, nome, t, ok in linhas:
        if not ok:
            print('  FALHOU', pasta, nome, [(a, round(v, 2)) for a, v, m in t if v < m])

if __name__ == '__main__':
    main()
