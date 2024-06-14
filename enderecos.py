import pandas as pd
import requests
import time

# Caminhos dos arquivos de entrada e saída
input_file = 'C:/Users/roger/Downloads/enderecos.xlsx'
output_file = 'C:/Users/roger/Downloads/enderecos_com_coordenadas.xlsx'

def get_coordinates(address):
    url = 'https://nominatim.openstreetmap.org/search'
    params = {
        'q': address,
        'format': 'json'
    }
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    try:
        response = requests.get(url, params=params, headers=headers, timeout=10)
        response.raise_for_status()  # Levanta um erro para códigos de status HTTP 4xx/5xx
        data = response.json()
        if data:
            latitude = data[0]['lat']
            longitude = data[0]['lon']
            return latitude, longitude
    except requests.exceptions.RequestException as e:
        print(f"Erro na solicitação para o endereço '{address}': {e}")
    return None, None

def add_coordinates_to_excel(input_file, output_file):
    # Carregar a planilha Excel
    df = pd.read_excel(input_file)

    # Supondo que a coluna com os endereços se chame 'Address'
    if 'Address' not in df.columns:
        raise ValueError("A coluna 'Address' não está presente na planilha.")

    # Adicionar colunas de latitude e longitude
    df['Latitude'] = None
    df['Longitude'] = None

    # Obter coordenadas para cada endereço
    for i, row in df.iterrows():
        address = row['Address']
        latitude, longitude = None, None
        # Tentar obter coordenadas com um máximo de 3 tentativas
        for attempt in range(3):
            latitude, longitude = get_coordinates(address)
            if latitude and longitude:
                break
            else:
                print(f"Tentativa {attempt + 1} falhou para o endereço '{address}'. Retentando em 5 segundos...")
                time.sleep(5)  # Esperar 5 segundos antes de tentar novamente
        df.at[i, 'Latitude'] = latitude
        df.at[i, 'Longitude'] = longitude

        # Adicionar um atraso entre as solicitações para não exceder a taxa permitida
        time.sleep(1)  # Esperar 1 segundo entre as solicitações

    # Salvar o resultado em um novo arquivo Excel
    df.to_excel(output_file, index=False)

# Executar a função
add_coordinates_to_excel(input_file, output_file)
