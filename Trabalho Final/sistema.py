# ARQUIVO PRINCIPAL: sistema.py (Versão Interface Gráfica com Tkinter e Matplotlib)
# Módulo responsável por construir a interface visual, gerenciar os eventos do usuário e exibir gráficos.

# Importa a biblioteca nativa Tkinter para construção da interface gráfica (GUI).
import tkinter as tk
# Importa o módulo ttk para componentes visuais avançados como combobox.
from tkinter import ttk
# Importa módulos auxiliares do Tkinter para caixas de mensagem e seleção de arquivos.
from tkinter import messagebox, filedialog, scrolledtext

# Configura o Matplotlib para trabalhar integrado com a interface gráfica do Tkinter.
import matplotlib
matplotlib.use("TkAgg")
# Importa o canvas especial do matplotlib que permite incorporar gráficos dentro da janela do Tkinter.
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
import pandas as pd

# Importa as funções analíticas e de tratamento dos módulos personalizados.
from util.carregar import carregar_dados
from util.calcular import (
    calcular_cobertura_plano_geral, 
    calcular_acesso_por_ra, 
    calcular_saude_por_renda,
    calcular_estatisticas_gerais
)
from util.exportar import exportar_para_txt


class SistemaSaudeGUI:
    """Classe responsável por estruturar os componentes visuais e gerenciar a interatividade do programa."""
    
    def __init__(self, janela_principal):
        """Inicializa a aplicação, configura as dimensões da tela e carrega a base de dados."""
        # Recebe a janela do Tkinter e armazena na variável de instância da classe.
        self.janela = janela_principal
        
        # Define o título que aparece na barra superior da janela do aplicativo.
        self.janela.title("Explorador de Saúde e Renda - PDAD 2024 (Recorte C) - Feito por Thayná Gonçalves Dutra")
        
        # Configura o tamanho da janela para acomodar os gráficos e filtros de forma legível.
        self.janela.geometry("950x700")
        
        # Inicializa a variável que armazena a tabela principal do PDAD como vazia.
        self.df_pdad = None
        # Inicializa o dataframe de filtro que será atualizado conforme a RA selecionada.
        self.df_filtrado = None

        # Executa o método interno para desenhar os botões, filtros e painel gráfico.
        self.montar_interface()
        
        # Executa o carregamento automático dos dados da PDAD assim que a janela é aberta.
        self.carregar_dados_inicial()

    def montar_interface(self):
        """Constrói e posiciona todos os elementos visuais (rótulos, filtros, botões e área gráfica) dentro da janela."""
        # BARRA LATERAL (PAINEL DE CONTROLE) 
        # Cria um contêiner lateral para agrupar os filtros e estatísticas à esquerda.
        self.frame_lateral = tk.Frame(self.janela, width=250, relief=tk.RIDGE, bd=2)
        self.frame_lateral.pack(side=tk.LEFT, fill=tk.Y, padx=10, pady=10)

        # Título da barra lateral.
        lbl_controle = tk.Label(self.frame_lateral, text="Painel de Controle", font=("Arial", 11, "bold"))
        lbl_controle.pack(pady=10)

        # Rótulo dinâmico para indicar quantos registros foram carregados do arquivo.
        self.lbl_registros = tk.Label(self.frame_lateral, text="Moradores: 0 · Domicílios: 0", font=("Arial", 9, "italic"))
        self.lbl_registros.pack(pady=2)

        # Separador horizontal para organizar visualmente os componentes da barra lateral.
        ttk.Separator(self.frame_lateral, orient='horizontal').pack(fill='x', pady=10)

        # Seção do filtro por Região Administrativa.
        lbl_filtro = tk.Label(self.frame_lateral, text="Filtrar por Cidade (RA):", font=("Arial", 9, "bold"))
        lbl_filtro.pack(anchor="w", padx=5)

        # Combobox interativo para seleção de RA pelo usuário.
        self.combobox_ra = ttk.Combobox(self.frame_lateral, state="readonly")
        self.combobox_ra.pack(fill=tk.X, padx=5, pady=5)
        # Associa a ação de seleção do combobox ao método de atualização dos dados.
        self.combobox_ra.bind("<<ComboboxSelected>>", self.ao_filtrar_ra)

        # Separador para separar a área de filtro do painel de estatísticas descritivas.
        ttk.Separator(self.frame_lateral, orient='horizontal').pack(fill='x', pady=10)

        # Painel de estatísticas descritivas calculadas em tempo real.
        self.frame_stats = tk.LabelFrame(self.frame_lateral, text="Indicadores da Região", font=("Arial", 9, "bold"))
        self.frame_stats.pack(fill=tk.X, padx=5, pady=5)

        # Rótulos para exibição das métricas estatísticas calculadas.
        self.lbl_stat_total = tk.Label(self.frame_stats, text="Amostra: - moradores", font=("Arial", 9), anchor="w")
        self.lbl_stat_total.pack(fill=tk.X, padx=5, pady=3)

        self.lbl_stat_plano = tk.Label(self.frame_stats, text="Possui Plano: -", font=("Arial", 9), anchor="w")
        self.lbl_stat_plano.pack(fill=tk.X, padx=5, pady=3)

        self.lbl_stat_renda_ind = tk.Label(self.frame_stats, text="Renda Ind. Média: -", font=("Arial", 9), anchor="w")
        self.lbl_stat_renda_ind.pack(fill=tk.X, padx=5, pady=3)

        self.lbl_stat_renda_dom = tk.Label(self.frame_stats, text="Renda Dom. Média: -", font=("Arial", 9), anchor="w")
        self.lbl_stat_renda_dom.pack(fill=tk.X, padx=5, pady=3)

        # Separador para a área de botões de ação.
        ttk.Separator(self.frame_lateral, orient='horizontal').pack(fill='x', pady=10)

        # Botão para exportar os dados atualmente filtrados por meio de uma janela de salvamento.
        self.btn_exportar = tk.Button(
            self.frame_lateral, 
            text="Exportar Dados Filtrados", 
            width=20, 
            bg="#d1e7dd", 
            command=self.acao_exportar_dialogo
        )
        self.btn_exportar.pack(fill=tk.X, padx=5, pady=5)

        # ÁREA PRINCIPAL (PAINEL DE EXIBIÇÃO)
        # Contêiner que abriga os painéis gráficos e informativos à direita.
        self.frame_principal = tk.Frame(self.janela)
        self.frame_principal.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Cabeçalho da área principal com título do recorte.
        lbl_titulo = tk.Label(
            self.frame_principal, 
            text="Análise Epidemiológica e de Acesso à Saúde (DF)", 
            font=("Arial", 14, "bold")
        )
        lbl_titulo.pack(pady=(0, 5))

        # Rótulo descritivo do recorte de dados analisado pelo sistema.
        lbl_descricao = tk.Label(
            self.frame_principal, 
            text="Exploração interativa dos dados sobre cobertura de plano de saúde privado, renda e SUS.", 
            font=("Arial", 9, "italic")
        )
        lbl_descricao.pack(pady=(0, 10))

        # Menu visual superior para alternar entre as abas do painel.
        self.frame_abas = tk.Frame(self.frame_principal)
        self.frame_abas.pack(fill=tk.X, pady=(0, 10))

        # Botões para alternar as funcionalidades de exibição gráfica, textual e de comparação.
        self.btn_aba_grafico = tk.Button(
            self.frame_abas, 
            text="Painel de Gráficos", 
            command=self.mostrar_painel_grafico, 
            font=("Arial", 9, "bold")
        )
        self.btn_aba_grafico.pack(side=tk.LEFT, padx=5)

        self.btn_aba_ranking = tk.Button(
            self.frame_abas, 
            text="Ranking de Cidades (Texto)", 
            command=self.mostrar_ranking_cidades, 
            font=("Arial", 9, "bold")
        )
        self.btn_aba_ranking.pack(side=tk.LEFT, padx=5)

        self.btn_aba_comparacao = tk.Button(
            self.frame_abas, 
            text="Comparar Cidades (D2)", 
            command=self.mostrar_painel_comparacao, 
            font=("Arial", 9, "bold")
        )
        self.btn_aba_comparacao.pack(side=tk.LEFT, padx=5)

        # CONTEÚDO DAS ABAS
        # 1. Aba de Gráficos (Matplotlib)
        self.frame_grafico = tk.Frame(self.frame_principal)
        self.frame_grafico.pack(fill=tk.BOTH, expand=True)

        # Cria a figura com dois subplots lado a lado para comportar os gráficos de barra e pizza.
        self.fig, (self.ax_bar, self.ax_pie) = plt.subplots(1, 2, figsize=(7, 4))
        self.fig.patch.set_facecolor('#f0f0f0') # Aplica cor cinza clara ao fundo do gráfico.

        # Incorpora a figura no Canvas do Tkinter.
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.frame_grafico)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # 2. Aba de Tabela Textual
        self.frame_tabela = tk.Frame(self.frame_principal)
        
        # Caixa de texto formatada com fonte monoespaçada para manter as colunas alinhadas.
        self.caixa_texto = scrolledtext.ScrolledText(
            self.frame_tabela, 
            width=70, 
            height=20, 
            font=("Courier", 9)
        )
        self.caixa_texto.pack(padx=5, pady=5, fill=tk.BOTH, expand=True)

        # Adicionado contêiner para comportar o painel de comparação entre duas cidades (Diferencial D2).
        self.frame_comparacao = tk.Frame(self.frame_principal)

        # Cria os controles superiores da aba de comparação.
        frame_controles_comp = tk.Frame(self.frame_comparacao)
        frame_controles_comp.pack(fill=tk.X, pady=5)

        tk.Label(frame_controles_comp, text="Cidade A:", font=("Arial", 9, "bold")).pack(side=tk.LEFT, padx=5)
        self.combobox_comp_ra1 = ttk.Combobox(frame_controles_comp, state="readonly", width=22)
        self.combobox_comp_ra1.pack(side=tk.LEFT, padx=5)
        self.combobox_comp_ra1.bind("<<ComboboxSelected>>", self.atualizar_comparacao)

        tk.Label(frame_controles_comp, text="VS", font=("Arial", 10, "bold")).pack(side=tk.LEFT, padx=15)

        tk.Label(frame_controles_comp, text="Cidade B:", font=("Arial", 9, "bold")).pack(side=tk.LEFT, padx=5)
        self.combobox_comp_ra2 = ttk.Combobox(frame_controles_comp, state="readonly", width=22)
        self.combobox_comp_ra2.pack(side=tk.LEFT, padx=5)
        self.combobox_comp_ra2.bind("<<ComboboxSelected>>", self.atualizar_comparacao)

        # Cria a tabela (grid) de comparação textual direta de indicadores.
        frame_grid = tk.Frame(self.frame_comparacao, relief=tk.GROOVE, bd=1)
        frame_grid.pack(pady=10, fill=tk.X)

        tk.Label(frame_grid, text="Indicador / Métrica", font=("Arial", 9, "bold")).grid(row=0, column=0, padx=15, pady=5, sticky="w")
        self.lbl_comp_head_ra1 = tk.Label(frame_grid, text="Cidade A", font=("Arial", 9, "bold"), fg="#3182bd")
        self.lbl_comp_head_ra1.grid(row=0, column=1, padx=15, pady=5)
        self.lbl_comp_head_ra2 = tk.Label(frame_grid, text="Cidade B", font=("Arial", 9, "bold"), fg="#e6550d")
        self.lbl_comp_head_ra2.grid(row=0, column=2, padx=15, pady=5)

        tk.Label(frame_grid, text="Tamanho da Amostra (Pessoas):").grid(row=1, column=0, padx=15, pady=3, sticky="w")
        self.lbl_comp_t1 = tk.Label(frame_grid, text="-")
        self.lbl_comp_t1.grid(row=1, column=1, padx=15, pady=3)
        self.lbl_comp_t2 = tk.Label(frame_grid, text="-")
        self.lbl_comp_t2.grid(row=1, column=2, padx=15, pady=3)

        tk.Label(frame_grid, text="Possui Plano de Saúde (%):").grid(row=2, column=0, padx=15, pady=3, sticky="w")
        self.lbl_comp_p1 = tk.Label(frame_grid, text="-")
        self.lbl_comp_p1.grid(row=2, column=1, padx=15, pady=3)
        self.lbl_comp_p2 = tk.Label(frame_grid, text="-")
        self.lbl_comp_p2.grid(row=2, column=2, padx=15, pady=3)

        tk.Label(frame_grid, text="Renda Individual Média:").grid(row=3, column=0, padx=15, pady=3, sticky="w")
        self.lbl_comp_ri1 = tk.Label(frame_grid, text="-")
        self.lbl_comp_ri1.grid(row=3, column=1, padx=15, pady=3)
        self.lbl_comp_ri2 = tk.Label(frame_grid, text="-")
        self.lbl_comp_ri2.grid(row=3, column=2, padx=15, pady=3)

        tk.Label(frame_grid, text="Renda Domiciliar Média:").grid(row=4, column=0, padx=15, pady=3, sticky="w")
        self.lbl_comp_rd1 = tk.Label(frame_grid, text="-")
        self.lbl_comp_rd1.grid(row=4, column=1, padx=15, pady=3)
        self.lbl_comp_rd2 = tk.Label(frame_grid, text="-")
        self.lbl_comp_rd2.grid(row=4, column=2, padx=15, pady=3)

        # Adiciona a figura matplotlib para o gráfico comparativo lado a lado.
        self.fig_comp, self.ax_comp = plt.subplots(figsize=(7, 3))
        self.fig_comp.patch.set_facecolor('#f0f0f0')
        self.canvas_comp = FigureCanvasTkAgg(self.fig_comp, master=self.frame_comparacao)
        self.canvas_comp.get_tk_widget().pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

    def carregar_dados_inicial(self):
        """Executa a leitura das planilhas na inicialização e informa o usuário sobre o progresso."""
        self.lbl_registros.config(text="Aguarde... Carregando dados...")
        self.janela.update()

        # Chama a função de carregamento que realiza o merge e limpa valores sentinela.
        self.df_pdad = carregar_dados()

        if self.df_pdad is None:
            messagebox.showerror("Erro de Leitura", "Não foi possível encontrar os arquivos da PDAD na pasta do programa.")
            self.lbl_registros.config(text="Erro de leitura dos dados.")
        else:
            # Obtém a contagem de linhas e o número de domicílios únicos para exibição.
            total_moradores = len(self.df_pdad)
            total_domicilios = self.df_pdad['A01nficha'].nunique()
            self.lbl_registros.config(text=f"{total_moradores:,} moradores · {total_domicilios:,} domicílios")

            # Popula a lista suspensa com todas as cidades encontradas nos microdados.
            lista_ras = sorted(self.df_pdad['nome_ra'].dropna().unique().tolist())
            self.combobox_ra['values'] = ["Distrito Federal (Geral)"] + lista_ras
            self.combobox_ra.current(0) # Define a seleção padrão como Geral.

            # Popula também as opções da aba de comparação de cidades.
            self.combobox_comp_ra1['values'] = lista_ras
            self.combobox_comp_ra2['values'] = lista_ras
            
            # Define seleções padrão distintas para as duas cidades comparadas.
            if len(lista_ras) > 1:
                self.combobox_comp_ra1.current(0)
                self.combobox_comp_ra2.current(1)
            else:
                self.combobox_comp_ra1.current(0)
                self.combobox_comp_ra2.current(0)

            # Inicializa a base filtrada com todos os dados carregados.
            self.df_filtrado = self.df_pdad
            
            # Executa a plotagem e cálculo inicial.
            self.atualizar_estatisticas()
            self.atualizar_graficos()

    def ao_filtrar_ra(self, event=None):
        """Filtra o DataFrame principal com base na cidade selecionada e redesenha a tela."""
        ra_selecionada = self.combobox_ra.get()

        if ra_selecionada == "Distrito Federal (Geral)":
            self.df_filtrado = self.df_pdad
        else:
            self.df_filtrado = self.df_pdad[self.df_pdad['nome_ra'] == ra_selecionada]

        # Atualiza os componentes visuais com os dados filtrados.
        self.atualizar_estatisticas()
        self.atualizar_graficos()

    def atualizar_estatisticas(self):
        """Calcula as estatísticas descritivas usando f-strings e exibe nos rótulos de texto."""
        if self.df_filtrado is None:
            return

        # Executa os cálculos estatísticos chamando a função do módulo calcular.py.
        total, pct, renda_ind, renda_dom = calcular_estatisticas_gerais(self.df_filtrado)

        # Atualiza os rótulos de controle com formatação decimal.
        self.lbl_stat_total.config(text=f"Amostra: {total:,} moradores")
        self.lbl_stat_plano.config(text=f"Possui Plano: {pct:.2f}%")
        self.lbl_stat_renda_ind.config(text=f"Renda Ind. Média: R$ {renda_ind:.2f}")
        self.lbl_stat_renda_dom.config(text=f"Renda Dom. Média: R$ {renda_dom:.2f}")

    def atualizar_graficos(self):
        """Limpa e redesenha o gráfico de barras e de pizza para a RA selecionada."""
        if self.df_filtrado is None:
            return

        # Limpa os eixos dos gráficos anteriores.
        self.ax_bar.clear()
        self.ax_pie.clear()

        # 1. Gráfico de Barras: Cobertura por Faixa de Renda (Diferencial D1)
        tabela_renda = calcular_saude_por_renda(self.df_filtrado)
        tabela_renda.plot(kind='bar', ax=self.ax_bar, color='#3182bd')
        self.ax_bar.set_title("Cobertura de Plano por Renda", fontsize=9, fontweight='bold')
        self.ax_bar.set_xlabel("Grupo de Renda", fontsize=8)
        self.ax_bar.set_ylabel("% com Plano", fontsize=8)
        self.ax_bar.set_xticklabels(tabela_renda.index, rotation=15, ha='right', fontsize=8)
        self.ax_bar.grid(axis='y', linestyle='--', alpha=0.5)

        # 2. Gráfico de Pizza: Proporção Geral na Região selecionada (Diferencial D1)
        proporcao = calcular_cobertura_plano_geral(self.df_filtrado)
        if not proporcao.empty:
            labels_pizza = []
            for k in proporcao.index:
                if k == 1.0:
                    labels_pizza.append("Tem Plano")
                else:
                    labels_pizza.append("SUS / Outro")

            self.ax_pie.pie(
                proporcao, 
                labels=labels_pizza, 
                autopct='%1.1f%%', 
                colors=['#41ab5d', '#ef3b2c'], 
                startangle=90,
                textprops={'fontsize': 8}
            )
            self.ax_pie.set_title("Proporção Geral", fontsize=9, fontweight='bold')
        else:
            self.ax_pie.text(0.5, 0.5, "Sem dados", ha='center', va='center', fontsize=8)

        # Ajusta automaticamente o layout da figura e atualiza o Canvas.
        self.fig.tight_layout()
        self.canvas.draw()

    # Adicionado método para comparar graficamente a posse de plano de saúde por renda de duas RAs (Diferencial D2).
    def atualizar_comparacao(self, event=None):
        """Filtra as duas RAs selecionadas, calcula suas estatísticas e plota o gráfico lado a lado."""
        if self.df_pdad is None:
            return

        ra1 = self.combobox_comp_ra1.get()
        ra2 = self.combobox_comp_ra2.get()

        # Altera os títulos dinâmicos da tabela de dados.
        self.lbl_comp_head_ra1.config(text=ra1)
        self.lbl_comp_head_ra2.config(text=ra2)

        # Filtra os dados de cada uma das RAs selecionadas.
        df_ra1 = self.df_pdad[self.df_pdad['nome_ra'] == ra1]
        df_ra2 = self.df_pdad[self.df_pdad['nome_ra'] == ra2]

        # Calcula os indicadores para ambas as cidades.
        t1, p1, ri1, rd1 = calcular_estatisticas_gerais(df_ra1)
        t2, p2, ri2, rd2 = calcular_estatisticas_gerais(df_ra2)

        # Atualiza a tabela informativa da tela.
        self.lbl_comp_t1.config(text=f"{t1:,}")
        self.lbl_comp_t2.config(text=f"{t2:,}")
        self.lbl_comp_p1.config(text=f"{p1:.2f}%")
        self.lbl_comp_p2.config(text=f"{p2:.2f}%")
        self.lbl_comp_ri1.config(text=f"R$ {ri1:.2f}")
        self.lbl_comp_ri2.config(text=f"R$ {ri2:.2f}")
        self.lbl_comp_rd1.config(text=f"R$ {rd1:.2f}")
        self.lbl_comp_rd2.config(text=f"R$ {rd2:.2f}")

        # Limpa o eixo gráfico comparativo.
        self.ax_comp.clear()

        # Calcula as coberturas de plano por faixa de renda para ambas.
        tabela_renda_ra1 = calcular_saude_por_renda(df_ra1)
        tabela_renda_ra2 = calcular_saude_por_renda(df_ra2)

        # Une os dois resultados em um único DataFrame para plotagem em colunas paralelas.
        df_plot = pd.DataFrame({
            ra1: tabela_renda_ra1,
            ra2: tabela_renda_ra2
        })

        # Desenha as barras lado a lado no matplotlib.
        df_plot.plot(kind='bar', ax=self.ax_comp, color=['#3182bd', '#e6550d'])
        self.ax_comp.set_title("Comparação de Cobertura por Faixa de Renda", fontsize=9, fontweight='bold')
        self.ax_comp.set_xlabel("Grupo de Renda", fontsize=8)
        self.ax_comp.set_ylabel("% com Plano Privado", fontsize=8)
        self.ax_comp.set_xticklabels(df_plot.index, rotation=15, ha='right', fontsize=8)
        self.ax_comp.grid(axis='y', linestyle='--', alpha=0.5)
        self.ax_comp.legend(fontsize=8)

        # Atualiza a área de desenho do matplotlib no Tkinter.
        self.fig_comp.tight_layout()
        self.canvas_comp.draw()

    def mostrar_painel_grafico(self):
        """Oculta o painel de tabelas em texto e exibe os gráficos do matplotlib."""
        self.frame_tabela.pack_forget()
        self.frame_comparacao.pack_forget()
        self.frame_grafico.pack(fill=tk.BOTH, expand=True)
        self.atualizar_graficos()

    def mostrar_ranking_cidades(self):
        """Oculta o painel gráfico e exibe a tabela ordenada de cobertura por RA."""
        self.frame_grafico.pack_forget()
        self.frame_comparacao.pack_forget()
        self.frame_tabela.pack(fill=tk.BOTH, expand=True)
        self.acao_cobertura_ra()

    # Adicionado método para alternar para a aba de comparação.
    def mostrar_painel_comparacao(self):
        """Oculta os painéis anteriores e exibe o painel de comparação lado a lado."""
        self.frame_grafico.pack_forget()
        self.frame_tabela.pack_forget()
        self.frame_comparacao.pack(fill=tk.BOTH, expand=True)
        self.atualizar_comparacao()

    def acao_cobertura_ra(self):
        """Calcula o acesso de planos por RA e insere a lista ordenada na caixa de texto."""
        if self.df_pdad is None: 
            return

        tabela_ra = calcular_acesso_por_ra(self.df_pdad)
        
        texto_out = "=== TAXA DE COBERTURA DE PLANO POR CIDADE (RA) ===\n"
        texto_out += "(Porcentagem da população da RA com plano privado)\n\n"
        texto_out += tabela_ra.to_string()
        
        # Limpa o texto anterior e insere os novos rankings.
        self.caixa_texto.delete("1.0", tk.END)
        self.caixa_texto.insert(tk.END, texto_out)

    def acao_exportar_dialogo(self):
        """Abre uma caixa de diálogo para salvar a base filtrada em um arquivo TXT."""
        if self.df_filtrado is None:
            messagebox.showwarning("Aviso", "Nenhum dado filtrado disponível para exportar.")
            return

        # Abre a caixa de diálogo padrão do sistema operacional para escolha do caminho do arquivo.
        caminho_arquivo = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Arquivo TXT", "*.txt"), ("Todos os arquivos", "*.*")],
            title="Salvar Microdados Filtrados"
        )

        if not caminho_arquivo:
            return

        # Grava os dados filtrados no formato TXT.
        exportar_para_txt(self.df_resultado, "resultados.txt")
        messagebox.showinfo("Exportação Concluída", f"Os dados foram salvos em '{caminho_arquivo}' com sucesso!")


def main():
    """Função principal que instancia o Tkinter e inicia o ciclo de execução da interface."""
    janela = tk.Tk()
    app = SistemaSaudeGUI(janela)
    janela.mainloop()


# Garante que o script seja executado apenas quando rodado diretamente no terminal.
if __name__ == "__main__":
    main()
