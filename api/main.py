from fastapi import FastAPI
from minio import Minio
import pandas as pd
from io import BytesIO
import uvicorn
from fastapi.middleware.cors import CORSMiddleware  # Importation correcte

app = FastAPI()

# Configuration CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Autorise toutes les origines
    allow_credentials=True,
    allow_methods=["*"],  # Autorise toutes les méthodes
    allow_headers=["*"],  # Autorise tous les headers
)

# Configuration du client MinIO
minio_client = Minio(
    "localhost:9000",
    access_key="minio",
    secret_key="minio123",
    secure=False
)

# Route pour obtenir les données
@app.get("/data")
async def get_data():
    try:
        # Liste des fichiers dans le répertoire
        objects = minio_client.list_objects("investment", prefix="delta/AssetPerformanceSummaryGold/", recursive=True)
        dfs = []  # Liste pour stocker les DataFrames

        for obj in objects:
            # Vérifier si le fichier est un fichier Parquet
            if obj.object_name.endswith(".parquet"):
                data = minio_client.get_object("investment", obj.object_name)
                df = pd.read_parquet(BytesIO(data.data), engine="pyarrow")
                dfs.append(df)

        # Concaténer tous les DataFrames
        all_data = pd.concat(dfs, ignore_index=True)

        # Convertir le DataFrame en JSON
        return all_data.to_dict(orient="records")
    except Exception as e:
        return {"error": str(e)}

# Point d'entrée pour exécuter l'application
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=5000)
