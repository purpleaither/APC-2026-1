# Arquivo responsável pelos cálculos do Recorte C (Saúde).

import pandas as pd

def calcular_cobertura_plano_geral(df):
    """Calcula a porcentagem da população geral do DF que possui plano de saúde privado (Pergunta G01)."""
    # A pergunta G01 tem o código '1' para SIM (tem plano) e '2' para NÃO.
    # O value_counts(normalize=True) calcula automaticamente a proporção de cada resposta.
    # Multiplico por 100 para transformar o resultado em porcentagem (ex: 35.4%).
    proporcao = df['G01'].value_counts(normalize=True) * 100
    
    return proporcao

def calcular_acesso_por_ra(df):
    """Agrupa os dados por Região Administrativa para comparar a cobertura de planos de saúde."""
    # Substitui o código '2' (Não tem plano) por '0' na coluna G01 para criar uma coluna binária.
    # Como o '1' (Tem plano) é mantido, a coluna fica apenas com números 1 e 0, 
    # permitindo calcular a porcentagem direta de cobertura através da média matemática (.mean()).
    df['tem_plano'] = df['G01'].replace(2, 0)
    
    # O comando groupby() agrupa os moradores pela sua cidade (nome_ra).
    # Em seguida, calcula a média (.mean()) da coluna 'tem_plano' e multiplica por 100
    # para descobrir a taxa de cobertura em cada Região Administrativa.
    tabela_ra = df.groupby('nome_ra')['tem_plano'].mean() * 100
    
    # Organiza a tabela em ordem decrescente (do maior para o menor),
    # exibindo no topo as cidades com maior acesso e no final as com menor acesso.
    tabela_ra = tabela_ra.sort_values(ascending=False)
    
    return tabela_ra

def calcular_saude_por_renda(df):
    """Analisa a correlação entre a faixa de renda individual e a posse de plano de saúde."""
    # Aplica novamente a substituição do '2' por '0' para viabilizar o cálculo da média.
    df['tem_plano'] = df['G01'].replace(2, 0)
    
    # Agrupa os dados pela 'faixa_renda' (criada no carregar.py) para calcular 
    # a porcentagem de pessoas com plano dentro de cada grupo socioeconômico.
    # O parâmetro observed=False garante que o Pandas exiba todas as faixas de renda na tabela final.
    tabela_renda = df.groupby('faixa_renda', observed=False)['tem_plano'].mean() * 100
    
    return tabela_renda


# Adicionado método para consolidar indicadores gerais de saúde e renda da população selecionada.
def calcular_estatisticas_gerais(df):
    """Calcula estatísticas de resumo para exibição nos rótulos de texto da interface gráfica."""
    # Conta quantas pessoas estão incluídas na seleção atual.
    total_pessoas = int(df.shape[0])
    
    # Cria uma cópia temporária para evitar avisos de fatiamento do pandas ao calcular a média.
    df_temp = df.copy()
    df_temp['tem_plano'] = df_temp['G01'].replace(2, 0)
    
    # Calcula a média direta da posse de plano de saúde.
    pct_plano = float(df_temp['tem_plano'].mean() * 100) if total_pessoas > 0 else 0.0
    
    # Calcula a média aritmética simples das rendas individuais e familiares.
    renda_ind_media = float(df['renda_ind'].mean()) if total_pessoas > 0 else 0.0
    renda_dom_media = float(df['renda_domiciliar'].mean()) if total_pessoas > 0 else 0.0
    
    return total_pessoas, pct_plano, renda_ind_media, renda_dom_media