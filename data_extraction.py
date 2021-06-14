""" Script para extrair os dados do site 'Comércio Exterior - Governo Federal' """

"""
Requisitos:
1 - O script deve checar no site quais são os últimos 3 anos
(ou arquivos) disponíveis, e fazer o download somente desses 3
últimos anos.
O script precisa renomear as variáveis para o padrão que
utilizamos:
2 - ANO, MES, COD_NCM, COD_UNIDADE, COD_PAIS, SG_UF,
COD_VIA, COD_URF, VL_QUANTIDADE, VL_PESO_KG,
VL_FOB
3 - Preencher com zero à esquerda as seguintes variáveis
nas seguintes quantidades: COD_NCM= 8, COD_URF= 7, COD_SH4=
4, COD_PAIS=3.
Exemplo: Se o valor da coluna COD_NCM vem assim: 8796387, ele tem
que ficar assim: 08796387.
Script precisa unir todas as bases ao final (dos últimos 3
anos de importação e exportação), criando assim uma coluna para
identificar se aquilo é um registro de importação ou exportação. O
nome desta coluna deve ser MOVIMENTACAO.
"""
import csv
from collections import namedtuple
from glob import glob
from os import path, makedirs
import urllib.request
import shutil
import ssl

import pandas as pd
import bs4

N_FILES = 3
# caminhos e URLs
EXPORT_DATA_URL_PATH = "balanca/bd/comexstat-bd/ncm/EXP"
IMPORT_DATA_URL_PATH = "balanca/bd/comexstat-bd/ncmv2/IMP"
RESOURCE_URL = "https://www.gov.br/produtividade-e-comercio-exterior/pt-br/assuntos/comercio-exterior/estatisticas/base-de-dados-bruta"
DOWNLOAD_PATH = "data/"
# colunas do arquivo de importação para dropar
IMPORT_COLUMNS_DROP = ["VL_FRETE", "VL_SEGURO"]
TARGET_FILENAME = "f_comex.csv"  # nome do arquivo final
# nomes final para as colunas de ambos os tipos de dados
TARGET_DATA_HEADER = [
    "ANO",
    "MES",
    "COD_NCM",
    "COD_UNIDADE",
    "COD_PAIS",
    "SG_UF",
    "COD_VIA",
    "COD_URF",
    " VL_QUANTIDADE",
    "VL_PESO_KG",
    "VL_FOB",
]
DELIMITER = ";"
ENCODING = "utf-8"

# zeros a adicionar no final destas colunas
SIZE_COD_NCM = 8
SIZE_COD_PAIS = 3
SIZE_COD_URF = 7
SIZE_COD_SH4 = 4

# cria o diretório que armarzena os dados
if not path.exists(DOWNLOAD_PATH):
     makedirs(DOWNLOAD_PATH)

DownloadLinks = namedtuple("DownloadLinks", ["type", "year", "url"])

# link de download dos arquivos está certificado por uma autoridade que não pode ser verificada formalmente,
# é necessário então forçar um contexto de sessão não verificado
# fonte: https://stackoverflow.com/a/60671292/9881255
ssl._create_default_https_context = ssl._create_unverified_context

try:
    url = urllib.request.urlopen(RESOURCE_URL)
    html_content = url.read().decode("utf-8")
    url.close()
# poderia tratar exceções específicas aqui depois
except:
    print("Houve um erro na conexão, devemos tentar novamente")
    exit()

soup = bs4.BeautifulSoup(html_content, features="html.parser")


# encontra a porção com o dado que queremos
tables = soup.find_all("table", class_="plain")
export_data_table, import_data_table = tables[:2]

# lista os links para download
import_download_anchors = import_data_table.find_all("a")
export_download_anchors = export_data_table.find_all("a")

# valida que são as tabelas que precisamos
try:
    assert EXPORT_DATA_URL_PATH in export_download_anchors[0].get("href")
    assert IMPORT_DATA_URL_PATH in import_download_anchors[0].get("href")
except AssertionError:
    print("Os links parecem ter mudado, que tal verificar a página?")
    exit()

export_download_links = []
for anchor in export_download_anchors:

    # skip em linhas que não contém arquivos por ano
    try:
        int(anchor.text)
    except ValueError:
        continue

    export_download_links.append(
        DownloadLinks(
            type="export", year=int(anchor.text), url=anchor.get("href", None)
        )
    )


import_download_links = []
for anchor in import_download_anchors:

    # skip em linhas que não contém arquivos por ano
    try:
        int(anchor.text)
    except ValueError:
        continue

    import_download_links.append(
        DownloadLinks(
            type="import", year=int(anchor.text), url=anchor.get("href", None)
        )
    )


# ordena por ano em ordem decrescente
export_download_links.sort(key=lambda link: link.year, reverse=True)
import_download_links.sort(key=lambda link: link.year, reverse=True)

# todo: cria o diretório data se não exisitir

downloaded_dfs = []
# Faz o donwload dos dados de exportação
for i, link in enumerate(
    export_download_links[:N_FILES] + import_download_links[:N_FILES], start=1
):

    # pasta mais nome de arquivo destino
    filename = DOWNLOAD_PATH + link.url.rsplit("/", 1)[-1]

    with urllib.request.urlopen(link.url) as response, open(filename, "wb") as out_file:
        shutil.copyfileobj(response, out_file)

    df = pd.read_csv(
        filename,
        delimiter=DELIMITER,
        dtype=str,
    )

    if link.type == "import":
        df.drop(
            IMPORT_COLUMNS_DROP,
            axis=1,
            inplace=True,
        )

    df.columns = TARGET_DATA_HEADER
    df["MOVIMENTACAO"] = "importação" if link.type == "import" else "exportação"

    downloaded_dfs.append(df)

    print(f"Arquivo finalizado {i}/{N_FILES*2}")


# Une os arquivos
final_df = pd.concat(downloaded_dfs)
final_df.to_csv(
    DOWNLOAD_PATH + TARGET_FILENAME, sep=DELIMITER, encoding=ENCODING, index=False
)
