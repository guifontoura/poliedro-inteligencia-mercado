# Metodologia — Mapeamento de Cidades e Escolas Prioritárias (Case Poliedro)

## 1. Fontes de dados

| Fonte | Edição | Uso |
|---|---|---|
| Censo Escolar INEP | 2025 (mais recente disponível) | Universo de escolas, infraestrutura, situação de funcionamento |
| Microdados ENEM | 2025 | Desempenho acadêmico por escola |
| IBGE — Tabela 10296 (SIDRA) | Censo 2022 | Renda domiciliar per capita por município |
| IBGE — Tabela 9514 (SIDRA) | Censo 2022 | População 0-17 anos e população total por município |

Justificativa de usar Censo Escolar 2025 (e não 2023, usado em versões anteriores deste projeto): é a edição mais recente e evita descompasso de ano com o ENEM 2025.

### 1.1. Fontes complementares avaliadas e não utilizadas

O case lista IBGE (PIB), Atlas Brasil/PNUD (IDH), REGIC/IBGE e QEdu como opcionais. Foram avaliadas e descartadas conscientemente:

| Fonte | Por que não entrou |
|---|---|
| PIB per capita municipal (IBGE) | Mistura riqueza industrial/institucional com renda das famílias — viés já identificado neste projeto antes deste case. Renda domiciliar (Tabela 10296) é o substituto correto. |
| IDH Municipal (Atlas Brasil/PNUD) | Verificado em jul/2026: o IDHM oficial por município ainda usa base do Censo 2010 — não há atualização completa com o Censo 2022 (só uma estimativa parcial via PNAD Contínua, o "Radar IDHM"). Dado desatualizado demais para um recorte de mercado de 2025. |
| REGIC (regiões de influência das cidades, IBGE) | Responderia "qual cidade polariza a região", pergunta diferente de "onde está a demanda e a oferta de prestígio privado hoje". Redundante com o que população + renda + volume de escolas já capturam para este objetivo. |
| QEdu (indicadores educacionais consolidados) | Seus indicadores derivam do mesmo Censo Escolar e do próprio ENEM/Saeb — acessar as fontes primárias (que já fizemos) é mais rastreável do que uma camada consolidada de terceiros. |

### 1.2. Critérios de exemplo do case não utilizados no score

- **Volume de matrículas no Ensino Médio** (`QT_MAT_MED`): coletado e exibido como contexto em ambas as partes, mas não pontua. Motivo: porte de matrícula mede tamanho, não prestígio — uma escola grande não é necessariamente mais prestigiada (e o exemplo do Censo 2025 mostrou porte podendo vir de dado inflado/mal preenchido, ver seção 7.4). Mesmo tratamento dado ao PIB per capita: informa a leitura, não decide o ranking.
- **Amplitude de segmentos ofertados (EI, EF, EM)**: não usada como critério de pontuação. Motivo: a amplitude de segmentos está mais associada a conveniência para a família (não trocar de escola do berçário ao 3º ano) do que a prestígio acadêmico — o objetivo deste case. Os dois critérios usados (ENEM + infraestrutura) já satisfazem o requisito mínimo de 2 critérios (1 Censo + 1 ENEM) com maior relação direta com a pergunta central.

## 2. Filtro de escopo (obrigatório, binário — não é critério de score)

- **Município**: população total > 100.000 habitantes → **319 municípios**.
- **Escola**: `TP_DEPENDENCIA == 4` (privada) E `TP_CATEGORIA_ESCOLA_PRIVADA` em `{1,2,3}` (exclui 4 = Filantrópica) E `TP_SITUACAO_FUNCIONAMENTO == 1` (em atividade) E `QT_TUR_MED > 0` (Tabela_Turma_2025, oferece ao menos Ensino Médio).

Resultado: **8.095 escolas elegíveis nacionalmente**, das quais **5.647 estão em municípios >100k habitantes (318 dos 319 municípios — exceção: Ibirité/MG, sem escola elegível)**.

Limpeza de outliers de porte: removida 1 escola com 4.444 matrículas de Ensino Médio em 10 salas (444 alunos/sala — erro de preenchimento). `QT_SALAS_UTILIZADAS` está top-codado em 202 nesta edição (12 escolas distintas com valor idêntico) — por isso `QT_MAT_MED` (matrículas) é a métrica de porte usada, não salas.

## 3. Parte 1 — Score de priorização de cidades

Aplicado aos 318 municípios elegíveis. Cada critério é normalizado por percentil (rank/N, 0 a 1) dentro desse universo.

```
score_priorizacao = 0.40 × percentil(score_socioeconomico)
                   + 0.30 × percentil(qtd_escolas_elegiveis)
                   + 0.30 × percentil(enem_media_praca)
```

- **score_socioeconomico** (peso 0.40): `0.85 × score_renda + 0.15 × percentil(população 0-17)`, onde `score_renda = 0.80 × %população em domicílios >5 SM + 0.20 × %população em domicílios 3-5 SM` (Tabela 10296). Não usa PIB per capita (mistura riqueza industrial/institucional com renda familiar real — lição já registrada neste projeto).
- **qtd_escolas_elegiveis** (peso 0.30): contagem de escolas elegíveis no município — é uma contagem simples (percentil do número de escolas), não pondera por porte nem qualidade; sinaliza concentração de mercado privado instalado, não riqueza.
- **enem_media_praca** (peso 0.30): média **ponderada por `qtd_participantes_enem`** (não é mais média simples das médias por escola — revisão de 21/07) do `enem_media_geral` (ver seção 5) das escolas elegíveis do município que têm dado ENEM vinculado. Motivo da revisão: a média simples dava o mesmo peso a uma escola de 15 participantes e a uma de 300 — a versão ponderada reflete melhor a praça como o aluno médio a experimenta. Municípios sem nenhuma escola com dado ENEM recebem o pior percentil (não são excluídos).

**Resultado (versão ponderada)**: Top 10 = Belo Horizonte, Niterói, Goiânia, Vitória, Florianópolis, Brasília, Porto Alegre, São José dos Campos, Recife, Ribeirão Preto. Script: `poliedro_04_score_cidades.py`.

**Nota sobre São José dos Campos:** é a sede nacional do Poliedro (CEV — Centro Empresarial do Vale, confirmado no site institucional). Sua presença no Top 10 provavelmente reflete um mercado onde a marca já tem forte presença, não uma oportunidade nova — leitura diferente das demais 9 cidades.

**Resolvido (21/07):** a mudança para média ponderada troca a 3ª colocação — Goiânia passa Vitória. Em vez de escolher entre as duas, a Parte 2 passou a usar as **4** cidades de maior score (Belo Horizonte, Niterói, Goiânia, Vitória) — cobre tanto a versão simples quanto a ponderada do critério, sem descartar nenhuma análise já validada, e ainda excede o mínimo de 3 cidades pedido pelo case.

## 4. Parte 2 — Score de destaque de escolas

Aplicado às 4 cidades de maior `score_priorizacao` (Belo Horizonte, Niterói, Goiânia, Vitória — topo do ranking da Parte 1, cobrindo tanto a versão simples quanto a ponderada do critério de qualidade ENEM). Percentis calculados sobre o universo nacional de 5.647 escolas elegíveis (não só dentro da cidade), para evitar instabilidade em praças com poucas escolas.

**Nota sobre escopo do percentil (22/07):** aqui (Parte 2, `poliedro_05_score_escolas.py`) o percentil é calculado sobre as 5.647 escolas elegíveis — mas isso não afeta o Top 5 de cada cidade (verificado: mesmas escolas, mesma ordem, mudando o escopo pra só as 4.121 com ENEM confiável — só o valor decimal do score varia ~0,005). Já o script irmão `poliedro_05b_score_destaque_nacional.py`, usado só para o funil/Golden Leads (seção 7, bônus de portfólio, não resposta formal ao case), calcula o percentil **só entre as 4.121 escolas com ENEM confiável** — porque ali a contagem final de Golden Leads É sensível ao escopo (869 com percentil só-confiáveis vs. 953 com percentil sobre as 5.647), e deixar escolas de amostra não-confiável "competirem" no percentil de quem é confiável seria inconsistente. Os 869/129 usados no deck e docs vêm desse segundo escopo.

**Validação empírica:** o Colégio Arena (Goiânia), 1º colocado na nova cidade, já aparece como depoimento de escola parceira no site institucional do Poliedro — um sinal de que o método aponta para escolas com fit real, não aleatório.

```
score_destaque = 0.60 × percentil(enem_media_geral) + 0.40 × percentil(indice_infra)
```

- **enem_media_geral** (peso 0.60, critério ENEM): média das 5 notas (CN, CH, LC, MT, Redação) dos participantes vinculados à escola (`CO_ESCOLA` em RESULTADOS_2025.csv), restrito a `TP_DEPENDENCIA_ADM_ESC==4` e `TP_SIT_FUNC_ESC==1`.
- **indice_infra** (peso 0.40, critério Censo): soma 0-5 de `IN_LABORATORIO_CIENCIAS + IN_LABORATORIO_INFORMATICA + IN_BIBLIOTECA + IN_QUADRA_ESPORTES_COBERTA + IN_AUDITORIO`.
- **Confiabilidade**: escolas com menos de 10 participantes ENEM vinculados não entram no ranking (média de amostra pequena é ruído, não sinal).
- `QT_MAT_MED` (matrículas) é reportado como contexto, não entra no score.

Script: `poliedro_05_score_escolas.py`. Resultado completo em `data/outputs/02_escolas_destaque_top3_cidades.csv`.

## 5. Extração ENEM 2025

`RESULTADOS_2025.csv` (nova estrutura 2025, ~4,8M linhas) filtrado por `CO_ESCOLA` não nulo + `TP_DEPENDENCIA_ADM_ESC==4` + `TP_SIT_FUNC_ESC==1` → 272.799 participantes em 8.200 escolas privadas. Script: `poliedro_02_extrair_enem.py`.

## 6. Bônus — Crescimento de matrículas de Ensino Médio (2023 → 2025)

Reaproveita `microdados_censo_escolar_2023.zip` (já estava na pasta de um exercício anterior; `QT_MAT_MED` já existia nesse schema, sem custo de novo download) cruzado por `CO_ENTIDADE` (código nacional de escola, estável entre edições) com `QT_MAT_MED` de 2025.

`crescimento_pct = (QT_MAT_MED_2025 - QT_MAT_MED_2023) / QT_MAT_MED_2023 × 100`

Cobertura: 85,8% das 5.647 escolas do recorte têm correspondência em 2023 (o restante são escolas novas ou mudança de código). Agregado por cidade usando **mediana** (não média), para não deixar 1-2 escolas com base muito pequena distorcerem o resultado (ex.: escola que foi de 2 para 56 matrículas gera crescimento de +2.687%, um valor real mas não representativo). Não altera os scores das Partes 1 e 2 — é uma coluna de contexto/momentum. Script: `poliedro_06_crescimento_matriculas.py`. Resultado: `data/outputs/03_crescimento_matriculas_2023_2025.csv`.

## 7. Ordem de execução (reprodutibilidade)

1. `poliedro_01_baixar_dados.py` — baixa Censo Escolar 2025 e população total IBGE (roda local, precisa de rede).
2. `poliedro_02_extrair_enem.py` — médias ENEM por escola.
3. `poliedro_03_extrair_censo.py` — escolas privadas elegíveis.
4. `poliedro_03b_extrair_enderecos.py` — endereço/CEP das escolas elegíveis (usado no passo 11).
5. `poliedro_04_score_cidades.py` — Parte 1.
6. `poliedro_05_score_escolas.py` — Parte 2 (Top 5 por cidade, resposta formal ao case).
7. `poliedro_05b_score_destaque_nacional.py` — mesmo `score_destaque`, mas sobre as 5.647 escolas nacionais (não só as 4 cidades) — base do funil e da segmentação comercial (bônus, passos 9-11). Gera `data/outputs/funil_escolas_pontuadas.csv`.
8. `poliedro_06_crescimento_matriculas.py` — bônus, crescimento 2023-2025 (opcional, não bloqueia os anteriores).
9. `poliedro_07_funil.py` — gera o gráfico de funil de priorização (8.095 → 5.647 → 4.121 → 869), terminando no universo único de Golden Leads (score ≥ 0,70). Contagens calculadas ao vivo a partir dos CSVs dos passos 3, 5b e 9 (não hardcoded).
10. `poliedro_08_visual_cosmos.py` — gera um visual procedural (estrelas + anéis concêntricos) usado no slide do Cosmos, sem dependência de internet/geração de imagem por IA.
11. `poliedro_09_icp_poliedro.py` — dentro do universo de 869 Golden Leads, tagueia cada escola com um segmento comercial baseado na posição dela no próprio município: Líder local (1º lugar), Desafiante (2º-5º lugar), Outras posições (6º+) ou Sem comparação local (cidade com <3 escolas confiáveis). Substitui a leitura anterior "129 Golden Leads vs 740 Qualificadas" — não é mais uma segunda faixa de score, é uma tag de posição dentro do mesmo universo. Gera `data/outputs/04_golden_leads_segmentadas.csv` (inclui `codigo_escola`, usado no passo 11).
12. `poliedro_10_segmentacao_comercial.py` — gráfico de barra segmentada com a distribuição dos 4 tags do passo 11.
13. `poliedro_11_geocodificar_ceps.py` — **roda localmente, precisa de internet** (o sandbox do assistente tem a rede bloqueada para APIs externas como ViaCEP). Geocodifica o CEP das Golden Leads das 10 cidades prioritárias para obter o bairro (primeiro passo de uma leitura geográfica mais fina que hoje só existe a nível de município). Não calcula renda por bairro — isso exigiria um pipeline maior com setor censitário do IBGE + geopandas, documentado como próximo passo no próprio script.
14. `poliedro_12_graficos_cidades.py` — gráficos Top10 e dispersão (tema escuro) a partir de `01_cidades_prioritarias.csv`.
15. `poliedro_13_detectar_salas_vitrine.py` — bônus, roda depois dos passos 2 e 3b. Detecta nacionalmente o padrão de "sala vitrine" (unidade pequena com média ENEM muito acima das unidades-irmãs da mesma mantenedora/cidade) — generaliza a checagem ad-hoc feita sobre o Farias Brito. Gera `data/outputs/13_salas_vitrine_suspeitas.csv`.

## 8. Limitações documentadas

1. **Vínculo escola-participante mudou em 2025.** `CO_ESCOLA` ("código da escola de conclusão do ensino médio", definição literal do dicionário) só existe em `RESULTADOS_2025.csv`, preenchido em 1.739.028 de 4.810.772 linhas (36,15%). `IN_TREINEIRO` e `TP_ST_CONCLUSAO` (que indicariam se o participante é treineiro/concluinte — o que ajudaria a entender quem, entre os 63,85% sem escola, é pré-vestibulando vs. aluno regular) só existem em `PARTICIPANTES_2025.csv`. O próprio dicionário do INEP declara, em nota de rodapé, que a chave de RESULTADOS (`NU_SEQUENCIAL`) é "variável distinta da NU_INSCRICAO disponível na base de Participantes, de modo que não é possível utilizá-la para relacionar as duas bases" — ou seja, essas duas informações não podem ser cruzadas linha a linha nesta edição, o que impede reconstruir empiricamente a composição exata dos sem vínculo. Nota à parte: pré-vestibular não implica ausência de `CO_ESCOLA` — cursinhos que são eles próprios registrados como "escola" no Censo (ex.: unidades de pré-vestibular da rede Farias Brito) podem aparecer normalmente com CO_ENTIDADE próprio.
2. **Viés regional de adesão ao ENEM.** Em praças com forte oferta de vestibular próprio (ex.: São Paulo — USP, Unicamp, Unesp, transferências Unifesp/UFABC), parte dos melhores alunos de escolas de elite pode não priorizar o ENEM, subestimando essas escolas no score.
3. **"Salas vitrine" de redes de ensino.** Unidades pequenas de uma mesma rede/mantenedora, na mesma cidade, podem reportar médias infladas por usarem um grupo curado de alunos. Não é um caso isolado do Farias Brito: `poliedro_13_detectar_salas_vitrine.py` generaliza a checagem (agrupa por `NU_CNPJ_MANTENEDORA` + município, exclui o CNPJ-placeholder 99999999999999 de "mantenedora não informada") e encontra **4 grupos confirmados nacionalmente** (rodado em 22/07): Christus Colégio Pré-Universitário (34 part., 779) vs. irmã de 74 part./654 — gap 125 pts; Farias Brito Colégio de Aplicação (30 part., 793) vs. 3 irmãs somando 565 part./670 — gap 123 pts; Colégio Gabarito, Uberaba/MG (31 part., 734) vs. irmã de 68 part./641 — gap 93 pts; Ari de Sá Cavalcante - Major Facundo (31 part., 766) vs. 3 irmãs somando 407 part./698 — gap 68 pts. Três dos quatro grupos são em Fortaleza/CE, um em Uberaba/MG — nenhum dos dois municípios está nas 10 cidades prioritárias nem entre as 4 do case formal, então **não afeta** as 20 escolas do Top 5×4 desta entrega, mas **afeta ~4 das 869 Golden Leads** (aparecem com `score_destaque` inflado e tag "Líder local"/alto rank no funil bônus). Todas passam no piso de 10 participantes — o filtro de confiabilidade mitiga ruído estatístico, mas não pega esse padrão específico.
4. **`score_destaque` (Parte 2) não mede renda familiar.** Testado cruzando o percentil de renda da cidade (Parte 1) com a posição de cada escola: percentil médio de renda da cidade é 0,85 nas escolas Líder/Desafiante de score mais alto e 0,74 nas demais Golden Leads — correlação positiva, porém moderada, não uma separação limpa por classe. O Censo Escolar não informa renda por aluno/família, então a tag de segmento comercial (seção 3, passo 9) é uma hipótese estratégica plausível, não uma segmentação por renda comprovada estatisticamente.
5. **Escolas filantrópicas excluídas** (categoria 4 do Censo — inclui APAE e similares) por não representarem o segmento de mercado privado relevante para este objetivo.
6. **Recorte nacional, não regional** — decisão de manter todas as 27 UFs em vez de restringir a uma região, dado que o volume de dados era processável no prazo.
7. **Segmento comercial (Líder/Desafiante) não sabe qual sistema de ensino a escola já usa.** Nenhuma fonte pública (Censo, ENEM, IBGE) informa isso. Piloto manual (busca individual, 21/07) nas 20 escolas de maior `score_destaque` nacional: cerca de metade já é dona do próprio sistema de ensino concorrente ou cliente declarada de um sistema estabelecido (Ari de Sá Cavalcante = origem do SAS/Arco; Objetivo, Etapa e Gabarito = donas de sistema próprio; Master = cliente Eleva; Podion = cliente Sistema Anglo; Embraer/Juarez Wanderley = Rede Pitágoras/Kroton). As demais (Colégio Cognitivo, Colégio de São Bento, Marília Mattoso, Santo Agostinho, Liceu Jardim, Escola São Domingos) não sinalizam publicamente nenhum sistema comercial — sinal direcional, não confirmação; precisa de verificação individual antes de qualquer prospecção real. Liceu Jardim (Santo André) foi o único caso com declaração explícita de "não vinculado a nenhum sistema fechado".
8. **Nome de arquivo desatualizado (cosmético).** `data/outputs/02_escolas_destaque_top3_cidades.csv` mantém o nome "top3" por compatibilidade com o restante do pipeline, mas contém as 4 cidades (Belo Horizonte, Niterói, Goiânia, Vitória) desde a revisão de 21/07.
9. **Sem benchmark setorial externo dedicado à educação básica privada.** Diferente de projetos anteriores deste portfólio que usaram o SEBRAE como benchmark (mercado geral de pequenos negócios), este projeto não incorporou uma fonte de contexto setorial externa — o Anuário Brasileiro da Educação Básica (Todos Pela Educação + Editora Moderna + Fundação Santillana, edição 2025 já inclui dado agregado da rede privada) é a fonte mais próxima de um "SEBRAE da educação básica" e não foi formalmente incorporada ao projeto, só usada para orientar esta resposta.
