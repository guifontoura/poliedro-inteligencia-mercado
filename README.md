# Mapeamento de Escolas — Case Poliedro

Onde o Poliedro deveria construir share de prestígio: cidades e escolas privadas de maior relevância no Brasil, usando dados públicos (Censo Escolar INEP 2025 + Microdados ENEM 2025 + IBGE).

## Entregáveis

- `Poliedro_Mapeamento_Prestigio.pptx` — apresentação final (9 slides).
- `METODOLOGIA.md` — critérios, pesos, fórmulas e limitações, documentado para reprodução.
- `poliedro_01_*.py` a `poliedro_05_*.py` — pipeline, nessa ordem de execução.
- `data/outputs/01_cidades_prioritarias.csv` — as 318 cidades elegíveis rankeadas (Top 10 = prioritárias).
- `data/outputs/02_escolas_destaque_top3_cidades.csv` — Top 5 escolas em Belo Horizonte, Niterói e Vitória.

## Como rodar do zero

```bash
pip install -r requirements.txt

python poliedro_01_baixar_dados.py     # baixa Censo Escolar 2025 + população IBGE (precisa de internet)
python poliedro_02_extrair_enem.py     # médias ENEM 2025 por escola (precisa do zip do ENEM em data/raw/)
python poliedro_03_extrair_censo.py    # escolas privadas elegíveis
python poliedro_04_score_cidades.py    # Parte 1 — score de priorização de cidades
python poliedro_05_score_escolas.py    # Parte 2 — score de destaque de escolas
```

O microdados do ENEM 2025 (~600MB) precisa ser baixado manualmente em
https://download.inep.gov.br/microdados/microdados_enem_2025.zip e salvo em
`data/raw/microdados_enem_2025.zip` antes do passo 2 — arquivo grande demais
para automatizar sem risco de timeout.

## Estrutura

```
data/
  raw/       — dados brutos baixados (Censo, ENEM, IBGE) e caches intermediários
  outputs/   — resultados finais (CSVs rankeados, gráficos)
```

## Não relacionados a este case

`pipeline.py`, `gerar_slides.py`, `analises_complementares.py`, `teste_analise.py`,
`mercado_educacional_local.db`, `escolas_premium_potencial.csv` e
`Mapeamento_Escolas_Poliedro.pptx` são de um exercício anterior (venda de
software educacional B2B) — mantidos na pasta mas não fazem parte desta
entrega. Ver METODOLOGIA.md para detalhes de por que a metodologia daquele
exercício (PIB per capita direto) não foi reaproveitada aqui.
