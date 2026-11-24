# -*- coding: utf-8 -*-
"""
Recorta, redimensiona e comprime as fotos de banco (Pexels) para as vagas de cada site,
e escreve o CREDITOS.txt de cada pasta img/.

Uso:  python -I fotos.py <pasta com os originais pNNNN.jpg>
"""
import os, sys
from PIL import Image

AQUI = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.dirname(AQUI)

# vaga: (id Pexels, proporção, tamanho final, foco vertical 0 a 1, foco horizontal 0 a 1)
HERO = ('16/9', (1920, 1080))
Q43 = ('4/3', (1200, 900))
Q11 = ('1/1', (1200, 1200))
Q32 = ('3/2', (1500, 1000))

MAPA = {
    'posto 1': {
        'hero.jpg': (1453781, HERO, .55, .5),
        'destaque.jpg': (2641886, Q43, .45, .5),
        'galeria-1.jpg': (27099096, Q43, .55, .45),
        'galeria-2.jpg': (14005602, Q43, .5, .5),
        'galeria-3.jpg': (27099094, Q43, .6, .5),
        'galeria-4.jpg': (2348359, Q43, .55, .5),
        'galeria-5.jpg': (5410923, Q43, .5, .5),
        'galeria-6.jpg': (12377481, Q43, .5, .5),
    },
    'posto 2': {
        'hero.jpg': (12377482, HERO, .5, .5),
        'destaque.jpg': (35411022, Q43, .5, .5),
        'galeria-1.jpg': (3812750, Q43, .5, .6),
        'galeria-2.jpg': (9074447, Q43, .45, .5),
        'galeria-3.jpg': (28097279, Q43, .7, .5),
        'galeria-4.jpg': (4199524, Q43, .45, .5),
        'galeria-5.jpg': (18280321, Q43, .5, .5),
        'galeria-6.jpg': (11009960, Q43, .5, .5),
    },
    'posto 3': {
        'hero.jpg': (4173094, HERO, .45, .5),
        'destaque.jpg': (18946615, Q43, .62, .5),
        'equipe.jpg': (27040519, Q32, .5, .5),
        'galeria-1.jpg': (24838063, Q11, .55, .5),
        'galeria-2.jpg': (3341067, Q11, .62, .5),
        'galeria-3.jpg': (5233271, Q11, .5, .7),
        'galeria-4.jpg': (3807450, Q11, .5, .55),
        'galeria-5.jpg': (10673908, Q11, .5, .5),
        'galeria-6.jpg': (3784137, Q11, .5, .5),
    },
    'posto 4': {
        'hero.jpg': (12377480, HERO, .5, .5),
        'galeria-1.jpg': (9216590, Q11, .5, .5),
        'galeria-2.jpg': (20500734, Q11, .5, .6),
        'galeria-3.jpg': (20500733, Q11, .55, .5),
        'galeria-4.jpg': (11316617, Q11, .5, .45),
        'galeria-5.jpg': (4112711, Q11, .55, .5),
        'galeria-6.jpg': (6684769, Q11, .5, .5),
    },
    'posto 5': {
        'hero.jpg': (8985514, HERO, .5, .5),
        'destaque.jpg': (10490609, Q43, .45, .5),
        'equipe.jpg': (8985723, Q43, .55, .5),
        'galeria-1.jpg': (3806249, Q43, .5, .5),
        'galeria-2.jpg': (8986033, Q43, .5, .5),
        'galeria-3.jpg': (6872591, Q43, .5, .5),
        'galeria-4.jpg': (10490621, Q43, .5, .5),
        'galeria-5.jpg': (6473244, Q43, .5, .5),
        'galeria-6.jpg': (5693651, Q43, .5, .5),
    },
    'posto 6': {
        'hero.jpg': (18612459, HERO, .45, .5),
        'destaque.jpg': (12824421, Q43, .5, .5),
        'galeria-1.jpg': (14143647, Q43, .5, .5),
        'galeria-2.jpg': (20560700, Q43, .6, .5),
        'galeria-3.jpg': (11087837, Q43, .5, .4),
        'galeria-4.jpg': (13663664, Q43, .55, .5),
        'galeria-5.jpg': (9195241, Q43, .5, .5),
        'galeria-6.jpg': (11911883, Q43, .5, .5),
    },
    'posto 7': {
        'hero.jpg': (27778013, HERO, .5, .5),
        'destaque.jpg': (10720381, Q43, .5, .5),
        'galeria-1.jpg': (311621, Q43, .5, .5),
        'galeria-2.jpg': (13008066, Q43, .5, .5),
        'galeria-3.jpg': (16310595, Q43, .5, .5),
        'galeria-4.jpg': (14797990, Q43, .5, .6),
        'galeria-5.jpg': (10588468, Q43, .5, .5),
        'galeria-6.jpg': (11911872, Q43, .45, .5),
    },
    'posto 8': {
        'hero.jpg': (28840460, HERO, .5, .5),
        'destaque.jpg': (22598227, Q43, .55, .5),
        'galeria-1.jpg': (27855359, Q43, .5, .5),
        'galeria-2.jpg': (9397596, Q43, .55, .5),
        'galeria-3.jpg': (19409031, Q43, .5, .5),
        'galeria-4.jpg': (18535645, Q43, .5, .5),
        'galeria-5.jpg': (12276484, Q43, .5, .5),
        'galeria-6.jpg': (1386649, Q43, .5, .5),
    },
    'posto 9': {
        'hero.jpg': (31065299, HERO, .5, .5),
        'destaque.jpg': (35736773, Q43, .5, .5),
        'galeria-1.jpg': (16842191, Q43, .5, .6),
        'galeria-2.jpg': (5025655, Q43, .5, .5),
        'galeria-3.jpg': (17719534, Q43, .55, .5),
        'galeria-4.jpg': (34729776, Q43, .5, .5),
        'galeria-5.jpg': (4824425, Q43, .5, .5),
        'galeria-6.jpg': (14780178, Q43, .5, .5),
    },
    'posto 10': {
        'hero.jpg': (6872580, HERO, .5, .5),
        'destaque.jpg': (5233259, Q43, .5, .5),
        'galeria-1.jpg': (6873088, Q43, .5, .5),
        'galeria-2.jpg': (6872575, Q43, .5, .5),
        'galeria-3.jpg': (6873119, Q43, .5, .5),
        'galeria-4.jpg': (5233264, Q43, .5, .5),
        'galeria-5.jpg': (5233285, Q43, .5, .5),
        'galeria-6.jpg': (4870664, Q43, .45, .5),
    },
}

ORIGENS = []
def achar(pid):
    for o in ORIGENS:
        f = os.path.join(o, 'p%d.jpg' % pid)
        if os.path.exists(f):
            return f
    raise FileNotFoundError('original p%d.jpg não encontrado' % pid)

def recortar(im, prop, fy, fx):
    a, b = [float(x) for x in prop.split('/')]
    alvo = a / b
    w, h = im.size
    if w / h > alvo:          # sobra largura
        nw = round(h * alvo); x = round((w - nw) * fx); return im.crop((x, 0, x + nw, h))
    nh = round(w / alvo); y = round((h - nh) * fy); return im.crop((0, y, w, y + nh))

def salvar(im, destino, limite_kb):
    for q in (82, 80, 78, 75, 72, 70, 67, 64, 60):
        im.save(destino, 'JPEG', quality=q, optimize=True, progressive=True)
        if os.path.getsize(destino) <= limite_kb * 1024:
            return q
    return q

def main(origem):
    relatorio = []
    for pasta, vagas in MAPA.items():
        img_dir = os.path.join(RAIZ, pasta, 'img')
        os.makedirs(img_dir, exist_ok=True)
        cred = ['CRÉDITOS DAS FOTOS: %s' % pasta, '=' * 60, '',
                'Fotos de banco gratuito usadas só para o modelo de demonstração.',
                'Banco: Pexels (pexels.com). Licença Pexels: uso gratuito, inclusive comercial,',
                'sem obrigação de dar crédito (https://www.pexels.com/license/).',
                'O nome do autor de cada foto aparece na página da foto, no link abaixo.',
                'Quando o posto mandar as fotos reais, é só salvar por cima com o mesmo nome.', '']
        for arq, (pid, (prop, tam), fy, fx) in vagas.items():
            im = Image.open(achar(pid)).convert('RGB')
            orig = im.size
            im = recortar(im, prop, fy, fx)
            if im.size[0] < tam[0]:
                relatorio.append('AVISO %s/%s: original menor que o ideal (%s)' % (pasta, arq, im.size))
            im = im.resize(tam, Image.LANCZOS) if im.size[0] >= tam[0] else im
            limite = 350 if arq == 'hero.jpg' else 200
            q = salvar(im, os.path.join(img_dir, arq), limite)
            kb = os.path.getsize(os.path.join(img_dir, arq)) / 1024
            relatorio.append('%-8s %-14s pexels %-9d %4dx%-4d q%d %6.1f KB' % (pasta, arq, pid, im.size[0], im.size[1], q, kb))
            cred += ['%-14s https://www.pexels.com/photo/%d/' % (arq, pid), '%-14s Banco: Pexels · Licença Pexels · original %dx%d' % ('', orig[0], orig[1]), '']
            if arq == 'hero.jpg':
                og = recortar(Image.open(achar(pid)).convert('RGB'), '1200/630', fy, fx).resize((1200, 630), Image.LANCZOS)
                salvar(og, os.path.join(img_dir, 'og.jpg'), 200)
                cred += ['og.jpg         recorte da mesma foto do hero.jpg', '']
        with open(os.path.join(img_dir, 'CREDITOS.txt'), 'w', encoding='utf-8', newline='\r\n') as f:
            f.write('\n'.join(cred) + '\n')
    total = {}
    for pasta in MAPA:
        d = os.path.join(RAIZ, pasta, 'img')
        total[pasta] = sum(os.path.getsize(os.path.join(d, x)) for x in os.listdir(d) if x.endswith('.jpg')) / 1024 / 1024
    print('\n'.join(relatorio))
    for p, mb in total.items():
        print('%s: %.2f MB em fotos' % (p, mb))

if __name__ == '__main__':
    ORIGENS.extend(sys.argv[1:])
    main(sys.argv[1])
