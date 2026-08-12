# Metodologia — Mapeamento de Cidades e Escolas Prioritárias (Case Poliedro)

*Última atualização: 12/08/2026 — reflete o pipeline completo `poliedro_01` a `poliedro_29c`, incluindo o roadmap 3.0 (funil nacional, produto Polígono, dashboard Power BI de 3 páginas). Revisão anterior (22/07) cobria só `poliedro_01`-`13`; os números e a fórmula de score mudaram desde então — ver seção 7 para o histórico das revisões.*

## 1. Fontes de dados

| Fonte | Edição | Uso |
|---|---|---|
| Censo Escolar INEP | 2025 (mais recente disponível) | Universo de escolas, infraestrutura, situação de funcionamento, tipo de mantenedora |
| Microdados ENEM | 2025 (principal) + 2024 (validação de estabilidade, seção 10) | Desempenho acadêmico por escola |
| IBGE — Tabela 10296 (SIDRA) | Censo 2022 | Renda domiciliar per capita por município (Parte 1) |
| IBGE — Tabela 9514 (SIDRA) | Censo 2022 | População 0-17 anos e população total por município |
| IBGE — Agregados por Setores Censitários, Rendimento do Responsável | Censo 2022 (publicado 08/05/2026) | Renda mediana do responsável por bairro/distrito (página 2 do dashboard, SP e RJ) |

Justificativa de usar Censo Escolar 2025 (e não 2023, usado em versões anteriores deste projeto): é a edição mais recente e evita descompasso de ano com o ENEM 2025.

### 1.1. Fontes complementares avaliadas e não utilizadas

O case lista IBGE (PIB), Atlas Brasil/PNUD (IDH), REGIC/IBGE e QEdu como opcionais. Foram avaliadas e descartadas conscientemente:

| Fonte | Por que não entrou |
|---|---|
| PIB per capita municipal (IBGE) | Mistura riqueza industrial/institucional com renda das famílias — viés já identificado neste projeto antes deste case. Renda domiciliar (Tabela 10296, e no nível de bairro/distrito a tabela de rendimento do responsável) é o substituto correto. |
| IDH Municipal (Atlas Brasil/PNUD) | Verificado em jul/2026: o IDHM oficial por município ainda usa base do Censo 2010 — não há atualização completa com o Censo 2022 (só uma estimativa parcial via PNAD Contínua, o "Radar IDHM"). Dado desatualizado demais para um recorte de mercado de 2025. |
| REGIC (regiões de influência das cidades, IBGE) | Responderia "qual cidade polariza a região", pergunta diferente de "onde está a demanda e a oferta de prestígio privado hoje". Redundante com o que população + renda + volume de escolas já capturam para este objetivo. |
| QEdu (indicadores educacionais consolidados) | Seus indicadores derivam do mesmo Censo Escolar e do próprio ENEM/Saeb — acessar as fontes primárias (que já fizemos) é mais rastreável do que uma camada consolidada de terceiros. |

### 1.2. Critérios de exemplo do case não utilizados no score

- **Volume de matrículas no Ensino Médio** (`QT_MAT_MED`): coletado e exibido como contexto em todas as partes, mas não pontua nos scores de qualidade/priorização. Motivo: porte de matrícula mede tamanho, não prestígio. Passa a ser usado como *filtro* (não score) só na classificação de produto Polígono — seção 7.
- **Amplitude de segmentos ofertados (EI, EF, EM)**: não usada como critério de pontuação. Motivo: mais associada a conveniência para a família do que a prestígio acadêmico. Os dois critérios usados na resposta formal (ENEM + infraestrutura) já satisfazem o requisito mínimo de 2 critérios (1 Censo + 1 ENEM) do case.

## 2. Filtro de escopo — dois recortes distintos

Este projeto usa **dois recortes de escolas elegíveis**, aplicados a objetivos diferentes. É importante não confundi-los:

**Recorte original** (`poliedro_01`-`poliedro_05`, resposta formal ao case — Partes 1 e 2):
- **Município**: população total > 100.000 habitantes → **319 municípios**.
- **Escola**: `TP_DEPENDENCIA == 4` (privada) E `TP_CATEGORIA_ESCOLA_PRIVADA` em `{1,2,3}` (exclui 4 = Filantrópica) E `TP_SITUACAO_FUNCIONAMENTO == 1` (em atividade) E `QT_TUR_MED > 0` (oferece ao menos Ensino Médio).
- Resultado: **8.095 escolas elegíveis nacionalmente**, das quais **5.647 estão em municípios >100k habitantes (318 dos 319 municípios — exceção: Ibirité/MG, sem escola elegível)**.
- Limpeza de outliers: removida 1 escola com 4.444 matrículas de EM em 10 salas (erro de preenchimento). `QT_SALAS_UTILIZADAS` está top-codado em 202 nesta edição — por isso `QT_MAT_MED` é a métrica de porte usada, não salas.
- Este recorte **não** exclui explicitamente o Sistema S (SESI/SENAI/SESC/SENAC) — checado manualmente: nenhuma das 20 escolas do Top 5×4 cidades (seção 4) é Sistema S, então não afeta a resposta formal, mas o filtro dedicado só existe no recorte ampliado abaixo.

**Recorte ampliado** (`poliedro_25` em diante — funil nacional, produto Polígono, dashboard Power BI, seção 7):
- Revisão de 24/07: categoria 4 (Filantrópica) passou a ser refinada por nome (ex.: mantém escola que só tem "Filantrópica" no registro administrativo mas opera como privada comum) em vez de excluída em bloco — isso ampliou a base.
- Mesmo filtro de município (>100k hab.) aplicado sobre a base ampliada: **6.308 escolas** (`funil_escolas_pontuadas.csv`), das quais **4.706 têm ENEM confiável** (≥10 participantes).
- Filtro adicional de **Sistema S** (`poliedro_filtros.remover_sistema_s`, via coluna oficial `IN_MANT_ESCOLA_PRIVADA_SIST_S` do Censo — SESI, SENAI, SESC, SENAC: mantidas por confederações patronais, têm sistema de ensino próprio, não são prospect comercial): remove 436 escolas do total (262 das 4.706 confiáveis) → **4.444 escolas**, o número de "Total Mapeado" do dashboard.

Os dois recortes convivem de propósito: o original é o que responde ao case tal como formulado (Partes 1 e 2, seções 3 e 4); o ampliado alimenta a leitura de portfólio/cross-sell mais ampla que o projeto evoluiu para cobrir (seção 7), com um filtro comercial (Sistema S) que não fazia sentido aplicar antes de o funil existir.

## 3. Parte 1 — Score de priorização de cidades

Aplicado aos 318 municípios elegíveis do recorte original. Cada critério é normalizado por percentil (rank/N, 0 a 1) dentro desse universo.

```
score_priorizacao = 0.40 × percentil(score_socioeconomico)
                   + 0.30 × percentil(qtd_escolas_elegiveis)
                   + 0.30 × percentil(enem_media_praca)
```

- **score_socioeconomico** (peso 0.40): `0.85 × score_renda + 0.15 × percentil(população 0-17)`, onde `score_renda = 0.80 × %população em domicílios >5 SM + 0.20 × %população em domicílios 3-5 SM` (Tabela 10296). Não usa PIB per capita.
- **qtd_escolas_elegiveis** (peso 0.30): contagem de escolas elegíveis no município — sinaliza concentração de mercado privado instalado, não riqueza.
- **enem_media_praca** (peso 0.30): média ponderada por `qtd_participantes_enem` do `enem_media_geral` (seção 5) das escolas elegíveis do município com dado ENEM vinculado. Municípios sem nenhuma escola com dado ENEM recebem o pior percentil (não são excluídos).

**Resultado**: Top 10 = Belo Horizonte, Niterói, Goiânia, Vitória, Florianópolis, Brasília, Porto Alegre, São José dos Campos, Recife, Ribeirão Preto. Script: `poliedro_04_score_cidades.py`.

**Nota sobre São José dos Campos:** é a sede nacional do Poliedro (CEV — Centro Empresarial do Vale). Sua presença no Top 10 provavelmente reflete um mercado onde a marca já tem forte presença, não uma oportunidade nova.

**Escolha das 4 cidades da Parte 2:** a mudança para média ponderada (revisão de 21/07) troca a 3ª colocação — Goiânia passa Vitória. Em vez de escolher entre as duas, a Parte 2 usa as **4** cidades de maior score (Belo Horizonte, Niterói, Goiânia, Vitória) — cobre tanto a versão simples quanto a ponderada do critério, e excede o mínimo de 3 cidades pedido pelo case.

## 4. Parte 2 — Score de destaque de escolas (resposta formal ao case)

Aplicado às 4 cidades de maior `score_priorizacao` (Belo Horizonte, Niterói, Goiânia, Vitória). Percentis calculados sobre o universo nacional de 5.647 escolas elegíveis do **recorte original** (não o ampliado da seção 7) — evita instabilidade em praças com poucas escolas.

```
score_destaque = 0.60 × percentil(enem_media_geral) + 0.40 × percentil(indice_infra)
```

- **enem_media_geral** (peso 0.60, critério ENEM): média das 5 notas (CN, CH, LC, MT, Redação) dos participantes vinculados à escola (`CO_ESCOLA` em RESULTADOS_2025.csv), restrito a `TP_DEPENDENCIA_ADM_ESC==4` e `TP_SIT_FUNC_ESC==1`.
- **indice_infra** (peso 0.40, critério Censo): soma 0-5 de `IN_LABORATORIO_CIENCIAS + IN_LABORATORIO_INFORMATICA + IN_BIBLIOTECA + IN_QUADRA_ESPORTES_COBERTA + IN_AUDITORIO`.
- **Confiabilidade**: escolas com menos de 10 participantes ENEM vinculados não entram no ranking (amostra pequena é ruído, não sinal).
- `QT_MAT_MED` é reportado como contexto, não entra no score.

**Validação empírica:** o Colégio Arena (Goiânia), 1º colocado, já aparece como depoimento de escola parceira no site institucional do Poliedro — sinal de que o método aponta para escolas com fit real.

Esta fórmula (60% ENEM / 40% infra) é **diferente** da usada no funil nacional/dashboard (seção 7, 75/15/5/5) — propositalmente: aqui o objetivo é a resposta mínima e defensável ao case, com o critério mais simples possível dentro do que o case pede (1 Censo + 1 ENEM); a versão nacional evoluiu depois, por pedido de negócio, para incorporar seletividade e inclusão como sinais adicionais (fracos, com peso baixo de propósito).

Script: `poliedro_05_score_escolas.py`. Resultado: `data/outputs/02_escolas_destaque_top3_cidades.csv` (nome mantém "top3" por compatibilidade — contém as 4 cidades desde 21/07).

## 5. Extração ENEM 2025

`RESULTADOS_2025.csv` (~4,8M linhas) filtrado por `CO_ESCOLA` não nulo + `TP_DEPENDENCIA_ADM_ESC==4` + `TP_SIT_FUNC_ESC==1` → 272.799 participantes em 8.200 escolas privadas. Script: `poliedro_02_extrair_enem.py`.

## 6. Bônus — Crescimento de matrículas de Ensino Médio (2023 → 2025)

Reaproveita `microdados_censo_escolar_2023.zip`, cruzado por `CO_ENTIDADE` com `QT_MAT_MED` de 2025.

```
crescimento_pct = (QT_MAT_MED_2025 - QT_MAT_MED_2023) / QT_MAT_MED_2023 × 100
```

Cobertura: 85,8% das 5.647 escolas do recorte original têm correspondência em 2023. Agregado por cidade usando **mediana** (não média), para não deixar 1-2 escolas com base pequena distorcerem o resultado. Não altera os scores das Partes 1 e 2 — é coluna de contexto. Script: `poliedro_06_crescimento_matriculas.py`.

## 7. Funil nacional e Golden Leads (bônus de portfólio)

Esta seção é **adicional** à resposta formal do case (seções 3-4) — nasceu de um pedido de negócio para uma leitura de portfólio/cross-sell mais ampla que 4 cidades, e evoluiu ao longo do projeto (roadmap 3.0). Alimenta o funil de priorização, a segmentação comercial e as páginas 1 e 3 do dashboard Power BI.

### 7.1. Score de destaque nacional

Calculado sobre o **recorte ampliado** (seção 2), só entre as 4.706 escolas com ENEM confiável (evita que escolas de amostra não-confiável influenciem o percentil de quem é confiável).

```
score_destaque_nacional = 0.75 × percentil(enem_media_geral)
                         + 0.15 × percentil(indice_infra)
                         + 0.05 × percentil(indice_seletividade)
                         + 0.05 × percentil(indice_inclusao)
```

- **ENEM** (peso 0.75) e **infraestrutura** (peso 0.15): mesma definição da seção 4, mas com pesos revisados — testes com dado real (Santos/SP) mostraram que 40% em infra deixava a fórmula sensível demais a diferenças de infraestrutura mesmo com gap grande de ENEM (escola com infra 5 e ENEM mediano ultrapassando escola com infra 4 e ENEM claramente melhor). 75/15 se mostrou mais estável: infra decide empate real, não domina o ranking.
- **Seletividade** (`IN_EXAME_SELECAO`, peso 0.05): escola faz exame de seleção para ingresso. Testado: escolas com essa flag têm ENEM médio 614 vs 593 sem — diferença real mas moderada, daí o peso baixo.
- **Inclusão** (`IN_SALA_ATENDIMENTO_ESPECIAL + IN_ACESSIBILIDADE_RAMPAS`, índice 0-2, peso 0.05): incluído como hipótese a testar, sem relação direta esperada com prestígio acadêmico — peso baixo até decisão de manter ou remover. `TP_AEE` foi descartado como critério (98,4% "não oferece" — variância baixa demais).
- Dispositivo do aluno (tablet/notebook) foi avaliado e descartado: ENEM médio praticamente igual com ou sem, e correlaciona forte com `indice_infra` (mediria a mesma coisa, sem sinal novo).

*Nota de honestidade metodológica: os pesos 75/15/5/5 são provisórios, pendentes de validação com o time Poliedro — o passo `poliedro_25` (seção 7.2) testou e documentou que a contagem de escolas acima do corte 0,70 varia de **817 a 1.412** só mudando pesos, sem mudar nenhum dado. O corte em si (0,70) também é uma escolha de negócio, não estatística.*

Script: `poliedro_05b_score_destaque_nacional.py`. Gera `data/outputs/funil_escolas_pontuadas.csv`.

### 7.2. Produto Poliedro vs. Polígono

Com dois produtos no portfólio (Poliedro: prestígio/vestibular concorrido; Polígono: linha secundária, mensalidade menor, foco em ENEM/mercado de trabalho), score baixo deixa de significar "lead ruim" e passa a significar "produto errado":

```python
CORTE_POLIEDRO = 0.70          # produto_alvo = "Poliedro" se score_destaque_nacional >= 0.70
CORTE_MINIMO_POLIGONO = 0.40   # produto_alvo = "Polígono" se 0.40 <= score < 0.70 E QT_MAT_MED >= 100
PORTE_MINIMO_POLIGONO = 100    # produto_alvo = "nenhum" caso contrário
```

Porte mínimo de 100 matrículas no Polígono porque esse produto compete por preço menor — só fecha a conta com volume. Faixa 0,40-0,70 com porte relevante representa um mercado antes invisível: **1.017 escolas** hoje (medido em 28/07: ~234 mil matrículas de EM, quase do tamanho do pool de Golden Leads da época).

Limitações explícitas do corte: (1) sem preço de mensalidade em nenhuma fonte pública, o encaixe do Polígono é inferido por proxy (score+porte), não medido; (2) `score_destaque` mede valor se converter, não probabilidade de conversão — escola de score altíssimo é a que menos tem motivo para trocar de sistema.

Script: `poliedro_25_produto_alvo.py`. Gera `data/outputs/25_produto_alvo.csv`.

### 7.3. Números atuais (medidos em 12/08/2026, sobre `29_universo_completo_powerbi.csv`)

| Categoria | Escolas |
|---|---|
| Total mapeado (recorte ampliado, ENEM confiável, sem Sistema S) | **4.444** |
| Golden Leads (`produto_alvo == "Poliedro"`, score ≥ 0,70) | **1.127** |
| Polígono (0,40 ≤ score < 0,70 + porte ≥ 100) | **1.017** |
| Nenhum produto (fora dos dois critérios) | 2.300 |
| Municípios distintos com escola no universo | **311** (dos 318 elegíveis — os demais não têm escola com ENEM confiável e sem Sistema S sobrevivendo ao filtro) |
| UFs distintas | 27 |

`score_destaque` no universo: mín. 0,028 — mediana 0,511 — máx. 0,966.

### 7.4. Sistema de ensino identificado, segmentação comercial e canibalização

- **Sistema de ensino**: sem fonte pública estruturada — pesquisa manual, escola por escola, com 3 níveis de confiança (`confirmado`, `provavel_proprio`, `nao_identificado`). Cobertura: 1.127/1.127 das Golden Leads originais (100%), mais 90 escolas fora do escopo original pesquisadas ad-hoc. Script: `poliedro_19_sistema_ensino_identificado.py`.
- **Segmentação comercial**: cada escola do universo é rankeada dentro do próprio município por `score_destaque` (`rank_municipio`), gerando tags Líder local (1º), Desafiante (2º-5º), Outras posições, ou Sem comparação local (município com <3 escolas confiáveis). Scripts: `poliedro_09_icp_poliedro.py` (original, só Golden Leads) e `poliedro_26_ranking_local_parceiro.py` (versão com parceiros sinalizados, sem exclusão).
- **Canibalização**: distância (haversine, mesmo município) até as 4 unidades próprias Poliedro e até parceiros de qualquer marca — sinaliza risco de sobreposição, não exclui escolas do universo. Scripts: `poliedro_18_risco_canibalizacao.py` e `poliedro_24_canibalizacao_parceiros.py`.

### 7.5. Filtro de Sistema S

`poliedro_filtros.remover_sistema_s()`: remove escolas com `IN_MANT_ESCOLA_PRIVADA_SIST_S == 1` (SESI, SENAI, SESC, SENAC — mantidas por confederações patronais, sistema de ensino próprio, não são prospect comercial). Aplica-se apenas ao recorte ampliado (seção 2) — remove 436 das 6.308 escolas do funil (262 das 4.706 com ENEM confiável).

## 8. Dashboard Power BI — páginas 1 e 3 (nacional)

As páginas 1 (Visão Executiva) e 3 (Ranking de Escolas Prioritárias) do dashboard consomem `29_universo_completo_powerbi.csv` — o universo completo de 4.444 escolas em 311 cidades (seção 7.3), não só as Golden Leads. Mecanismos de filtro interativo:

- **Golden Leads x Outras Escolas** (página 1): tabela-ponte (`poliedro_29c_golden_leads_bridge.py`) — toda escola tem 1 linha "Outras Escolas (4.444)", Golden Leads ganham uma 2ª linha "Golden Leads (1.127)". Relacionamento many-to-many bidirecional por `codigo_escola`, necessário porque uma Golden Lead precisa poder estar nas duas categorias ao mesmo tempo.
- **Top 5 / Top 10 / Demais escolas por cidade** (página 3): mesmo mecanismo (`poliedro_29b_faixas_rank_bridge.py`), sobre `rank_municipio` — que reseta a cada cidade. Combinado com o slicer de Cidade, este mecanismo já responde à curadoria de "Top 5 por cidade" em qualquer subconjunto de cidades escolhido pelo usuário, sem precisar de um visual hardcoded separado para a Parte 2 formal do case.

## 9. Página 2 do dashboard — Inteligência Comercial (SP e RJ)

Achado de negócio, não exigência literal do case: São Paulo e Rio de Janeiro saem do Top 10 nacional (seção 3) por diluição estatística do score agregado por cidade — RJ fica em 19º, SP em 29º — mas são as duas maiores praças em volume absoluto de escolas elegíveis (503 em SP, 338 no Rio, ver seção 7.3), justificando um recorte de bairro/distrito à parte.

- **Granularidade**: distrito em São Paulo (88 distritos), bairro no Rio de Janeiro (`NO_DISTRITO` é degenerado no RJ — sempre "Rio de Janeiro" no Censo). Uma tentativa de usar Região Administrativa oficial do Rio (33 RAs) foi revertida: RA escondia diferença de renda relevante dentro da mesma região (ex.: Leblon/Ipanema junto com Gávea/São Conrado na RA "Lagoa").
- **Renda**: rendimento nominal **mediano** mensal do responsável pelo domicílio (V06006, IBGE Censo 2022, Agregados por Setores Censitários), por bairro/distrito — mais robusto a outliers que a média. Mede renda do responsável, não renda per capita domiciliar (métrica diferente da usada na Parte 1, que é per capita por município) — mistura tamanho de família com renda do responsável, mas é o dado mais fino disponível nesse nível geográfico. Script: `poliedro_16_renda_bairro_distrito.py`.
- **Região de oportunidade** (`regiao_oportunidade`): sinaliza região com renda mediana **acima da mediana das regiões elegíveis da mesma cidade** (SP e RJ nunca misturados numa mediana única — patamares de renda muito diferentes entre as duas cidades). É um recorte de leitura para achar bairros nobres com pouca presença Poliedro — não é um filtro aplicado às tabelas do dashboard: todas as regiões e escolas ficam visíveis, mesmo as de renda mediana/baixa, para permitir prospecção manual em qualquer bairro (inclusive os bem posicionados no ranking ENEM da cidade, independente de renda). Script: `poliedro_16_renda_bairro_distrito.py`, função `marcar_regiao_oportunidade`.
- **Distância até parceiro mais próximo**: mediana (não média) por região, mesma lógica anti-outlier do restante do projeto. Script: `poliedro_16b_distancia_regiao.py`.

## 10. Validação de estabilidade temporal (ENEM 2024 vs. 2025)

Com só uma edição do ENEM (2025), não havia como saber se a posição de uma escola no ranking é sinal ou ruído de turma única. `poliedro_27_extrair_enem_2024.py` extraiu as médias de 2024 para o mesmo cruzamento.

**Achado**: correlação de posto 2024×2025 = **0,874**, desvio de variação de **22 pontos** em média. Líder local estável em 73% dos municípios; a banda "Desafiante (2º-5º)" é mais frágil (mediana de oscilação de 4 posições, só 41% variam no máximo 2 posições). O filtro de confiabilidade (≥10 participantes) é permissivo: escolas com 10-19 participantes oscilam 28 pontos entre edições, contra 12 pontos nas com 100+ participantes — variância que afeta principalmente escolas de amostra pequena dentro do próprio corte de "confiável".

## 11. Ordem de execução (reprodutibilidade)

**Resposta formal ao case (Partes 1 e 2):**
1. `poliedro_01_baixar_dados.py` — Censo Escolar 2025 e população total IBGE.
2. `poliedro_02_extrair_enem.py` — médias ENEM por escola.
3. `poliedro_03_extrair_censo.py` — escolas privadas elegíveis (recorte original).
4. `poliedro_03b_extrair_enderecos.py` — endereço/CEP das escolas elegíveis.
5. `poliedro_04_score_cidades.py` — Parte 1.
6. `poliedro_05_score_escolas.py` — Parte 2 (Top 5 por cidade, 60/40 ENEM/infra).

**Bônus — funil nacional, portfólio, dashboard (roadmap 3.0):**
7. `poliedro_05b_score_destaque_nacional.py` — score nacional 75/15/5/5, recorte ampliado.
8. `poliedro_06_crescimento_matriculas.py` — crescimento de matrículas 2023-2025.
9. `poliedro_07_funil.py` — gráfico de funil de priorização (contagens ao vivo a partir dos CSVs anteriores).
10. `poliedro_08_visual_cosmos.py` — visual procedural (sem IA/internet).
11. `poliedro_09_icp_poliedro.py` — segmentação comercial original (só Golden Leads).
12. `poliedro_10_segmentacao_comercial.py` — gráfico da segmentação.
13. `poliedro_11_geocodificar_ceps.py` — geocodificação (roda local, precisa de internet).
14. `poliedro_12_graficos_cidades.py` — gráficos Top10/dispersão.
15. `poliedro_13_detectar_salas_vitrine.py` — detecção nacional de "sala vitrine".
16. `poliedro_19_sistema_ensino_identificado.py` — pesquisa manual (pré-requisito de 14).
17. `poliedro_28_universo_expandido.py` — universo Poliedro+Polígono expandido.
18. `poliedro_14_consolidar_dataset_powerbi.py` — dataset de Golden Leads para Power BI.
19. `poliedro_18_risco_canibalizacao.py` — distância a unidades próprias.
20. `poliedro_24_canibalizacao_parceiros.py` — distância a parceiros.
21. `poliedro_26_ranking_local_parceiro.py` — ranking com parceiros sinalizados.
22. `poliedro_29_universo_completo_powerbi.py` — fonte única das páginas 1 e 3 (depende de 19 e 25/`produto_alvo`).
23. `poliedro_15_regioes_sp_rj.py` → `poliedro_16_renda_bairro_distrito.py` → `poliedro_16b_distancia_regiao.py` — página 2 (ordem real: 15 → 16 → 29 → 16b, pois 16b depende de coluna gerada no 29).
24. `poliedro_29b_faixas_rank_bridge.py` e `poliedro_29c_golden_leads_bridge.py` — tabelas-ponte dos slicers em bloco do dashboard.

*A ordem de dependência não é sequencial pela numeração dos arquivos — os números refletem a ordem cronológica de criação, não de execução. Ver docstring de cada script para a dependência exata.*

## 12. Limitações documentadas

1. **Vínculo escola-participante mudou em 2025.** `CO_ESCOLA` só existe em `RESULTADOS_2025.csv`, preenchido em 36,15% das linhas. Não é possível cruzar com `PARTICIPANTES_2025.csv` (chaves incompatíveis, conforme o próprio dicionário do INEP) para separar treineiros de concluintes entre os sem vínculo.
2. **Viés regional de adesão ao ENEM.** Em praças com forte oferta de vestibular próprio (ex.: São Paulo), parte dos melhores alunos de escolas de elite pode não priorizar o ENEM, subestimando essas escolas no score.
3. **"Salas vitrine" de redes de ensino.** `poliedro_13` encontrou 4 grupos confirmados nacionalmente (3 em Fortaleza/CE, 1 em Uberaba/MG) com gap de 68 a 125 pontos entre a unidade pequena e as irmãs da mesma mantenedora. Nenhum dos dois municípios está entre as 10 cidades prioritárias nem entre as 4 do case formal — não afeta as 20 escolas do Top 5×4 desta entrega, mas afeta uma fração pequena das 1.127 Golden Leads do funil nacional (aparecem com score inflado).
4. **`score_destaque` não mede renda familiar diretamente.** Percentil médio de renda da cidade é 0,85 nas escolas Líder/Desafiante de score mais alto e 0,74 nas demais Golden Leads — correlação positiva, mas moderada, não uma separação limpa por classe.
5. **Escolas filantrópicas** (categoria 4 do Censo, recorte original) excluídas por não representarem o segmento de mercado privado relevante. No recorte ampliado (seção 2), o critério foi refinado por nome em vez de bloco — trade-off entre cobertura e risco de incluir alguma escola filantrópica remanescente.
6. **Recorte nacional, não regional.**
7. **Corte de produto (0,70/0,40) é uma escolha de negócio, não estatística** — a contagem de Golden Leads varia de 817 a 1.412 só ajustando pesos do score, sem mudar dado nenhum (seção 7.1). Os pesos atuais (75/15/5/5) são provisórios, pendentes de validação com o time Poliedro.
8. **`score_destaque` mede valor se converter, não probabilidade de conversão** — uma escola de score altíssimo tem, por definição, menos motivo para trocar de sistema de ensino. Isso é relevante para priorização comercial (seção 7.4), não para a resposta formal ao case.
9. **Sem dado de mensalidade em nenhuma fonte pública** — o encaixe do produto Polígono por faixa de preço é inferido por proxy (score + porte), não medido diretamente.
10. **Estabilidade temporal limitada, especialmente na banda "Desafiante"** — ver seção 10. O filtro de 10 participantes ENEM é permissivo: escolas no limite inferior desse corte oscilam mais entre edições do que escolas de amostra grande.
11. **Segmento comercial não sabe qual sistema de ensino a escola já usa**, além do que a pesquisa manual (seção 7.4) já cobriu — sinal direcional, não confirmação; precisa de verificação individual antes de prospecção real.
12. **Nome de arquivo desatualizado (cosmético).** `data/outputs/02_escolas_destaque_top3_cidades.csv` mantém "top3" por compatibilidade, mas contém as 4 cidades desde 21/07.
13. **Sem benchmark setorial externo dedicado à educação básica privada** — o Anuário Brasileiro da Educação Básica (Todos Pela Educação + Editora Moderna + Fundação Santillana) é a fonte mais próxima e não foi formalmente incorporado ao projeto, só usado para orientar esta resposta.
