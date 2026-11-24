# PROMPT: 5 SITES DE POSTO DE COMBUSTÍVEL (fotos de banco gratuito + motion + seletores de paleta e de motion)

Copie tudo abaixo da linha e cole no Claude Code (com o MazyOS), aberto na pasta
`Desktop\SITES\SITES POSTOS`.

---

## Papel

Você é um designer e desenvolvedor front-end sênior, especialista em sites para
negócios locais brasileiros. Vai criar **5 sites completos e diferentes entre si
para postos de combustível**. Eles servem de **modelo de demonstração**: depois,
cada um vai virar o site de um posto real, trocando os textos e as fotos.

Tudo em **português do Brasil**, com acentuação correta.

## Referências que já existem nesta máquina (leia antes de começar)

1. `Desktop\MazyOS-main\site-nkl\index.html`: site da NKL (sistema para postos).
   Use como referência de qualidade, de organização das seções, de acessibilidade
   (`aria-labelledby`, `alt`, contraste) e do vocabulário do setor (pista, loja de
   conveniência, frota, troca de óleo, bandeira).
2. `Desktop\MazyOS-main\skills\prospecta-maps\modelo-demo.html`: modelo de site
   de prévia. Use como referência de estrutura técnica: variáveis de cor e fonte
   no `:root`, cabeçalho que fica sólido ao rolar, botão de WhatsApp, seção final
   de contato.
3. `Desktop\MazyOS-main\identidade\design-guide.md`, se existir: siga só o que
   for regra de qualidade. **As cores e fontes da NKL NÃO entram nestes sites**,
   porque cada posto tem a sua identidade.

Não copie textos nem imagens desses arquivos. Use só como padrão de qualidade.

## O que entregar

```
SITES POSTOS/
  LEIA-ME.md                  como trocar fotos e dados (explicado para leigo)
  index.html                  página que lista os 5 modelos com link para cada um
  01-rodovia/
    index.html
    img/                      fotos de banco gratuito, já com os nomes padrão
      LEIA-ME-FOTOS.txt       lista das vagas de foto (nome, descrição, tamanho)
      CREDITOS.txt            origem e licença de cada foto usada
  02-urbano-premium/
  03-familia-cidade/
  04-economico/
  05-autocenter/
```

Cada site tem **um único `index.html`**, com CSS e JS dentro dele. Não use
framework, build, npm, React nem Tailwind. Ele precisa abrir com dois cliques,
direto no navegador, sem servidor. As fontes vêm só do Google Fonts. Sem
nenhuma outra dependência externa.

## Os 5 conceitos (cada um com cara própria)

Os 5 sites **não podem parecer o mesmo site com outra cor**. Mude paleta, fonte,
estilo do topo, formato dos cards e ordem das seções. Os nomes abaixo são
fictícios e servem só de demonstração.

| # | Pasta | Nome fictício | Público e foco | Estilo visual |
|---|---|---|---|---|
| 1 | `01-rodovia` | Posto Estrada Real | Caminhoneiro e viajante na BR. Diesel S10, Arla 32, pátio para carreta, banho, restaurante, aberto 24h | Escuro (grafite), destaque amarelo-âmbar, fonte condensada e forte (ex.: Barlow Condensed + Inter). Topo com foto grande de rodovia à noite |
| 2 | `02-urbano-premium` | Posto Avenida | Carro de passeio na cidade. Gasolina aditivada, loja de conveniência com café, pagamento por aproximação e Pix, app de fidelidade | Claro e sofisticado, branco + azul-petróleo, fonte moderna (ex.: Manrope). Bastante espaço em branco, cantos arredondados |
| 3 | `03-familia-cidade` | Auto Posto Bom Jesus | Posto tradicional de cidade pequena, "desde 19XX", atendimento pelo nome, lavagem, calibragem, padaria ou lanchonete | Acolhedor, creme + verde e um toque de laranja, fonte com personalidade nos títulos (ex.: Fraunces + Nunito Sans). Seção com a história do posto |
| 4 | `04-economico` | Posto Preço Justo | Bandeira branca, foco no menor preço. Tabela de preços em destaque, formas de pagamento, horário | Direto e chamativo, branco + vermelho + preto, fonte bold (ex.: Archivo). Faixa com os preços logo no topo |
| 5 | `05-autocenter` | Posto & Autocenter Central | Posto com troca de óleo, alinhamento, balanceamento, pneus, bateria, lavagem. Agendamento pelo WhatsApp | Industrial, azul-marinho + laranja, fonte técnica (ex.: Space Grotesk + IBM Plex Sans). Grade de serviços com ícones |

## Seções de cada site

Todos os sites têm estas seções, adaptadas ao conceito (a ordem pode mudar):

1. **Cabeçalho fixo**: logo (reservada, veja a regra de imagens), menu âncora,
   botão "Chamar no WhatsApp". No celular, menu hambúrguer acessível
   (`aria-expanded`, fecha com Esc e ao clicar num link).
2. **Topo (hero)**: título com a promessa principal do posto, subtítulo,
   2 botões ("Como chegar" e "WhatsApp"), selos curtos (ex.: "Aberto 24h",
   "Aceitamos Pix") e a foto principal reservada.
3. **Combustíveis e preços**: cards com gasolina comum, aditivada, etanol,
   diesel S10 e o que fizer sentido no conceito (Arla 32, GNV). Os preços ficam
   num único bloco de dados no JS, para trocar fácil. Mostre "Preços atualizados
   em DD/MM/AAAA" e, embaixo, "Preços sujeitos a alteração sem aviso".
4. **Serviços**: grade com ícones SVG desenhados em linha (nada de emoji). Ex.:
   conveniência, troca de óleo, lavagem, calibragem, ducha, Arla 32, banheiros,
   Wi-Fi, estacionamento.
5. **Conveniência ou diferencial**: a seção que mais vende o conceito
   (restaurante no site 1, café no 2, história no 3, preço no 4, oficina no 5).
6. **Galeria**: de 4 a 6 fotos reservadas.
7. **Formas de pagamento**: Pix, débito, crédito, cartão frota, dinheiro. Só
   em texto e ícone genérico, **sem logo de bandeira de cartão**.
8. **Bandeira e parceiros**: selo da bandeira e faixa de parceiros (veja
   SELETOR DE MOTION).
9. **Depoimentos**: 3 cards **visivelmente marcados como exemplo** (veja as
   regras).
10. **Horário e localização**: horário de funcionamento em tabela, endereço,
   botão "Abrir no Google Maps" e um espaço reservado para o mapa (veja abaixo).
11. **Chamada final + rodapé**: CTA de WhatsApp, telefone, endereço, CNPJ,
    Instagram, horário e o aviso "Modelo de demonstração".
12. **Botão flutuante de WhatsApp** fixo no canto inferior direito, com
    `aria-label`.

## REGRA DAS IMAGENS (a mais importante)

As imagens funcionam em duas camadas:

1. **Vaga reservada:** toda imagem do site é uma vaga com nome de arquivo fixo.
   Se o arquivo não existir, a vaga mostra um quadro dizendo que foto vai ali.
2. **Foto de banco gratuito:** para o modelo ficar bonito, você preenche as
   vagas com fotos baixadas de bancos gratuitos e salva cada uma em `img/` com
   o nome da vaga. Depois, o posto real troca pela foto dele, salvando um
   arquivo com o mesmo nome. Não é preciso mexer no código.

### Onde buscar as fotos

- Use **só bancos com licença livre para uso comercial**: **Unsplash**
  (unsplash.com), **Pexels** (pexels.com) e **Pixabay** (pixabay.com).
  Nada de Google Imagens, Freepik, Shutterstock, Getty, Adobe Stock ou foto
  tirada de site de outro posto.
- Baixe o arquivo original pelo link de download do próprio banco.
- Para cada foto, anote em `img/CREDITOS.txt`: nome do arquivo, banco, autor,
  link da página da foto e a licença.

### Como escolher a foto (descarte o que falhar)

- **Sem marca de terceiros visível**: nada de logo de Shell, BP, Petrobras,
  Ipiranga, Texaco, Chevron, Esso, Exxon, cartões ou refrigerantes. Se a marca
  aparecer pequena e der para cortar, corte. Se não der, descarte.
- **Com cara de Brasil sempre que possível.** Evite placa em inglês, preço em
  galão, bomba americana com tela de anúncio e carro americano em destaque. Se
  não houver opção brasileira, prefira enquadramento fechado (bico, mão
  abastecendo, cobertura iluminada à noite, prateleira, café, pneu, chave).
- **Coerente com o conceito**: carreta e rodovia no site 1, café e conveniência
  no 2, clima de cidade pequena no 3, bomba e preço no 4, oficina no 5.
- **Sem foto repetida entre os 5 sites.**
- Nada de foto com marca d'água, ilustração 3D ou imagem gerada por IA.

### Tratamento das fotos (obrigatório)

Use o que estiver instalado na máquina (Python com Pillow, `ffmpeg` ou `sharp`):
- Recorte na proporção da vaga, centralizando o assunto principal.
- Redimensione para o "Tamanho ideal" da tabela abaixo. Nunca aumente uma
  foto menor que isso; nesse caso, escolha outra.
- Salve em JPG com qualidade entre 78 e 82, sem metadados. Meta de peso: hero
  com até 350 KB e as demais com até 200 KB. A logo é a exceção: fica em PNG.
- **Logo e selo de bandeira NÃO vêm de banco.** Ficam como vaga reservada, e
  o cabeçalho mostra o nome do posto escrito (veja o item 6 abaixo).
- Se não achar uma foto boa para alguma vaga, **deixe a vaga reservada**.
  Isso é melhor do que usar uma foto ruim, e você avisa no final.

### Como cada vaga funciona

HTML de cada vaga:

```html
<figure class="foto" data-foto="hero.jpg" data-proporcao="16/9"
        data-desc="Fachada do posto ao entardecer, com as bombas e a cobertura iluminadas"
        data-tamanho="1920 x 1080">
  <img alt="Fachada do Posto Estrada Real ao entardecer">
</figure>
```

Comportamento obrigatório (um único script no fim do `<body>`, para todas as
vagas):

1. Toda `.foto` usa `aspect-ratio` vindo de `data-proporcao`. **O layout não
   pode pular** com ou sem foto.
2. Ao carregar a página, o script tenta abrir `img/` + `data-foto` com
   `new Image()`.
   - **Se a foto existir:** coloca no `src` do `<img>` com
     `object-fit: cover` e adiciona a classe `tem-foto`.
   - **Se não existir:** mostra o quadro reservado. Fundo neutro com listras
     diagonais bem suaves (CSS `repeating-linear-gradient`), borda tracejada,
     um ícone de câmera em SVG e três linhas de texto centralizadas:
     - **FOTO: hero.jpg** (nome do arquivo, em negrito)
     - a descrição de `data-desc`
     - "Tamanho ideal: 1920 x 1080"
3. O quadro reservado precisa ser legível no tema do site (claro ou escuro) e
   no celular. Texto com no mínimo 12px e contraste AA.
4. O `<img>` nunca fica com `src` quebrado (nada de ícone de imagem quebrada).
5. Fotos abaixo da primeira dobra usam `loading="lazy"`. A do hero não.
6. **A logo** segue a mesma regra, com `data-foto="logo.png"`. Sem o arquivo,
   mostra o nome do posto escrito na fonte de título, para o cabeçalho nunca
   ficar vazio.
7. **Mapa:** em vez de iframe, um quadro reservado com `data-foto="mapa.jpg"`
   e a descrição "Print do mapa ou substituir pelo iframe do Google Maps", mais
   o botão "Abrir no Google Maps" com link
   `https://www.google.com/maps/search/?api=1&query=` + endereço codificado.

### Nomes de arquivo padronizados (os mesmos nos 5 sites)

| Arquivo | Onde aparece | Proporção | Tamanho ideal |
|---|---|---|---|
| `logo.png` | cabeçalho e rodapé (PNG transparente) | livre, altura 48px | 600 x 200 |
| `hero.jpg` | topo | 16/9 (no celular, 4/5 com `object-position` central) | 1920 x 1080 |
| `destaque.jpg` | seção de conveniência ou diferencial | 4/3 | 1200 x 900 |
| `galeria-1.jpg` até `galeria-6.jpg` | galeria | 1/1 ou 4/3, conforme o layout | 1200 x 1200 |
| `equipe.jpg` | seção de história ou equipe (sites 3 e 5) | 3/2 | 1500 x 1000 |
| `mapa.jpg` | localização | 16/9 | 1280 x 720 |
| `og.jpg` | prévia ao compartilhar no WhatsApp (meta `og:image`) | 1200/630 | 1200 x 630 |

Cada `data-desc` diz **exatamente que foto tirar**, pensando no dono do posto
fotografando com o celular. Ex.: "Frentista abastecendo um carro, de lado, com
o uniforme do posto" ou "Prateleiras da conveniência com a geladeira de bebidas
ao fundo".

Em cada `img/LEIA-ME-FOTOS.txt`, liste todas as vagas daquele site: nome do
arquivo, descrição, tamanho ideal e a dica "foto na horizontal, com boa luz,
sem pessoas de rosto aparente sem autorização".

## MOTION (animações no padrão do site da NKL)

O site da NKL (`Desktop\MazyOS-main\site-nkl\index.html`) tem as animações
abaixo. **Abra o arquivo e estude o código de cada uma antes de escrever** (os
`@keyframes` e os blocos de JS citados). Reescreva com as cores e o estilo de
cada posto. Não copie o código colado, e não use biblioteca: tudo em CSS e JS
puro.

### O catálogo (nomes como estão no código da NKL)

| # | Efeito | Como é na NKL | Onde procurar no código |
|---|---|---|---|
| M1 | **Entrada do hero em cascata** | selo, título, texto e botões sobem e aparecem um depois do outro (atraso de 0,08s entre eles) | `.hero-anim`, `@keyframes subir` |
| M2 | **Zoom lento na foto do hero** | a foto começa em 106% e volta para 100% em 14s | `.hero-foto img`, `@keyframes zoom` |
| M3 | **Cabeçalho que muda ao rolar** | transparente no topo, sólido com desfoque depois de 40px | classe `rolou` |
| M4 | **Aparecer ao rolar** | blocos e cards entram com opacidade e deslocamento, em sequência | `IntersectionObserver` |
| M5 | **Números que contam** | o número conta do zero até o valor quando aparece na tela, com desaceleração suave | `data-contar`, "Números: contam do zero" |
| M6 | **Faixa infinita (marquee)** | faixa de itens rolando sem parar; vertical no `subirY` | `.trilho-faixa`, `@keyframes rolar` e `subirY` |
| M7 | **Rolagem horizontal fixa** | a seção trava na tela e os cards passam para o lado conforme a pessoa rola, com a foto em parallax dentro do card. No celular vira carrossel com `scroll-snap` | `.hscroll`, `.pilha-item` |
| M8 | **Abas com barra de progresso** | as abas trocam sozinhas a cada 5s, com uma barra que enche; pausam com o mouse em cima e quando a seção sai da tela | `@keyframes encher`, classe `tocando` |
| M9 | **Inclinação 3D com o mouse + parallax** | um elemento inclina seguindo o mouse (até 14°) e se move com a rolagem. Só com mouse (`pointer:fine`) | `--gx`, `--gy`, `--py` |
| M10 | **Linha tracejada correndo** | traço animado ligando as etapas de um fluxo | `@keyframes correr` e `descer` |
| M11 | **Flutuar** | elemento sobe e desce devagar, em loop de 6s | `@keyframes flutuar` |
| M12 | **Barras que crescem** | barras de gráfico crescem do zero quando aparecem | `@keyframes crescerX` e `crescerY` |
| M13 | **Partículas no canvas seguindo o mouse** | linhas e faíscas que nascem no cursor e somem; o canvas para sozinho quando não há movimento | bloco com `cristais` e `faiscas` |

### Quais efeitos em cada site

Todos os sites usam **M1, M2, M3 e M4**. Além disso:

| Site | Efeitos extras | Como aplicar |
|---|---|---|
| 01-rodovia | M5, M7, M10, M13 | M5: "24h", "km 000", vagas para carreta. M7: serviços da parada (diesel, banho, restaurante, pátio) passando na horizontal. M10: linha da estrada ligando "Abasteça, descanse, siga viagem". M13: faíscas âmbar no hero, discretas |
| 02-urbano-premium | M8, M9, M11, M6 | M8: abas "Pista / Conveniência / Café / Fidelidade" com foto e texto. M9: card do app de fidelidade (desenhado em HTML/CSS) inclinando com o mouse. M11: selo "Pague com Pix" flutuando. M6: faixa com as formas de pagamento |
| 03-familia-cidade | M5, M10, M6 | M5: "anos de história", "famílias atendidas" (números do objeto `POSTO`, claramente de exemplo). M10: linha do tempo da história com traço correndo entre as datas. M6: faixa lenta com os serviços |
| 04-economico | M6, M12, M5 | M6: faixa de preços rolando logo abaixo do cabeçalho, estilo letreiro. M12: barras comparando os combustíveis pelo preço (só os do próprio posto, sem comparar com concorrente). M5: os preços contam até o valor ao aparecer |
| 05-autocenter | M7, M8, M9, M12 | M7: serviços da oficina na horizontal. M8: abas "Óleo / Pneus / Alinhamento / Lavagem". M9: card de "Agende pelo WhatsApp" inclinando. M12: barras de "checklist do carro" (óleo, pneus, freios) enchendo |

### Regras de motion (não quebre)

- **`prefers-reduced-motion: reduce` desliga tudo**, igual à NKL: transições e
  animações em 0,01ms, sem loop, sem canvas, sem inclinação. O conteúdo
  aparece completo e parado.
- Anime **só `transform` e `opacity`** (e `background-position` nos
  tracejados). Nunca `top`, `left`, `width` ou `height`.
- Eventos de rolagem com `{ passive: true }` e cálculo dentro de
  `requestAnimationFrame`, um quadro por vez.
- Loops (marquee, abas, canvas, flutuar) **param quando a seção sai da tela**
  (`IntersectionObserver`) e quando a aba do navegador fica oculta.
- Marquee: duplique o conteúdo para o loop não ter emenda; a cópia leva
  `aria-hidden="true"`. Pausa ao passar o mouse.
- Abas automáticas são acessíveis: `role="tablist"`, `tab` e `tabpanel`,
  `aria-selected`, setas do teclado navegam e o foco pausa a troca.
- M7 e M9 só no desktop. No celular (até 900px), M7 vira carrossel com
  `scroll-snap` e M9 fica parado.
- Nada pode atrasar a leitura: o texto do hero aparece inteiro em menos de 1s.
- Sem animação que pisca, treme ou gira sem parar.
- Se o JS falhar, tudo continua visível. Os elementos só começam escondidos
  se uma classe `js` estiver no `<html>`, colocada pelo próprio script.

## SELETOR DE PALETA (trocar as cores na hora)

Cada site tem um **seletor de paletas** para trocar as cores na hora, sem
recarregar a página. Serve para mostrar ao dono do posto as opções e escolher
junto com ele, inclusive com as cores reais da marca dele.

### Como funciona

1. **Todas as cores do site vêm de variáveis CSS** no `:root`. Nenhuma cor
   fica escrita direto num seletor: nem em SVG, nem em sombra, nem em gradiente.
   Use `currentColor`, `var(--...)` e `color-mix()`. Variáveis mínimas:
   `--marca`, `--marca-esc`, `--marca-texto`, `--destaque`, `--fundo`,
   `--fundo-2`, `--card`, `--texto`, `--suave`, `--linha`.
2. Cada paleta é um objeto no JS que define essas variáveis:

```js
const PALETAS = [
  { id: "padrao",   nome: "Grafite e âmbar",     cores: { marca: "#F5A524", fundo: "#121417", ... } },
  { id: "vermelho", nome: "Vermelho e branco",   cores: { ... } },
  { id: "azul",     nome: "Azul e amarelo",      cores: { ... } },
  { id: "verde",    nome: "Verde e branco",      cores: { ... } },
  { id: "laranja",  nome: "Laranja e grafite",   cores: { ... } }
];
```

3. **5 paletas por site:** a primeira é a do conceito (a da tabela dos 5
   conceitos). As outras 4 são combinações comuns em posto: vermelho, azul,
   verde e laranja/amarelo, cada uma com fundo claro ou escuro, conforme
   combinar com o estilo do site. Os nomes descrevem a cor, **nunca uma marca**
   ("Verde e amarelo", e não "estilo Petrobras").
4. **Cor personalizada:** além das 5, há um campo `<input type="color">`
   "Cor da marca do posto". Ao escolher uma cor, o script:
   - aplica a cor em `--marca`;
   - gera `--marca-esc` (12% mais escura) e as variações claras com
     `color-mix()`;
   - calcula o contraste pela fórmula do WCAG e escolhe `--marca-texto` branco
     ou quase preto, o que der mais contraste;
   - se a cor contra o fundo ficar abaixo de 3:1 (botão e ícone), mostra o
     aviso "Pouco contraste com o fundo" e sugere usar a versão escura.
   Tem também um segundo campo para `--destaque`, que é opcional.
5. **Painel do seletor:** um botão redondo com ícone de paleta (SVG) no canto
   inferior **esquerdo**, para não brigar com o WhatsApp à direita. Ao clicar,
   abre um painel pequeno com:
   - as 5 paletas em bolinhas de duas cores, com o nome no `title` e um
     `aria-label`; a paleta ativa fica marcada;
   - os campos de cor personalizada;
   - o botão "Copiar cores", que copia as variáveis CSS da paleta atual para
     colar no código;
   - o botão "Voltar ao padrão".
   O painel fecha com Esc e ao clicar fora, funciona no teclado e usa
   `role="dialog"`. No celular, abre como gaveta de baixo para cima.
6. **Transição suave:** ao trocar, as cores mudam em 0,4s (`transition` em
   `background-color`, `color`, `border-color` e `fill`). Com
   `prefers-reduced-motion`, a troca é instantânea.
7. **Lembrar e compartilhar:**
   - A escolha fica salva no `localStorage`. Use `try/catch`, porque em janela
     anônima pode falhar, e o site precisa funcionar mesmo assim.
   - A URL aceita `?paleta=verde` ou `?cor=1E7F4F` (com `&destaque=...`). Assim
     você manda o link para o cliente já com a cor escolhida. A URL tem
     prioridade sobre o `localStorage`.
   - "Copiar link desta paleta" no painel gera esse link.
8. **Tudo acompanha a paleta**, inclusive o motion: faíscas do canvas (M13),
   barras (M12), tracejados (M10), quadros das vagas de foto, favicon SVG
   (o monograma muda de cor) e `<meta name="theme-color">`. Escute um evento
   `paleta:trocou` disparado no `document` e releia as cores com
   `getComputedStyle`.
9. **Esconder para publicar:** em `POSTO`, os campos `paleta: "padrao"` (a que
   abre por padrão) e `mostrarSeletor: true`. Com `false`, o botão some, mas
   a paleta escolhida continua aplicada. É assim que vai para o ar no site
   real.
10. **Contraste garantido nas 5 paletas prontas:** todas passam no WCAG AA
    (4,5:1 no texto, 3:1 em botões e ícones). Calcule antes de entregar; se uma
    falhar, ajuste o tom.

### Na página índice

Cada card de modelo mostra as 5 bolinhas de paleta. Clicando numa delas, o
botão "Abrir modelo" passa a abrir com `?paleta=...` já aplicada.

## SELETOR DE MOTION (escolher as animações na hora)

O mesmo painel do seletor de paleta vira um painel **"Personalizar"** com duas
abas: **Cores** e **Movimento**. Na aba Movimento você escolhe, bloco por
bloco, qual animação usar, e vê o resultado na hora. Serve para montar junto
com o dono do posto o jeito que o site se mexe.

### Seção nova: Bandeira e parceiros (todos os 5 sites)

Inclua em todos os sites uma seção **"Bandeira e parceiros"**, logo depois do
hero ou antes do rodapé (escolha o que fizer mais sentido no conceito):
- **Selo da bandeira:** vaga `bandeira.png` em destaque, com o texto "Posto
  bandeira {{nome da bandeira}}" vindo de `POSTO.bandeira`. Num posto bandeira
  branca, a seção mostra o selo "Bandeira branca" e o texto muda sozinho.
- **Parceiros:** de 6 a 8 vagas, `parceiro-1.png` até `parceiro-8.png`
  (distribuidora, cartões frota, app de pagamento, marcas da conveniência).
  A lista vem de `POSTO.parceiros`; vaga sem nome não aparece.
- **No modelo, essas vagas NÃO recebem foto de banco nem logo real.** Elas
  mostram o quadro reservado em formato de logo ("LOGO PARCEIRO 1" e a dica
  "PNG transparente, 400 x 160"). Isso basta para ver o motion funcionando.
  O posto real coloca as logos dele, com autorização das marcas.

Acrescente na tabela de nomes de arquivo:

| Arquivo | Onde aparece | Proporção | Tamanho ideal |
|---|---|---|---|
| `bandeira.png` | selo da bandeira (PNG transparente) | 1/1 | 600 x 600 |
| `parceiro-1.png` até `parceiro-8.png` | faixa de parceiros (PNG transparente) | 5/2 | 400 x 160 |

### Variações por bloco

Cada bloco tem de 4 a 6 variações, e uma delas é sempre **"Parado"**. Os
nomes no painel são estes, em português:

| Bloco | Variações (id: nome no painel) | Como é |
|---|---|---|
| **Bandeira** | `brilho`: Brilho passando | um reflexo de luz atravessa o selo na diagonal a cada 4s, como placa nova |
| | `virar`: Virar 3D | ao aparecer na tela, o selo gira em Y de 90° para 0°, como placa virando; com mouse, inclina levemente (M9) |
| | `totem`: Totem | o selo sobe de baixo dentro de um totem desenhado em CSS (o poste de preço do posto); os preços do totem rolam como dígitos de bomba |
| | `pulsar`: Luz pulsando | anel de luz na cor `--marca` pulsa em volta do selo, devagar (3s) |
| | `flutuar`: Flutuar | M11 |
| | `parado`: Parado | sem animação |
| **Parceiros** | `faixa`: Faixa contínua | M6 na horizontal, logos em cinza que ganham cor no hover |
| | `faixa-dupla`: Faixa dupla | duas faixas em sentidos opostos e velocidades diferentes |
| | `colunas`: Colunas subindo | 3 colunas verticais rolando (M6 com `subirY`), a do meio em sentido contrário, igual à seção de maquininhas da NKL |
| | `cascata`: Grade em cascata | grade estática; os logos aparecem um a um com escala de 0,9 para 1 ao entrar na tela |
| | `destaque`: Carrossel com destaque | carrossel automático; o logo do centro fica maior e colorido, os laterais menores e em cinza; troca a cada 2,5s |
| | `parado`: Parado | grade simples |
| **Entrada do hero** | `cascata`: Cascata | M1 |
| | `mascara`: Revelar por máscara | cada linha do título sobe de dentro de uma máscara (`overflow:hidden` + `translateY(100%)`) |
| | `palavras`: Palavra por palavra | o título entra palavra a palavra, com 0,05s de atraso; cada palavra vira `<span>` via JS, sem quebrar a leitura de tela (`aria-label` no `<h1>`) |
| | `foco`: Desfoque para nítido | o texto entra de `blur(8px)` e opacidade 0 para nítido |
| | `parado`: Parado | |
| **Foto do hero** | `zoom`: Zoom lento | M2 |
| | `parallax`: Parallax | a foto se move a 30% da velocidade da rolagem |
| | `cortina`: Cortina | a foto é revelada por um `clip-path` que abre da esquerda para a direita em 1,1s |
| | `parado`: Parado | |
| **Cards** | `subir`: Subir | M4 |
| | `escala`: Crescer | de `scale(.94)` e opacidade 0 para normal |
| | `inclinar`: Inclinar com o mouse | M9 em cada card, com no máximo 6° |
| | `parado`: Parado | |
| **Preços e números** | `contar`: Contar | M5 |
| | `bomba`: Dígitos de bomba | cada dígito rola verticalmente como o visor de uma bomba (coluna de 0 a 9 com `translateY`), parando no valor, com atraso de 0,06s entre os dígitos |
| | `parado`: Parado | |
| **Fundo do hero** | `faiscas`: Faíscas no mouse | M13 |
| | `linhas`: Linhas de estrada | faixas tracejadas descendo devagar no fundo (M10 na vertical), bem sutis |
| | `nenhum`: Nenhum | |
| **Velocidade geral** | `suave` / `normal` / `intenso` | multiplica durações e distâncias (1,4x / 1x / 0,75x de duração; 0,6x / 1x / 1,3x de distância) por uma variável `--m-vel` |

O **padrão de cada site** segue a tabela "Quais efeitos em cada site" da seção
MOTION. Ou seja, ao abrir, cada site já vem com a combinação dele.

### Como o seletor funciona

1. Cada bloco escolhido vira um atributo no `<html>`, por exemplo
   `data-m-bandeira="brilho"` e `data-m-parceiros="faixa-dupla"`. O CSS de cada
   variação fica preso a esse atributo.
2. Variações com JS (faixas, carrossel, canvas, dígitos, inclinação, parallax)
   são módulos com `iniciar()` e `parar()`. Ao trocar de variação, o `parar()`
   da anterior **desfaz tudo**: cancela `requestAnimationFrame`, desconecta
   observers, remove listeners e apaga clones e spans criados. Trocar 20
   vezes seguidas não pode deixar o site mais lento nem duplicar logos.
3. No painel, cada bloco é uma linha com o nome e as variações em botões
   pequenos (`role="radiogroup"`). Ao lado, há um botão **"▶ Ver de novo"**
   que rola até o bloco e repete a animação de entrada.
4. Botões do painel: **"Copiar configuração"** (copia o objeto
   `motion: {...}` pronto para colar no `POSTO`), **"Copiar link"** (a URL
   recebe `?m=bandeira.brilho,parceiros.faixa-dupla,hero.mascara,vel.suave`,
   junto com os parâmetros de cor, se houver) e **"Voltar ao padrão"**.
5. A escolha fica no `localStorage`, com `try/catch`. A URL tem prioridade.
6. **"Reduzir movimento" do sistema sempre vence.** Com
   `prefers-reduced-motion: reduce`, tudo fica parado, e a aba Movimento mostra
   o aviso: "Seu computador está com 'reduzir movimento' ligado, então as
   animações ficam desligadas." Não existe botão para forçar.
7. Todas as variações usam as cores da paleta ativa e continuam seguindo as
   "Regras de motion" acima.
8. Em `POSTO`, use `motion: { bandeira: "brilho", parceiros: "faixa", ... }`
   para o padrão. Com `mostrarSeletor: false`, o painel inteiro some (cores e
   movimento), e o site fica com o que está no `POSTO`.

## Dados fáceis de trocar

No topo do `<script>` de cada site, crie um objeto `POSTO` com **tudo** que muda
de um cliente para outro. O HTML é preenchido a partir dele:

```js
const POSTO = {
  nome: "Posto Estrada Real",
  slogan: "...",
  whatsapp: "5535900000000",        // só dígitos, com 55 + DDD
  telefone: "(35) 0000-0000",
  endereco: "Rodovia BR-000, km 000, Cidade - UF",
  cnpj: "00.000.000/0000-00",
  instagram: "postoexemplo",
  horario: [["Segunda a domingo", "24 horas"]],
  precos: { atualizado: "22/11/2026", itens: [["Gasolina comum", 0.00], ...] },
  mensagemWhats: "Olá! Vim pelo site e gostaria de mais informações.",
  bandeira: "Bandeira branca",      // ou o nome da bandeira do posto
  parceiros: ["Parceiro 1", "Parceiro 2", "Parceiro 3", "Parceiro 4", "Parceiro 5", "Parceiro 6"],
  paleta: "padrao",                 // id de PALETAS que abre por padrão
  motion: { bandeira: "brilho", parceiros: "faixa", hero: "cascata", foto: "zoom",
            cards: "subir", numeros: "contar", fundo: "nenhum", vel: "normal" },
  mostrarSeletor: true              // false esconde o painel Personalizar (cores e movimento)
};
```

- Preço em formato brasileiro com `Intl.NumberFormat('pt-BR', {style:'currency', currency:'BRL'})`
  e **3 casas decimais**, como na bomba (R$ 6,290).
- Todos os links de WhatsApp são montados como
  `https://wa.me/${POSTO.whatsapp}?text=${encodeURIComponent(POSTO.mensagemWhats)}`.
- O texto também precisa estar escrito no HTML (não só gerado por JS), para o
  Google ler e para o site funcionar com JS desligado. O JS apenas sobrescreve.
- Em telefone, CNPJ e WhatsApp, use dados claramente falsos (zeros). Nunca um
  número que possa ser de alguém.

## Regras de conteúdo (não quebre)

1. **Nada de marca de terceiros no modelo.** Sem logo, nome ou cores
   registradas de Petrobras/BR, Shell, Ipiranga, Ale, Visa, Mastercard, Elo
   etc. Bandeira e parceiros ficam só como vagas reservadas (`bandeira.png`,
   `parceiro-N.png`); quem coloca as logos reais é o posto, com autorização.
2. **Depoimentos são exemplo.** Cada card leva o selo "Exemplo de depoimento"
   e um nome genérico ("Cliente de exemplo, Cidade - UF"). Nada de nota de
   estrelas inventada como se fosse do Google.
3. **Sem promessa que o posto não pode provar.** Nada de "o mais barato da
   região", "combustível 100% garantido", "nº 1". Prefira fatos que o dono
   confirma: horário, serviços, formas de pagamento.
4. **Sem travessão (—)** nos textos. Use vírgula, dois-pontos ou ponto.
5. **Sem lorem ipsum.** Todo texto é copy real, escrita para o público daquele
   conceito, curta e direta.
6. Rodapé de todos: "Modelo de demonstração. Textos, preços e imagens serão
   substituídos pelos do posto."

## Qualidade técnica (obrigatório)

- **Responsivo de verdade**: teste mental em 360px, 768px e 1440px. Nenhuma
  rolagem horizontal. Margem lateral mínima de 16px no celular. Botões com
  altura mínima de 44px.
- **Acessibilidade WCAG AA**: contraste de 4,5:1 no texto, `alt` descritivo em
  toda imagem, foco visível no teclado, `lang="pt-BR"`, um único `<h1>`,
  hierarquia de títulos correta e `prefers-reduced-motion` respeitado.
- **Animações**: seguir a seção MOTION acima.
- **SEO local** no `<head>`: `<title>` e `meta description` próprios, Open Graph
  (`og:title`, `og:description`, `og:image` = `img/og.jpg`), favicon em SVG
  inline (monograma com a inicial do posto) e JSON-LD do tipo `GasStation`
  com nome, endereço, telefone e horário (`openingHoursSpecification`),
  coerente com o objeto `POSTO`.
- `<meta name="robots" content="noindex">` enquanto for modelo, com um
  comentário avisando para remover quando for publicar o site real.
- **Performance**: `font-display: swap`, só os pesos de fonte usados, CSS
  enxuto, fotos dentro do peso da regra de imagens, nenhuma imagem embutida em
  base64. A soma das fotos de cada site fica em até 2,5 MB.
- **Código limpo**: CSS organizado por seção, com variáveis no `:root`
  (`--marca`, `--fundo`, `--texto`...) e comentários curtos em português.

## Página índice (`SITES POSTOS/index.html`)

Uma página simples que apresenta os 5 modelos em cards (nome, conceito em uma
linha, as 2 cores principais em bolinhas e o botão "Abrir modelo"). A imagem de
cada card é o `hero.jpg` do próprio modelo (caminho `01-rodovia/img/hero.jpg`),
com a mesma regra de vaga reservada se a foto não existir. Usa M1 e M4.

## LEIA-ME.md (para quem não é programador)

Explique em passos curtos:
1. Como abrir os sites (dois cliques no `index.html`).
2. **Como trocar as fotos**: os modelos vêm com fotos de banco gratuito. Para
   colocar a foto do posto, salve com o mesmo nome dentro da pasta `img/` do
   site, substituindo a antiga. Ela aparece sozinha, sem mexer no código. Se
   apagar uma foto, aparece o quadro dizendo o que fotografar.
3. Como trocar nome, telefone, endereço e preços (objeto `POSTO` no fim do
   arquivo).
4. **Como trocar as cores:** clicar no botão de paleta, no canto inferior
   esquerdo, e escolher uma das 5 ou colocar a cor da marca do posto. Para
   deixar fixo: "Copiar cores" e colar no `:root`, ou trocar
   `paleta` no objeto `POSTO`. Para mandar ao cliente: "Copiar link desta
   paleta".
5. **Como trocar as animações:** no mesmo botão, aba "Movimento". Escolha a
   variação de cada bloco (bandeira, parceiros, topo, cards, preços) e clique
   em "Ver de novo" para assistir. "Copiar link" manda a escolha ao cliente;
   "Copiar configuração" deixa fixo no `POSTO`.
6. **Logos da bandeira e dos parceiros:** salvar `bandeira.png` e
   `parceiro-1.png`, `parceiro-2.png`... em `img/` (PNG com fundo transparente)
   e escrever os nomes em `POSTO.bandeira` e `POSTO.parceiros`.
7. Antes de publicar: colocar `mostrarSeletor: false`, remover o `noindex` e o aviso de modelo, trocar os
   depoimentos de exemplo pelos reais e conferir a lista de verificação abaixo.

## Lista de verificação final (rode e mostre o resultado)

Antes de dizer que terminou, confira cada item nos 5 sites e mostre uma tabela
com ✓ ou ✗:

- [ ] Abre direto no navegador, sem erro no console.
- [ ] Todas as fotos baixadas estão na vaga certa, recortadas, dentro do peso
      e listadas em `CREDITOS.txt` com banco, autor, link e licença.
- [ ] Nenhuma foto com marca de terceiros visível nem repetida entre os sites.
- [ ] Renomeando temporariamente a pasta `img/` de um site, todas as vagas
      mostram o quadro reservado com nome do arquivo, descrição e tamanho, sem
      imagem quebrada (depois volte o nome da pasta).
- [ ] Os efeitos de motion da tabela estão em cada site, funcionando.
- [ ] Com "reduzir movimento" ligado (emule `prefers-reduced-motion` no
      DevTools), nada se mexe e todo o conteúdo aparece.
- [ ] Loops param fora da tela; a rolagem fica lisa (sem travar) no celular.
- [ ] Seletor de paleta: as 5 paletas trocam **todas** as cores do site
      (busque cor fixa `#` fora do `:root` e de `PALETAS`; não pode sobrar),
      incluindo canvas, SVG, favicon e `theme-color`.
- [ ] As 5 paletas de cada site passam no WCAG AA (mostre a tabela de
      contraste calculada).
- [ ] Cor personalizada: com amarelo-claro (#FFE600), o texto do botão fica
      escuro e aparece o aviso de pouco contraste.
- [ ] `?paleta=verde` e `?cor=1E7F4F` abrem já com a cor; a escolha continua
      depois de recarregar; com `mostrarSeletor: false`, o botão some.
- [ ] Seletor de motion: todas as variações de todos os blocos funcionam e
      combinam com qualquer paleta. Teste trocar a variação de Parceiros 20
      vezes: nada duplica, nada fica mais lento, sem erro no console.
- [ ] "Ver de novo" repete a animação do bloco; `?m=...` abre com as
      variações certas; "Copiar configuração" gera um objeto que, colado no
      `POSTO`, reproduz a mesma escolha.
- [ ] Com `POSTO.bandeira = "Bandeira branca"` o texto do selo muda; com menos
      parceiros na lista, as vagas sobrando somem e a faixa não fica com
      buraco.
- [ ] Com "reduzir movimento" ligado, a aba Movimento mostra o aviso e nada
      se mexe.
- [ ] Nenhum `{{`, "lorem", "TODO" ou travessão (—) sobrando (busque nos arquivos).
- [ ] Todos os links de WhatsApp montados a partir do objeto `POSTO`.
- [ ] Nenhuma marca de terceiros.
- [ ] Depoimentos com o selo "Exemplo".
- [ ] Sem rolagem horizontal em 360px; menu do celular abre e fecha.
- [ ] JSON-LD válido e com os mesmos dados do objeto `POSTO`.
- [ ] Os 5 sites são visualmente diferentes entre si (paleta, fonte, hero e
      formato dos cards).

Se algum item falhar, corrija e rode a lista de novo. Só entregue com tudo ✓.
No final, mostre o caminho de cada `index.html`, quais vagas ficaram sem foto
de banco (se houver) e a lista de fotos que o posto real precisa mandar para
substituir as de banco.
