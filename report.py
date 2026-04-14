import boto3
import csv
from datetime import datetime, timedelta, timezone


REGIOES = ["sa-east-1", "us-east-1"]

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

    session = boto3.Session(profile_name="default")
    s3 = session.client("s3")

    response = s3.list_buckets()
    buckets = response["Buckets"]

    for bucket in buckets:
        nome = bucket["Name"]

        regiao = get_bucket_region(s3, nome)

        if regiao not in REGIOES:
            print(f"  Ignorando {nome} ({regiao})")
            continue

        print(f"Analisando: {nome} ({regiao})")

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
                    "bucket":        nome,
                    "regiao":        regiao,
                    "storage_class": storage_label,
                    "tamanho_gb":    round(tamanho_gb, 4),
                    "coletado_em":   datetime.now(tz=timezone.utc).strftime("%Y-%m-%d %H:%M:%S"),
                })

    return resultados


def salvar_csv(dados, nome_arquivo):
    campos = ["bucket", "regiao", "storage_class", "tamanho_gb", "coletado_em"]

    with open(nome_arquivo, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=campos)
        writer.writeheader()
        writer.writerows(dados)

    print(f"\n{nome_arquivo} salvo com {len(dados)} registros.")


if __name__ == "__main__":
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    dados = collect()
    salvar_csv(dados, f"data/storage_{timestamp}.csv")
    salvar_csv(dados, "data/data.csv")import boto3
import csv
from datetime import datetime, timedelta, timezone


REGIOES = ["sa-east-1", "us-east-1"]

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

    session = boto3.Session(profile_name="default")
    s3 = session.client("s3")

    response = s3.list_buckets()
    buckets = response["Buckets"]

    for bucket in buckets:
        nome = bucket["Name"]

        regiao = get_bucket_region(s3, nome)

        if regiao not in REGIOES:
            print(f"  Ignorando {nome} ({regiao})")
            continue

        print(f"Analisando: {nome} ({regiao})")

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
                    "bucket":        nome,
                    "regiao":        regiao,
                    "storage_class": storage_label,
                    "tamanho_gb":    round(tamanho_gb, 4),
                    "coletado_em":   datetime.now(tz=timezone.utc).strftime("%Y-%m-%d %H:%M:%S"),
                })

    return resultados


def salvar_csv(dados, nome_arquivo):
    campos = ["bucket", "regiao", "storage_class", "tamanho_gb", "coletado_em"]

    with open(nome_arquivo, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=campos)
        writer.writeheader()
        writer.writerows(dados)

    print(f"\n{nome_arquivo} salvo com {len(dados)} registros.")


if __name__ == "__main__":
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    dados = collect()
    salvar_csv(dados, f"data/storage_{timestamp}.csv")
    salvar_csv(dados, "data/data.csv")