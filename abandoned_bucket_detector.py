import boto3
import csv
from datetime import datetime, timezone, timedelta


REGIOES = ["sa-east-1", "us-east-1"]


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
        objects_response = cw.get_metric_statistics(
            Namespace="AWS/S3",
            MetricName="NumberOfObjects",
            Dimensions=[
                {"Name": "BucketName", "Value": nome},
                {"Name": "StorageType", "Value": "AllStorageTypes"},
            ],
            StartTime=datetime.now(tz=timezone.utc) - timedelta(days=90),
            EndTime=datetime.now(tz=timezone.utc),
            Period=90 * 86400,
            Statistics=["Average"],
        )
        datapoints = objects_response["Datapoints"]
        if datapoints:
            total_objetos = datapoints[0]["Average"]
        else:
            total_objetos = 0

        request_response = cw.get_metric_statistics(
            Namespace="AWS/S3",
            MetricName="NumberOfRequests",
            Dimensions=[
                {"Name": "BucketName", "Value": nome},
            ],
            StartTime=datetime.now(tz=timezone.utc) - timedelta(days=90),
            EndTime=datetime.now(tz=timezone.utc),
            Period=90 * 86400,
            Statistics=["Sum"],
        )
        datapoints_req = request_response["Datapoints"]
        if datapoints_req:
            total_requests = datapoints_req[0]["Sum"]
        else:
            total_requests = 0

        print(f"{nome}: {total_requests} requests and {total_objetos} objetos")

        if total_objetos == 0:
            status = "vazio"
        elif total_requests == 0:
            status = "abandonado"
        else:
            status = "ativo"

        resultados.append(
            {
                "bucket": nome,
                "region": regiao,
                "status": status,
                "total_objetos": int(total_objetos),
                "total_requests": int(total_requests),
                "coletado_em": datetime.now(tz=timezone.utc).strftime(
                    "%Y-%m-%d %H:%M:%S"
                ),
            }
        )

    return resultados


def salvar_csv(dados, nome_arquivo):
    with open(nome_arquivo, mode="w", newline="") as arquivo_csv:
        campos = [
            "bucket",
            "region",
            "status",
            "total_objetos",
            "total_requests",
            "coletado_em",
        ]
        writer = csv.DictWriter(arquivo_csv, fieldnames=campos)
        writer.writeheader()
        writer.writerows(dados)
    print(f"\n{nome_arquivo} salvo com {len(dados)} registros.")


if __name__ == "__main__":
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    dados = collect()
    salvar_csv(dados, f"data/abandoned_{timestamp}.csv")
    salvar_csv(dados, "data/abandoned.csv")
