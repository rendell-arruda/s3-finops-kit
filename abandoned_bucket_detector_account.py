import boto3
import csv
from datetime import datetime, timedelta, timezone


# ---------------------------------------------------------------
# configuração — adicione aqui todos os profiles que quer rodar
# ---------------------------------------------------------------
AWS_PROFILES = ["default", "sandbox"]
REGIOES = ["sa-east-1", "us-east-1"]
# ---------------------------------------------------------------

STORAGE_CLASSES = {
    "StandardStorage":           "S3 Standard",
    "StandardIAStorage":         "Standard-IA",
    "OneZoneIAStorage":          "One Zone-IA",
    "GlacierInstantStorage":     "Glacier Instant Retrieval",
    "GlacierStorage":            "Glacier Flexible Retrieval",
    "DeepArchiveStorage":        "Glacier Deep Archive",
    "IntelligentTieringStorage": "Intelligent-Tiering",
}


def get_bucket_region(s3_client, bucket_name):
    response = s3_client.get_bucket_location(Bucket=bucket_name)
    regiao = response["LocationConstraint"]
    return regiao if regiao else "us-east-1"


def collect():
    resultados = []

    for profile in AWS_PROFILES:
        print(f"\nColetando conta: {profile}")

        session = boto3.Session(profile_name=profile)
        s3 = session.client("s3")

        response = s3.list_buckets()
        buckets = response["Buckets"]

        for bucket in buckets:
            nome = bucket["Name"]

            regiao = get_bucket_region(s3, nome)

            if regiao not in REGIOES:
                print(f"  Ignorando {nome} ({regiao})")
                continue

            print(f"  Analisando: {nome} ({regiao})")

            cw = session.client("cloudwatch", region_name=regiao)

            for storage_key, storage_label in STORAGE_CLASSES.items():
                cw_response = cw.get_metric_statistics(
                    Namespace="AWS/S3",
                    MetricName="BucketSizeBytes",
                    Dimensions=[
                        {"Name": "BucketName",  "Value": nome},
                        {"Name": "StorageType", "Value": storage_key},
                    ],
                    StartTime=datetime.now(tz=timezone.utc) - timedelta(days=2),
                    EndTime=datetime.now(tz=timezone.utc),
                    Period=86400,
                    Statistics=["Average"],
                )

                datapoints = cw_response["Datapoints"]

                if datapoints:
                    tamanho_gb = datapoints[0]["Average"] / (1024 ** 3)
                    resultados.append({
                        "account":       profile,
                        "bucket":        nome,
                        "regiao":        regiao,
                        "storage_class": storage_label,
                        "tamanho_gb":    round(tamanho_gb, 4),
                        "coletado_em":   datetime.now(tz=timezone.utc).strftime("%Y-%m-%d %H:%M:%S"),
                    })

    return resultados


def salvar_csv(dados, nome_arquivo):
    campos = ["account", "bucket", "regiao", "storage_class", "tamanho_gb", "coletado_em"]

    with open(nome_arquivo, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=campos)
        writer.writeheader()
        writer.writerows(dados)

    print(f"\n{nome_arquivo} salvo com {len(dados)} registros.")


if __name__ == "__main__":
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    dados = collect()
    salvar_csv(dados, f"data/abandoned_{timestamp}.csv")
    salvar_csv(dados, "data/abandoned.csv")