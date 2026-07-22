# Guia — Dashboard Power BI (roadmap 2.0)

Objetivo (mesmo do slide 18): painel interativo com filtros por UF, cidade e
segmento comercial, pra o time comercial explorar as Golden Leads sem depender
de planilha ou slide fixo. Isso já monta o essencial em ~20-30min.

## 1. Dado pronto

Rode `python poliedro_14_consolidar_dataset_powerbi.py` (depende dos passos 01,
04, 09 e 11 já terem rodado). Gera duas tabelas:

- `data/outputs/14_escolas_powerbi.csv` — 869 Golden Leads, 1 linha por escola,
  com cidade, UF, segmento comercial, score, e bairro/CEP onde já geocodificado
  (167 das 869 — as demais ficam em branco nessas duas colunas, não é erro).
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
- Contagem de linhas de `14_escolas_powerbi` = **869** (total Golden Leads)
- Filtre uma cópia por `segmento_comercial = Líder local` → **193**
- Filtre outra por `segmento_comercial = Desafiante (2º-5º local)` → **330**

**Linha 2 — Gráfico de barras** ("Gráfico de Colunas Clusterizadas"):
- Eixo: `nome_municipio_ibge` (tabela cidades), filtrado por `top10 = Verdadeiro`
- Valor: `score_priorizacao`
- Reproduz o slide 8 (Top10 cidades), mas interativo.

**Linha 3 — Tabela ou Matriz**:
- Colunas: `NO_ENTIDADE`, `cidade`, `UF`, `segmento_comercial`, `score_destaque`, `bairro`
- Ordene por `score_destaque` decrescente.
- Essa é a visão que o time comercial mais vai usar no dia a dia.

**Painel de segmentações (slicers)**, à esquerda ou acima de tudo:
- Slicer de `UF`
- Slicer de `cidade`
- Slicer de `segmento_comercial`

Com isso, clicar em "SP" no slicer de UF já filtra o mapa de barras, a tabela
e os cartões juntos — é exatamente o "sem depender de planilha" que o roadmap promete.

## 5. Sobre o mapa geográfico (limitação atual)

Não incluí um visual de mapa de pontos porque **não temos latitude/longitude**
— só bairro (texto) e CEP. O visual "Mapa" do Power BI consegue plotar por UF
(nome do estado) usando geocodificação automática do Bing, então dá pra fazer
um mapa de calor por estado se quiser. Bairro no mapa de verdade só com
lat/long — isso está no roadmap 3.0 (setor censitário IBGE via geopandas),
ainda não feito.

## 6. Estética (opcional)

Pra manter a identidade do deck: Formatar → Tema → tema customizado com fundo
`#141B2C`, destaque `#D4AF37` (dourado), texto `#F5F7FA`. Não é obrigatório,
mas fica consistente com a apresentação se você for mostrar os dois juntos.
