# Explorador de Saude e Acesso a Servicos - PDAD 2024

Este sistema é uma aplicação interativa desenvolvida para explorar os microdados da Pesquisa Distrital por Amostra de Domicílios (PDAD) de 2024, focando no recorte de saúde e acesso a serviços públicos e privados no Distrito Federal. A interface gráfica permite filtrar as informações por Região Administrativa (RA), exibindo estatísticas descritivas como média de renda, cobertura de plano de saúde e renda domiciliar. Adicionalmente, o programa gera gráficos dinâmicos de barra e pizza para ilustrar a distribuição das coberturas médicas por faixa de renda e de forma geral. O usuário também dispõe de uma funcionalidade para exportar os resultados e tabelas analisadas diretamente para arquivos formatados em CSV.

## Como Executar

Para iniciar o aplicativo, certifique-se de que os arquivos de dados estejam na pasta raiz do projeto e execute o comando abaixo no terminal:

```bash
python sistema.py
```

## Dependencias

As bibliotecas necessarias para o funcionamento do sistema estão descritas no arquivo `requirements.txt`. Você pode instalá-las rodando:

```bash
pip install -r requirements.txt
```

## Arquivos de Dados Necessarios

O programa precisa dos seguintes arquivos na raiz do projeto:
- `moradores.csv` (Microdados completos dos moradores da PDAD 2024)
- `domicilios.xlsx` (Microdados completos dos domicilios da PDAD 2024)

## Trabalho realizado por Thayna Goncalves Dutra

*Trabalho desenvolvido para a disciplina de Algoritmos e Programacao de Computadores (APC) — CIC/UnB.*
