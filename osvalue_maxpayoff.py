#Calcula o valor da Estrutura Organizacional baseado no Principio do Máximo Payoff

import pandas as pd
import numpy as np


# Função para calcular o valor da estrutura conforme o modelo matemático
def calcular_valor_estrutura(membros_por_nivel, n_departamentos, intensidade_interacao, compartilhamento_lateral):
    n_niveis = len(membros_por_nivel)
    n_total_membros = sum(membros_por_nivel.values())

    # Fórmula do valor conforme o modelo
    valor = intensidade_interacao ** 2 * n_departamentos * (
            (1 + (n_departamentos - 2) * intensidade_interacao + (n_departamentos - 1) * (
                        compartilhamento_lateral ** 2 - 2 * compartilhamento_lateral * intensidade_interacao))
            / (1 - intensidade_interacao)
    )
    return valor


# Função principal para processar a planilha de entrada e gerar a planilha de saída
def processar_planilha(entrada, saida):
    # Ler a planilha de entrada
    df = pd.read_excel(entrada)

    # Lista para armazenar os resultados
    resultados = []

    # Iterar sobre as linhas da planilha de entrada
    for index, row in df.iterrows():
        membros_por_nivel = {}
        for col in df.columns:
            if 'Membros_Nivel' in col:
                nivel = col.split('_')[-1]
                membros_por_nivel[nivel] = row[col]

        n_departamentos = row['Numero_de_Departamentos']

        # Definir valores arbitrários para intensidade_interacao e compartilhamento_lateral
        # Você pode ajustar esses valores conforme necessário
        intensidade_interacao = 0.5
        compartilhamento_lateral = 0.3

        # Calcular o valor da estrutura
        valor = calcular_valor_estrutura(membros_por_nivel, n_departamentos, intensidade_interacao,
                                         compartilhamento_lateral)

        # Armazenar o resultado
        resultado = {col: row[col] for col in df.columns}
        resultado['Valor_da_Estrutura'] = valor
        resultados.append(resultado)

    # Criar um DataFrame com os resultados
    df_resultados = pd.DataFrame(resultados)

    # Salvar o DataFrame de resultados em uma nova planilha Excel
    df_resultados.to_excel(saida, index=False)

# Arquivo de entrada e saída
arquivo_entrada = 'C:/Users/ra52440/OneDrive - AGCO Corp/00. ROGERIO ALVES_Documentos/Python/entrada.xlsx'
arquivo_saida = 'C:/Users/ra52440/OneDrive - AGCO Corp/00. ROGERIO ALVES_Documentos/Python/saida.xlsx'

# Chamar a função principal
processar_planilha(arquivo_entrada, arquivo_saida)
