import os
from urllib.parse import urlparse, parse_qs, quote

import requests
import pandas as pd
from dash import Output, Input, State, html

backendURL = "https://picmoneyback-e4gbaaexb8ayg5b8.canadacentral-01.azurewebsites.net"
#backendURL = "http://localhost:5000"
backendURLCSV = backendURL+'/get_csv'


# Arrays para armazenar as planilhas
dfCupons = []
dfBaseCadastral = []
dfBasePedestre = []
dfMassaTeste = []

def get_df_for_period(array, ano, mes):
    for item in array:
        if item["ano"] == ano and item["mes"] == mes:
            return item["data"]
    return None

# Remove o ponto depois do 5000
def safe_url(url):
    if backendURL == "https://picmoneyback-e4gbaaexb8ayg5b8.canadacentral-01.azurewebsites.net":
        return url.replace(".net./", ".net/")
    else:
        return url.replace(":5000./", ":5000/")


def safe_csv_url(path):
    if path.startswith("http://") or path.startswith("https://"):
        base, filename = path.rsplit("/", 1)
        return f"{base}/{quote(filename)}"
    else:
        return path

try:
    response = requests.get(backendURLCSV)
    response.raise_for_status()
    json_data = response.json()

    for row in json_data:
        tipo_base = row["tipoBase"]
        caminho = row["caminho"]
        ano = row["ano"]
        mes = row["mes"]
        titulo = row["titulo"]

        csv_path_0 = safe_url(backendURL+caminho)
        csv_path = safe_csv_url(csv_path_0)

        try:
            df = pd.read_csv(csv_path, sep=";")

            entry = {
                "titulo": titulo,
                "ano": ano,
                "mes": mes,
                "data": df
            }

            if tipo_base == "base_cadastral":
                dfBaseCadastral.append(entry)
            elif tipo_base == "base_teste":
                dfMassaTeste.append(entry)
            elif tipo_base == "base_pedestre":
                dfBasePedestre.append(entry)
            elif tipo_base == "base_transicao":
                dfCupons.append(entry)

        except Exception as e:
            print(f"⚠️ Erro ao carregar CSV '{titulo}': {e}")

except Exception as e:
    print(f"Erro ao conectar com o backend: {e}")


def get_mes(mes):
    if mes == 1:
        return "Janeiro"
    if mes == 2:
        return "Fevereiro"
    if mes == 3:
        return "Março"
    if mes == 4:
        return "Abril"
    if mes == 5:
        return "Maio"
    if mes == 6:
        return "Junho"
    if mes == 7:
        return "Julho"
    if mes == 8:
        return "Agosto"
    if mes == 9:
        return "Setembro"
    if mes == 10:
        return "Outubro"
    if mes == 11:
        return "Novembro"
    if mes == 12:
        return "Dezembro"


