# Arquivo responsável por exportar os relatórios calculados para arquivos externos.

import pandas as pd

def exportar_para_txt(df_tabela, nome_arquivo):
    """Salva uma tabela de resultados em um arquivo no formato texto (.txt)."""
    # O comando .to_csv() converte a tabela do Pandas em um arquivo de texto.
    # Utilizei o parâmetro sep='\t' (tabulação) para separar as colunas de forma estruturada.
    df_tabela.to_csv(nome_arquivo, sep='\t', decimal=',', index=True)
    
    print(f"Sucesso: O arquivo '{nome_arquivo}' foi gerado na pasta do projeto.")