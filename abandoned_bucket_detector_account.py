import boto3
import csv
from datetime import datetime, timezone, timedelta

# ---------------------------------------------------------------
# configuração — adicione aqui todos os profiles que quer rodar
# ---------------------------------------------------------------
AWS_PROFILES = ["default", "sandbox"]
REGIOES = ["sa-east-1", "us-east-1", "us-east-2"]
# ---------------------------------------------------------------


def get_bucket_region(s3_client, bucket_name):
    response = s3_client.get_bucket_location(Bucket=bucket_name)
    regiao = response["LocationConstraint"]
    return regiao if regiao else "us-east-1"


def collect():
    resultados = []

    # percorre cada profile/conta
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
            total_objetos = datapoints[0]["Average"] if datapoints else 0

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
            total_requests = datapoints_req[0]["Sum"] if datapoints_req else 0

            if total_objetos == 0:
                status = "vazio"
            elif total_requests == 0:
                status = "abandonado"
            else:
                status = "ativo"

            print(f"    {status} — {total_objetos:.0f} objetos, {total_requests:.0f} requests")

            resultados.append({
                "account":        profile,
                "bucket":         nome,
                "region":         regiao,
                "status":         status,
                "total_objetos":  int(total_objetos),
                "total_requests": int(total_requests),
                "coletado_em":    datetime.now(tz=timezone.utc).strftime("%Y-%m-%d %H:%M:%S"),
            })

    return resultados


def salvar_csv(dados, nome_arquivo):
    campos = ["account", "bucket", "region", "status", "total_objetos", "total_requests", "coletado_em"]

    with open(nome_arquivo, mode="w", newline="") as arquivo_csv:
        writer = csv.DictWriter(arquivo_csv, fieldnames=campos)
        writer.writeheader()
        writer.writerows(dados)

    print(f"\n{nome_arquivo} salvo com {len(dados)} registros.")


if __name__ == "__main__":
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    dados = collect()
    salvar_csv(dados, f"data/abandoned_{timestamp}.csv")
    salvar_csv(dados, "data/abandoned.csv")