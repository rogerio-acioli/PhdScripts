#Calcula a Complexidade e a previsão de qualidade de um produto desenvolvido de acordo com o modelo de estrutura organizacional
import pandas as pd

# Função para calcular o nível de complexidade organizacional
def calcular_complexidade(membros, OS, CC):
    # Aqui, definimos a complexidade como uma combinação linear simples das métricas
    # Ajuste os pesos conforme necessário
    complexidade = 0.3 * membros + 0.4 * OS + 0.3 * CC
    return complexidade

# Função para prever a qualidade do produto
def prever_qualidade(complexidade):
    # Simples inverso da complexidade como uma medida de qualidade
    # Quanto maior a complexidade, menor a qualidade
    # Ajuste essa função conforme a necessidade
    qualidade = 100 / (1 + complexidade)
    return qualidade

# Leitura do arquivo de entrada
input_file = 'C:/Users/roger/OneDrive/Doutorado/Python/dados_entrada.xlsx'
df = pd.read_excel(input_file)

# Verificação da validade dos dados
for index, row in df.iterrows():
    membros = row['Membros']
    OS = row['Org_Size']

    if OS < membros:
        raise ValueError(
            f"A linha {index + 1} tem um valor de Org_Size ({OS}) menor que o número de Membros ({membros}).")

# Inicialização das colunas de saída com tipo float
df['Complexidade Organizacional'] = 0.0
df['Qualidade Prevista'] = 0.0

# Cálculo da complexidade e qualidade para cada linha do dataframe
for index, row in df.iterrows():
    membros = row['Membros']
    OS = row['Org_Size']
    CC = row['CC']

    complexidade = calcular_complexidade(membros, OS, CC)
    qualidade = prever_qualidade(complexidade)

    df.at[index, 'Complexidade Organizacional'] = complexidade
    df.at[index, 'Qualidade Prevista'] = qualidade

# Escrita dos resultados no arquivo de saída
output_file = 'C:/Users/roger/OneDrive/Doutorado/Python/resultado_qualidade.xlsx'
df.to_excel(output_file, index=False)

print(f'Resultados salvos em {output_file}')

