import pandas as pd
import pulp
import math

# Carregar a planilha com dados das lojas
file_path = 'C:/Users/roger/Downloads/lojas.xlsx'  # Substitua pelo caminho correto da planilha
lojas_df = pd.read_excel(file_path)

# Função para calcular a distância entre duas coordenadas geográficas
def calcular_distancia(lat1, lon1, lat2, lon2):
    R = 6371  # Raio da Terra em km
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon2)
    a = math.sin(dlat / 2) * math.sin(dlat / 2) + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2) * math.sin(dlon / 2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    distancia = R * c
    return distancia

# Calcular a matriz de distâncias entre todas as lojas
num_lojas = len(lojas_df)
distancias = [[calcular_distancia(lojas_df['Latitude'][i], lojas_df['Longitude'][i], lojas_df['Latitude'][j], lojas_df['Longitude'][j]) for j in range(num_lojas)] for i in range(num_lojas)]

# Parâmetros do problema
tempo_visita_min = 2  # horas
tempo_visita_max = 8  # horas
jornada_diaria = 8    # horas
dias_trabalho_semana = 6
faturamento_limite = 200000
jornada_semanal = jornada_diaria * dias_trabalho_semana

# Inicializar o problema de otimização
prob = pulp.LpProblem("Otimizacao_Promotores", pulp.LpMinimize)

# Variáveis de decisão
# x[i, j] = 1 se o promotor j atende a loja i
x = pulp.LpVariable.dicts("x", [(i, j) for i in range(num_lojas) for j in range(num_lojas)], lowBound=0, cat='Binary')
# y[j] = 1 se o promotor j é fixo, 0 se é de roteiro
y = pulp.LpVariable.dicts("y", range(num_lojas), lowBound=0, upBound=1, cat='Binary')

# Função objetivo: minimizar a diferença entre o total de horas de trabalho e 48 horas
prob += pulp.lpSum([pulp.lpSum([x[i, j] * (tempo_visita_min + distancias[i][j] / 60) for i in range(num_lojas)]) - jornada_semanal for j in range(num_lojas)])

# Restrição: cada loja deve ser atendida por exatamente um promotor
for i in range(num_lojas):
    prob += pulp.lpSum([x[i, j] for j in range(num_lojas)]) == 1

# Restrições para promotores fixos nas lojas com faturamento >= 200000
for i in range(num_lojas):
    if lojas_df['Faturamento'][i] >= faturamento_limite:
        for j in range(num_lojas):
            prob += x[i, j] <= y[j]
        # Um promotor fixo deve trabalhar exatamente 48 horas em uma única loja
        for j in range(num_lojas):
            prob += x[i, j] * jornada_diaria * dias_trabalho_semana == y[j] * jornada_semanal

# Restrição para garantir que promotores fixos atendam apenas uma loja durante a semana
for j in range(num_lojas):
    prob += pulp.lpSum([x[i, j] for i in range(num_lojas) if lojas_df['Faturamento'][i] >= faturamento_limite]) <= 1

# Restrição para garantir jornada semanal de exatamente 48 horas (visitas + deslocamentos)
for j in range(num_lojas):
    total_horas = pulp.lpSum([x[i, j] * tempo_visita_min for i in range(num_lojas)]) + \
                  pulp.lpSum([x[i, j] * distancias[i][j] / 60 for i in range(num_lojas)])
    prob += total_horas <= jornada_semanal
    prob += total_horas >= jornada_semanal - 2  # Permitir uma pequena margem

# Resolver o problema
prob.solve()

# Verificar o status da solução
print(f"Status: {pulp.LpStatus[prob.status]}")

# Extrair a solução
resultados = []
for j in range(num_lojas):
    lojas_atendidas = []
    horas_visita = 0
    horas_deslocamento = 0
    for i in range(num_lojas):
        if pulp.value(x[i, j]) == 1:
            lojas_atendidas.append(str(lojas_df['Loja'][i]))  # Convertendo os índices das lojas para strings
            if lojas_df['Faturamento'][i] >= faturamento_limite:
                horas_visita += jornada_diaria * dias_trabalho_semana
            else:
                horas_visita += tempo_visita_min
            horas_deslocamento += distancias[i][j] / 60
    total_horas = horas_visita + horas_deslocamento
    if lojas_atendidas and total_horas <= jornada_semanal:
        resultados.append({
            'Promotor': j,
            'Tipo': 'Fixo' if pulp.value(y[j]) == 1 else 'Roteiro',
            'Horas_Visita': horas_visita,
            'Horas_Deslocamento': horas_deslocamento,
            'Quantidade_Lojas': len(lojas_atendidas),
            'Lojas': ", ".join(lojas_atendidas),
            'Total_Horas': total_horas
        })

# Criar a planilha de saída
resultados_df = pd.DataFrame(resultados)
output_path = 'C:/Users/roger/Downloads/alocacao_promotores.xlsx'
resultados_df.to_excel(output_path, index=False)

print(f"Planilha gerada em: {output_path}")
