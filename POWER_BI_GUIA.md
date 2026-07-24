# Guia — Dashboard Power BI (roadmap 2.0)

Objetivo (mesmo do slide 18): painel interativo com filtros por UF, cidade e
segmento comercial, pra o time comercial explorar as Golden Leads sem depender
de planilha ou slide fixo. Isso já monta o essencial em ~20-30min.

## 1. Dado pronto

Rode `python poliedro_14_consolidar_dataset_powerbi.py` (depende dos passos 01,
04, 09 e 11 já terem rodado). Gera duas tabelas:

- `data/outputs/14_escolas_powerbi.csv` — 969 Golden Leads, 1 linha por escola,
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
- Contagem de linhas de `14_escolas_powerbi` = **969** (total Golden Leads)
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
