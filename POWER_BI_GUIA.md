# Guia Power BI — Case Poliedro

Formato: `Visual > Campo > Onde > Ação`. Se a tela não bater, pare e mande print.

---

## Norte do projeto — 3 perguntas, 3 páginas

O case pergunta uma coisa só: **"onde o Poliedro deveria construir share de prestígio?"**. As 3 páginas respondem essa pergunta em 3 etapas de decisão — não são 3 dashboards soltos, são 3 passos da mesma história.

| Página | Pergunta de negócio | O que resolve no case |
|---|---|---|
| 1 — Visão Executiva | Onde investir? | **Parte 1** do case: 10 cidades prioritárias, metodologia justificada |
| 2 — Inteligência Comercial | Como entrar em SP/RJ? | Não pedido pelo case — mas é a prioridade de negócio que você ouviu na reunião (Poliedro quer entrar forte nesses 2 mercados) e o maior diferencial analítico do projeto |
| 3 — Ranking de Escolas Prioritárias | Quais escolas, e como pesquisar qualquer uma? | **Parte 2** do case (top escolas por cidade, ≥2 critérios) + exploração livre + resumo de metodologia |

Revisão 06/08: reordenei depois de comparar com um segundo parecer (Gemini) e com o seu reforço de que SP/RJ é prioridade explícita de negócio, não só uma descoberta lateral — ver "Sobre os pareceres do GPT e do Gemini" mais abaixo pra entender a mudança de posição em relação à versão anterior deste guia (que tinha Inteligência Comercial na página 3).

Frase de abertura sugerida (adapte pra sua voz, não decore): *"O desafio era identificar onde o Poliedro deveria construir share de prestígio. Transformei isso em um processo de decisão em 3 níveis: primeiro os mercados prioritários — cidades —, depois onde concentrar esforço nos 2 maiores mercados do país — SP e RJ, por distrito/bairro —, e por fim as instituições específicas pra prospectar, com uma ferramenta de exploração completa."*

⚠️ Só 3 páginas de dashboard. Um "Roadmap/Metodologia" completo (pesos, fontes, limitações) **não é uma 4ª página** — vira o documento escrito, entrega separada da apresentação. Dentro do dashboard, a página 3 tem só um resumo curto da metodologia (card), não o documento inteiro — ver seção da página 3. Resista à tentação de criar mais abas: com 10 minutos de apresentação, 3 páginas bem feitas comunicam mais do que 5 páginas rasas.

### O achado SP/RJ — números reais pra defender na banca

Pergunta óbvia de Q&A: "cadê São Paulo e Rio no top 10?". Responda com dado, não com desculpa:

| Cidade | Rank nacional | Score final | Percentil volume de escolas | Percentil socioeconômico | Percentil qualidade ENEM |
|---|---|---|---|---|---|
| Rio de Janeiro | 19º | 0,8408 | 0,997 (quase máximo) | 0,950 | **0,540 — o mais baixo dos 3** |
| São Paulo | 29º | 0,8116 | 1,000 (máximo) | 0,953 | **0,435 — o mais baixo dos 3** |

As duas cidades têm o melhor volume de escolas elegíveis do país (465 e 603) e socioeconômico alto — o que derruba o score é só o percentil de qualidade ENEM. Motivo: esse indicador é uma média da cidade inteira; com 400-600 escolas de qualidade muito heterogênea, os polos de excelência ficam diluídos entre um mar de escolas medianas. É limitação estrutural de qualquer score agregado por cidade grande, não bug do pipeline. A página 2 (Inteligência Comercial) existe justamente pra não perder esses dois mercados: troca a unidade de análise de "cidade" pra "bairro/distrito", onde a diluição não acontece.

### Sobre os pareceres do GPT e do Gemini

Os dois convergem no essencial, o que é sinal forte de que a leitura está certa: separar "o que o case pediu" do "o que você descobriu além", e não esconder o achado SP/RJ — transformar em mérito, com número. Ambos concordam também que uma 4ª aba de puro texto ("Roadmap") desperdiça espaço de dashboard.

Onde eles discordam entre si — e a decisão tomada aqui:

- **GPT** botava Escolas Prioritárias na página 2 e Inteligência Comercial (SP/RJ) na página 3, como "bônus" no fim. **Gemini** botava Inteligência Comercial na página 2, argumentando que é a pergunta mais urgente pro negócio agora. Fiquei com a ordem do Gemini porque você confirmou que SP/RJ é prioridade explícita da liderança, não só uma descoberta sua — quando existe um sinal de negócio real (não um palpite de IA), ele pesa mais que uma convenção genérica de "o que o case pediu primeiro vem primeiro". A Parte 2 do case continua obrigatória e continua na página 3, só não abre a apresentação.
- **GPT** sugeriu documentar a metodologia só como texto separado. **Gemini** sugeriu um painel/card dentro do dashboard. Os dois têm razão em coisas diferentes: o case pede uma "metodologia documentada" como entrega — isso é objeto arquivável, citável, que um avaliador relê depois; um card dentro do Power BI não substitui isso. Mas na hora da fala, ninguém vai abrir um PDF no meio da demonstração — um resumo curto na tela ajuda a responder perguntas ao vivo. Fiz as duas coisas: o documento completo é a entrega oficial, o card na página 3 é um atalho de consulta durante a apresentação.
- **GPT** sugeriu Top 20 escolas por cidade na tabela principal. Isso não serve como resposta final da Parte 2 (o case pede 5, não 20) — mantido como estava: a tabela completa/exploratória pode mostrar quantas você quiser (inclusive menos de 20, cidades pequenas não têm 20 escolas elegíveis — comportamento normal de qualquer filtro Top N), mas o visual que responde formalmente a Parte 2 fica travado em 5.
- **Ambos sugeriram um "Score Comercial" novo combinando renda + distância + sistema + cliente.** Não implementei agora — um score novo, com pesos definidos às pressas faltando ~2 dias, quebra a própria regra que seguimos o projeto inteiro (toda métrica de score precisa de peso justificado, não arbitrário). Se sobrar tempo depois de fechar o essencial, dá pra revisitar; até lá, a página 3 deixa as colunas separadas (renda, distância, sistema, cliente) pro time comercial ordenar/filtrar manualmente — mais lento, mas 100% defensável numa pergunta de banca.

---

## Página 1 — Visão Executiva (Onde investir?)

**Renomear página:** aba "Página 1" > clique, espere 1s, clique de novo > `Visão Executiva`

### Segmentações
Visual = **Segmentação de Dados** (não "Segmentação de Lista Versão Prévia" — essa não tem modo Suspenso).
Cada uma: arrastar campo > canto superior direito do visual > **Suspenso**.

| # | Campo | Config extra |
|---|---|---|
| 1 | `produto_alvo` | marcar só "Poliedro" |
| 2 | `UF` | — |
| 3 | `cidade` | — |
| 4 | `segmento_comercial` | — |

### Cartões
Visual = **Cartão** (não "KPI", não "Cartão Múltiplo"). Passo fixo: arrastar `codigo_escola` > caixinha "Dados do cartão" > seta ao lado do campo > **Contagem**.

| # | Rótulo | Filtro **neste visual** | Esperado |
|---|---|---|---|
| 1 | Total | nenhum | 1.127 |
| 2 | Líder local | `segmento_comercial` = Líder local | 210 |
| 3 | Desafiante | `segmento_comercial` = Desafiante (2º-5º local) | 405 |
| 4 | Cliente Poliedro | `ja_cliente_poliedro_qualquer_marca` = Verdadeiro | 62 |

⚠️ O filtro tem que estar em **"Filtros neste visual"** (cartão selecionado), nunca em "Filtros nesta página" — senão os 4 cartões ficam presos ao mesmo filtro.

Rótulo de cada cartão: Inserir > Caixa de texto > nome > posicionar em cima do cartão.

### Gráfico Top 10 cidades
Gráfico de Colunas Clusterizadas > tabela `14_cidades_powerbi` > Eixo X `nome_municipio_ibge` > Valores `score_priorizacao` > Filtros neste visual: `top10` = Verdadeiro

### Mapa
Mapa (não "Mapa de Densidade"/"Coroplético"/"ArcGIS") > Local: `LATITUDE` + `LONGITUDE` > Legenda: `segmento_comercial` > Tamanho: `score_destaque`

**Por que LATITUDE/LONGITUDE aparecem no tooltip mesmo sem eu arrastar pra lá:** o Power BI mostra automaticamente, no tooltip padrão, TODOS os campos usados em qualquer caixinha do visual — como estão em "Local", entram de graça no tooltip. Não tem um botão "esconder só esse campo do tooltip"; a única forma garantida de controlar exatamente o que aparece é criar uma **página de tooltip customizada**:

1. Clique no **"+"** pra criar uma página nova > renomeie pra `Tooltip Mapa`.
2. Com a página selecionada (nenhum visual nela) > painel **Formatar página** (ou clique na área vazia > Formato) > seção **"Tipo de página"** > troque de "Personalizado" pra **"Dica de Ferramenta"**. A página encolhe pro tamanho certo.
3. Nessa página, crie um **Cartão Múltiplo** (ou 2 Cartões separados) com `NO_ENTIDADE` e `endereco_completo` — só o que você quer mostrar.
4. Volte pra página do mapa > clique no mapa > painel Visualizações > ícone de pincel "Formatar visual" > seção **"Dicas de ferramentas"** > campo **"Tipo"**: troque de "Padrão" pra **"Relatório da página"** > campo **"Página"**: escolha `Tooltip Mapa`.
5. Teste passando o mouse numa bolha — agora só aparece o que você desenhou na página de tooltip, sem LATITUDE/LONGITUDE.

### Tabela principal
Tabela (não "Matriz") > Colunas nesta ordem: `NO_ENTIDADE`, `cidade`, `UF`, `segmento_comercial`, `score_destaque`, `sistema_ensino_identificado`, `ja_cliente_poliedro_qualquer_marca`, `distancia_parceiro_atual_km`, `renda_mediana_responsavel` > clique cabeçalho `score_destaque` 2x (decrescente)

### Formatar colunas
Painel Dados > tabela `29_universo_completo_powerbi` > coluna `score_destaque` > aba **Ferramentas de Coluna** > Formato > **Número Decimal Fixo** > Casas decimais **3**
Repita para `renda_mediana_responsavel` > Formato > **Moeda**

### Gráfico de Rosca — Sistema de Ensino (confirmados)
Gráfico de Rosca > Legenda: `sistema_ensino_top_outros` > **Valores: arraste `codigo_escola` pra essa caixinha (sem isso o gráfico fica em branco — é o erro mais comum aqui, Legenda sozinha não desenha nada)** > seta ao lado do campo em Valores > **Contagem** > Filtros neste visual: `confianca` = **confirmado**.

Por que `sistema_ensino_top_outros` e não `sistema_ensino_identificado`: o campo bruto tem ~56 valores distintos, ilegível num gráfico de rosca. Esse campo já vem pronto do pipeline agrupando tudo abaixo de 25 escolas confirmadas em **"Outros (sistema minoritário)"** — ajuste o limiar em `LIMIAR_SISTEMA_ENSINO_GRAFICO` no `poliedro_29...py` se quiser mais/menos fatias.

### Modo de Análise — Golden Leads x Outras Escolas (revisado 09/08 — bookmark trocado por tabela-ponte)
**Substituído pelo mesmo motivo do slicer em Bloco da página 3: o mecanismo de Indicadores (bookmark) de página inteira dá erro/quebra silenciosamente se qualquer visual da página mudar depois — o Gui pediu pra trocar por algo 100% dirigido a dado, sem bookmark, com 2 blocos reais mostrando os números certos ("Golden Leads (1.127)" e "Outras Escolas (4.444)").**

⚠️ Por que isso não dá numa coluna comum da tabela 29 (1ª tentativa, coluna `segmento_golden_lead` que ainda existe lá — inofensiva, não usada mais): pra o bloco "Outras Escolas" mostrar honestamente 4.444 (todo mundo, Golden Leads incluídas), uma escola Golden Lead precisa aparecer em **duas** categorias ao mesmo tempo. Uma coluna só dá 1 valor por linha — mesmo problema estrutural do Top 5/Top 10/Demais escolas, resolvido com o mesmo mecanismo: **tabela-ponte**.

Nova tabela: `poliedro_29c_golden_leads_bridge.py` → `data/outputs/29c_golden_leads_bridge.csv`. TODA escola ganha 1 linha `"Outras Escolas (4.444)"`; só as Golden Leads ganham uma 2ª linha extra `"Golden Leads (1.127)"` (escola comum aparece 1x, Golden Lead aparece 2x — 5.571 linhas no total). Já rodei e validei (4.444 cobertas em "Outras Escolas", 1.127 em "Golden Leads", batendo com `produto_alvo == 'Poliedro'`).

**Configuração (mesma mecânica do 29b/página 3):**

1. Obter Dados > Texto/CSV > `29c_golden_leads_bridge.csv` (pasta `data/outputs/`) > Carregar, sem Transformar Dados.
2. Ícone **Modelo** > arraste `codigo_escola` de `29_universo_completo_powerbi` até `codigo_escola` de `29c_golden_leads_bridge` > cardinalidade **"Um-para-muitos"** (29 = um, ponte = muitos) > **Direção do filtro: "Ambas"** (não "Único").
3. Painel Dados > tabela `29c_golden_leads_bridge` > coluna `segmento_golden_lead` > aba Ferramentas de Coluna > **Ordenar por Coluna** > `segmento_ordem` — sem isso os blocos aparecem em ordem alfabética ("Golden Leads" depois de "Outras Escolas", ordem errada).
4. Apague os 4 botões antigos "🟡 Golden Leads (1.127)" / "🔵 Outras Escolas (4.444)" (topo da página, dois pares sobrepostos) — clique em cada um, Delete.
5. Inserir > Segmentação de dados > arraste `segmento_golden_lead` **da tabela `29c_golden_leads_bridge`** (não da coluna homônima em `29_universo_completo_powerbi`) pro campo.
6. Formatar visual > Geral > Estilo do segmentador de dados > **Bloco**. Pra ficar lado a lado (não empilhado): Formatar visual > **Configurações da segmentação de dados** > subseção **Grade** > `Colunas` = **2**, `Linhas` = **1**; redimensione o visual mais largo que alto.
7. Abra Ferramentas de Exibição (aba Modelagem/Página Inicial) > **Editor de Bookmarks** (Indicadores) > apague os 2 indicadores "Golden Leads" e "Outras Escolas" — não são mais usados por nenhum visual.
8. Teste: clique em "Golden Leads (1.127)" (deve filtrar mapa/tabelas pra 1.127); clique em "Outras Escolas (4.444)" (deve mostrar as 4.444, Golden Leads incluídas). Se algum bloco trouxer número errado, o relacionamento provavelmente ficou "Único" em vez de "Ambas" (passo 2).
9. Reordenar segmentações no canvas: `segmento_golden_lead` > `UF` > `cidade` > `sistema_ensino_identificado` > `ja_cliente_poliedro_qualquer_marca` > `segmento_comercial`.
10. Título da página > caixa de texto > `Visão Executiva — Onde Investir?`

*(correção 06/08: essa caixa de título estava com o nome errado — "Inteligência Comercial", que hoje é o título da página 3, não da 1. Se o seu arquivo ainda tem o texto antigo, corrija.)*

### Botão "Limpar filtros" (Reset, nativo — sem bookmark)

Inserir > Botões > escolha um formato simples > redimensione/posicione num canto (ex.: perto dos slicers) > selecione o botão > painel Formatar botão > **Ação** > **Tipo**: **"Limpar todas as segmentações"** (não confundir com "Aplicar todas as segmentações de dados", que faz o oposto) > **Ativar** = Ativado. Renomeie o rótulo do botão pra "Limpar filtros" (Formatar botão > Rótulo do texto > Texto). Mecanismo 100% nativo do Power BI — sem bookmark, não quebra se um visual novo for adicionado depois. Já configurado e testado nas páginas 1 e 3.

Ctrl+S

---

## Página 2 — Inteligência Comercial (Como entrar em SP/RJ?)

Era a antiga "Página 2 — Renda x ENEM" — **mantém a posição 2**, só o título/enquadramento mudou (ver "Norte do projeto" acima). Não responde ao case (não foi pedida) — é o insight que você descobriu e que a liderança confirmou como prioridade real: bairros ricos com pouca cobertura Poliedro em SP/RJ (ver "O achado SP/RJ" no topo deste guia). Vem em 2º lugar porque é a pergunta mais urgente pro negócio agora, não porque é a resposta formal do case.

Nova página (**+**) > renomear `Inteligência Comercial`

Filtros nesta página: `amostra_significativa` (tabela `16_regioes_sp_rj_com_renda`) = Verdadeiro

**Gráfico de Dispersão** > tabela `16_regioes_sp_rj_com_renda` > Eixo X `renda_mediana_responsavel` > Eixo Y `enem_ponderado` > Tamanho `qtd_escolas_elegiveis` > Legenda `qtd_golden_leads` > **Valores** `regiao`

⚠️ **Cor do gradiente da Legenda (`qtd_golden_leads`) — Resumo tem que ser Média, não Contagem nem Soma (achado 12/08).** Como cada bolha (região) já é um grupo único de `qtd_golden_leads` idêntico dentro dela, qualquer agregação não-soma/não-contagem devolve o mesmo valor correto — mas Contagem conta quantas LINHAS caem naquele valor (0 fica "no máximo" por ser o mais comum, errado) e Soma multiplica o valor pelo tamanho do grupo (valores medianos ficam inflados sobre extremos raros, errado). Formatar visual > campo `qtd_golden_leads` na Legenda > seta > **Média** (ou Mínimo/Máximo, equivalentes aqui — nunca Contagem/Soma).

⚠️ **Sem campo em Valores, o gráfico agrupa errado** (uma bolha por combinação de Legenda, não por região) — o visual novo de Dispersão renomeou o antigo campo "Detalhes" pra "Valores". `regiao` sozinho já é único aqui (confirmado: nenhum nome se repete entre SP e RJ nos dados atuais).

Leitura: quadrante inferior direito (renda alta, ENEM baixo/médio) = bairro rico com pouca presença Poliedro.

**Slicer de cidade:** Segmentação de Dados > campo `cidade` > Estilo **Bloco** (só 2 valores — São Paulo/Rio de Janeiro — vira 2 botões lado a lado, mais rápido que dropdown) > posicionar acima do gráfico/tabela. Sem escopo especial: por padrão afeta todos os visuais da página que usam essa tabela (dispersão, tabela de regiões prioritárias e a nova tabela de escolas por região, todas juntas), que é o comportamento que você quer aqui.

**Por que `enem_ponderado` usa MÉDIA (ponderada) e não mediana:** renda usa mediana porque a distribuição de renda é enviesada — uma família muito rica distorce a média de um bairro pequeno, não distorce a mediana (mesmo motivo documentado no `poliedro_16`). ENEM não tem esse problema (nota é limitada a 0-1000, sem "outlier bilionário") — o risco aqui é outro: escola pequena (5 participantes) puxando o número tanto quanto escola grande (300 participantes) se você tirasse uma média/mediana simples entre escolas. Por isso `enem_ponderado` pondera pela quantidade de participantes de cada escola (`poliedro_15`, função `media_ponderada`) — informação que uma mediana jogaria fora. Resumindo: mediana é a ferramenta certa pra "elimina outlier", ponderação é a ferramenta certa pra "elimina distorção de amostra pequena" — são problemas diferentes, cada métrica usa a solução certa pro problema dela.

### Caixa de texto — leitura guiada
Inserir > Caixa de texto, ao lado/abaixo do gráfico:

> **Como ler:** cada bolha é uma região (distrito em SP, bairro no RJ). Eixo X = renda mediana do responsável (mais à direita = bairro mais rico). Eixo Y = ENEM ponderado (mais pra cima = nota mais alta). Tamanho = quantidade de escolas elegíveis na região. Cor = quantas Golden Leads já existem ali.
> **Quadrante de oportunidade:** direita (renda alta comparada com o resto da própria cidade — SP e RJ são comparados separadamente, não misturados). ENEM não entra nesse critério — nota da região não é sinal de oportunidade comercial por si só.

### Tabela — Regiões prioritárias
Tabela > tabela `16_regioes_sp_rj_com_renda` > colunas: `cidade`, `regiao`, `renda_mediana_responsavel`, `qtd_golden_leads`, `distancia_parceiro_mais_proximo_km` > **sem filtro fixo** neste visual > ordenar por `renda_mediana_responsavel` decrescente

⚠️ **Revisão 12/08 — filtro `regiao_oportunidade = Verdadeiro` removido deste visual** (versão anterior deste guia recomendava mantê-lo). Motivo: esse filtro escondia por completo qualquer região de renda abaixo da mediana da própria cidade — inclusive bairros bem posicionados no ranking ENEM (ex.: Santa Cruz, Bangu, Realengo, Campo Grande, Jardim Carioca, Curicica no RJ). O Gui apontou que uma recrutadora deveria poder ver escolas de qualquer bairro top-10 no ENEM da cidade, independente de renda, pra prospecção manual — renda alta é só um dos sinais, não um pré-requisito de visibilidade. `regiao_oportunidade` continua existindo como coluna (pode ser adicionada à tabela ou usada num slicer opcional), só não gate mais o visual.

O que é `regiao_oportunidade`: coluna calculada no pipeline (`poliedro_16_renda_bairro_distrito.py`), não em DAX — sinaliza região com `renda_mediana_responsavel` acima da mediana das regiões elegíveis **da mesma cidade** (mediana de SP e mediana do RJ calculadas separadamente — correção do Gui em 05/08, a versão anterior misturava as duas e sub-representava o RJ). Ver docstring da função `marcar_regiao_oportunidade` pra critério completo.

### Tabela — Escolas da região selecionada

Gap real, apontado pelo Gui em 06/08: quem clica numa bolha/linha de região sabia que ali era promissor, mas precisava voltar pra página 1 e filtrar manualmente pra ver quais escolas existem ali. Causa raiz: `29_universo_completo_powerbi` (nível escola) e `16_regioes_sp_rj_com_renda` (nível região) nunca tiveram relacionamento no modelo — sem relacionamento, clique num visual de uma tabela nunca filtra visual de outra tabela, é comportamento normal do Power BI, não bug de configuração.

Correção 06/08 (feita no pipeline, não em DAX): as duas tabelas agora exportam uma coluna `chave_regiao` (`cidade + "|" + regiao`, ex. `"São Paulo|Moema"`) — já está nos CSVs depois de rodar `poliedro_29` e `poliedro_16`/`poliedro_16b` de novo. Falta só criar o relacionamento no Power BI Desktop:

1. Ícone **Modelo** (barra lateral esquerda) > arraste `chave_regiao` de `29_universo_completo_powerbi` até `chave_regiao` de `16_regioes_sp_rj_com_renda`.
2. Confirme cardinalidade **"Muitos-para-um"** (29 = muitos, 16 = um) e direção do filtro **"Único"** (16 → 29 — região filtra escola, não o contrário; não marque "Ambos").
3. Volte pra página Inteligência Comercial > Tabela nova > tabela `29_universo_completo_powerbi` > colunas: `NO_ENTIDADE`, `regiao`, `score_destaque`, `sistema_ensino_identificado`, `ja_cliente_poliedro_qualquer_marca`, `distancia_parceiro_atual_km` — **sem filtro fixo nenhum**. Clicar numa bolha do gráfico de dispersão ou numa linha da tabela de regiões prioritárias agora filtra essa tabela sozinho, via interação cruzada padrão (o relacionamento é o que faz isso funcionar).

⚠️ **Use `regiao`, não `bairro`, como coluna de exibição (achado 12/08).** As duas existem na tabela 29 e normalmente coincidem, mas não sempre: `bairro` é o campo bruto do Censo (endereço postal), `regiao` é o campo geocodificado usado no relacionamento (`chave_regiao`) e no agrupamento da tabela 16. Exemplo real: duas escolas "Sao Luis Colegio" têm `bairro = VILA MARIANA` nas duas, mas `regiao` diferente (Moema numa, Jardim Paulista na outra) — se a coluna exibida for `bairro`, uma escola pode aparecer "no bairro errado" quando você clica numa região específica, porque o filtro usa `regiao` mas o rótulo mostra `bairro`. Se em algum momento você importar a tabela de novo do zero e essa coluna reverter para `bairro`, troque de volta.
4. Se você tinha adicionado campos avulsos em "Filtros neste visual" dessa tabela antes (ex. `bairro` ou `NO_ENTIDADE` como "é Tudo") pra tentar simular esse comportamento manualmente, remova — com o relacionamento certo eles não fazem mais nada.

⚠️ **Cobertura real, não escondida:** rodando o pipeline atualizado, 98,7% das 841 escolas de SP+RJ casam com uma região da tabela 16. 9 bairros do Rio (Cosme Velho, Jardim Botânico, Praça da Bandeira, Grajaú, Penha, Glória, Encantado, Saúde, Gamboa) não têm linha correspondente em `16` — provavelmente porque o Censo IBGE de renda não cobre esses bairros na granularidade usada, ou porque `poliedro_15` não teve escola confiável suficiente ali pra virar linha. Escolas nesses 9 bairros continuam aparecendo normalmente na página 1/3, só não aparecem quando você filtra por região nesta página. Se quiser fechar esse gap, o próximo passo é investigar esses 9 nomes especificamente no arquivo de renda do IBGE — não fiz isso agora pra não atrasar a sincronização principal.

Ctrl+S

---

## Página 3 — Ranking de Escolas Prioritárias (Quais escolas? + metodologia)

Era a antiga "Página 3 — Explorador Completo", depois "Escolas Prioritárias & Explorador" — renomeada em 12/08 (nome anterior avaliado como ruim pelo Gui). Reúne 3 coisas na mesma página: a resposta curada da Parte 2 do case, a exploração livre de qualquer escola, e um resumo curto de metodologia pra consulta durante a apresentação.

Segmentação de Dados x2 (`29_universo_completo_powerbi`): `cidade`, `produto_alvo` — aqui deixe **"Selecionar tudo"** marcado (diferente da página 1).

**Tabela (modo exploração completa)** > colunas nesta ordem: `NO_ENTIDADE`, `rank_municipio`, `segmento_comercial`, `produto_alvo`, `score_destaque`, `QT_MAT_MED`, `indice_infra`, `distancia_parceiro_atual_km`, `nome_parceiro_mais_proximo`, `sistema_ensino_identificado` > ordenar por `rank_municipio` crescente

Uso: ver a posição real de qualquer escola, mesmo `produto_alvo = nenhum`. Sinal de expansão: `distancia_parceiro_atual_km` alto + `renda_mediana_responsavel` alta.

### Slicer em Bloco — Top 5 / Top 10 / Demais escolas

Pedido do Gui (07/08): um slicer em Bloco pra filtrar a tabela de exploração por faixa de `rank_municipio`, com comportamento **cumulativo** — clicar "Top 10" tem que trazer as escolas 1 a 10 (já incluindo o Top 5), não só as 6ª-10ª; clicar "Demais escolas" tem que trazer TODAS as escolas pesquisadas, não só quem ficou fora do Top 10.

⚠️ **Por que isso não dá pra fazer com uma coluna categórica simples** (a 1ª tentativa, `faixa_rank_cidade` na tabela `29_universo_completo_powerbi`): uma coluna categórica dá só UM valor por escola — rank 3 vira "Top 5" e nunca também "Top 10". Um slicer normal nessa coluna só mostra quem tem exatamente o rótulo clicado, sem cumulatividade. Também descartei resolver com **bookmark** (Indicadores + Botões, mesmo mecanismo do "Golden Leads x Outras Escolas" da página 1) — pedido explícito do Gui, porque um bookmark de página inteira fotografa o estado de *todos* os visuais da página de uma vez; qualquer visual novo ou removido depois quebra o bookmark silenciosamente, sem aviso nenhum. Solução adotada: resolver 100% no pipeline com uma **tabela-ponte** (técnica padrão de mercado pra "Top N" clicável em Power BI).

**Como funciona:** `poliedro_29b_faixas_rank_bridge.py` gera `data/outputs/29b_faixas_rank_bridge.csv` — cada escola aparece uma linha **pra cada faixa que ela pertence** (rank 3 → 3 linhas: Top 5, Top 10, Demais escolas; rank 8 → 2 linhas: Top 10, Demais escolas; rank 15 → 1 linha: Demais escolas). O slicer aponta pra essa tabela nova, não mais pra `29_universo_completo_powerbi` — clicar num bloco filtra a ponte, que propaga o filtro de volta pra tabela de escolas via relacionamento bidirecional. Sanity check do último run: 7.842 linhas na ponte, 1.350 escolas em "Top 5", 2.048 em "Top 10" (cumulativo, ≥ Top 5 ✓), 4.444 em "Demais escolas" (bate com o universo inteiro ✓).

**Configuração (só refazer 1x):**

1. Obter Dados > Texto/CSV > `29b_faixas_rank_bridge.csv` (pasta `data/outputs/`) > Carregar, sem Transformar Dados.
2. Ícone **Modelo** > arraste `codigo_escola` de `29_universo_completo_powerbi` até `codigo_escola` de `29b_faixas_rank_bridge` > cardinalidade **"Um-para-muitos"** (29 = um, ponte = muitos) > **Direção do filtro: "Ambas"** (não "Único" — é isso que deixa o clique na ponte filtrar a tabela de escolas de volta).
3. Painel Dados > tabela `29b_faixas_rank_bridge` > coluna `faixa_rank_cidade` > aba Ferramentas de Coluna > **Ordenar por Coluna** > `faixa_ordem` — sem isso os blocos aparecem em ordem alfabética ("Demais escolas, Top 10, Top 5"), não na ordem certa.
4. No slicer em Bloco existente na página 3 (o que hoje aponta pro campo antigo): remova o campo velho e arraste `faixa_rank_cidade` **da tabela `29b_faixas_rank_bridge`** no lugar.
5. Teste: clicar "Top 10" deve trazer escolas de rank 1 a 10 juntas; "Demais escolas" deve trazer as 4.444 (não só quem ficou fora do Top 10). Se algum bloco mostrar número errado, o relacionamento provavelmente ficou "Único" em vez de "Ambas" (passo 2).

⚠️ A coluna antiga `faixa_rank_cidade` **continua existindo** dentro de `29_universo_completo_powerbi` (não removida do pipeline) — ela não faz mal nenhum ali parada, só não alimenta mais o slicer. Não precisa excluir/reimportar a tabela 29 por causa dela.

Ctrl+S

### Curadoria pra Parte 2 do case (top 5 por cidade) — resolvido pelo slicer em Bloco, sem visual extra (12/08)

Versão anterior deste guia recomendava um 2º visual hardcoded (tabela nova com `rank_municipio <= 5` fixo + cidades fixas na segmentação). Decisão revista: **é redundante**, o Gui perguntou e a resposta é sim — o slicer em Bloco Top 5/Top 10/Demais escolas (seção abaixo) já resolve isso, sem precisar de outro visual:

1. Confirmado no código-fonte (`poliedro_29`): `rank_municipio` reinicia em 1 a cada cidade (`groupby("codigo_municipio")["score_destaque"].rank(...)`).
2. A tabela-ponte `29b_faixas_rank_bridge` já inclui toda escola com `rank_municipio <= 5` **da própria cidade dela**, pra todas as 311 cidades do universo — não só as 10 prioritárias.
3. Na prática: clicar "Top 5" no slicer em Bloco + selecionar as cidades desejadas na segmentação `cidade` reproduz exatamente a tabela curada que a versão anterior deste guia propunha construir à parte — mesmo filtro, sem visual duplicado, sem manutenção dupla se a lista de cidades apresentadas mudar.
4. Pra apresentação: clique "Top 5" + selecione as ≥3 cidades que você vai citar na fala (das que estão em `top10`). Cidades com menos de 5 escolas elegíveis mostram menos de 5 linhas — comportamento esperado de Top N, não erro.

### Card — Resumo de metodologia (consulta rápida durante a apresentação)

Inserir > Caixa de texto, num canto discreto da página (não é o documento de metodologia completo — esse continua sendo entrega separada, ver "Norte do projeto" acima):

> **Como o score foi construído:** `score_destaque` combina ENEM (desempenho), infraestrutura do Censo Escolar (porte/estrutura), seletividade e inclusão — nenhum peso arbitrário sem justificativa (ver documento de metodologia pros pesos exatos e a razão de cada um).
> **Limitações conhecidas:** sem dado de mensalidade (não é público); ~76% das escolas fora do recorte comercial ainda não têm sistema de ensino pesquisado; SP e RJ saem do Top 10 nacional por diluição estatística (ver página 2).

Ctrl+S

---

## Referência de colunas

| Coluna | O que é |
|---|---|
| `chave_regiao` | (tabelas `29_universo_completo_powerbi` e `16_regioes_sp_rj_com_renda`) `cidade + "\|" + regiao` — chave de relacionamento entre as 2 tabelas no modelo. Só existe pra São Paulo/Rio (NaN nas demais cidades, de propósito) |
| `regiao` | (tabela `29_universo_completo_powerbi`) = `distrito` em São Paulo, `bairro` no Rio — mesma unidade que a coluna `regiao` da tabela 16, só que no nível de escola |
| `distancia_parceiro_mais_proximo_km` | (tabela `16_regioes_sp_rj_com_renda`) Mediana da distância das escolas da região até o parceiro Poliedro mais próximo — calculada no `poliedro_16b`, depois do passo 29 |
| `regiao_oportunidade` | (tabela `16_regioes_sp_rj_com_renda`) Verdadeiro/Falso — renda mediana da região acima da mediana da própria cidade (SP e RJ comparados separadamente) |
| `segmento_comercial` | Líder local / Desafiante (2º-5º) / Outras posições / Sem comparação local — posição real no ranking da cidade |
| `produto_alvo` | Poliedro / Polígono / nenhum — classificação comercial por score (Polígono ainda especulativo, sem mensalidade real) |
| `score_destaque` | Score nacional (ENEM+infra+seletividade+inclusão), 0 a 1 |
| `indice_infra` | 0 a 5 — soma de lab. ciências, lab. informática, biblioteca, quadra coberta, auditório |
| `sistema_ensino_identificado` | Sistema já usado hoje. "Pendente de pesquisa" = ninguém confirmou ainda (nunca pesquisou OU pesquisou e não achou — unificado pra virar planilha viva que o time comercial vai preenchendo); "Fora do escopo da pesquisa" = nem é candidata comercial hoje (produto_alvo=nenhum) |
| `endereco_completo` | Rua, número, bairro e CEP prontos pro tooltip do mapa — evita expor LATITUDE/LONGITUDE cru pro time comercial |
| `sistema_ensino_top_outros` | Mesma coisa que `sistema_ensino_identificado`, mas com sistemas confirmados de menos de 25 escolas agrupados em "Outros (sistema minoritário)" — use essa versão em gráfico de pizza/rosca, não a bruta |
| `ja_cliente_poliedro_qualquer_marca` | Verdadeiro/Falso — já é cliente Poliedro, própria ou outra marca |
| `distancia_parceiro_atual_km` | Km até o cliente/parceiro Poliedro mais próximo na mesma cidade |
| `nome_parceiro_mais_proximo` | Nome desse parceiro/cliente |
| `renda_mediana_responsavel` | Renda mediana do responsável pelo domicílio, IBGE Censo 2022 |
| `enem_media_2anos` | Média 2024+2025 — mais estável que 1 ano só |
| `delta_enem_2025_2024` | Diferença entre edições — variação até ±22 pontos é ruído normal |
| `segmento_golden_lead` | (tabela-ponte `29c_golden_leads_bridge`, não a coluna homônima em `29`) "🟡 Golden Leads (N)" / "🔵 Outras Escolas (N)" — toda escola tem linha "Outras Escolas", só Golden Leads têm a 2ª linha extra |
| `segmento_ordem` | (tabela `29c_golden_leads_bridge`) 1=Golden Leads, 2=Outras Escolas — usado em "Ordenar por Coluna" pra fixar a ordem do slicer |
| `faixa_rank_cidade` | (tabela-ponte `29b_faixas_rank_bridge`, não a coluna homônima em `29`) "Top 5" / "Top 10" / "Demais escolas" — cada escola aparece 1x por faixa cumulativa que pertence |
| `faixa_ordem` | (tabela `29b_faixas_rank_bridge`) 1=Top 5, 2=Top 10, 3=Demais escolas — usado em "Ordenar por Coluna" |

---

## Erros comuns

**Tile "(Em branco)" aparece num slicer de `cidade` (12/08) — não é erro de dado.** Confirmado via CSV: zero valores em branco em `cidade` nas tabelas 16 e 29. Causa real: comportamento automático do Power BI em relacionamentos um-para-muitos sem integridade referencial — quando muitas linhas do lado "muitos" (aqui, as ~4.270 escolas nacionais fora de SP/RJ, que têm `chave_regiao = NaN` de propósito, já que só SP/RJ têm linha na tabela 16) não casam com nenhuma linha do lado "um", o Power BI injeta um membro fantasma "(Em branco)" pra representá-las no slicer. Duas correções, escolha uma: (1) no próprio slicer, marque manualmente só "São Paulo"/"Rio de Janeiro" em vez de "Selecionar tudo"; (2) no relacionamento (aba Modelo) > editar > marque **"Pressuponha integridade referencial"** — mais robusto, remove o tile de vez.

**Sincronizar segmentações de dados (Sync Slicers) apagou visuais inteiros da página de origem (12/08).** Ao desmarcar "Sincronizado" pra uma página em Exibição > Sincronizar Segmentações de Dados, o Power BI tem uma 2ª coluna "Visível" separada — desmarcar ela por engano (fácil de confundir com "Sincronizado", ficam lado a lado no painel) esconde o slicer daquela página específica, mesmo sem afetar a sincronização propriamente dita. Sintoma: todos os slicers de uma página somem de uma vez, mesmo sem ter sido excluído nenhum visual. Recuperação: Exibição > **Seleção** (Selection pane) — lista todos os visuais da página **por nome**, inclusive os invisíveis; clique no nome do slicer sumido pra selecioná-lo mesmo sem conseguir vê-lo no canvas, depois volte no painel de Sincronizar Segmentações e marque "Visível" de novo pra página certa (deixando "Sincronizado" como estava).

**Cartão mostra número sem separador de milhar, tipo "4444" ou "1020,417" cortado (07/08):** causa diferente da abaixo ("4 Mil") — aqui o cartão usa o visual novo "Cartões" (não o clássico), que tem sua PRÓPRIA seção de formatação de número por campo, independente do `FormatString` da medida e das Opções do arquivo. Clique no cartão > painel Formatar visual > aba **Geral** (não Visual) > **"Formato de dados"** > confira "Formato" (deve ser "Número inteiro" pra contagens, não "Número decimal" nem "Geral") e ligue **"Separador de milhares"**. Se o cartão mostra casas decimais indevidas (ex. "1020,417" cortado no card), é sinal de que "Formato" tá em "Número decimal" com "Casas decimais" alto — troque pra "Número inteiro". Cada campo dentro do mesmo visual "Cartões" (quando há mais de um) tem sua config separada, selecionável no dropdown "Aplicar configurações para".

**Cartão mostra "4 Mil" em vez de "4.444" (06/08):** não é o formato da medida — é a opção **"Unidades de exibição"** do visual, que por padrão vem em "Auto" e comprime qualquer número grande em K/Mil/Mi, independente do `FormatString` da medida (`#,##0` não evita isso, os dois são configurações separadas). Sintoma típico: alguns cartões da mesma página arredondam e outros não — os que não arredondam já tiveram essa opção ajustada antes, os novos (ou que trocaram de campo, como ao mover `Qtd Escolas` pra `_Medidas`) voltam pro padrão "Auto". Correção: clique no cartão > painel Visualizações > ícone de pincel "Formatar visual" > seção de valor/retorno de chamada (nome exato varia com a versão — use a lupa de busca no topo do painel "Formatar visual" e digite "unidades de exibição" se não achar de primeira) > troque **"Auto"** por **"Nenhum"**. Repita em cada cartão afetado — é uma configuração por visual, não do modelo, então não tem como corrigir uma vez só pra todos.

**"Coluna X não foi encontrada" ao Atualizar:** cache de importação antigo — normalmente só acontece quando uma coluna existente foi **renomeada ou removida** no CSV (adicionar coluna nova, como fizemos com `regiao`/`chave_regiao` em 06/08, não costuma quebrar Atualizar). Se acontecer: Página Inicial > Transformar Dados > botão direito na consulta > Excluir > feche o Power Query > Obter Dados > importe o CSV de novo, do zero. ⚠️ Essa ação (excluir + reimportar) tem um efeito colateral sério — ver o item logo abaixo antes de fazer isso.

**Card mostrando um número muito menor do que o esperado (ex.: Total = 63 em vez de 1.127):** provável filtro vazado — confira se algum campo (ex.: `ja_cliente_poliedro_qualquer_marca`) está em **"Filtros nesta página"** em vez de **"Filtros neste visual"**. Filtro de página afeta todos os cartões juntos.

**Números decimais errados (`9738` em vez de `0,9738`):** mesma causa/solução do cache antigo acima.

**Formato mudou na tabela do modelo mas o visual continua com 2 casas decimais:** clique na tabela (canvas) > painel Visualizações > ícone de pincel "Formatar visual" > seção "Valores" > ajuste "Casas decimais" ali também — o visual pode ter uma formatação própria por cima da do modelo.

**Medida `Qtd Escolas` some do painel Dados sempre que a tabela `29` é reimportada (05/08, de novo em 06/08) — causa raiz e correção definitiva:**

Por que continua acontecendo mesmo seguindo "prefira Atualizar": uma medida DAX fica presa ao **objeto** da tabela, não só ao nome dela. "Excluir a consulta + Obter Dados de novo" cria um objeto novo por baixo do capô (mesmo nome na tela, identidade diferente pro motor do Power BI) — qualquer medida presa à tabela antiga vira órfã e some, mesmo que o nome da tabela seja idêntico depois. Isso vai continuar acontecendo pra sempre enquanto a medida morar dentro de `29_universo_completo_powerbi`, porque cedo ou tarde uma mudança de estrutura de coluna (renomear/remover) vai forçar um reimport completo de novo — não é um erro seu, é a arquitetura do Power BI.

⚠️ **O mesmo vale pros relacionamentos** (`29↔14_cidades`, `29↔16_regioes` via `chave_regiao`) — eles também ficam presos ao objeto da tabela. Excluir+reimportar `29` derruba os relacionamentos junto, não só a medida. Não tem como blindar relacionamento (por natureza ele liga 2 tabelas físicas específicas); a única defesa é comportamental: use **Atualizar** sempre que só linhas ou colunas novas mudaram (é o caso de qualquer rerun do pipeline Python), e reserve "Excluir + Obter Dados" só pra quando Atualizar realmente reclamar de coluna renomeada/removida — sabendo que, se fizer isso, vai ter que recriar os 2 relacionamentos manualmente na aba Modelo depois.

**Correção definitiva pra medida (faça uma vez, nunca mais se repete):** tire a medida de dentro de `29_universo_completo_powerbi` e coloque numa **tabela de medidas separada**, que não vem de CSV nenhum — como ela não é uma consulta importada, nenhum "Excluir + Obter Dados" da tabela 29 encosta nela.

1. Modelagem (ou Página Inicial) > **Nova Tabela** > cole essa fórmula DAX: `_Medidas = {BLANK()}` — cria uma tabelinha de 1 coluna e 1 linha vazia, sem ligação com nenhum CSV.
2. Painel Dados > botão direito em `_Medidas` > **Ocultar no modo de exibição de relatório** (opcional — deixa o painel de campos mais limpo; a medida continua aparecendo normalmente nos visuais).
3. Clique em `_Medidas` > **Nova medida** > recrie `Qtd Escolas` com a fórmula original (`COUNTROWS(...)`) e reaplique a formatação de número que tinha antes.
4. Em cada visual que já usava a medida antiga (agora quebrada/sumida), remova o campo quebrado e arraste a medida nova de `_Medidas` no lugar.
5. A partir daqui: pode excluir e reimportar `29_universo_completo_powerbi` quantas vezes quiser (por causa de mudança de coluna no pipeline, por exemplo) — `Qtd Escolas` nunca mais some, porque não está mais fisicamente dentro dela. Só lembre que os 2 relacionamentos (item acima) continuam vulneráveis e precisam ser recriados manualmente se você excluir+reimportar.

---

## Configuração inicial (só refazer numa máquina nova / arquivo do zero)

1. Obter Dados > Texto/CSV > importar (5x, um de cada vez, `Carregar` sem "Transformar Dados"): `29_universo_completo_powerbi.csv`, `14_cidades_powerbi.csv`, `16_regioes_sp_rj_com_renda.csv`, `29b_faixas_rank_bridge.csv`, `29c_golden_leads_bridge.csv` (pasta `data/outputs/`)

⚠️ **Ordem pra rodar o pipeline do zero:** `poliedro_15` → `poliedro_16` → `poliedro_19` → `poliedro_29` → **`poliedro_16b`** (por último — ele volta e acrescenta `distancia_parceiro_mais_proximo_km` no arquivo do passo 16, porque essa distância só existe depois que o passo 29 sabe quem já é cliente Poliedro). Se rodar só o `poliedro_16` de novo sozinho depois, essa coluna some do CSV — precisa rodar o `16b` de novo também.
2. Ícone **Modelo** > arrastar `codigo_municipio` de `29_universo_completo_powerbi` até `codigo_municipio` de `14_cidades_powerbi` > confirmar cardinalidade "Muitos-para-Um"
3. Ícone **Modelo** > arrastar `chave_regiao` de `29_universo_completo_powerbi` até `chave_regiao` de `16_regioes_sp_rj_com_renda` > cardinalidade "Muitos-para-Um", direção do filtro "Único" (16 → 29) — relacionamento novo de 06/08, sem ele a página de Inteligência Comercial não consegue filtrar a tabela de escolas ao clicar numa região (ver seção "Tabela — Escolas da região selecionada")
4. Ícone **Modelo** > arrastar `codigo_escola` de `29_universo_completo_powerbi` até `codigo_escola` de `29b_faixas_rank_bridge` > cardinalidade "Um-para-muitos", direção do filtro **"Ambas"** (ver seção "Slicer em Bloco — Top 5/Top 10/Demais escolas")
5. Ícone **Modelo** > arrastar `codigo_escola` de `29_universo_completo_powerbi` até `codigo_escola` de `29c_golden_leads_bridge` > cardinalidade "Um-para-muitos", direção do filtro **"Ambas"** (ver seção "Modo de Análise — Golden Leads x Outras Escolas")
6. Exibição > Temas > Procurar temas > `powerbi_tema_poliedro.json`
