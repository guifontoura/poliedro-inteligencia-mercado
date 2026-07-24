# Guia — Dashboard Power BI (roadmap 2.0)

Objetivo (mesmo do slide 18): painel interativo com filtros por UF, cidade e
segmento comercial, pra o time comercial explorar as Golden Leads sem depender
de planilha ou slide fixo. Isso já monta o essencial em ~20-30min.

## 1. Dado pronto

Rode `python poliedro_14_consolidar_dataset_powerbi.py` (depende dos passos 01,
04, 09 e 11 já terem rodado). Gera duas tabelas:

- `data/outputs/14_escolas_powerbi.csv` — 1.127 Golden Leads, 1 linha por escola,
  com cidade, UF, segmento comercial, score, bairro/lat-long nativos do Censo
  Escolar (99,5% com bairro, 82% com lat/long), renda mediana do responsável
  + categoria legível (IBGE Censo 2022) e sistema de ensino já identificado
  por pesquisa manual (passo 19, 2% de cobertura até agora, crescente). A
  coluna `distrito` é o distrito real do Censo em São Paulo, mas no Rio de
  Janeiro (onde o Censo só preenche um valor degenerado, sempre "Rio de
  Janeiro") ela é substituída pela **Região Administrativa (RA)** oficial da
  Prefeitura/IPP — 33 RAs, mesmo nível de granularidade dos distritos de SP,
  mas com estatuto administrativo real (ao contrário da divisão informal em
  "zonas"). A coluna `granularidade_geo` deixa explícito qual é qual
  (`distrito` em SP, `regiao_administrativa` no RJ). Não inclui escolas do
  "Sistema S" (SESI/SENAI/SESC/SENAC) nem da PRÓPRIA rede Poliedro (achado
  24/07: 4 unidades próprias estavam entrando como leads — corrigido, ver
  `poliedro_09_icp_poliedro.py`). Peso do score_destaque aqui é PROVISÓRIO
  (75/15/5/5 — ENEM/infra/seletividade/inclusão), pendente de validação com
  o time Poliedro.
- `data/outputs/14_cidades_powerbi.csv` — as 318 cidades do recorte, com
  `rank_cidade` e uma coluna `top10` (verdadeiro/falso) pra filtrar rápido.

## 2. Importar no Power BI Desktop

1. Abra o Power BI Desktop (gratuito, se não tiver: `powerbi.microsoft.com/desktop`).
2. **Página Inicial → Obter Dados → Texto/CSV** → selecione `14_escolas_powerbi.csv` → Carregar.
3. Repita para `14_cidades_powerbi.csv`.

O CSV é gerado com separador `;` e decimal `,` (formato brasileiro) de
propósito — com a instalação do Power BI em Português (Brasil), ele reconhece
os números decimais (score, percentis) automaticamente ao importar, sem
precisar do passo manual "Alterar Tipo com Localidade" no Power Query. Se
você já tinha importado uma versão anterior do CSV e os números vieram
errados (tipo `9738` em vez de `0,9738`), apague as duas consultas em
**Transformar dados** e importe de novo do zero — não dá pra só "atualizar",
porque o tipo da coluna já ficou gravado errado na consulta antiga.

## 3. Criar o relacionamento

1. Vá na visualização **Modelo** (ícone de tabelas conectadas, barra lateral esquerda).
2. Arraste `codigo_municipio` da tabela `14_escolas_powerbi` até `codigo_municipio`
   da tabela `14_cidades_powerbi`. O Power BI detecta automaticamente
   cardinalidade **Muitos-para-um** (várias escolas por cidade) — confirme.

## 4. Visuais sugeridos

Na visualização **Relatório**, monte esta grade:

**Linha 1 — Cartões KPI** (visual "Cartão"):
- Contagem de linhas de `14_escolas_powerbi` = **1.127** (total Golden Leads)
- Filtre uma cópia por `segmento_comercial = Líder local` → **205**
- Filtre outra por `segmento_comercial = Desafiante (2º-5º local)` → **365**

**Linha 2 — Gráfico de barras** ("Gráfico de Colunas Clusterizadas"):
- Eixo: `nome_municipio_ibge` (tabela cidades), filtrado por `top10 = Verdadeiro`
- Valor: `score_priorizacao`
- Reproduz o slide 8 (Top10 cidades), mas interativo.

**Linha 3 — Tabela ou Matriz**:
- Colunas: `NO_ENTIDADE`, `cidade`, `UF`, `segmento_comercial`, `score_destaque`, `bairro`, `distrito`, `renda_categoria`, `sistema_ensino_identificado`
- Ordene por `score_destaque` decrescente.
- Essa é a visão que o time comercial mais vai usar no dia a dia. Em SP,
  `distrito` é o distrito real; no RJ, é a Região Administrativa (ver seção 7
  pra montar a página que separa SP por distrito e RJ por RA num mapa).

**Painel de segmentações (slicers)**, à esquerda ou acima de tudo:
- Slicer de `UF`
- Slicer de `cidade`
- Slicer de `segmento_comercial`

Com isso, clicar em "SP" no slicer de UF já filtra o mapa de barras, a tabela
e os cartões juntos — é exatamente o "sem depender de planilha" que o roadmap promete.

## 5. Sobre o mapa geográfico (atualizado 23/07)

Agora dá pra fazer mapa de pontos de verdade: `14_escolas_powerbi.csv` já
traz `LATITUDE`/`LONGITUDE` nativas do Censo (82% de cobertura). Use o visual
"Mapa" ou "Mapa Densidade" do Power BI, campo "Local" = `LATITUDE`/`LONGITUDE`
diretamente (não precisa geocodificação automática do Bing por nome). Cor por
`segmento_comercial` e tamanho por `score_destaque` funcionam bem aqui. As
18% sem lat/long (escolas onde o Censo não preencheu o campo) ficam de fora
do mapa, mas continuam na tabela normalmente.

## 6. Estética (opcional)

Pra manter a identidade do deck: Formatar → Tema → tema customizado com fundo
`#141B2C`, destaque `#D4AF37` (dourado), texto `#F5F7FA`. Não é obrigatório,
mas fica consistente com a apresentação se você for mostrar os dois juntos.

## 7. Página bônus — Renda x ENEM (SP/RJ), pedido pela recrutadora (23/07)

Objetivo: achar visualmente bairros/distritos de alta renda onde a Poliedro
ainda tem pouca presença (poucas Golden Leads) — candidatos a expansão por
prestígio de marca, não só por nota. Os dois exemplos que essa página já
revelou: VI Lagoa (Região Administrativa do RJ, renda mediana ~R$10.177,
5 Golden Leads) e, em SP, Itaim Bibi/Vila Leopoldina/Perdizes — renda alta,
poucas Golden Leads relativas ao potencial.

**Atualizado 24/07**: a coluna `regiao` deste CSV já vem no nível certo pra
cada cidade — distrito real em São Paulo, e **Região Administrativa (RA)**
oficial no Rio de Janeiro (não mais bairro cru). Antes, RJ tinha ~24-88
bairros individuais, muitos com 1-2 escolas só (ruído estatístico); a RA
agrupa isso em 33 regiões oficiais — mesma lógica dos distritos de SP,
"o que equivale aos distritos de São Paulo" segundo a própria definição da
RA. Se quiser conferir a divisão bairro → RA usada, está no dicionário
`RA_POR_BAIRRO_RJ` em `poliedro_15_regioes_sp_rj.py`.

**1. Importar o dado**: Página Inicial → Obter Dados → Texto/CSV →
`data/outputs/16_regioes_sp_rj_com_renda.csv` → Carregar. (Mesmo formato
brasileiro `;`/`,` dos outros CSVs — importa direto, sem passo manual.)

**2. Criar a página**: clique no "+" na barra de abas embaixo, renomeie pra
"Renda x ENEM (SP/RJ)".

**3. Montar o gráfico de dispersão**:
- Adicione o visual "Gráfico de Dispersão" (ícone de pontos espalhados, no
  painel de Visualizações).
- Campo **Eixo X**: `renda_mediana_responsavel`
- Campo **Eixo Y**: `enem_ponderado`
- Campo **Tamanho**: `qtd_escolas_elegiveis` (regiões com mais escolas
  aparecem como bolhas maiores)
- Campo **Legenda** (cor): `qtd_golden_leads` (ou `cidade`, se preferir
  separar visualmente São Paulo de Rio de Janeiro por cor)
- Campo **Detalhes**: `regiao` (aparece no tooltip ao passar o mouse — mostra
  o nome do distrito em SP ou da RA no RJ, ex. "XXIV Barra da Tijuca")

**4. Ler o gráfico**: o quadrante que interessa é **canto direito-inferior**
(renda alta no eixo X, ENEM baixo/médio no eixo Y) — são as regiões ricas
"não conquistadas academicamente ainda". Adicione um filtro de página
`amostra_significativa = Verdadeiro` (painel Filtros) pra tirar regiões com
menos de 3 escolas confiáveis, que são ruído estatístico.

**5. Opcional — linha de referência**: Formatar visual → Linhas de
referência → adicione uma linha vertical no valor médio de
`renda_mediana_responsavel` da cidade, pra dividir visualmente "bairro rico"
de "bairro não-rico" sem precisar decorar o número.

**Sobre escalar pra outras cidades**: já existe uma versão nacional,
`data/outputs/17_regioes_nacional_com_renda.csv` (318 cidades, ~81% de
match de renda) — mesma estrutura de colunas, o mesmo gráfico funciona só
trocando o CSV de origem. Ainda é uma primeira versão (ver docstring do
`poliedro_17_regioes_nacional_renda.py` pras limitações), recomendo revisão
amostral antes de usar em decisão comercial real.

## 8. Slicer de bairro/distrito dentro de São Paulo e Rio (pedido do Gui, 24/07)

Objetivo: no lugar de um slicer de cidade que só mostra "São Paulo" como uma
linha única, ter algo tipo "São Paulo - Itaim Bibi" / "São Paulo - Vila
Mariana", só com as combinações que realmente têm Golden Lead.

**Correção (24/07 — o Gui checou e eu errei o diagnóstico na primeira
versão deste guia)**: o slicer que você mostrou já usa `14_escolas_powerbi`
(o campo `cidade` de lá, junto com `UF` e `segmento_comercial` — todos
existem nessa tabela de FATO). Não é problema de tabela errada. O motivo
de mostrar só "São Paulo" como linha única é mais simples: o campo `cidade`
é só o nome da cidade, sem subdivisão nenhuma — não existe hoje nenhum
campo que já venha pronto tipo "São Paulo - Itaim Bibi". Cada distrito/RA
já está na coluna `distrito` (separada), só falta CRIAR um campo que
combine as duas coisas — é o que o passo a passo abaixo faz.

**Passo a passo:**

1. **Criar uma coluna combinada** (Power Query, não DAX, pra ficar mais
   simples): Dados/Transformar Dados → selecione a consulta
   `14_escolas_powerbi` → Adicionar Coluna → Coluna Personalizada → nome
   `cidade_regiao`, fórmula:
   ```
   if [cidade] = "São Paulo" or [cidade] = "Rio de Janeiro" then [cidade] & " - " & [distrito] else [cidade]
   ```
   Isso cria "São Paulo - Vila Mariana", "Rio de Janeiro - IV Botafogo" só
   pras duas cidades que têm subdivisão; as outras 316 continuam só com o
   nome da cidade (não faz sentido subdividir uma cidade com 1-2 leads).
2. Feche e Aplique (botão no canto superior esquerdo do Power Query).
3. Arraste um novo visual "Slicer" pro canvas, campo = `cidade_regiao` (da
   tabela `14_escolas_powerbi`, não da `14_cidades_powerbi`).
4. Esse novo slicer filtra `14_escolas_powerbi` diretamente; se seus outros
   visuais (tabela, cartões) também vierem dessa tabela, o filtro já
   propaga sozinho.

**Nota sobre bairro vs. distrito** — o seu exemplo mencionou "Jardim
Europa" e "Itaim Bibi": Itaim Bibi é distrito oficial de SP (aparece certo
na coluna `distrito`), mas Jardim Europa é um **bairro** dentro do distrito
Jardim Paulista/Pinheiros, não um distrito em si — não vai aparecer em
`distrito`, só em `bairro`. Se você quiser a granularidade de bairro (mais
fina, mais nomes reconhecíveis tipo "Jardim Europa") em vez de distrito
oficial (mais estável estatisticamente, menos linhas com 1 escola só),
troque `[distrito]` por `[bairro]` na fórmula acima — os dois campos
existem em `14_escolas_powerbi`, é só escolher qual granularidade prefere
pro slicer.

**Pergunta do Gui: `14_cidades_powerbi` também deveria ter bairro/distrito?**
Não — e vale explicar o porquê, é um conceito útil de modelagem. `14_cidades_powerbi`
é uma tabela de DIMENSÃO: 1 linha por município (318 linhas), usada pra
relacionar com `14_escolas_powerbi` via `codigo_municipio` numa cardinalidade
Muitos-para-Um (várias escolas apontam pra 1 cidade). Bairro/distrito é um
atributo de ESCOLA, não de cidade — se eu colasse bairro/distrito nessa
tabela, cada município passaria a ter várias linhas (uma por bairro), o que
quebra a premissa "1 linha = 1 cidade" que o relacionamento inteiro depende
pra funcionar direito (senão o Power BI não sabe mais somar direito os
totais por cidade). A regra geral: granularidade de bairro/distrito já
está no lugar certo, dentro de `14_escolas_powerbi` (cada linha é uma
escola, então bairro/distrito da escola faz sentido ali). Se um dia você
quiser um terceiro nível — uma tabela "1 linha por bairro/RA" com métricas
PRÓPRIAS de região (não de escola individual, tipo renda mediana e ENEM
ponderado do bairro inteiro) — isso já existe separado, é o
`16_regioes_sp_rj_com_renda.csv` (SP/RJ) ou `17_regioes_nacional_com_renda.csv`
(nacional) que usamos na Seção 7. Um bom dashboard usa as 3 tabelas juntas,
cada uma na sua granularidade certa, relacionadas entre si — não tenta
espremer tudo numa tabela só.

## 9. Solução de problemas — dado não atualiza / falta coluna / decimais errados

Se depois de reimportar `14_escolas_powerbi.csv` você não vê `distrito`
como RA no RJ, `sistema_ensino_identificado`, `rede_propria_poliedro`, ou o
`score_destaque` continua com 2 casas decimais, confira nesta ordem:

1. **O dado novo chegou no modelo?** Painel **Dados** (lado direito) →
   expanda a tabela `14_escolas_powerbi` → confira se as colunas aparecem
   na lista de campos. Se SIM (colunas existem no modelo, só não aparecem
   no visual): você só precisa arrastar o campo pra dentro do visual/tabela
   que está olhando — não é problema de dado, é de que o visual não usa
   aquela coluna ainda.
2. **Se as colunas NÃO aparecem no painel Dados**: o modelo está lendo uma
   versão antiga do arquivo. Excluir e recriar a conexão às vezes não basta
   porque o Power BI guarda os PASSOS aplicados (Origem, Tipo Alterado
   etc.) na consulta salva. Vá em **Transformar Dados** → clique na
   consulta `14_escolas_powerbi` → confira o passo **Origem** (primeiro da
   lista, ícone de engrenagem) → o caminho do arquivo bate com
   `data/outputs/14_escolas_powerbi.csv` mesmo? Se sim, clique com botão
   direito na consulta → **Atualizar Visualização Prévia** e depois
   **Página Inicial → Fechar e Aplicar**. Se o caminho estiver errado
   (apontando pra uma cópia antiga em outra pasta), corrija ali.
3. **`score_destaque` com 2 casas decimais mesmo com o dado certo**: isso
   quase sempre é FORMATAÇÃO DE EXIBIÇÃO, não o dado em si (o CSV já vem
   com 3 casas — confirmei rodando o script de novo, os valores estão lá).
   Existem DOIS lugares onde essa formatação pode estar travada em 2 casas
   — o visual costuma vencer o modelo, então cheque os dois:

   **a) No MODELO** (afeta todos os visuais que usarem a coluna, é o
   padrão): clique na aba **Modelagem** (barra superior) → no painel
   **Dados** (direita), clique na tabela `14_escolas_powerbi` pra expandir
   e clique no campo **`score_destaque`** — atenção pra selecionar essa
   coluna específica, não `renda_mediana_responsavel` por engano (isso
   muda a faixa/ribbon de cima pra "Ferramentas de Coluna"). Nessa faixa:
   campo **Formato** (mostra "Geral" por padrão) → troque pra **"Número
   Decimal Fixo"** — só depois disso o controle **Casas decimais** (que
   mostra "Auto") fica editável; clique na seta pra cima até chegar em 3,
   ou digite 3 direto no campo.

   **b) No VISUAL específico** (sobrescreve o modelo SÓ nesse gráfico/
   tabela — é provavelmente o seu caso, já que você viu 2 casas numa tabela
   específica): clique no visual (tabela) pra selecioná-lo → no painel
   **Visualizações** (direita), ícone de pincel/formato (parece um rolo de
   pintura) → **Formatar visual** → seção **Valores** (pode estar dentro de
   "Células" dependendo da versão) → expanda e procure `score_destaque` →
   campo **Casas decimais** → mude pra 3. Se você formatou manualmente essa
   tabela antes (comum, principalmente com Copilot/sugestão automática do
   Power BI), é bem provável que o valor "2" esteja fixado bem aqui, não no
   modelo.

## 10. Primeira aba do dashboard executivo — quais colunas manter

Pergunta do Gui: quantas/quais colunas deixar na tabela principal da
primeira página. Regra geral pra dashboard executivo: quem olha (gestor,
supervisor) quer decidir rápido "essa escola é prioridade ou não", não ler
todo o dado bruto — cada coluna a mais é um pouco mais de tempo pra achar o
que importa. Recomendo 9 colunas, cada uma respondendo uma pergunta
específica de quem for usar:

| # | Coluna | Por que está na lista |
|---|---|---|
| 1 | `NO_ENTIDADE` | Identifica a escola — óbvio, mas é a única coluna que não dá pra cortar. |
| 2 | `cidade` (ou `cidade_regiao`, se criar a coluna da Seção 8) | Onde fica — primeiro filtro mental de quem olha. |
| 3 | `UF` | Agrupamento regional rápido (times comerciais costumam ser organizados por estado/região). |
| 4 | `segmento_comercial` | A tese comercial em 1 palavra: Líder local, Desafiante, Outras posições — decide a ABORDAGEM de venda, não só o "quão boa é a escola". |
| 5 | `score_destaque` | O número que resume tudo (ENEM+infra+seletividade+inclusão) — ordenação padrão da tabela. |
| 6 | `bairro` | Granularidade fina pra quem já conhece a cidade (SP/RJ principalmente). |
| 7 | `renda_mediana_responsavel` | **Atualizado 24/07 (concordo com o Gui)**: mais preciso que `renda_categoria` — a categoria agrupa em 4 faixas largas (ex. R$ 5.001 e R$ 10.001 caem os dois em "Alta", perdendo a diferença real). O número bruto discrimina melhor entre bairros que a categoria empata. Formate como Moeda (R$) na coluna pra ficar legível sem casas decimais desnecessárias. `renda_categoria` continua útil como filtro/slicer rápido ou cor condicional, só não como coluna fixa da tabela executiva. |
| 8 | `sistema_ensino_identificado` | A pergunta mais prática pro time comercial: "essa escola já usa concorrente, é livre, ou já é nossa?" — literalmente decide se vale ligar. |
| 9 | `rede_propria_poliedro` | Flag booleana rápida pra não ligar acidentalmente pra uma unidade que já é Poliedro — mais direto que ler o texto de `sistema_ensino_identificado`. |

**Deixaria de fora da primeira aba** (mas mantidas na tabela de dados, só
não na visão executiva): `codigo_escola`/`codigo_municipio` (chaves
técnicas, ruído visual pra quem não vai fazer join manual),
`score_priorizacao_cidade` (é sobre a CIDADE, não a escola — já implícito
no ranking de UF/cidade), `granularidade_geo` (é metadado explicando a
coluna `distrito`, não um dado em si — bom pra tooltip, não pra coluna
fixa), `confianca` (relevante só quando alguém for confirmar uma pesquisa
específica, não pra visão rápida), `cep`/`LATITUDE`/`LONGITUDE` (usadas no
mapa, não na tabela).

Se quiser reduzir mais ainda pra caber na tela sem rolar (dashboards
executivos costumam ter 5-6 colunas), tiraria `bairro` e `UF` primeiro —
`cidade` e `segmento_comercial` já cobrem a localização/prioridade
essencial, e quem quiser o detalhe fino pode clicar na linha ou usar o
slicer da Seção 8.
