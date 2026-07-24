"""
Case Poliedro — Passo 19 (roadmap 3.0, pedido do Gui em 24/07: "comece a
documentar qual o sistema de ensino de cada uma das escolas"): REGISTRO
PERSISTENTE de qual sistema de ensino cada Golden Lead já usa hoje.

Por que isso importa: uma Golden Lead que já usa um sistema concorrente
(Objetivo, Anglo, SAS, Positivo...) tem uma venda mais difícil (precisa
trocar de fornecedor) do que uma que usa material próprio/apostila autoral
(mais fácil de convencer a adotar um sistema pela primeira vez) ou, no
extremo, uma que já é Poliedro (não é prospect, ver poliedro_09).

Não existe base pública estruturada com essa informação — não tem como
"baixar" isso de um dataset do INEP/IBGE. É pesquisa manual, escola por
escola, via busca no site/imprensa de cada uma. Esse script não CALCULA
nada — é um registro (memória de projeto) que cresce a cada pesquisa,
igual um cache manual. Sempre que uma nova escola for pesquisada, adicione
uma linha em `REGISTROS` abaixo e rode de novo.

Achado da 1ª leva (10 escolas, busca genérica): taxa de confirmação baixa —
só 1 de 10 (Objetivo Colégio Integrado, concorrente direto).

Achado da 2ª leva (24/07 à noite, mais 8 escolas — desta vez usando os
operadores de busca `"nome da escola" "sistema de ensino" OR "material
didático"` sugeridos pelo Gui): taxa de confirmação melhorou bastante — 2 de
8 (Bahiense usa SAS, Nossa Senhora do Rosário usa Anglo, ambos concorrentes
diretos). O operador de busca importa: frases exatas entre aspas acham a
página certa do site da escola com muito mais precisão que busca livre.
Segue valendo o padrão: escolas tradicionais/confessionais/bilíngues com
identidade de marca forte (Marista, Franco-Brasileiro, Alfa Cem, Escola
Parque, Israelita) não usam sistema de terceiros — moldam a intuição
inicial de que esse perfil de escola é prospect mais difícil.

Gera: data/outputs/19_sistema_ensino_identificado.csv
"""

from pathlib import Path

import pandas as pd

OUT_DIR = Path("data/outputs")

# codigo_escola: (sistema_identificado, confianca, fonte_resumo)
# confianca: "confirmado" (o site da própria escola/notícia cita o sistema
# por nome) | "provavel_proprio" (escola tradicional/confessional, sem
# menção pública a sistema de terceiros — inferência, não confirmação) |
# "nao_identificado" (busca não trouxe sinal suficiente pra nem inferir)
REGISTROS = {
    "33065403": ("não identificado", "provavel_proprio", "Colégio Santo Agostinho (Leblon) — confessional agostiniano, tradicional, sem menção pública a sistema de terceiros"),
    "33135371": ("não identificado", "provavel_proprio", "Colégio Cruzeiro (Jacarepaguá) — escola alemã (Deutsche Schule), pedagogia própria, sem menção a sistema de terceiros"),
    "35103524": ("não identificado", "provavel_proprio", "Dante Alighieri — currículo ítalo-brasileiro reconhecido pelo governo italiano, material próprio"),
    "33062633": ("não identificado", "provavel_proprio", "Colégio de São Bento (RJ) — tradição beneditina de 163 anos, sem menção a sistema de terceiros"),
    "35399197": ("Sistema Objetivo", "confirmado", "Objetivo Colégio Integrado — usa Coleção Didática do Sistema Objetivo (concorrente direto)"),
    "33104220": ("não identificado", "nao_identificado", "Recanto Inf. Imaculada Conceição — busca não trouxe menção a sistema de ensino"),
    "33100713": ("não identificado", "nao_identificado", "Colégio Saint John (Barra da Tijuca) — busca não trouxe menção a sistema de ensino"),
    "35143406": ("não identificado", "nao_identificado", "Augusto Laranja (Moema) — parceria Cambridge International, mas sem menção a sistema de ensino nacional"),
    "35165347": ("não identificado", "nao_identificado", "Mobile Colégio — busca não retornou informação suficiente"),
    "35105314": ("não identificado", "provavel_proprio", "Colégio Franciscano Pio XII — confessional franciscano, bilíngue Cambridge, sem menção a sistema de terceiros"),
    # Segunda leva (24/07 à noite) — usando operadores de busca sugeridos pelo Gui
    # ("nome da escola" "sistema de ensino" OR "material didático").
    "33077029": ("Sistema SAS", "confirmado", "Colégio Bahiense (Barra da Tijuca) — material \"SAS Bahiense\", confirma uso do Sistema SAS"),
    "35107190": ("Sistema Anglo", "confirmado", "Colégio Nossa Senhora do Rosário (SP) — usa Sistema Anglo de Ensino no Ensino Médio"),
    "33160830": ("não identificado", "provavel_proprio", "Marista São José Barra — rede confessional marista, material institucional próprio da rede"),
    "33063419": ("não identificado", "provavel_proprio", "Colégio Franco Brasileiro — modelo bilíngue franco-brasileiro, currículo próprio + parceria Ontario Virtual School"),
    "33075425": ("não identificado", "nao_identificado", "Colégio Pentágono — menciona \"sistema\" conectando 210 mil alunos no Brasil, mas não nomeia a marca; precisa verificar melhor"),
    "33188092": ("não identificado", "provavel_proprio", "Colégio Alfa Cem Bilíngue — método fonético e material próprios, parceria Cambridge pro inglês"),
    "33184739": ("não identificado", "provavel_proprio", "Colégio Alfa Cem Bilíngue (2ª unidade) — mesma rede, método próprio"),
    "33065837": ("não identificado", "provavel_proprio", "Escola Parque (Gávea) — pedagogia construtivista/por projetos, tradição própria de 55 anos"),
    "33064040": ("não identificado", "provavel_proprio", "Escola Israelita Brasileira Eliezer Steinbarg Max Nordau — escola comunitária judaica, identidade própria"),
    # Terceira leva (24/07, batch nas Golden Leads de maior score_destaque ainda sem registro).
    "53020570": ("não identificado", "nao_identificado", "Colégio Pódion (Brasília) — descrição institucional só fala de 'programa de ensino desafiador' próprio, sem citar material de terceiros"),
    "31004651": ("não identificado", "provavel_proprio", "Colégio Santo Agostinho (BH) — confessional agostiniano, Microsoft Showcase School é certificação de tecnologia, não sistema didático de terceiros"),
    "25097539": ("não identificado", "nao_identificado", "Colégio e Curso Evolução (João Pessoa) — só cita 'material didático atualizado do mercado', sem nomear marca"),
    "23246871": ("Sistema SAS", "confirmado", "Ari de Sá Cavalcante - Mário Mamede (Fortaleza) — usa SAS (Sistema Ari de Sá), marca criada pela PRÓPRIA rede Ari de Sá e hoje vendida a +12mil escolas via Arco Educação; concorrente, mas a rede não compraria de fora"),
    "23245573": ("Sistema Eleva", "confirmado", "Master Colégio (Fortaleza) — usa material Eleva (Portal do Aluno, conteúdo interdisciplinar)"),
    "27220885": ("Sistema Poliedro", "confirmado", "Colégio Contato (Maceió) — ATENÇÃO: site do próprio colégio se declara 'parceiro exclusivo em Alagoas do Sistema de Ensino Poliedro'. Já é rede Poliedro sob outra marca — não passou pelo filtro de exclusão do passo 09 (que só olha 'POLIEDRO' no nome oficial do Censo). Ver observação abaixo do dict."),
    "26189569": ("não identificado", "provavel_proprio", "Colégio Cognitivo (Recife, unidade Casa Forte) — material 'fundamentado em livros didáticos' escolhido pela própria equipe de professores, sem sistema de terceiros citado"),
    "26534711": ("não identificado", "provavel_proprio", "Colégio Cognitivo (Recife, unidade Boa Viagem) — mesma rede/material da unidade Casa Forte"),
    "26118165": ("Sistema Equipe", "confirmado", "Colégio Equipe (Recife) — Sistema de Ensino Equipe, com editora própria (marca própria da rede, vendida a outras escolas do Norte/Nordeste)"),
    "23272430": ("Sistema SAS", "confirmado", "Ari de Sá Cavalcante - Aldeota (Fortaleza) — mesma rede/material SAS da unidade Mário Mamede"),
    "35805555": ("Sistema Pitágoras", "confirmado", "Colégio Embraer Juarez Wanderley (São José dos Campos) — gerido pelo Sistema Pitágoras de Ensino (Kroton) via Instituto Embraer; ATENÇÃO: escola de bolsa integral (~80% bolsistas), não é comprador comercial típico"),
    "32041152": ("Sistema Eleva", "confirmado", "Escola São Domingos (Vitória) — material Eleva citado em contrato público (4 volumes), ao lado de Edify (bilíngue) e Escola da Inteligência; confiança média-alta, fonte é documento contratual, não o site oficial"),
    "15168344": ("Sistema Equipe", "confirmado", "Colégio Equipe Cristal (Belém) — unidade da rede Sistema de Ensino Equipe, mesma marca própria da unidade de Recife"),
    "31333921": ("não identificado", "provavel_proprio", "Colégio Santo Agostinho (Nova Lima) — mesma rede confessional da unidade BH, sem sistema de terceiros citado"),
    "24057169": ("Sistema SAS", "confirmado", "FACEX (Natal) — corrigido pelo Gui (24/07), achado via busca direta no Google que a minha busca não trouxe: usa Sistema SAS de Ensino"),
    # Correções do Gui (24/07) — casos que a minha busca via API não achou mas ele achou rápido no Google
    # direto. Ver conversa: provável causa é que a API de busca não indexa/prioriza páginas específicas
    # (ex. vídeo institucional "SAS Educação + Colégio Pódion", ou página de resultado que só aparece em
    # busca normal do Google) do jeito que a busca nativa do Google faz.
    "53020570": ("Sistema SAS", "confirmado", "Colégio Pódion (Brasília) — corrigido pelo Gui: usa Sistema SAS de Ensino (confirmado via vídeo institucional 'SAS Educação + Colégio Pódion')"),
    "25097539": ("Sistema Bernoulli", "confirmado", "Colégio e Curso Evolução (João Pessoa) — corrigido pelo Gui: usa Sistema Bernoulli de Ensino"),
    # Rede própria Poliedro (achado 24/07 via nome no Censo, ver poliedro_09) — passou a ficar VISÍVEL nos
    # Golden Leads em vez de excluída (pedido do Gui). Sistema de ensino é óbvio pelo próprio nome, não
    # precisou de pesquisa: são literalmente unidades/franquia Poliedro.
    "35004269": ("Sistema Poliedro", "confirmado", "Colégio Poliedro (Campinas, Taquaral) — unidade própria/franquia Poliedro, nome no Censo"),
    "35009757": ("Sistema Poliedro", "confirmado", "Colégio Poliedro Unidade Centro (Campinas) — unidade própria/franquia Poliedro, nome no Censo"),
    "35175572": ("Sistema Poliedro", "confirmado", "Poliedro Colégio (São José dos Campos) — unidade própria/franquia Poliedro, nome no Censo"),
    "35134132": ("Sistema Poliedro", "confirmado", "Colégio Poliedro de Educação (São Paulo, Barra Funda) — unidade própria/franquia Poliedro, nome no Censo"),
    # Cross-check com a lista de "Escolas Associadas" do próprio site institucional do Poliedro (passada
    # pelo Gui, 24/07) contra a base de escolas do Censo — achado 1 match direto num Golden Lead atual.
    "35108923": ("Sistema Poliedro", "confirmado", "Colégio Ábaco (São Bernardo do Campo) — site oficial do Poliedro lista como Escola Associada ('Outros Estados: Colégio Ábaco...')"),
}

# Observação (24/07): o caso do Colégio Contato (27220885) revelou que o filtro de exclusão de
# "rede própria Poliedro" no passo 09 (busca "POLIEDRO" no NO_ENTIDADE do Censo) não pega parceiros/
# franquias que vendem sob marca PRÓPRIA mas usam o material Poliedro por trás (achado só via pesquisa
# manual de sistema de ensino, não dava pra prever isso de outro jeito). Vale revisar as escolas com
# sistema_ensino_identificado == "Sistema Poliedro" e decidir com o Gui se elas devem ser excluídas das
# Golden Leads (mesma lógica do poliedro_09), não só marcadas.


def montar_tabela() -> "tuple[pd.DataFrame, int]":
    """Junta o registro manual com os dados de score/segmento já calculados."""
    golden = pd.read_csv(OUT_DIR / "04_golden_leads_segmentadas.csv", dtype={"codigo_escola": str})
    linhas = []
    for codigo, (sistema, confianca, fonte) in REGISTROS.items():
        linhas.append({"codigo_escola": codigo, "sistema_ensino_identificado": sistema,
                        "confianca": confianca, "fonte_resumo": fonte})
    registro = pd.DataFrame(linhas)
    tabela = golden.merge(registro, on="codigo_escola", how="inner")[
        ["codigo_escola", "NO_ENTIDADE", "codigo_municipio", "segmento_comercial", "rede_propria_poliedro",
         "score_destaque", "sistema_ensino_identificado", "confianca", "fonte_resumo"]
    ]
    return tabela, len(golden)


def exibir_resumo(df: pd.DataFrame, total_golden_leads: int) -> None:
    print(f"[Sanity check] Escolas pesquisadas até agora: {len(df)} de {total_golden_leads} Golden Leads "
          f"totais ({len(df) / total_golden_leads * 100:.1f}%)")
    print(f"\n[Sanity check] Distribuição de confiança:\n{df['confianca'].value_counts()}")
    print(f"\n[Sanity check] Sistemas concorrentes confirmados: "
          f"{(df['confianca'] == 'confirmado').sum()}")
    ja_poliedro = df["rede_propria_poliedro"].sum()
    if ja_poliedro:
        print(f"[Sanity check] Dessas, {ja_poliedro} já são rede própria/franquia Poliedro (nome no Censo).")


def main():
    df, total_golden_leads = montar_tabela()
    exibir_resumo(df, total_golden_leads)
    df.to_csv(OUT_DIR / "19_sistema_ensino_identificado.csv", index=False, sep=";", decimal=",")
    print(f"\n[✓] Salvo em {OUT_DIR / '19_sistema_ensino_identificado.csv'}")


if __name__ == "__main__":
    main()
