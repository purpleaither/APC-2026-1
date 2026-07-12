# Arquivo responsável por exportar os relatórios calculados para arquivos externos.

import pandas as pd

def exportar_tabela_csv(df_tabela, nome_arquivo):
    """Salva uma tabela de resultados em um arquivo no formato CSV."""
    # O comando .to_csv() converte a tabela do Pandas em um arquivo de texto separado por ponto e vírgula.
    # Utilizei o parâmetro sep=';' e o decimal=',' para garantir a abertura correta 
    # no Microsoft Excel ou no LibreOffice no padrão brasileiro.
    # O parâmetro index=True é mantido aqui porque, em tabelas agrupadas (.groupby),
    # o nome da cidade (ou da faixa de renda) fica guardado no índice da tabela.
    df_tabela.to_csv(nome_arquivo, sep=';', decimal=',', index=True)
    
    print(f"Sucesso: O arquivo '{nome_arquivo}' foi gerado na pasta do projeto.")

def exportar_para_excel(df_tabela, nome_arquivo):
    """Salva a tabela de resultados em um arquivo no formato Excel (.xlsx)."""
    # O método .to_excel() exporta os dados diretamente para uma planilha nativa do Excel.
    # A biblioteca 'openpyxl' (instalada separadamente) faz o trabalho.
    df_tabela.to_excel(nome_arquivo, index=True)
    
    print(f"Sucesso: A planilha '{nome_arquivo}' foi gerada com sucesso.")