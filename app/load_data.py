""" todo: Carrega os dados nos modelos sql """
import csv
import datetime

from app import models
from app.database import SessionLocal, engine

db = SessionLocal()

models.Base.metadata.create_all(bind=engine)

with open("data/f_comex.csv", "r") as f:
    csv_reader = csv.DictReader(f)

    for row in csv_reader:
        db_record = models.Record(
            ano=row["ANO"],
            mes=row["MES"],
            cod_ncm=row["COD_NCM"],
            cod_unidade=row["COD_UNIDADE"],
            cod_pais=row["COD_PAIS"],
            cod_via=row["COD_VIA"],
            cod_urf=row["COD_URF"],
            vl_qantidade=row["VL_QUANTIDADE"],
            vl_peso_kg=row["VL_PESO_KG"],
            vl_fob=row["VL_FOB"],
        )
        db.add(db_record)

    db.commit()

db.close()
