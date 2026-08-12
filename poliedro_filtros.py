"""
Case Poliedro — filtros de escopo compartilhados pelo pipeline.

Este módulo existe por causa de um bug que aconteceu DUAS vezes (28/07): o
filtro de Sistema S estava implementado solto dentro do `poliedro_09`, e
qualquer passo novo que montasse universo direto do
`funil_escolas_pontuadas.csv` (passos 25, 26 e 28) reintroduzia as escolas
SESI/SENAI/SESC/SENAC sem perceber. Centralizar aqui garante que o escopo do
projeto seja aplicado num lugar só.

ESCOPO DO PROJETO (não mudar sem alinhar com o Gui): o mapeamento cobre
escolas PRIVADAS que são prospect comercial de um sistema de ensino
licenciado. Sistema S está fora.

Por que Sistema S está fora: SESI, SENAI, SESC e SENAC são mantidos pelas
confederações patronais (Serviço Social da Indústria/Comércio), com
financiamento por contribuição compulsória sobre a folha das empresas, e já
operam sistema de ensino PRÓPRIO (ex.: Sistema SESI-SP de Ensino). Ou seja:
não compram sistema de ensino de terceiros — não são prospect, e a
mensalidade (quando existe) não segue lógica de mercado.

Nota técnica que vale pra entrevista: no Censo Escolar essas escolas
aparecem como `TP_DEPENDENCIA = 4` (privada), não como rede pública — são
entidades privadas SEM FINS LUCRATIVOS (paraestatais), não órgãos do Estado.
O motivo de excluir é comercial (têm sistema próprio, não compram), não o
fato de serem públicas. A conclusão prática é a mesma, mas a justificativa
correta é essa.
"""

import pandas as pd

COLUNA_FLAG_SISTEMA_S = "IN_MANT_ESCOLA_PRIVADA_SIST_S"


def remover_sistema_s(escolas: pd.DataFrame, verboso: bool = True) -> pd.DataFrame:
    """Remove escolas do Sistema S (SESI/SENAI/SESC/SENAC) pela flag oficial do Censo."""
    if COLUNA_FLAG_SISTEMA_S not in escolas.columns:
        raise KeyError(
            f"Coluna '{COLUNA_FLAG_SISTEMA_S}' não está no DataFrame — sem ela não dá pra "
            "aplicar o filtro de escopo do projeto com segurança. Verifique se a base de "
            "origem é o funil_escolas_pontuadas.csv (que carrega essa coluna do Censo)."
        )
    flag = pd.to_numeric(escolas[COLUNA_FLAG_SISTEMA_S], errors="coerce")
    eh_sistema_s = flag == 1
    if verboso:
        print(
            f"[Filtro Sistema S] Removendo {eh_sistema_s.sum()} escolas "
            "(SESI/SENAI/SESC/SENAC — sistema de ensino próprio, fora do escopo)."
        )
    return escolas[~eh_sistema_s].copy()


def listar_codigos_sistema_s(funil: pd.DataFrame) -> set:
    """Devolve o conjunto de códigos de escola do Sistema S, pra auditar outras saídas."""
    flag = pd.to_numeric(funil[COLUNA_FLAG_SISTEMA_S], errors="coerce")
    return set(funil.loc[flag == 1, "codigo_escola"])
