import sys
import tkinter as tk
from tkinter import ttk
import os
from PIL import Image, ImageTk

class WindTurbineSimulator:
    def __init__(self, root):
        self.root = root
        self.root.title("Simulador de Turbina Eólica")
        self.root.geometry("900x650")
        self.root.configure(bg="#f0f0f0")
        
        # Configurar o estilo
        self.style = ttk.Style()
        self.style.configure('TFrame', background='#f0f0f0')
        self.style.configure('TLabel', background='#f0f0f0', font=('Arial', 11))
        self.style.configure('TButton', font=('Arial', 11))
        self.style.configure('Header.TLabel', font=('Arial', 16, 'bold'))
        self.style.configure('Title.TLabel', font=('Arial', 24, 'bold'))
        self.style.configure('Subtitle.TLabel', font=('Arial', 14, 'italic'))
        
        self.create_widgets()
    
    def create_widgets(self):
        # Frame principal
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Título e subtítulo
        title_label = ttk.Label(
            main_frame, 
            text="Simulador de Turbina Eólica de Velocidade Variável", 
            style='Title.TLabel'
        )
        title_label.pack(pady=(0, 10))
        
        subtitle_label = ttk.Label(
            main_frame, 
            text="Modelagem e Análise de Componentes de Turbinas Eólicas",
            style='Subtitle.TLabel'
        )
        subtitle_label.pack(pady=(0, 20))
        
        # Separador
        separator = ttk.Separator(main_frame, orient='horizontal')
        separator.pack(fill=tk.X, pady=10)
        
        # Frame para conteúdo
        content_frame = ttk.Frame(main_frame)
        content_frame.pack(fill=tk.BOTH, expand=True)
        
        # Seção de objetivos
        objectives_frame = ttk.LabelFrame(content_frame, text="Objetivos do Projeto")
        objectives_frame.pack(fill=tk.X, pady=10, padx=5)
        
        # Objetivo geral
        ttk.Label(
            objectives_frame, 
            text="Objetivo Geral:",
            style='Header.TLabel'
        ).pack(anchor=tk.W, pady=(10, 5))
        
        ttk.Label(
            objectives_frame, 
            text="Desenvolver um simulador de turbina eólica de velocidade variável, além de um sistema de supervisão\n"
                 "que possibilite testar a turbina em diferentes regimes de vento e pontos de operação.",
            wraplength=800
        ).pack(anchor=tk.W, padx=15)
        
        # Objetivos específicos
        ttk.Label(
            objectives_frame, 
            text="Objetivos Específicos:",
            style='Header.TLabel'
        ).pack(anchor=tk.W, pady=(15, 5))
        
        objectives = [
            "Revisão da literatura sobre sistemas de conversão eólica.",
            "Obtenção do perfil médio de vento em Cachoeira do Sul.",
            "Aquisição da série temporal do vento, incluindo turbulência e rajadas de vento.",
            "Desenvolvimento de um sistema de controle para uma turbina eólica de 20 kW, abrangendo desde a velocidade\n"
            "mínima de cut-in, técnica de MPPT, limitação de potência e cut-off.",
            "Implementação de uma plataforma de simulação que permita a modelagem e análise de todos os componentes\n"
            "de uma turbina eólica.",
            "Desenvolvimento de um sistema de supervisão utilizando Python.",
            "Avaliação do desempenho do sistema de emulação em diferentes cenários operacionais."
        ]
        
        for i, obj in enumerate(objectives, 1):
            ttk.Label(
                objectives_frame, 
                text=f"{i}. {obj}",
                wraplength=800
            ).pack(anchor=tk.W, padx=15, pady=2)
        
        # Separador
        separator2 = ttk.Separator(main_frame, orient='horizontal')
        separator2.pack(fill=tk.X, pady=10)
        
        # Seção de contexto
        context_frame = ttk.LabelFrame(content_frame, text="Contexto e Motivação")
        context_frame.pack(fill=tk.X, pady=10, padx=5)
        
        context_text = (
            "A crescente necessidade de geração de energia elétrica, impulsionada pelo aumento da população e pela "
            "expansão econômica, evidencia a urgência de soluções energéticas eficientes e sustentáveis. A energia "
            "eólica emerge como uma opção viável e necessária para atender à demanda crescente por eletricidade de "
            "forma ambientalmente responsável.\n\n"
            
            "O Brasil tem uma matriz energética considerada uma das mais limpas do mundo, com cerca de 83% da "
            "eletricidade proveniente de fontes renováveis. A energia eólica representa aproximadamente 10% da "
            "geração elétrica do país, com capacidade instalada superior a 16 gigawatts, e potencial para expansão "
            "significativa, especialmente nas regiões Nordeste e Sul.\n\n"
            
            "Com investimentos substanciais tanto do setor público quanto do privado, o setor de energia eólica no "
            "Brasil continua em expansão. Neste contexto, torna-se cada vez mais necessário desenvolver estudos para "
            "prever e reduzir problemas no controle de turbinas, otimizando a qualidade da energia produzida através "
            "do aprimoramento das técnicas de operação, controle de velocidade e limitação de potência."
        )
        
        context_label = ttk.Label(
            context_frame,
            text=context_text,
            wraplength=800,
            justify=tk.LEFT
        )
        context_label.pack(anchor=tk.W, padx=10, pady=10)
        
        # Botões de navegação
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=15)
        
        ttk.Button(
            button_frame, 
            text="Cadastrar Localidade",
            command=self.open_cadastro_localidade
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            button_frame, 
            text="Listar Localidades",
            command=self.open_listar_localidades
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            button_frame, 
            text="Simulador de Turbina",
            command=self.open_simulador
        ).pack(side=tk.LEFT, padx=5)
        
        # Botão sair
        ttk.Button(
            button_frame, 
            text="Sair",
            command=self.root.quit
        ).pack(side=tk.RIGHT, padx=5)
    
    def open_cadastro_localidade(self):
        try:
            # Verifica se o arquivo existe no diretório pages
            if os.path.exists("pages/cadastro_localidade.py"):
                # Importa e executa
                import pages.cadastro_localidade as cadastro
                cadastro.show_window(self.root)
            elif os.path.exists("pagess/wind_pages/cadastro_localidade.py"):
                # Alternativa se existir no outro diretório
                import pagess.wind_pages.cadastro_localidade as cadastro
                cadastro.show_window(self.root)
            else:
                print("Módulo de cadastro de localidade não encontrado.")
        except Exception as e:
            print(f"Erro ao abrir cadastro de localidade: {e}")
    
    def open_listar_localidades(self):
        try:
            # Verifica se o arquivo existe no diretório pages
            if os.path.exists("pages/listar_localidades.py"):
                # Importa e executa
                import pages.listar_localidades as listar
                listar.show_window(self.root)
            elif os.path.exists("pagess/wind_pages/listar_localidades.py"):
                # Alternativa se existir no outro diretório
                import pagess.wind_pages.listar_localidades as listar
                listar.show_window(self.root)
            else:
                print("Módulo de listagem de localidades não encontrado.")
        except Exception as e:
            print(f"Erro ao abrir listagem de localidades: {e}")
    
    def open_simulador(self):
        # Esta função seria implementada quando o simulador estiver pronto
        print("Módulo de simulação ainda não implementado.")
        messagebox = tk.messagebox.showinfo(
            title="Em desenvolvimento", 
            message="O módulo de simulação está em desenvolvimento."
        )


if __name__ == "__main__":
    try:
        from tkinter import messagebox
        root = tk.Tk()
        app = WindTurbineSimulator(root)
        root.mainloop()
    except Exception as e:
        print(f"Erro ao iniciar aplicação: {e}")
