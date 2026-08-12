# Estado do Projeto — Case Poliedro (leia isto primeiro num chat novo)

Última atualização: 12/08/2026

## O que é este projeto
Case de Analista de Inteligência de Mercado pra Poliedro Sistema de Ensino (processo seletivo). Pergunta central: "onde o Poliedro deveria construir share de prestígio?". Duas partes formais: Parte 1 — 10 cidades prioritárias, metodologia justificada. Parte 2 — dentro de pelo menos 3 dessas 10 cidades, ranquear escolas com ≥2 critérios (1 do Censo Escolar/INEP + 1 do ENEM) e listar as 5 de maior destaque em cada uma. Entrega: dashboard Power BI (3 páginas) + `METODOLOGIA.md` (existe, reescrito em 12/08 — ver abaixo). Ensaio de apresentação oral **não é mais necessário** (Gui, 12/08) — o objetivo agora é publicar o case no GitHub e no LinkedIn.

## Onde estão as coisas
- Pipeline: scripts `poliedro_XX_*.py` na raiz, cada um uma etapa (extração/tratamento/enriquecimento).
- **Ordem pra rodar do zero:** `poliedro_15` → `poliedro_16` → `poliedro_19` → `poliedro_29` → `poliedro_16b` (o porquê dessa ordem estranha está documentado em `POWER_BI_GUIA.md`).
- CSVs finais pro Power BI, em `data/outputs/`: `29_universo_completo_powerbi.csv` (nível escola, 4.444 linhas), `14_cidades_powerbi.csv` (nível cidade), `16_regioes_sp_rj_com_renda.csv` (nível bairro/distrito, só São Paulo e Rio).
- **`POWER_BI_GUIA.md` (+ `.html`) é a fonte de verdade técnica do dashboard** — passo a passo de cada página, referência de toda coluna, e uma seção "Erros comuns" com todo problema real já resolvido e a causa raiz. Leia antes de reconstruir ou debugar qualquer coisa no Power BI.
- Arquivo Power BI Desktop: `poliedro-mapeamento`.

## Estrutura decidida do dashboard (3 páginas — não crie uma 4ª sem motivo forte)
1. **Visão Executiva** — Parte 1 do case (10 cidades, KPIs, mapa, ranking nacional).
2. **Inteligência Comercial** — bairro/distrito em SP e RJ. Não é exigência literal do case — é achado do Gui (essas 2 cidades saem do Top 10 nacional por diluição estatística do score agregado; RJ fica em 19º, SP em 29º, números reais documentados no guia) e prioridade de negócio confirmada em reunião.
3. **Ranking de Escolas Prioritárias** (renomeada em 12/08, nome anterior "Escolas Prioritárias & Explorador") — Parte 2 do case (top 5 escolas por cidade, curado via slicer em Bloco + slicer de Cidade — ver pendência #3, resolvida) + exploração livre + card resumo de metodologia.

## Decisões técnicas que não devem ser refeitas do zero
- Medidas DAX manuais (ex. `Qtd Escolas`) moram numa tabela calculada separada `_Medidas` (`{BLANK()}`), nunca dentro de `29_universo_completo_powerbi` — senão qualquer reimportação da tabela 29 derruba a medida (já aconteceu 2x). Os relacionamentos (`29↔14_cidades` por `codigo_municipio`, `29↔16_regioes` por `chave_regiao`) têm o mesmo problema e não têm como ser blindados — se excluir e reimportar a tabela 29, precisam ser recriados manualmente na aba Modelo.
- `score_destaque` já combina ENEM + infraestrutura (Censo) + seletividade + inclusão — não criar outro score novo sem motivo forte (peso arbitrário sem justificativa quebra a metodologia).
- PIB per capita municipal não é bom proxy de renda familiar — usa-se renda mediana do responsável (Censo IBGE 2022).
- São Paulo e Rio nunca são misturados numa mediana só (renda, ENEM etc.) — sempre calculados separadamente, patamares muito diferentes.

## Regra de conduta desta sessão (pedido do Gui, 07/08)
**Sempre pedir confirmação antes de começar a editar via Cowork (computer-use/controle de tela)** — não só avisar depois de terminar. Motivo do Gui: essa funcionalidade custa muito token e ainda não está estável (já travou em bug de redimensionamento de janela do Power BI Desktop nesta sessão). Isso vale só pra controle de tela (mouse/teclado/screenshot); editar arquivo direto (`.py`, `.json` do relatório PBIR etc.) não precisa dessa confirmação, mas abrir o Power BI Desktop pra verificar o resultado, sim.

## Pendências conhecidas
1. ~~Cartões que usam `Qtd Escolas` mostrando "4 Mil"/separador errado~~ — **resolvido em 07/08.** Causa raiz real não era locale nem a medida: cada cartão (visual "Cartões" novo) tem sua própria seção "Formato de dados" com "Separador de milhares" desligado por padrão e, num caso (Desafiantes), "Número decimal" com 3 casas em vez de "Número inteiro" (por isso aparecia "1020,..." cortado). Corrigido cartão a cartão (Total Mapeado, Líder Local, Desafiantes, Clientes Poliedro Atuais). Média ENEM já herdava o formato certo da medida, não precisou mexer. Também setei, por segurança: Opções > Arquivo Atual > Configurações regionais > "Localidade padrão da cadeia de caracteres pra datas e números" = Português (Brasil) (estava "Automático") + "Unidades de exibição padrão pra 'none'" marcado — isso já limpou o eixo X da página 2 (mostrava "2 Mil" agora mostra "2000"). Fica documentado: se um cartão novo aparecer com número sem separador, o primeiro lugar pra olhar é Formatar visual > Geral > "Formato de dados" daquele cartão específico, não as Opções do arquivo.
2. ~~Fundir/remover a aba "Roadmap & Metodologia" e qualquer aba solta de teste~~ — **resolvido em 07/08.** "TESTES" excluída; "Roadmap & Metodologia" (estava vazia) virou a página 3 de verdade, renomeada pra "Escolas Prioritárias & Explorador" (depois "Ranking de Escolas Prioritárias", 12/08). Arquivo hoje tem só as 3 páginas decididas.
3. ~~Construir a curadoria Top 5 escolas por cidade na página 3~~ — **resolvido em 12/08, sem construir visual novo.** O slicer em Bloco Top 5/Top 10/Demais escolas (pendência #6, já pronto) + o slicer de Cidade já reproduzem exatamente essa curadoria: `rank_municipio` reseta por cidade e a tabela-ponte `29b_faixas_rank_bridge` inclui toda escola rank≤5 da própria cidade, pras 311 cidades do universo. Clicar "Top 5" + selecionar as cidades da apresentação = a tabela curada. `POWER_BI_GUIA.md` atualizado (seção "Curadoria pra Parte 2 do case") pra refletir isso — não recomenda mais um 2º visual hardcoded.
4. ~~Escrever/atualizar o documento de metodologia~~ — **resolvido em 12/08.** `METODOLOGIA.md` **já existia** (não era uma pendência real — engano meu numa sessão anterior, corrigido pelo Gui) mas estava congelado desde 22/07 (commit `b151aed`), descrevendo só `poliedro_01`-`13`. Reescrito do zero pra refletir o pipeline atual: fórmula do score nacional revisada (60/40 → **75/15/5/5** ENEM/infra/seletividade/inclusão, script `poliedro_05b`), recorte ampliado (6.308 → 4.706 confiáveis → **4.444** pós filtro Sistema S), produto Polígono (`poliedro_25`, 1.017 escolas), Golden Leads atual (**1.127**, não mais os 869 antigos), escopo nacional real (**311 cidades**, não só as 4 da Parte 2 formal), metodologia da página 2 (renda por bairro/distrito, `regiao_oportunidade`) e validação de estabilidade temporal ENEM 2024×2025 (`poliedro_27`). A fórmula da Parte 2 formal do case (Top 5×4 cidades, `poliedro_05`) **continua 60/40 ENEM/infra** — não foi alterada, é intencionalmente diferente da versão nacional/bônus.
5. ~~Ensaiar a apresentação de 10 min~~ — **removida em 12/08, a pedido do Gui ("não precisa mais").** Objetivo mudou pra publicação no GitHub/LinkedIn, não apresentação oral. `Roteiro_Apresentacao_Oral.md` continua no repo mas não é mais um entregável ativo — não foi atualizado com os números novos, se for reaproveitado no futuro precisa de revisão.
6. ~~Slicer em Bloco Top 5 / Top 10 / Demais escolas na página 3~~ — **resolvido e confirmado funcionando em 09/08.** Solução final: tabela-ponte `poliedro_29b_faixas_rank_bridge.py` → `data/outputs/29b_faixas_rank_bridge.csv` (cada escola 1 linha por faixa que pertence, cumulativo de verdade — 7.842 linhas). Passo a passo em `POWER_BI_GUIA.md`, seção "Slicer em Bloco — Top 5 / Top 10 / Demais escolas".
7. **Nenhuma pendência aberta de construção de dashboard.** Restam só verificações finais antes de publicar — ver seção "Checklist pré-publicação" abaixo.

## Limitação documentada em 09/08: corte de ≥10 participantes no ENEM
Gui notou que "Escola Verde" e "Colégio Lumiar" (Ponta da Praia, Santos) não aparecem na base final. Investigado: as duas existem no INEP bruto, mas `confiavel_enem = False` (`qtd_participantes_enem < 10`, constante `MIN_PARTICIPANTES_CONFIAVEL` em `poliedro_05_score_escolas.py`) — filtro aplicado em `carregar_universo_confiavel()` (`poliedro_29`) desde a primeira versão do pipeline, não é bug novo. Adicionada frase no card "Limitações conhecidas" da página 3 (visual `9576a8a49a0b511c1a27`, textbox) citando esse corte explicitamente, com o Lumiar como exemplo. Editado direto no PBIR (`.Report/definition/pages/164c16d10a492a703a50/visuals/9576a8a49a0b511c1a27/visual.json`) — Gui só precisa abrir o Power BI Desktop e recarregar/salvar pra ver a mudança (não precisa reimportar tabela nem mexer em relacionamento).

## Slicer Golden Leads x Outras Escolas na página 1 — bookmark trocado por tabela-ponte (09/08)
Mesmo pedido/motivo do slicer em Bloco da página 3: os 2 "Indicadores" (bookmarks) "Golden Leads"/"Outras Escolas" davam erro/quebravam silenciosamente. Duas iterações:

1ª tentativa: coluna `segmento_golden_lead` direto em `poliedro_29_universo_completo_powerbi.py` (só 1 valor marcado "Golden Leads (1.127)", resto em branco — funcionava como liga/desliga de 1 bloco só). Essa coluna **continua no arquivo, inofensiva, não usada mais** — Gui pediu um 2º bloco de verdade mostrando "Outras Escolas (4.444)" também, o que uma coluna comum não resolve (uma Golden Lead precisaria estar em 2 categorias ao mesmo tempo — mesmo problema estrutural do Top 5/Top 10/Demais escolas).

Solução final: **tabela-ponte**, `poliedro_29c_golden_leads_bridge.py` → `data/outputs/29c_golden_leads_bridge.csv` — toda escola ganha 1 linha "🔵 Outras Escolas (4.444)", Golden Leads ganham uma 2ª linha extra "🟡 Golden Leads (1.127)" (5.571 linhas no total). **Confirmado funcionando em 09/08** (2 blocos lado a lado, emoji corretos após corrigir encoding para `utf-8-sig`, ordem via `segmento_ordem`, botões antigos e bookmarks removidos). Passo a passo completo em `POWER_BI_GUIA.md`, seção "Modo de Análise — Golden Leads x Outras Escolas".

## Página 2 (Inteligência Comercial) — estado real em 12/08
Estava mais avançada do que a pendência antiga sugeria (gráfico de dispersão, slicer de cidade em bloco, caixa "Como ler" e as duas tabelas já existiam). Corrigido em 07/08:
- Tabela "Regiões prioritárias" não tinha ordenação por renda — adicionada ordenação decrescente por `renda_mediana_responsavel`.
- Tabela "Escolas da região selecionada" só tinha `NO_ENTIDADE` e `bairro` — adicionadas `score_destaque`, `sistema_ensino_identificado`, `ja_cliente_poliedro_qualquer_marca`, `distancia_parceiro_atual_km`.
- Filtro `amostra_significativa = Verdadeiro` estava só no gráfico de dispersão — movido/adicionado também em "Filtros nesta página".
Relacionamento `29↔16_regioes` por `chave_regiao` já existia e funciona (testado: clicar numa região filtra a tabela de escolas corretamente).

**Corrigido em 12/08 (4 achados via debug ao vivo com o Gui, todos confirmados resolvidos):**
- **Filtro `regiao_oportunidade = Verdadeiro` removido da tabela "Regiões prioritárias".** Estava escondendo por completo bairros de renda abaixo da mediana da própria cidade (Santa Cruz, Bangu, Realengo, Campo Grande, Jardim Carioca, Curicica no RJ) mesmo quando bem posicionados no ranking ENEM — Gui: recrutadora deveria poder ver qualquer bairro top-10 ENEM pra prospecção manual, renda não devia ser pré-requisito de visibilidade. Coluna `regiao_oportunidade` continua disponível, só não filtra mais o visual por padrão.
- **Coluna de exibição "Bairro/Distrito" trocada de `bairro` pra `regiao`** na tabela "Escolas da região selecionada" — `bairro` é o campo bruto do Censo (pode divergir do `regiao` geocodificado usado no relacionamento; ex.: 2 escolas "Sao Luis Colegio" com `bairro=VILA MARIANA` idêntico mas `regiao` diferente, Moema vs. Jardim Paulista — causava a impressão de escola "no bairro errado" ao clicar numa região).
- **Tile fantasma "(Em branco)" no slicer de `cidade` explicado e corrigido.** Não é erro de dado (CSVs sem blanks) — é o comportamento automático do Power BI pra relacionamento um-para-muitos sem integridade referencial, quando ~4.270 escolas nacionais fora de SP/RJ (`chave_regiao=NaN` de propósito) não casam com a tabela 16. Corrigido marcando só SP/RJ manualmente no slicer (alternativa: "Pressuponha integridade referencial" no relacionamento).
- **Gradiente de cor da Legenda (`qtd_golden_leads`) no gráfico de dispersão — Resumo trocado pra Média.** Contagem e Soma davam cor máxima pro valor errado (Contagem: valor mais comum, não o maior; Soma: multiplica pelo tamanho do grupo, distorce). Média (ou Mín/Máx, equivalentes aqui) é o correto porque cada bolha já é um grupo de valor único.

Detalhes completos de cada fix em `POWER_BI_GUIA.md` (seções da página 2 + "Erros comuns").

## Checklist pré-publicação (GitHub/LinkedIn) — 12/08
- [x] Dashboard funcionando nas 3 páginas (slicers, tabelas, gráficos, botão Limpar filtros em 1 e 3).
- [x] `METODOLOGIA.md` reescrito e batendo com os números atuais do pipeline (4.444 total, 1.127 Golden Leads, 75/15/5/5 nacional, 60/40 na resposta formal, 311 cidades).
- [x] `POWER_BI_GUIA.md` atualizado com todos os fixes de 09/08 e 12/08.
- [ ] Rodar o pipeline do zero (`poliedro_01` em diante) numa checagem final antes de publicar, pra confirmar que não há passo manual escondido — não feito ainda nesta sessão.
- [ ] Decidir se `Roteiro_Apresentacao_Oral.md` é removido do repo ou mantido como está (desatualizado, não é mais entregável ativo).

## Como retomar num chat novo
Cole algo como: "Estou continuando o Case Poliedro. Leia `ESTADO_DO_PROJETO.md` e `POWER_BI_GUIA.md` na pasta do projeto antes de responder. Pendência de hoje: [descreva]." Isso já traz o essencial sem depender de eu lembrar da conversa antiga — os arquivos são a fonte de verdade, não o histórico do chat.
