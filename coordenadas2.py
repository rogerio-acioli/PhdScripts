import pandas as pd
import requests
import time

def get_opencage_coordinates(address, api_key):
    url = 'https://api.opencagedata.com/geocode/v1/json'
    params = {
        'q': address,
        'key': api_key,
        'limit': 1,
        'countrycode': 'BR'
    }
    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        if data['results']:
            location = data['results'][0]['geometry']
            latitude = location['lat']
            longitude = location['lng']
            return latitude, longitude
    except requests.exceptions.RequestException as e:
        print(f"Erro na solicitação para o endereço '{address}': {e}")
    return None, None

def add_coordinates_to_excel(input_file, output_file, api_key):
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
            latitude, longitude = get_opencage_coordinates(address, api_key)
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

# Chave da API do OpenCage
api_key = 'f2d03633d61641c6b62e189aa38157ee'

# Caminhos dos arquivos de entrada e saída
input_file = 'C:/Users/roger/Downloads/enderecos.xlsx'
output_file = 'C:/Users/roger/Downloads/enderecos_com_coordenadas.xlsx'

# Executar a função
add_coordinates_to_excel(input_file, output_file, api_key)