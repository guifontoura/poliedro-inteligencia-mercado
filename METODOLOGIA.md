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
- **qtd_escolas_elegiveis** (peso 0.30): contagem de escolas elegíveis no município.
- **enem_media_praca** (peso 0.30): média do `enem_media_geral` (ver seção 5) das escolas elegíveis do município que têm dado ENEM vinculado. Municípios sem nenhuma escola com dado ENEM recebem o pior percentil (não são excluídos).

**Resultado**: Top 10 = Belo Horizonte, Niterói, Vitória, Florianópolis, Porto Alegre, São Caetano do Sul, Brasília, São José dos Campos, Goiânia, Jundiaí. Script: `poliedro_04_score_cidades.py`.

## 4. Parte 2 — Score de destaque de escolas

Aplicado às 3 cidades de maior `score_priorizacao` (Belo Horizonte, Niterói, Vitória — escolha não-arbitrária: simples topo do ranking da Parte 1). Percentis calculados sobre o universo nacional de 5.647 escolas elegíveis (não só dentro da cidade), para evitar instabilidade em praças com poucas escolas.

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
4. `poliedro_04_score_cidades.py` — Parte 1.
5. `poliedro_05_score_escolas.py` — Parte 2.
6. `poliedro_06_crescimento_matriculas.py` — bônus, crescimento 2023-2025 (opcional, não bloqueia os anteriores).

## 8. Limitações documentadas

1. **Vínculo escola-participante mudou em 2025.** Só ~37% das linhas de RESULTADOS têm `CO_ESCOLA` preenchido (participantes vinculados a uma escola no ato da inscrição — majoritariamente quem está cursando). Até o ENEM 2023, sociodemográfico e resultado vinham no mesmo arquivo (linkáveis por construção); em 2025 os arquivos PARTICIPANTES e RESULTADOS passaram a não compartilhar chave (nota oficial do dicionário do INEP), o que impede reconstruir empiricamente a composição exata dos 63% sem vínculo.
2. **Viés regional de adesão ao ENEM.** Em praças com forte oferta de vestibular próprio (ex.: São Paulo — USP, Unicamp, Unesp, transferências Unifesp/UFABC), parte dos melhores alunos de escolas de elite pode não priorizar o ENEM, subestimando essas escolas no score.
3. **"Salas vitrine" de redes de ensino.** Unidades pequenas de uma mesma rede/mantenedora, na mesma cidade, podem reportar médias infladas por usarem um grupo curado de alunos (confirmado empiricamente: Colégio de Aplicação Farias Brito, Fortaleza — 5 salas, 30 participantes, média 793, contra 656-686 das unidades-irmãs com 220+ participantes). Não afeta as 15 escolas do Top 5×3 apresentadas (verificado individualmente), mas é um padrão nacional não resolvido pelo piso de 10 participantes.
4. **Escolas filantrópicas excluídas** (categoria 4 do Censo — inclui APAE e similares) por não representarem o segmento de mercado privado relevante para este objetivo.
5. **Recorte nacional, não regional** — decisão de manter todas as 27 UFs em vez de restringir a uma região, dado que o volume de dados era processável no prazo.
