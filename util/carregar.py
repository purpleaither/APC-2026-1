import os # Biblioteca nativa do sistema operacional, utilizada para verificar a existência dos arquivos
import pandas as pd
import numpy as np

# Dicionário extraido do anexo 1 do arquivo de "dicionário de dados" presente na PDAD 2024
DICIONARIO_RAS = {
    5301: 'Plano Piloto', 5302: 'Gama', 5303: 'Taguatinga', 5304: 'Brazlândia',
    5305: 'Sobradinho', 5306: 'Planaltina', 5307: 'Paranoá', 5308: 'Núcleo Bandeirante',
    5309: 'Ceilândia', 5310: 'Guará', 5311: 'Cruzeiro', 5312: 'Samambaia',
    5313: 'Santa Maria', 5314: 'São Sebastião', 5315: 'Recanto Das Emas', 5316: 'Lago Sul',
    5317: 'Riacho Fundo', 5318: 'Lago Norte', 5319: 'Candangolândia', 5320: 'Águas Claras',
    5321: 'Riacho Fundo II', 5322: 'Sudoeste e Octogonal', 5323: 'Varjão', 5324: 'Park Way',
    5325: 'SCIA', 5326: 'Sobradinho II', 5327: 'Jardim Botânico', 5328: 'Itapoã',
    5329: 'SIA', 5330: 'Vicente Pires', 5331: 'Fercal', 5332: 'Sol Nascente / Pôr do Sol',
    5333: 'Arniqueira', 5334: 'Arapoanga', 5335: 'Água Quente', 5336: 'Área Rural',
    5241: 'Águas Lindas de Goiás', 5242: 'Alexânia', 5243: 'Cidade Ocidental', 5244: 'Cristalina',
    5245: 'Cocalzinho de Goiás', 5246: 'Formosa', 5247: 'Luziânia', 5248: 'Novo Gama',
    5249: 'Padre Bernardo', 5250: 'Planaltina de Goiás', 5251: 'Santo Antônio do Descoberto', 5252: 'Valparaíso de Goiás'
}

# Tradução dos níveis educacionais conforme o dicionário da variável 'escolaridade'

DICIONARIO_ESCOLARIDADE = {
    1: 'Sem instrução', 2: 'Fund. incompleto', 3: 'Fund. completo',
    4: 'Médio incompleto', 5: 'Médio completo', 6: 'Sup. incompleto',
    7: 'Sup. completo', 8: 'Sem classif.'
}

def carregar_dados():
    ### Lê as planilhas da PDAD 2024, limpa sentinelas e realiza o merge entre moradores e domicílios.

    # Abaixo estão os nomes do arquivos que devem ser lidos
    caminho_moradores = 'moradores.csv'
    caminho_domicilios = 'domicilios.xlsx'
    
    # Abaixo ocorre verificação de existência dos arquivos no sistema operacional. Caso não existam, retornará erro.
    if not os.path.exists(caminho_moradores) or not os.path.exists(caminho_domicilios):
        print(f"ERRO: Verifique se os arquivos '{caminho_moradores}' e '{caminho_domicilios}' estão na mesma pasta do programa.")
        return None
        
    # Adicionada a codificação utf-8-sig para ler corretamente o arquivo moradores.csv e remover o caractere BOM do início.
    df_mor = pd.read_csv(caminho_moradores, sep=';', low_memory=False, encoding='utf-8-sig') 
    # Utilizei o low_memory=False para ler o arquivo todo e evitar aviso do Pandas sobre tipos de dados mistos (DtypeWarning)
    df_dom = pd.read_excel(caminho_domicilios)
    
    # Selecionei apenas as colunas relevantes para o Recorte C e adicionei as mesmas nas listas abaixo
    cols_mor = ['A01nficha', 'localidade', 'idade_calculada', 'renda_ind', 'escolaridade']
    cols_dom = ['A01nficha', 'renda_domiciliar']
    
    # Movido o fatiamento de colunas para depois do loop para não perder as colunas que iniciam com 'G'.
    for coluna in df_mor.columns: #Aqui adiciono as colunas relacionadas à saúde uma por uma
            if coluna.startswith('G'):
                cols_mor.append(coluna)

    df_mor = df_mor[cols_mor]
    df_dom = df_dom[cols_dom]
    
    # REQUISITO 6: TRATAMENTO DE VALORES SENTINELA (OBRIGATÓRIO)
    # Substituí os códigos 99999 e 88888 por np.nan para normalizar dados faltantes.
    valores_sentinela = [99999, 88888, '99999', '88888']
    # Substituído pd.NA por np.nan para viabilizar a conversão de tipos e evitar problemas com o acessador de strings.
    df_mor = df_mor.replace(valores_sentinela, np.nan)
    df_dom = df_dom.replace(valores_sentinela, np.nan)
    
    # TRADUÇÃO DAS RAs
        # Criei uma função para verificar a existência do número da RA no DICIONARIO_RAS:
    def traduzir_ra(codigo):
            if codigo in DICIONARIO_RAS:
                return DICIONARIO_RAS[codigo]
            else:
                return f"RA não encontrada"
        
        # Converte o código numérico da localidade para o nome textual da RA:
    df_mor['nome_ra'] = df_mor['localidade'].apply(traduzir_ra)
    
    # TRADUÇÃO DAS ESCOLARIDADES 
    def traduzir_escolaridade(codigo):
            if codigo in DICIONARIO_ESCOLARIDADE:
                return DICIONARIO_ESCOLARIDADE[codigo]
            else:
                return "Sem classificação"
            
    # Converte o código numérico no nome textual do nível de escolaridade:
    df_mor['nome_escolaridade'] = df_mor['escolaridade'].apply(traduzir_escolaridade)
    
    # Troca a vírgula pelo ponto na coluna de renda individual para o formato decimal padrão.
    if df_mor['renda_ind'].dtype == 'object': #Verifica o tipo do dado
        df_mor['renda_ind'] = df_mor['renda_ind'].str.replace(',', '.') # Substitui vírgula por ponto
            
        # Converte a coluna de renda para o tipo numérico float (função do astype):
    df_mor['renda_ind'] = df_mor['renda_ind'].astype(float)
        
        # Converte a coluna de idade para o tipo numérico inteiro, novamente utilizando o astype:
    df_mor['idade_calculada'] = df_mor['idade_calculada'].astype(int)
    
    # --- CATEGORIZAÇÃO DEMOGRÁFICA DO RECORTE C ---
    # Transforma a variável contínua 'idade_calculada' em faixas etárias.
    # Isso é importante para análises epidemiológicas, pois o padrão de uso de serviços de saúde 
    # e a cobertura de planos mudam drasticamente entre jovens, adultos em idade laboral e idosos.
        
    # Define os limites matemáticos dos intervalos (os "cortes" ou "bins") no eixo numérico.
    # O valor 0 é utilizado no início inclui5r bebês com 0 anos (recém-nascidos)
    # O valor 150 no final é o teto máximo para englobar as pessoas mais velhas da amostra.
    bins_idade = [0, 18, 59, 150]
        
    # Cria uma lista com os rótulos textuais que darão nome para cada um dos intervalos acima.
    # A quantidade de rótulos deve ser exatamente igual à quantidade de intervalos criados pelos cortes.
    labels_idade = ['0-18 (Jovens)', '19-59 (Adultos)', '60+ (Idosos)']
        
    # Aplica o  pd.cut() para agrupar as idades nas faixas etárias predefinidas.
    # O Pandas avalia a idade de cada morador, verifica em qual intervalo (bin) o número se encaixa
    # e cria a nova coluna 'faixa_etaria' preenchida com o rótulo correspondente:
    df_mor['faixa_etaria'] = pd.cut(
        df_mor['idade_calculada'], 
        bins=bins_idade, 
        labels=labels_idade
    )
    # Segmentação de Renda baseada no Salário Mínimo (aprox. R$ 1.412 em 2024)
    # Adicionado o limite de -1 para que pessoas com 0 de renda fiquem no primeiro bin ('Sem Renda').
    bins_renda = [-1, 0, 1412, 4236, float('inf')]
    df_mor['faixa_renda'] = pd.cut(
        df_mor['renda_ind'], 
        bins=bins_renda, 
        labels=['Sem Renda', 'Até 1 SM', '1 a 3 SM', 'Mais de 3 SM']
    )
    # DIFERENCIAL D3: MERGE ENTRE AS DUAS TABELAS
    # Cruzei a tabela de moradores com a tabela de domicílios usando a chave 'A01nficha'
    # (que representa o número do questionário do domicílio). O 'inner join' garante que 
    # teremos na mesma linha os dados individuais de saúde e os dados da casa da pessoa.
    df_completo = pd.merge(df_mor, df_dom, on='A01nficha', how='inner')
    
    return df_completo