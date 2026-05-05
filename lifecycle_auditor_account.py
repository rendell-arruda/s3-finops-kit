from datetime import datetime, timezone
import csv
import boto3


# ---------------------------------------------------------------
# configuração — adicione aqui todos os profiles que quer rodar
# ---------------------------------------------------------------
AWS_PROFILES = ["default", "sandbox"]
# ---------------------------------------------------------------


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

            try:
                lifecycle = s3.get_bucket_lifecycle_configuration(Bucket=nome)
                regras = lifecycle.get("Rules", [])
                resultados.append({
                    "account":       profile,
                    "bucket":        nome,
                    "tem_lifecycle": True,
                    "total_regras":  len(regras),
                    "coletado_em":   datetime.now(tz=timezone.utc).strftime("%Y-%m-%d %H:%M:%S"),
                })
            except s3.exceptions.from_code("NoSuchLifecycleConfiguration"):
                resultados.append({
                    "account":       profile,
                    "bucket":        nome,
                    "tem_lifecycle": False,
                    "total_regras":  0,
                    "coletado_em":   datetime.now(tz=timezone.utc).strftime("%Y-%m-%d %H:%M:%S"),
                })

    return resultados


def salvar_csv(dados, nome_arquivo):
    campos = ["account", "bucket", "tem_lifecycle", "total_regras", "coletado_em"]

    with open(nome_arquivo, mode="w", newline="") as arquivo_csv:
        writer = csv.DictWriter(arquivo_csv, fieldnames=campos)
        writer.writeheader()
        writer.writerows(dados)

    print(f"\n{nome_arquivo} salvo com {len(dados)} registros.")


if __name__ == "__main__":
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    dados = collect()
    salvar_csv(dados, f"data/lifecycle_{timestamp}.csv")
    salvar_csv(dados, "data/lifecycle.csv")