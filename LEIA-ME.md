# Modelos de site para posto: como usar

São 10 modelos prontos, cada um numa pasta:

| Pasta | Modelo | Para quem |
|---|---|---|
| `posto 1` | Posto Estrada Real | Posto de rodovia: caminhoneiro, diesel, Arla, pátio, banho, restaurante |
| `posto 2` | Posto Avenida | Posto da cidade: conveniência, café, Pix, fidelidade |
| `posto 3` | Auto Posto Bom Jesus | Posto de família em cidade pequena: história, lanchonete, lavagem |
| `posto 4` | Posto Preço Justo | Bandeira branca, foco no preço |
| `posto 5` | Posto & Autocenter Central | Posto com oficina: óleo, pneus, alinhamento, lavagem |
| `posto 6` | Posto Serra Azul | Variação do 1: rodovia de serra, painel de preço do diesel no topo |
| `posto 7` | Posto Rota Sul | Variação do 1: rodovia à noite, topo centralizado, serviços numerados |
| `posto 8` | Posto Parada Certa | Variação do 1: parada para quem viaja de carro com a família |
| `posto 9` | Posto Via Expressa | Urbano: GNV, recarga elétrica, motorista de aplicativo |
| `posto 10` | Posto Brilho Total | Posto com estética automotiva premium: pacotes de lavagem e polimento |

Os modelos 6, 7 e 8 usam as mesmas 10 paletas do modelo 1. O modelo 10 tem pacotes de lavagem
com preço: troque em `pacotes` no bloco DADOS DO POSTO. No modelo 9, o terceiro item de cada preço
é a unidade (ex.: `["GNV", 4.79, "por m³"]`).

Os nomes, telefones e endereços são fictícios. Tudo é **modelo de demonstração**.

---

## 1. Abrir os sites

Dê dois cliques no `index.html` desta pasta. Ele mostra os 5 modelos lado a lado.
Clique numa bolinha de cor para abrir o modelo já com aquela paleta.

Também dá para abrir direto o `index.html` de dentro de cada pasta `posto N`.

Precisa de internet só para as fontes (letras). Sem internet o site abre igual, com uma fonte padrão.

## 2. Trocar as fotos

Cada site tem a pasta `img/`. Os modelos vêm com fotos de banco gratuito (Pexels).

Para colocar a foto do posto, **salve com o mesmo nome** dentro de `img/`, por cima da antiga.
Ela aparece sozinha, sem mexer no código.

- A lista de fotos, com o que fotografar e o tamanho ideal, está em `img/LEIA-ME-FOTOS.txt`.
- De onde veio cada foto de banco: `img/CREDITOS.txt`.
- Se apagar uma foto, o site mostra um quadro dizendo o nome do arquivo e o que fotografar.
- Logo, selo da bandeira e logos de parceiros não vêm do banco: o posto manda os arquivos em PNG com fundo transparente
  (`logo.png`, `bandeira.png`, `parceiro-1.png`, `parceiro-2.png`...). Enquanto não manda, o cabeçalho mostra o nome do posto escrito.

## 3. Trocar nome, telefone, endereço e preços

Abra o `index.html` do site no Bloco de Notas (ou VS Code) e procure por:

```
DADOS DO POSTO
```

Fica no começo do arquivo. Troque só o que está entre aspas:

- `nome`, `slogan`, `telefone`, `endereco`, `cnpj`, `instagram`
- `whatsapp`: só números, com 55 e DDD (ex.: `5535912345678`)
- `horario`: cada linha é `["Dia", "Horário"]`
- `precos`: a data em `atualizado` e cada combustível como `["Nome", 6.29]` (com ponto, não vírgula)
- `bandeira`: o nome da bandeira, ou `"Bandeira branca"`
- `parceiros`: os nomes, na mesma ordem dos arquivos `parceiro-1.png`, `parceiro-2.png`...

Salve e recarregue a página.

## 4. Trocar as cores (na hora, com o cliente)

Clique em **Personalizar**, no canto inferior esquerdo, aba **Cores**:

- Escolha uma das 5 paletas prontas, ou
- Coloque a **cor da marca do posto** no campo de cor. O site ajusta o texto dos botões sozinho e avisa se a cor tiver pouco contraste.
- **Copiar link desta paleta**: manda o link para o cliente já com a cor escolhida.
- **Copiar cores**: copia o código das cores, para deixar fixo.

Para deixar uma das paletas prontas fixa, troque `paleta: "padrao"` no bloco DADOS DO POSTO pelo id dela
(`vermelho`, `azul`, `verde`...).

O modelo 1 tem também 5 paletas de três cores (fundo, cor de apoio e cor vibrante):
`petroleo`, `marinho`, `oliva`, `vinho` e `cobre`.

## 5. Trocar as animações

No mesmo botão **Personalizar**, aba **Movimento**. Escolha a animação de cada parte do site:
bandeira, parceiros, topo, foto do topo, cards, preços, fundo e velocidade.

- **▶ Ver de novo** repete a animação daquela parte.
- **Copiar link** manda a escolha para o cliente.
- **Copiar configuração** copia uma linha `motion: { ... }`. Cole no lugar da linha `motion` do bloco DADOS DO POSTO para deixar fixo.

Quem usa o computador com "reduzir movimento" ligado vê o site parado, por acessibilidade.

## 5b. Estilo Apple (vidro, cápsulas e cartões do iPhone)

**Os 10 modelos já abrem com o estilo Apple.** Ele segue as regras do kit da pasta `APPLE GLASS`:

- **Vidro só no que flutua:** cabeçalho, botões sobre foto, botões flutuantes e menu do celular.
- **O conteúdo fica sólido:** cartões com canto suave, sombra leve no tema claro e linha fina no escuro.
- **No celular**, preços, serviços e formas de pagamento viram uma lista agrupada, como a tela Ajustes
  do iPhone. A página fica bem mais curta no celular (13% no modelo 1, 22% no modelo 2).
- **Acabamento de texto** em todos: título sem palavra sozinha na última linha, "R$" menor que o número
  nos preços grandes e rótulo das seções sem traço (nos modelos 2, 3, 5 e 9).

Ficou de fora do padrão, de propósito, o que enfeita mas atrapalha: o aviso que cobre o topo da tela,
a barra de abas que repete o menu, o painel de vidro sobre a foto do topo (esconde a foto), os cartões de vidro
(vidro no conteúdo vai contra a regra da Apple) e a fonte do sistema (no Android e no Windows ela não é a da Apple).
Tudo isso continua no painel, para o cliente que pedir.

No botão **Personalizar**, aba **Estilo Apple**, dá para mudar cada parte ou voltar ao visual antigo.

**Combinações prontas:** Original (o visual de antes), Toque Apple, Vidro, Apple completo e **Sugestão do designer**
(é o padrão de cada modelo, tabela abaixo).

**Escolha por parte do site** (o painel só mostra o que existe no modelo):

| Parte | Opções |
|---|---|
| Cabeçalho | Original · Barra de vidro · Cápsula flutuante |
| Botões | Original · Pílula · Pílula de vidro |
| Texto do topo | Original · Painel fosco · Painel transparente (para foto bonita no fundo) |
| Preços | Original · Widgets de vidro · Lista estilo Ajustes |
| Cards, serviços e horário | Original · Cartões iOS · Cartões de vidro |
| Abas (modelos 2, 5 e 9) | Original · Segmentado iOS |
| Botões flutuantes | Original · De vidro · Barra de abas (atalhos no rodapé, com o WhatsApp no meio) |
| Aviso de preço | Desligado · Notificação estilo iPhone com o preço do dia, 1 vez por visita |
| Letra | Do modelo · Fonte do sistema Apple |

O vidro usa as cores da paleta escolhida, então combina com qualquer cor da marca.
Quem usa "reduzir transparência" no aparelho vê superfícies sólidas no lugar do vidro.

- **Copiar link** já leva o estilo junto (parâmetro `g=`). Para mostrar o visual antigo: `index.html?g=original`.
- **Copiar configuração** copia uma linha `vidro: { ... }`. Para deixar fixo no site do cliente, cole no bloco DADOS DO POSTO
  no lugar da linha `vidro`.
- Na galeria (`index.html` da pasta), cada modelo tem o botão **Ver o original**, para comparar com o cliente.

**Padrão de cada modelo**

| Modelo | O que entra | Por quê |
|---|---|---|
| 1, 6, 7, 8 (rodovia) | cápsula, pílula, cartões iOS, flutuantes de vidro | Foto forte no topo: o vidro deixa a foto aparecer. Títulos em maiúsculas continuam |
| 2 Avenida | cápsula, pílula, cartões iOS, segmentado, flutuantes de vidro | Claro e arredondado: o mais próximo do iPhone |
| 3 Bom Jesus | barra de vidro, pílula, cartões iOS, flutuantes de vidro | A serifa e o creme são a identidade da família: barra discreta no lugar da cápsula |
| 4 Preço Justo | barra de vidro, flutuantes de vidro | O visual bruto do preço é a identidade: botões e cartões ficam como eram |
| 5 Autocenter | cápsula, pílula, cartões iOS, segmentado, flutuantes de vidro | Fundo escuro: os cartões ganham linha fina e o vidro dá profundidade |
| 9 Via Expressa | cápsula, pílula, cartões iOS, segmentado, flutuantes de vidro | Público de app: o visual de iPhone conversa direto com ele |
| 10 Brilho Total | cápsula, pílula, cartões iOS com filete dourado, flutuantes de vidro | Premium e escuro; a serifa dourada e o pacote em destaque continuam |

Para mudar o padrão de um modelo: `SUGESTAO_VIDRO` no `_fonte/gerar.py`. As opções ficam em `VIDRO_OPCOES`
e o visual no `_fonte/core.css` (seção ESTILO APPLE).
Cópias de antes: `_backup/antes-integracao-apple/` (esta mudança) e `_backup/_fonte-antes-estilo-apple/` (antes do estilo Apple).

## 6. Antes de publicar o site real de um posto

1. No bloco DADOS DO POSTO, troque todos os dados e coloque `mostrarSeletor: false` (o botão Personalizar some).
2. Apague a linha `<meta name="robots" content="noindex">` (está logo no começo, com um aviso em cima).
3. Troque os 3 depoimentos de exemplo por frases reais de clientes, com autorização. Eles estão no arquivo, procure por `Exemplo de depoimento`.
4. Troque o aviso "Modelo de demonstração" do rodapé.
5. Troque as fotos de banco pelas fotos reais do posto, e coloque `logo.png`, `bandeira.png` e as logos dos parceiros.
6. Para publicar, suba a pasta do site inteira (o `index.html` e a pasta `img`) para a hospedagem.

---

## Para quem mexe no código: a pasta `_fonte`

Os 5 sites são gerados a partir da pasta `_fonte`. Para mudanças grandes (textos, seções, cores das paletas),
edite lá e rode:

```
python _fonte/gerar.py
```

Isso **regrava** os `index.html` das 5 pastas. Se você editou um `index.html` à mão, essa edição se perde.
Para trocar só dados de um posto, edite direto o `index.html` dele, como no item 3.

- `gerar.py`: dados dos 5 postos, textos e montagem das páginas
- `core.css` e `core.js`: vagas de foto, motion e painel Personalizar (comum aos 5)
- `pre.js`: aplica cor e motion antes da página aparecer
- `posto1.css` a `posto5.css`: o visual de cada modelo
- `fotos.py`: recorta e comprime as fotos de banco
- `contraste.txt`: conferência de contraste das 25 paletas (todas passam no WCAG AA)

Observação: no console do navegador aparecem avisos "arquivo não encontrado" para as vagas que ainda
estão vazias (logo, bandeira, parceiros, mapa). É esperado: é assim que o site descobre que a foto ainda não chegou.
