from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from starlette.responses import RedirectResponse
import pandas as pd

STATES = {
    "AC": "Acre",
    "AL": "Alagoas",
    "AP": "Amapá",
    "AM": "Amazonas",
    "BA": "Bahia",
    "CE": "Ceará",
    "DF": "Distrito Federal",
    "ES": "Espírito Santo",
    "GO": "Goiás",
    "MA": "Maranhão",
    "MT": "Mato Grosso",
    "MS": "Mato Grosso do Sul",
    "MG": "Minas Gerais",
    "PA": "Pará",
    "PB": "Paraíba",
    "PR": "Paraná",
    "PE": "Pernambuco",
    "PI": "Piauí",
    "RJ": "Rio de Janeiro",
    "RN": "Rio Grande do Norte",
    "RS": "Rio Grande do Sul",
    "RO": "Rondônia",
    "RR": "Roraima",
    "SC": "Santa Catarina",
    "SP": "São Paulo",
    "SE": "Sergipe",
    "TO": "Tocantins",
}

INDICATOR_OPTIONS = [
    "VL_QUANTIDADE",
    "VL_PESO_KG",
    "VL_FOB",
]

OPERATION_OPTIONS_REVERSER = {"import": "importação", "export":"exportação"}

DELIMITER = ";"

main = FastAPI()

main.add_middleware(
    CORSMiddleware,
    # todo: poderia limitar ao localhost e um wildcard para *.herokuapp.com
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=True,
)

# Importando os dados
file_path = "data/f_comex.csv"
dataset = pd.read_csv(file_path, delimiter=DELIMITER)


@main.get("/")
def home():
    return RedirectResponse(url="/docs/")


@main.get("/cod_ncm_listing/")
def cod_ncm_listing():
    """Listagem com os códigos de produto"""
    return dataset["COD_NCM"].unique().tolist()


@main.get("/oepration_statistics/{year}/{operation}/{cod_ncm}")
def get_operation_statistics(year: int, operation: str, cod_ncm: int):
    """Obtém dados de movimentação"""

    filters = (
        (dataset["ANO"] == year)
        & (dataset["MOVIMENTACAO"] == OPERATION_OPTIONS_REVERSER[operation])
        & (dataset["COD_NCM"] == cod_ncm)
    )

    df = dataset[filters].groupby(by="MES")[INDICATOR_OPTIONS].sum()
    df.reset_index(level=0, inplace=True)  # remove MES como index

    return df.to_dict()


@main.get("/via_statistics/{year}/{operation}/{cod_ncm}")
def get_via_statistics(year: int, operation: str, cod_ncm: int):
    """Obtém dados de uso da via"""

    filters = (
        (dataset["ANO"] == year)
        & (dataset["MOVIMENTACAO"] == OPERATION_OPTIONS_REVERSER[operation])
        & (dataset["COD_NCM"] == cod_ncm)
    )

    filtered = dataset[filters]

    # Calcula o uso percentual da via
    count = pd.DataFrame(
        {
            "code": filtered["COD_VIA"].value_counts().index,
            "count": filtered["COD_VIA"].value_counts().values,
        }
    )
    total = count["count"].sum()
    count["as_percentage"] = count["count"].apply(lambda x: round(x / total * 100))

    return count.to_dict()


@main.get("/states_contribution/")
def get_states_contribution():
    """Caclula a contribuição percentual de cada estado
        para cada indicador
    Retorna:
        pd.DataFrame: Tabela com as contribuições percentuais por estado
    """

    # agrupa por estado e soma os totais
    total_by_state = dataset.groupby(["SG_UF"])[INDICATOR_OPTIONS].sum()
    total_by_state.reset_index(level=0, inplace=True)  # remove SG_UF como index externo

    # calcula os percentuais por estado
    for indicator in INDICATOR_OPTIONS:
        # nome da nova coluna com a contribuição percenutal
        new_col_name = f"{indicator}_CONTRIB_%"

        total = total_by_state[indicator].sum()
        total_by_state[new_col_name] = total_by_state[indicator].apply(
            lambda x: round(x / total * 100, 2)
        )

    # Substitui a sigla pelo nome do estado
    total_by_state["SG_UF"] = total_by_state["SG_UF"].apply(
        lambda x: STATES.get(x, "Exportação")
    )

    return total_by_state.to_dict()
