import tkinter as tk
from tkinter import ttk, simpledialog, messagebox, scrolledtext
import math
import random
from graph import Graph
from caminho_mais_curto import dijkstra
import database_manager as db_manager

# Constantes Globais
CANVAS_WIDTH = 400
CANVAS_HEIGHT = 380
NODE_RADIUS = 15
FONT_SIZE = 8

TIPOS_CAMIAO = ["Carga Seca", "Frigorífico", "Basculante", "Tanque", "Porta-Contentores", "Sider", "Outro"]
ESTADOS_CAMIAO = ["Disponível", "Em Rota", "Em Manutenção", "Indisponível"]
UNIDADES_CAPACIDADE = ["ton", "kg", "m³", "paletes", "unidades"]
CATEGORIAS_CNH = ["A", "B", "C", "D", "E", "AB", "AC", "AD", "AE"]
ESTADOS_MOTORISTA = ["Disponível", "Em Rota", "De Folga", "Indisponível"]
TIPOS_CARGA = ["Paletizada", "Granel Solido", "Granel Líquido", "Refrigerada", "Congelada", "Perigosa", "Viva", "Geral", "Outra"]
ESTADOS_CARGA = ['Pendente', 'Agendada', 'Coletada', 'Em Trânsito', 'Entregue', 'Cancelada', 'Atrasada']

class CityGraphApp:
    def __init__(self, root_window):
        self.root = root_window
        self.root.title("Sistema Integrado de Logística e Transportes")
        self.root.geometry("1600x900")

        if not db_manager.initialize_database():
            messagebox.showerror("Erro Crítico de Base de Dados", 
                                "Não foi possível inicializar a base de dados. A aplicação será encerrada.")
            self.root.destroy()
            return

        self.city_graph = Graph()
        self.node_attributes = {}
        
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(expand=True, fill='both', padx=10, pady=10)

        self.camiao_form_widgets = {}
        self.motorista_form_widgets = {}
        self.carga_form_widgets = {}
        self.entrega_form_widgets = {}

        self.selected_camiao_db_id = None
        self.selected_motorista_db_id = None
        self.selected_carga_db_id = None

        self.tab_mapa = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(self.tab_mapa, text='Gestão de Mapa (Pontos e Conexões)')
        self._setup_mapa_tab()

        self.tab_camioes = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(self.tab_camioes, text='Cadastro de Caminhões')
        self._setup_camioes_tab()

        self.tab_motoristas = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(self.tab_motoristas, text='Cadastro de Motoristas')
        self._setup_motoristas_tab()

        self.tab_cargas = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(self.tab_cargas, text='Cadastro de Cargas')
        self._setup_cargas_tab()

        self.tab_entregas = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(self.tab_entregas, text='Operações de Entrega')
        self._setup_entregas_tab()
        
        self._load_all_initial_data()
        self.log_result("Interface iniciada. Dados carregados da base de dados.")

    def _load_all_initial_data(self):
        self._load_graph_from_db()
        self._load_camioes_gui()
        self._load_motoristas_gui()
        self._load_cargas_gui()
        self._update_carga_form_combos()
        self._update_entrega_form_combos()

    def _setup_mapa_tab(self):
        main_frame = self.tab_mapa
        graph_input_frame = ttk.LabelFrame(main_frame, text="Definir Pontos e Conexões", padding="10")
        graph_input_frame.grid(row=0, column=0, padx=5, pady=5, sticky="ns")
        operations_frame = ttk.LabelFrame(main_frame, text="Operações do Grafo e Log", padding="10")
        operations_frame.grid(row=0, column=1, padx=5, pady=5, sticky="nsew")
        map_frame = ttk.LabelFrame(main_frame, text="Visualização do Mapa", padding="10")
        map_frame.grid(row=0, column=2, padx=5, pady=5, sticky="nsew")
        main_frame.columnconfigure(1, weight=1); main_frame.columnconfigure(2, weight=1); main_frame.rowconfigure(0, weight=1)

        ttk.Label(graph_input_frame, text="Nome do Ponto:").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.vertex_name_entry = ttk.Entry(graph_input_frame, width=20)
        self.vertex_name_entry.grid(row=0, column=1, pady=2, columnspan=2)
        ttk.Label(graph_input_frame, text="Tipo:").grid(row=1, column=0, sticky=tk.W, pady=2)
        self.vertex_type_combo = ttk.Combobox(graph_input_frame, values=["Depósito", "Cidade"], width=18, state="readonly")
        self.vertex_type_combo.grid(row=1, column=1, pady=2, columnspan=2); self.vertex_type_combo.current(0)
        ttk.Button(graph_input_frame, text="Adicionar Ponto", command=self.add_vertex_gui).grid(row=2, column=0, columnspan=3, pady=5)
        ttk.Separator(graph_input_frame, orient='horizontal').grid(row=3, column=0, columnspan=3, sticky='ew', pady=10)
        ttk.Label(graph_input_frame, text="De (Ponto U):").grid(row=4, column=0, sticky=tk.W, pady=2)
        self.edge_u_combo = ttk.Combobox(graph_input_frame, width=25, state="readonly")
        self.edge_u_combo.grid(row=4, column=1, columnspan=2, pady=2)
        ttk.Label(graph_input_frame, text="Para (Ponto V):").grid(row=5, column=0, sticky=tk.W, pady=2)
        self.edge_v_combo = ttk.Combobox(graph_input_frame, width=25, state="readonly")
        self.edge_v_combo.grid(row=5, column=1, columnspan=2, pady=2)
        ttk.Label(graph_input_frame, text="Distância (km):").grid(row=6, column=0, sticky=tk.W, pady=2)
        self.edge_weight_entry = ttk.Entry(graph_input_frame, width=20)
        self.edge_weight_entry.grid(row=6, column=1, columnspan=2, pady=2)
        self.bidirectional_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(graph_input_frame, text="Bidirecional", variable=self.bidirectional_var).grid(row=7, column=1, sticky=tk.W, pady=2)
        ttk.Button(graph_input_frame, text="Adicionar Conexão", command=self.add_edge_gui).grid(row=7, column=0, padx=5, pady=5, sticky=tk.E)
        ttk.Separator(graph_input_frame, orient='horizontal').grid(row=8, column=0, columnspan=3, sticky='ew', pady=10)
        ttk.Button(graph_input_frame, text="Limpar Grafo (e BD)", command=self.clear_graph_gui).grid(row=9, column=0, columnspan=3, pady=5)
        ttk.Button(graph_input_frame, text="Recarregar Grafo da BD", command=self._load_graph_from_db).grid(row=10, column=0, columnspan=3, pady=5)

        dijkstra_frame = ttk.LabelFrame(operations_frame, text="Cálculo de Rota (Dijkstra)", padding="10")
        dijkstra_frame.pack(fill=tk.X, pady=5) 
        ttk.Label(dijkstra_frame, text="Ponto de Partida:").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.start_node_combo = ttk.Combobox(dijkstra_frame, width=30, state="readonly")
        self.start_node_combo.grid(row=0, column=1, padx=5, pady=2)
        ttk.Label(dijkstra_frame, text="Ponto de Chegada:").grid(row=1, column=0, sticky=tk.W, pady=2)
        self.end_node_combo = ttk.Combobox(dijkstra_frame, width=30, state="readonly")
        self.end_node_combo.grid(row=1, column=1, padx=5, pady=2)
        ttk.Button(dijkstra_frame, text="Calcular Rota", command=self.run_dijkstra_gui).grid(row=2, column=0, columnspan=2, pady=10)
        
        ttk.Label(operations_frame, text="Estrutura do Grafo (Texto):").pack(anchor=tk.W, pady=(10,0))
        self.graph_display_text = scrolledtext.ScrolledText(operations_frame, width=60, height=10, wrap=tk.WORD)
        self.graph_display_text.pack(fill=tk.BOTH, expand=True, pady=5); self.graph_display_text.config(state=tk.DISABLED)

        ttk.Label(operations_frame, text="Log de Operações:").pack(anchor=tk.W, pady=(10,0))
        self.results_text = scrolledtext.ScrolledText(operations_frame, width=60, height=10, wrap=tk.WORD)
        self.results_text.pack(fill=tk.BOTH, expand=True, pady=5); self.results_text.config(state=tk.DISABLED)

        self.map_canvas = tk.Canvas(map_frame, width=CANVAS_WIDTH, height=CANVAS_HEIGHT, bg="ivory", relief=tk.SUNKEN, borderwidth=1)
        self.map_canvas.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        ttk.Button(map_frame, text="Reorganizar e Guardar Layout", command=self.randomize_and_save_layout_gui).pack(pady=5)
    
    def _setup_camioes_tab(self):
        camioes_main_frame = ttk.Frame(self.tab_camioes)
        camioes_main_frame.pack(fill=tk.BOTH, expand=True)
        form_frame = ttk.LabelFrame(camioes_main_frame, text="Detalhes do Camião", padding="10")
        form_frame.grid(row=0, column=0, padx=5, pady=5, sticky="ns")
        list_frame = ttk.LabelFrame(camioes_main_frame, text="Camiões Registados", padding="10")
        list_frame.grid(row=0, column=1, padx=5, pady=5, sticky="nsew")
        camioes_main_frame.columnconfigure(1, weight=1); camioes_main_frame.rowconfigure(0, weight=1)

        form_fields = [
            ("Matrícula(*):", "matricula_camiao_entry", None), ("Nome/Descrição:", "nome_camiao_entry", None),
            ("Capacidade:", "capacidade_camiao_entry", None), ("Unidade Capac.:", "unidade_cap_camiao_combo", UNIDADES_CAPACIDADE),
            ("Tipo Veículo:", "tipo_veiculo_camiao_combo", TIPOS_CAMIAO), ("Estado:", "estado_camiao_combo", ESTADOS_CAMIAO),
            ("Localização Atual:", "localizacao_camiao_combo", []), ("Observações:", "obs_camiao_text", "Text")
        ]
        for i, (label_text, widget_name, combo_values) in enumerate(form_fields):
            ttk.Label(form_frame, text=label_text).grid(row=i, column=0, sticky=tk.W, padx=5, pady=3)
            if combo_values == "Text": widget = scrolledtext.ScrolledText(form_frame, width=30, height=3, wrap=tk.WORD)
            elif isinstance(combo_values, list):
                widget = ttk.Combobox(form_frame, width=28, values=combo_values, state="readonly" if combo_values else "normal")
                if combo_values: widget.current(0)
            else: widget = ttk.Entry(form_frame, width=30)
            widget.grid(row=i, column=1, sticky=tk.EW, padx=5, pady=3); self.camiao_form_widgets[widget_name] = widget
        
        action_buttons_frame = ttk.Frame(form_frame)
        action_buttons_frame.grid(row=len(form_fields), column=0, columnspan=2, pady=10)
        self.add_camiao_btn = ttk.Button(action_buttons_frame, text="Adicionar", command=self._add_camiao_gui)
        self.add_camiao_btn.pack(side=tk.LEFT, padx=5)
        self.update_camiao_btn = ttk.Button(action_buttons_frame, text="Guardar", command=self._update_camiao_gui, state=tk.DISABLED)
        self.update_camiao_btn.pack(side=tk.LEFT, padx=5)
        self.remove_camiao_btn = ttk.Button(action_buttons_frame, text="Remover", command=self._remove_camiao_gui, state=tk.DISABLED)
        self.remove_camiao_btn.pack(side=tk.LEFT, padx=5)
        self.clear_camiao_fields_btn = ttk.Button(action_buttons_frame, text="Limpar", command=self._clear_camiao_fields_gui)
        self.clear_camiao_fields_btn.pack(side=tk.LEFT, padx=5)

        cols = ("id", "matricula", "nome", "tipo_veiculo", "estado", "localizacao")
        col_names = ("ID", "Matrícula", "Nome/Descrição", "Tipo", "Estado", "Localização")
        col_widths = (40, 100, 180, 120, 100, 150)
        self.camioes_treeview = ttk.Treeview(list_frame, columns=cols, show="headings", height=15)
        for i, col_name in enumerate(col_names):
            self.camioes_treeview.heading(cols[i], text=col_name); self.camioes_treeview.column(cols[i], width=col_widths[i], anchor=tk.W)
        ys = ttk.Scrollbar(list_frame, orient="vertical", command=self.camioes_treeview.yview)
        xs = ttk.Scrollbar(list_frame, orient="horizontal", command=self.camioes_treeview.xview)
        self.camioes_treeview.configure(yscrollcommand=ys.set, xscrollcommand=xs.set)
        ys.pack(side=tk.RIGHT, fill=tk.Y); xs.pack(side=tk.BOTTOM, fill=tk.X); self.camioes_treeview.pack(fill=tk.BOTH, expand=True)
        self.camioes_treeview.bind("<<TreeviewSelect>>", self._on_camiao_select)

    def _setup_motoristas_tab(self):
        motoristas_main_frame = ttk.Frame(self.tab_motoristas)
        motoristas_main_frame.pack(fill=tk.BOTH, expand=True)
        form_frame = ttk.LabelFrame(motoristas_main_frame, text="Detalhes do Motorista", padding="10")
        form_frame.grid(row=0, column=0, padx=5, pady=5, sticky="ns")
        list_frame = ttk.LabelFrame(motoristas_main_frame, text="Motoristas Registados", padding="10")
        list_frame.grid(row=0, column=1, padx=5, pady=5, sticky="nsew")
        motoristas_main_frame.columnconfigure(1, weight=1); motoristas_main_frame.rowconfigure(0, weight=1)

        form_fields = [
            ("Nome Completo(*):", "nome_motorista_entry", None), ("CNH(*):", "cnh_motorista_entry", None),
            ("Categoria CNH:", "cat_cnh_motorista_combo", CATEGORIAS_CNH), ("Validade CNH:", "val_cnh_motorista_entry", "YYYY-MM-DD"),
            ("Telefone:", "tel_motorista_entry", None), ("Email:", "email_motorista_entry", None),
            ("Estado:", "estado_motorista_combo", ESTADOS_MOTORISTA), ("Observações:", "obs_motorista_text", "Text")
        ]
        for i, (label_text, widget_name, combo_values_or_placeholder) in enumerate(form_fields):
            ttk.Label(form_frame, text=label_text).grid(row=i, column=0, sticky=tk.W, padx=5, pady=3)
            if combo_values_or_placeholder == "Text": widget = scrolledtext.ScrolledText(form_frame, width=30, height=3, wrap=tk.WORD)
            elif isinstance(combo_values_or_placeholder, list):
                widget = ttk.Combobox(form_frame, width=28, values=combo_values_or_placeholder, state="readonly")
                if combo_values_or_placeholder: widget.current(0)
            else:
                widget = ttk.Entry(form_frame, width=30)
                if isinstance(combo_values_or_placeholder, str):
                    widget.insert(0, combo_values_or_placeholder)
                    widget.config(foreground="grey")
                    widget.bind("<FocusIn>", lambda e, w=widget, p=combo_values_or_placeholder: self._clear_placeholder(e, w, p))
                    widget.bind("<FocusOut>", lambda e, w=widget, p=combo_values_or_placeholder: self._add_placeholder(e, w, p))
            widget.grid(row=i, column=1, sticky=tk.EW, padx=5, pady=3); self.motorista_form_widgets[widget_name] = widget
        
        action_buttons_frame = ttk.Frame(form_frame)
        action_buttons_frame.grid(row=len(form_fields), column=0, columnspan=2, pady=10)
        self.add_motorista_btn = ttk.Button(action_buttons_frame, text="Adicionar", command=self._add_motorista_gui)
        self.add_motorista_btn.pack(side=tk.LEFT, padx=5)
        self.update_motorista_btn = ttk.Button(action_buttons_frame, text="Guardar", command=self._update_motorista_gui, state=tk.DISABLED)
        self.update_motorista_btn.pack(side=tk.LEFT, padx=5)
        self.remove_motorista_btn = ttk.Button(action_buttons_frame, text="Remover", command=self._remove_motorista_gui, state=tk.DISABLED)
        self.remove_motorista_btn.pack(side=tk.LEFT, padx=5)
        self.clear_motorista_fields_btn = ttk.Button(action_buttons_frame, text="Limpar", command=self._clear_motorista_fields_gui)
        self.clear_motorista_fields_btn.pack(side=tk.LEFT, padx=5)

        cols = ("id", "nome", "cnh", "categoria_cnh", "estado", "telefone")
        col_names = ("ID", "Nome Completo", "CNH", "Cat. CNH", "Estado", "Telefone")
        col_widths = (40, 200, 100, 80, 100, 120)
        self.motoristas_treeview = ttk.Treeview(list_frame, columns=cols, show="headings", height=15)
        for i, col_name in enumerate(col_names):
            self.motoristas_treeview.heading(cols[i], text=col_name); self.motoristas_treeview.column(cols[i], width=col_widths[i], anchor=tk.W)
        ys = ttk.Scrollbar(list_frame, orient="vertical", command=self.motoristas_treeview.yview)
        xs = ttk.Scrollbar(list_frame, orient="horizontal", command=self.motoristas_treeview.xview)
        self.motoristas_treeview.configure(yscrollcommand=ys.set, xscrollcommand=xs.set)
        ys.pack(side=tk.RIGHT, fill=tk.Y); xs.pack(side=tk.BOTTOM, fill=tk.X); self.motoristas_treeview.pack(fill=tk.BOTH, expand=True)
        self.motoristas_treeview.bind("<<TreeviewSelect>>", self._on_motorista_select)

    def _setup_cargas_tab(self):
        cargas_main_frame = ttk.Frame(self.tab_cargas)
        cargas_main_frame.pack(fill=tk.BOTH, expand=True)
        form_frame = ttk.LabelFrame(cargas_main_frame, text="Detalhes da Carga", padding="10")
        form_frame.grid(row=0, column=0, padx=5, pady=5, sticky="ns")
        list_frame = ttk.LabelFrame(cargas_main_frame, text="Cargas Registadas", padding="10")
        list_frame.grid(row=0, column=1, padx=5, pady=5, sticky="nsew")
        cargas_main_frame.columnconfigure(1, weight=1); cargas_main_frame.rowconfigure(0, weight=1)

        form_fields = [
            ("Descrição(*):", "desc_carga_entry", None), ("Tipo Carga:", "tipo_carga_combo", TIPOS_CARGA),
            ("Peso (kg):", "peso_carga_entry", None), ("Volume (m³):", "volume_carga_entry", None),
            ("Ponto Origem(*):", "origem_carga_combo", []), ("Ponto Destino(*):", "destino_carga_combo", []),
            ("Cliente:", "cliente_carga_entry", None), ("Data Coleta:", "dt_coleta_carga_entry", "YYYY-MM-DD"),
            ("Data Entrega:", "dt_entrega_carga_entry", "YYYY-MM-DD"), ("Estado:", "estado_carga_combo", ESTADOS_CARGA),
            ("Camião Atribuído:", "camiao_carga_combo", []), ("Motorista Atribuído:", "motorista_carga_combo", []),
            ("Observações:", "obs_carga_text", "Text")
        ]
        for i, (label_text, widget_name, combo_values_or_placeholder) in enumerate(form_fields):
            ttk.Label(form_frame, text=label_text).grid(row=i, column=0, sticky=tk.W, padx=5, pady=2)
            if combo_values_or_placeholder == "Text": widget = scrolledtext.ScrolledText(form_frame, width=30, height=2, wrap=tk.WORD)
            elif isinstance(combo_values_or_placeholder, list):
                widget = ttk.Combobox(form_frame, width=28, values=combo_values_or_placeholder, state="readonly" if combo_values_or_placeholder else "normal")
                if combo_values_or_placeholder and widget['state'] == 'readonly': widget.current(0)
            else:
                widget = ttk.Entry(form_frame, width=30)
                if isinstance(combo_values_or_placeholder, str):
                    widget.insert(0, combo_values_or_placeholder)
                    widget.config(foreground="grey")
                    widget.bind("<FocusIn>", lambda e, w=widget, p=combo_values_or_placeholder: self._clear_placeholder(e, w, p))
                    widget.bind("<FocusOut>", lambda e, w=widget, p=combo_values_or_placeholder: self._add_placeholder(e, w, p))
            widget.grid(row=i, column=1, sticky=tk.EW, padx=5, pady=2); self.carga_form_widgets[widget_name] = widget
        
        action_buttons_frame = ttk.Frame(form_frame)
        action_buttons_frame.grid(row=len(form_fields), column=0, columnspan=2, pady=10)
        self.add_carga_btn = ttk.Button(action_buttons_frame, text="Adicionar", command=self._add_carga_gui)
        self.add_carga_btn.pack(side=tk.LEFT, padx=5)
        self.update_carga_btn = ttk.Button(action_buttons_frame, text="Guardar", command=self._update_carga_gui, state=tk.DISABLED)
        self.update_carga_btn.pack(side=tk.LEFT, padx=5)
        self.remove_carga_btn = ttk.Button(action_buttons_frame, text="Remover", command=self._remove_carga_gui, state=tk.DISABLED)
        self.remove_carga_btn.pack(side=tk.LEFT, padx=5)
        self.clear_carga_fields_btn = ttk.Button(action_buttons_frame, text="Limpar", command=self._clear_carga_fields_gui)
        self.clear_carga_fields_btn.pack(side=tk.LEFT, padx=5)

        cols = ("id", "descricao", "origem", "destino", "estado_carga", "camiao", "motorista")
        col_names = ("ID", "Descrição", "Origem", "Destino", "Estado", "Camião", "Motorista")
        col_widths = (40, 200, 120, 120, 100, 100, 150)
        self.cargas_treeview = ttk.Treeview(list_frame, columns=cols, show="headings", height=15)
        for i, col_name in enumerate(col_names):
            self.cargas_treeview.heading(cols[i], text=col_name); self.cargas_treeview.column(cols[i], width=col_widths[i], anchor=tk.W)
        ys = ttk.Scrollbar(list_frame, orient="vertical", command=self.cargas_treeview.yview)
        xs = ttk.Scrollbar(list_frame, orient="horizontal", command=self.cargas_treeview.xview)
        self.cargas_treeview.configure(yscrollcommand=ys.set, xscrollcommand=xs.set)
        ys.pack(side=tk.RIGHT, fill=tk.Y); xs.pack(side=tk.BOTTOM, fill=tk.X); self.cargas_treeview.pack(fill=tk.BOTH, expand=True)
        self.cargas_treeview.bind("<<TreeviewSelect>>", self._on_carga_select)

    def _setup_entregas_tab(self):
        entregas_main_frame = ttk.Frame(self.tab_entregas)
        entregas_main_frame.pack(fill=tk.BOTH, expand=True)
        control_frame = ttk.LabelFrame(entregas_main_frame, text="Planeamento de Entrega", padding="10")
        control_frame.pack(pady=10, padx=10, fill=tk.X)

        ttk.Label(control_frame, text="Carga a Entregar:").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        self.entrega_carga_combo = ttk.Combobox(control_frame, width=40, state="readonly")
        self.entrega_carga_combo.grid(row=0, column=1, padx=5, pady=5, sticky=tk.EW)
        ttk.Label(control_frame, text="Motorista Designado:").grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)
        self.entrega_motorista_combo = ttk.Combobox(control_frame, width=40, state="readonly")
        self.entrega_motorista_combo.grid(row=1, column=1, padx=5, pady=5, sticky=tk.EW)
        ttk.Label(control_frame, text="Camião Designado:").grid(row=2, column=0, padx=5, pady=5, sticky=tk.W)
        self.entrega_camiao_combo = ttk.Combobox(control_frame, width=40, state="readonly")
        self.entrega_camiao_combo.grid(row=2, column=1, padx=5, pady=5, sticky=tk.EW)
        ttk.Label(control_frame, text="Ponto de Origem:").grid(row=3, column=0, padx=5, pady=5, sticky=tk.W)
        self.entrega_origem_label = ttk.Label(control_frame, text="N/A", width=40)
        self.entrega_origem_label.grid(row=3, column=1, padx=5, pady=5, sticky=tk.EW)
        ttk.Label(control_frame, text="Ponto de Destino:").grid(row=4, column=0, padx=5, pady=5, sticky=tk.W)
        self.entrega_destino_label = ttk.Label(control_frame, text="N/A", width=40)
        self.entrega_destino_label.grid(row=4, column=1, padx=5, pady=5, sticky=tk.EW)
        control_frame.columnconfigure(1, weight=1)
        self.entrega_carga_combo.bind("<<ComboboxSelected>>", self._on_entrega_carga_selected)

        action_frame = ttk.Frame(entregas_main_frame); action_frame.pack(pady=10)
        ttk.Button(action_frame, text="Calcular Rota e Ver Detalhes", command=self._calcular_rota_entrega_gui).pack(side=tk.LEFT, padx=10)
        self.iniciar_entrega_btn = ttk.Button(action_frame, text="Iniciar Entrega (Simulação)", command=self._iniciar_entrega_gui, state=tk.DISABLED)
        self.iniciar_entrega_btn.pack(side=tk.LEFT, padx=10)

        map_entrega_frame = ttk.LabelFrame(entregas_main_frame, text="Mapa da Rota da Entrega", padding="10")
        map_entrega_frame.pack(pady=10, padx=10, fill=tk.BOTH, expand=True)
        self.entrega_map_canvas = tk.Canvas(map_entrega_frame, width=CANVAS_WIDTH+100, height=CANVAS_HEIGHT+50, bg="lightyellow", relief=tk.SUNKEN, borderwidth=1)
        self.entrega_map_canvas.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(entregas_main_frame, text="Detalhes da Rota Calculada:").pack(anchor=tk.W, padx=10, pady=(5,0))
        self.entrega_rota_details_text = scrolledtext.ScrolledText(entregas_main_frame, width=80, height=5, wrap=tk.WORD)
        self.entrega_rota_details_text.pack(padx=10, pady=5, fill=tk.X, expand=False); self.entrega_rota_details_text.config(state=tk.DISABLED)
        
    def _clear_placeholder(self, event, widget, placeholder_text):
        if widget.get() == placeholder_text and widget.cget('foreground') == "grey":
            widget.delete(0, tk.END); widget.config(foreground="black")

    def _add_placeholder(self, event, widget, placeholder_text):
        if not widget.get(): widget.insert(0, placeholder_text); widget.config(foreground="grey")

    def _load_graph_from_db(self):
        self.log_result("A carregar grafo da base de dados...")
        self.city_graph = Graph(); self.node_attributes = {}
        pontos_db = db_manager.obter_todos_pontos_db()
        if pontos_db is None: messagebox.showerror("Erro BD", "Falha ao carregar pontos."); return
        for p_data in pontos_db:
            nome, db_id, tipo = p_data['nome'], p_data['id'], p_data['tipo']
            cx, cy = p_data.get('coord_x'), p_data.get('coord_y')
            self.city_graph.add_vertex(nome)
            self.node_attributes[nome] = {
                'id': db_id, 'type': tipo,
                'coords': (cx, cy) if cx is not None and cy is not None \
                        else self._assign_and_save_random_coords(db_id, nome)
            }
        conexoes_db = db_manager.obter_todas_conexoes_db()
        if conexoes_db is None: messagebox.showerror("Erro BD", "Falha ao carregar conexões."); return
        for c_data in conexoes_db:
            n_o, n_d = c_data['nome_origem'], c_data['nome_destino']
            dist, bidir = float(c_data['distancia']), bool(c_data['bidirecional'])
            if n_o in self.city_graph.get_vertices() and n_d in self.city_graph.get_vertices():
                self.city_graph.add_edge(n_o, n_d, dist, bidirectional=bidir)
        self.update_graph_display_gui(); self.update_all_node_comboboxes_gui(); self.redraw_canvas_gui()
        self.log_result(f"{len(pontos_db)} pontos e {len(conexoes_db)} conexões carregadas.")

    def _assign_and_save_random_coords(self, db_id: int, node_name: str) -> tuple[int, int]:
        pad = NODE_RADIUS + 10; x,y = random.randint(pad, CANVAS_WIDTH-pad), random.randint(pad, CANVAS_HEIGHT-pad)
        if db_manager.atualizar_ponto_coords_db(db_id, x, y): self.log_result(f"Coords para '{node_name}' guardadas.")
        else: self.log_result(f"Aviso: Falha ao guardar coords para '{node_name}'.")
        return (x,y)

    def randomize_and_save_layout_gui(self):
        if not self.city_graph.get_vertices(): messagebox.showinfo("Info", "Grafo vazio."); return
        up_c = 0
        for n_name, attrs in self.node_attributes.items():
            if 'id' in attrs:
                db_id = attrs['id']; pad = NODE_RADIUS + 10
                nx, ny = random.randint(pad,CANVAS_WIDTH-pad), random.randint(pad,CANVAS_HEIGHT-pad)
                if db_manager.atualizar_ponto_coords_db(db_id, nx, ny): attrs['coords']=(nx,ny); up_c+=1
        self.redraw_canvas_gui(); self.log_result(f"Layout reorganizado, {up_c} coords atualizadas na BD.")

    def add_vertex_gui(self):
        nome, tipo = self.vertex_name_entry.get().strip(), self.vertex_type_combo.get()
        if not nome: messagebox.showerror("Erro", "Nome do ponto vazio."); return
        if db_manager.obter_ponto_por_nome_db(nome): messagebox.showwarning("Aviso", f"Ponto '{nome}' já existe."); return
        pad = NODE_RADIUS + 10; cx,cy = random.randint(pad,CANVAS_WIDTH-pad), random.randint(pad,CANVAS_HEIGHT-pad)
        db_id = db_manager.adicionar_ponto_db(nome, tipo, cx, cy)
        if db_id:
            self.city_graph.add_vertex(nome); self.node_attributes[nome] = {'id':db_id,'type':tipo,'coords':(cx,cy)}
            self.vertex_name_entry.delete(0,tk.END)
            self.update_graph_display_gui(); self.update_all_node_comboboxes_gui(); self.redraw_canvas_gui()
            self.log_result(f"{tipo} '{nome}' (ID:{db_id}) adicionado.")
        else: messagebox.showerror("Erro BD", f"Falha ao adicionar '{nome}'.")

    def add_edge_gui(self):
        u_n, v_n = self.edge_u_combo.get().split(" (")[0], self.edge_v_combo.get().split(" (")[0]
        w_s, bidir = self.edge_weight_entry.get().strip(), self.bidirectional_var.get()
        if not u_n or not v_n: messagebox.showerror("Erro", "Selecione pontos De/Para."); return
        if u_n == v_n: messagebox.showerror("Erro", "Conexão para o mesmo ponto não."); return
        if not w_s: messagebox.showerror("Erro", "Distância obrigatória."); return
        try: dist = float(w_s); assert dist > 0
        except: messagebox.showerror("Erro", "Distância deve ser número positivo."); return
        u_a, v_a = self.node_attributes.get(u_n), self.node_attributes.get(v_n)
        if not u_a or 'id' not in u_a or not v_a or 'id' not in v_a: messagebox.showerror("Erro", "ID BD não encontrado."); return
        if db_manager.adicionar_conexao_db(u_a['id'], v_a['id'], dist, bidir):
            self.city_graph.add_edge(u_n,v_n,dist,bidirectional=bidir); self.edge_weight_entry.delete(0,tk.END)
            self.update_graph_display_gui(); self.redraw_canvas_gui()
            self.log_result(f"Conexão '{u_n}' {'<-->' if bidir else '-->'} '{v_n}' adicionada.")
        else: messagebox.showwarning("Aviso BD", "Falha ao adicionar conexão.")

    def redraw_canvas_gui(self, highlight_path=None, canvas_widget=None, node_attrs_override=None):
        target_canvas = canvas_widget if canvas_widget else self.map_canvas
        target_node_attrs = node_attrs_override if node_attrs_override else self.node_attributes
        
        target_canvas.delete("all")
        if not self.city_graph.get_vertices() and not node_attrs_override : 
            target_canvas.create_text(target_canvas.winfo_width()/2 if target_canvas.winfo_width() > 1 else CANVAS_WIDTH/2, 
                                    target_canvas.winfo_height()/2 if target_canvas.winfo_height() > 1 else CANVAS_HEIGHT/2, 
                                    text="Grafo vazio", font=("Arial", 12), fill="grey"); return
        if canvas_widget == self.entrega_map_canvas and not target_node_attrs:
            target_canvas.create_text(target_canvas.winfo_width()/2 if target_canvas.winfo_width() > 1 else (CANVAS_WIDTH+100)/2, 
                                    target_canvas.winfo_height()/2 if target_canvas.winfo_height() > 1 else (CANVAS_HEIGHT+50)/2, 
                                    text="Selecione uma carga.", font=("Arial", 12), fill="grey"); return

        drawn_edges_base = set() 
        nodes_to_iterate_for_edges = self.city_graph.get_vertices() if target_canvas == self.map_canvas else (highlight_path if highlight_path else [])
        for u_name in nodes_to_iterate_for_edges:
            u_attrs = target_node_attrs.get(u_name)
            if not u_attrs or 'coords' not in u_attrs or u_attrs['coords'] is None: continue
            ux, uy = u_attrs['coords']
            neighbors_to_draw = []
            if target_canvas == self.entrega_map_canvas and highlight_path:
                if u_name in highlight_path:
                    try:
                        u_idx = highlight_path.index(u_name)
                        if u_idx < len(highlight_path) -1: neighbors_to_draw = [{'node': highlight_path[u_idx+1]}]
                    except ValueError: pass
            else: neighbors_to_draw = self.city_graph.get_neighbors(u_name)

            for edge_info in neighbors_to_draw:
                v_name = edge_info['node']
                v_attrs = target_node_attrs.get(v_name)
                if not v_attrs or 'coords' not in v_attrs or v_attrs['coords'] is None: continue
                vx, vy = v_attrs['coords']
                edge_key_sorted = tuple(sorted((u_name, v_name)))
                if target_canvas == self.map_canvas and edge_key_sorted not in drawn_edges_base:
                    target_canvas.create_line(ux, uy, vx, vy, fill="lightgrey", width=1.5, tags="edge_base")
                    drawn_edges_base.add(edge_key_sorted)

        if highlight_path and len(highlight_path) >= 2:
            for i in range(len(highlight_path) - 1):
                u_p, v_p = highlight_path[i], highlight_path[i+1]
                u_a_p, v_a_p = target_node_attrs.get(u_p), target_node_attrs.get(v_p)
                if u_a_p and v_a_p and u_a_p.get('coords') and v_a_p.get('coords'):
                    ux_p, uy_p = u_a_p['coords']; vx_p, vy_p = v_a_p['coords']
                    target_canvas.create_line(ux_p, uy_p, vx_p, vy_p, fill="blue", width=3, arrow=tk.LAST, tags="edge_highlight")

        nodes_to_draw_on_canvas = target_node_attrs.keys() if target_canvas == self.entrega_map_canvas and target_node_attrs else self.node_attributes.keys()
        for node_name in nodes_to_draw_on_canvas:
            attrs = target_node_attrs.get(node_name)
            if not attrs or 'coords' not in attrs or attrs['coords'] is None: continue
            x, y = attrs['coords']
            node_type = attrs.get("type", "N/D")
            is_highlighted = highlight_path and node_name in highlight_path
            default_fill, deposito_fill, cidade_fill = "skyblue", "khaki", "lightgreen"
            highlight_node_fill = "dodgerblue" if target_canvas == self.entrega_map_canvas else "orangered"
            fill_color = highlight_node_fill if is_highlighted else \
                        (deposito_fill if node_type == "Depósito" else \
                        (cidade_fill if node_type == "Cidade" else default_fill))
            text_color = "white" if is_highlighted else "black"
            target_canvas.create_oval(x-NODE_RADIUS,y-NODE_RADIUS,x+NODE_RADIUS,y+NODE_RADIUS,fill=fill_color,outline="black",width=1.5,tags="node")
            target_canvas.create_text(x,y,text=node_name,font=("Arial",FONT_SIZE,"bold"),fill=text_color,tags="node_text")

    def clear_graph_gui(self):
        if messagebox.askyesno("Confirmar Limpeza", "Isto removerá PONTOS e CONEXÕES da BD. Continuar?"):
            self.log_result("A limpar pontos e conexões da BD...")
            pontos = db_manager.obter_todos_pontos_db()
            err = 0
            if pontos:
                for p in pontos:
                    if not db_manager.remover_ponto_db(p['id']): err+=1
            self.log_result("Pontos e conexões removidos." if not err else f"{err} erros ao remover.")
            self.city_graph,self.node_attributes=Graph(),{}; self._load_all_initial_data()

    def run_dijkstra_gui(self):
        start_f, end_f = self.start_node_combo.get(), self.end_node_combo.get()
        if not start_f or not end_f: messagebox.showerror("Erro", "Selecione partida e chegada."); self.redraw_canvas_gui(canvas_widget=self.map_canvas); return
        start_n, end_n = start_f.split(" (")[0], end_f.split(" (")[0]
        self.log_result(f"\n--- Dijkstra (Mapa Geral): '{start_n}' -> '{end_n}' ---")
        dist, path = dijkstra(self.city_graph, start_n, end_n)
        if dist == math.inf:
            msg = f"Caminho de '{start_n}' para '{end_n}' não encontrado."
            self.log_result(msg); messagebox.showinfo("Dijkstra", msg); self.redraw_canvas_gui(canvas_widget=self.map_canvas)
        else:
            p_log = " -> ".join([f"{p} ({self.node_attributes.get(p,{}).get('type','N/D')})" for p in path])
            r_log = f"Caminho (Mapa): {p_log}\nDistância: {dist} km"
            self.log_result(r_log); messagebox.showinfo("Dijkstra", f"Caminho: {' -> '.join(path)}\nDistância: {dist} km")
            self.redraw_canvas_gui(highlight_path=path, canvas_widget=self.map_canvas)

    def _get_formatted_node_list_gui(self):
        return [f"{n_name} ({attrs.get('type', 'N/D')})" for n_name, attrs in sorted(self.node_attributes.items())]
    
    def _get_formatted_camiao_list_gui(self):
        camioes = db_manager.obter_todos_camioes_db()
        if camioes is None: return ["Erro ao carregar camiões"]
        return [f"{c['matricula']} ({c.get('nome_descricao','N/A')}) - ID:{c['id']}" for c in camioes]

    def _get_formatted_motorista_list_gui(self):
        motoristas = db_manager.obter_todos_motoristas_db()
        if motoristas is None: return ["Erro ao carregar motoristas"]
        return [f"{m['nome_completo']} (CNH: {m['cnh']}) - ID:{m['id']}" for m in motoristas]

    def _get_formatted_carga_list_gui(self, apenas_aptas=True): # Parâmetro para filtrar cargas
        cargas = db_manager.obter_todas_cargas_db_detalhado()
        if cargas is None: return ["Erro ao carregar cargas"]
        
        if apenas_aptas:
            cargas_filtradas = [c for c in cargas if c.get('estado') in ['Pendente', 'Agendada']]
        else:
            cargas_filtradas = cargas # Para outros usos, se necessário

        return [f"ID:{c['id']} - {c['descricao']} (Orig: {c.get('nome_ponto_origem','?')}, Dest: {c.get('nome_ponto_destino','?')}, Estado: {c.get('estado')})" for c in cargas_filtradas]

    def update_all_node_comboboxes_gui(self): 
        formatted_nodes = self._get_formatted_node_list_gui()
        map_combos = [self.start_node_combo, self.end_node_combo, self.edge_u_combo, self.edge_v_combo]
        if 'localizacao_camiao_combo' in self.camiao_form_widgets: map_combos.append(self.camiao_form_widgets['localizacao_camiao_combo'])
        if 'origem_carga_combo' in self.carga_form_widgets: map_combos.append(self.carga_form_widgets['origem_carga_combo'])
        if 'destino_carga_combo' in self.carga_form_widgets: map_combos.append(self.carga_form_widgets['destino_carga_combo'])
        
        for combo_widget in map_combos:
            if combo_widget: 
                current_val = combo_widget.get()
                combo_widget['values'] = [""] + formatted_nodes # Adiciona opção vazia
                if formatted_nodes:
                    if current_val in combo_widget['values']: combo_widget.set(current_val)
                    else: combo_widget.set("") # Padrão para vazio se não for válido
                else: combo_widget.set("")
    
    def _update_carga_form_combos(self):
        if 'camiao_carga_combo' in self.carga_form_widgets:
            self.carga_form_widgets['camiao_carga_combo']['values'] = ["Nenhum"] + self._get_formatted_camiao_list_gui()
            self.carga_form_widgets['camiao_carga_combo'].set("Nenhum")
        if 'motorista_carga_combo' in self.carga_form_widgets:
            self.carga_form_widgets['motorista_carga_combo']['values'] = ["Nenhum"] + self._get_formatted_motorista_list_gui()
            self.carga_form_widgets['motorista_carga_combo'].set("Nenhum")

    def _update_entrega_form_combos(self):
        self.entrega_carga_combo['values'] = [""] + self._get_formatted_carga_list_gui(apenas_aptas=True)
        self.entrega_motorista_combo['values'] = ["Nenhum"] + self._get_formatted_motorista_list_gui()
        self.entrega_camiao_combo['values'] = ["Nenhum"] + self._get_formatted_camiao_list_gui()
        
        self.entrega_carga_combo.set("")
        self.entrega_motorista_combo.set("Nenhum")
        self.entrega_camiao_combo.set("Nenhum")
        self.entrega_origem_label.config(text="N/A") # Limpa labels de origem/destino
        self.entrega_destino_label.config(text="N/A")


    def log_result(self, message: str):
        self.results_text.config(state=tk.NORMAL); self.results_text.insert(tk.END, message + "\n")
        self.results_text.see(tk.END); self.results_text.config(state=tk.DISABLED)

    def update_graph_display_gui(self):
        self.graph_display_text.config(state=tk.NORMAL); self.graph_display_text.delete(1.0, tk.END)
        if not self.city_graph.get_vertices(): self.graph_display_text.insert(tk.END, "Grafo vazio.");
        else:
            lines = []
            for v_name, attrs in sorted(self.node_attributes.items()):
                v_type, db_id = attrs.get("type","N/A"), attrs.get('id','N/A')
                lines.append(f"{v_name} ({v_type}) (ID:{db_id}):")
                neigh = self.city_graph.get_neighbors(v_name)
                if not neigh: lines.append("  (Sem conexões)")
                else:
                    for e in sorted(neigh, key=lambda ed: ed['node']):
                        n_attrs = self.node_attributes.get(e['node'],{}); n_type = n_attrs.get("type","N/A")
                        lines.append(f"  -> {e['node']} ({n_type}) (Dist: {e['weight']} km)")
                lines.append("")
            self.graph_display_text.insert(tk.END, "\n".join(lines))
        self.graph_display_text.config(state=tk.DISABLED)

    def _load_camioes_gui(self):
        for i in self.camioes_treeview.get_children(): self.camioes_treeview.delete(i)
        camioes_data = db_manager.obter_todos_camioes_db()
        if camioes_data is None: messagebox.showerror("Erro BD", "Falha ao carregar camiões."); return
        for c in camioes_data:
            loc_nome = c.get('nome_localizacao_atual', 'N/A')
            self.camioes_treeview.insert("", tk.END, values=(
                c['id'], c['matricula'], c.get('nome_descricao',''), c.get('tipo_veiculo',''), c.get('estado',''), loc_nome))
        self.log_result(f"{len(camioes_data)} camiões carregados.")
        self._update_carga_form_combos() 
        self._update_entrega_form_combos()

    def _on_camiao_select(self, event=None):
        sel = self.camioes_treeview.selection()
        if not sel: self._clear_camiao_fields_gui(); self.selected_camiao_db_id=None; return
        self.selected_camiao_db_id = self.camioes_treeview.item(sel[0])['values'][0]
        camiao_data = db_manager.obter_camiao_por_id_db(self.selected_camiao_db_id)
        if not camiao_data: messagebox.showerror("Erro BD", "Camião não encontrado."); self._clear_camiao_fields_gui(); return
        
        self.camiao_form_widgets['matricula_camiao_entry'].delete(0,tk.END); self.camiao_form_widgets['matricula_camiao_entry'].insert(0, camiao_data.get('matricula',''))
        self.camiao_form_widgets['nome_camiao_entry'].delete(0,tk.END); self.camiao_form_widgets['nome_camiao_entry'].insert(0, camiao_data.get('nome_descricao',''))
        self.camiao_form_widgets['capacidade_camiao_entry'].delete(0,tk.END); self.camiao_form_widgets['capacidade_camiao_entry'].insert(0, str(camiao_data.get('capacidade','0.0') or '')) # Evita 'None'
        self.camiao_form_widgets['unidade_cap_camiao_combo'].set(camiao_data.get('unidade_capacidade','') if camiao_data.get('unidade_capacidade','') in UNIDADES_CAPACIDADE else (UNIDADES_CAPACIDADE[0] if UNIDADES_CAPACIDADE else ""))
        self.camiao_form_widgets['tipo_veiculo_camiao_combo'].set(camiao_data.get('tipo_veiculo','') if camiao_data.get('tipo_veiculo','') in TIPOS_camiao else (TIPOS_camiao[0] if TIPOS_camiao else ""))
        self.camiao_form_widgets['estado_camiao_combo'].set(camiao_data.get('estado','') if camiao_data.get('estado','') in ESTADOS_camiao else (ESTADOS_camiao[0] if ESTADOS_camiao else ""))
        self.camiao_form_widgets['obs_camiao_text'].delete(1.0,tk.END); self.camiao_form_widgets['obs_camiao_text'].insert(tk.END, camiao_data.get('observacoes',''))
        
        loc_id = camiao_data.get('localizacao_atual_ponto_id')
        loc_str_combo = ""
        if loc_id:
            p_loc_data = db_manager.obter_ponto_por_id_db(loc_id)
            if p_loc_data: loc_str_combo = f"{p_loc_data['nome']} ({p_loc_data['tipo']})"
        self.camiao_form_widgets['localizacao_camiao_combo'].set(loc_str_combo)

        self.update_camiao_btn.config(state=tk.NORMAL); self.remove_camiao_btn.config(state=tk.NORMAL)

    def _clear_camiao_fields_gui(self):
        for name, widget in self.camiao_form_widgets.items():
            if isinstance(widget, ttk.Entry): widget.delete(0, tk.END)
            elif isinstance(widget, ttk.Combobox): widget.set(widget['values'][0] if widget['values'] and name not in ['localizacao_camiao_combo'] else ("" if name == 'localizacao_camiao_combo' else (widget['values'][0] if widget['values'] else "")))
            elif isinstance(widget, scrolledtext.ScrolledText): widget.delete(1.0, tk.END)
        self.selected_camiao_db_id=None; self.camioes_treeview.selection_remove(self.camioes_treeview.selection())
        self.update_camiao_btn.config(state=tk.DISABLED); self.remove_camiao_btn.config(state=tk.DISABLED)
        self.log_result("Campos do camião limpos.")

    def _add_camiao_gui(self):
        data = {name: widget.get().strip() if isinstance(widget, ttk.Entry) else \
                    (widget.get(1.0, tk.END).strip() if isinstance(widget, scrolledtext.ScrolledText) else widget.get())
                for name, widget in self.camiao_form_widgets.items()}
        
        if not data['matricula_camiao_entry']: messagebox.showerror("Erro", "Matrícula obrigatória."); return
        try: cap = float(data['capacidade_camiao_entry']) if data['capacidade_camiao_entry'] else None
        except ValueError: messagebox.showerror("Erro", "Capacidade deve ser número."); return

        loc_id = None
        if data['localizacao_camiao_combo']:
            loc_nome = data['localizacao_camiao_combo'].split(" (")[0]
            if loc_nome in self.node_attributes: loc_id = self.node_attributes[loc_nome]['id']
        
        camiao_id = db_manager.adicionar_camiao_db(
            data['matricula_camiao_entry'], data['nome_camiao_entry'], cap, data['unidade_cap_camiao_combo'],
            data['tipo_veiculo_camiao_combo'], data['estado_camiao_combo'], loc_id, data['obs_camiao_text'])
        if camiao_id: self.log_result(f"Camião '{data['matricula_camiao_entry']}' adicionado."); self._load_camioes_gui(); self._clear_camiao_fields_gui()
        else: messagebox.showerror("Erro BD", "Falha ao adicionar camião (verifique se matrícula já existe).")

    def _update_camiao_gui(self):
        if not self.selected_camiao_db_id: messagebox.showerror("Erro", "Nenhum camião selecionado."); return
        data_to_update = {
            "matricula": self.camiao_form_widgets['matricula_camiao_entry'].get().strip(),
            "nome_descricao": self.camiao_form_widgets['nome_camiao_entry'].get().strip(),
            "unidade_capacidade": self.camiao_form_widgets['unidade_cap_camiao_combo'].get(),
            "tipo_veiculo": self.camiao_form_widgets['tipo_veiculo_camiao_combo'].get(),
            "estado": self.camiao_form_widgets['estado_camiao_combo'].get(),
            "observacoes": self.camiao_form_widgets['obs_camiao_text'].get(1.0, tk.END).strip()
        }
        if not data_to_update["matricula"]: messagebox.showerror("Erro", "Matrícula obrigatória."); return
        cap_str = self.camiao_form_widgets['capacidade_camiao_entry'].get().strip()
        try: data_to_update["capacidade"] = float(cap_str) if cap_str else None
        except ValueError: messagebox.showerror("Erro", "Capacidade deve ser número."); return
        
        loc_full = self.camiao_form_widgets['localizacao_camiao_combo'].get()
        loc_id = None
        if loc_full:
            loc_nome = loc_full.split(" (")[0]
            if loc_nome in self.node_attributes: loc_id = self.node_attributes[loc_nome]['id']
        data_to_update["localizacao_atual_ponto_id"] = loc_id

        if db_manager.atualizar_camiao_db(self.selected_camiao_db_id, data_to_update):
            self.log_result(f"Camião ID {self.selected_camiao_db_id} atualizado."); self._load_camioes_gui(); self._clear_camiao_fields_gui()
        else: messagebox.showerror("Erro BD", "Falha ao atualizar camião.")

    def _remove_camiao_gui(self):
        if not self.selected_camiao_db_id: messagebox.showerror("Erro", "Nenhum camião selecionado."); return
        mat = self.camiao_form_widgets['matricula_camiao_entry'].get()
        if messagebox.askyesno("Confirmar", f"Remover camião {mat} (ID:{self.selected_camiao_db_id})?"):
            if db_manager.remover_camiao_db(self.selected_camiao_db_id):
                self.log_result(f"Camião ID {self.selected_camiao_db_id} removido."); self._load_camioes_gui(); self._clear_camiao_fields_gui()
            else: messagebox.showerror("Erro BD", "Falha ao remover camião.")

    def _load_motoristas_gui(self):
        for i in self.motoristas_treeview.get_children(): self.motoristas_treeview.delete(i)
        motoristas_data = db_manager.obter_todos_motoristas_db()
        if motoristas_data is None: messagebox.showerror("Erro BD", "Falha ao carregar motoristas."); return
        for m in motoristas_data:
            self.motoristas_treeview.insert("", tk.END, values=(
                m['id'], m.get('nome_completo',''), m.get('cnh',''),
                m.get('categoria_cnh',''), m.get('estado',''), m.get('telefone','')
            ))
        self.log_result(f"{len(motoristas_data)} motoristas carregados.")
        self._update_carga_form_combos()
        self._update_entrega_form_combos()

    def _on_motorista_select(self, event=None):
        sel = self.motoristas_treeview.selection()
        if not sel: self._clear_motorista_fields_gui(); self.selected_motorista_db_id=None; return
        self.selected_motorista_db_id = self.motoristas_treeview.item(sel[0])['values'][0]
        motorista_data = db_manager.obter_motorista_por_id_db(self.selected_motorista_db_id)
        if not motorista_data: messagebox.showerror("Erro BD", "Motorista não encontrado."); self._clear_motorista_fields_gui(); return
        
        self.motorista_form_widgets['nome_motorista_entry'].delete(0,tk.END); self.motorista_form_widgets['nome_motorista_entry'].insert(0, motorista_data.get('nome_completo',''))
        self.motorista_form_widgets['cnh_motorista_entry'].delete(0,tk.END); self.motorista_form_widgets['cnh_motorista_entry'].insert(0, motorista_data.get('cnh',''))
        self.motorista_form_widgets['cat_cnh_motorista_combo'].set(motorista_data.get('categoria_cnh','') if motorista_data.get('categoria_cnh','') in CATEGORIAS_CNH else (CATEGORIAS_CNH[0] if CATEGORIAS_CNH else ""))
        
        val_cnh_str = str(motorista_data.get('validade_cnh','YYYY-MM-DD') or "YYYY-MM-DD")
        self.motorista_form_widgets['val_cnh_motorista_entry'].delete(0,tk.END); self.motorista_form_widgets['val_cnh_motorista_entry'].insert(0, val_cnh_str)
        self._add_placeholder(None, self.motorista_form_widgets['val_cnh_motorista_entry'], "YYYY-MM-DD") if val_cnh_str == "YYYY-MM-DD" else self.motorista_form_widgets['val_cnh_motorista_entry'].config(foreground="black")

        self.motorista_form_widgets['tel_motorista_entry'].delete(0,tk.END); self.motorista_form_widgets['tel_motorista_entry'].insert(0, motorista_data.get('telefone',''))
        self.motorista_form_widgets['email_motorista_entry'].delete(0,tk.END); self.motorista_form_widgets['email_motorista_entry'].insert(0, motorista_data.get('email',''))
        self.motorista_form_widgets['estado_motorista_combo'].set(motorista_data.get('estado','') if motorista_data.get('estado','') in ESTADOS_MOTORISTA else (ESTADOS_MOTORISTA[0] if ESTADOS_MOTORISTA else ""))
        self.motorista_form_widgets['obs_motorista_text'].delete(1.0,tk.END); self.motorista_form_widgets['obs_motorista_text'].insert(tk.END, motorista_data.get('observacoes',''))
        self.update_motorista_btn.config(state=tk.NORMAL); self.remove_motorista_btn.config(state=tk.NORMAL)

    def _clear_motorista_fields_gui(self):
        for name, widget in self.motorista_form_widgets.items():
            if isinstance(widget, ttk.Entry):
                widget.delete(0, tk.END)
                if name == 'val_cnh_motorista_entry': self._add_placeholder(None, widget, "YYYY-MM-DD")
            elif isinstance(widget, ttk.Combobox): widget.set(widget['values'][0] if widget['values'] else "")
            elif isinstance(widget, scrolledtext.ScrolledText): widget.delete(1.0, tk.END)
        self.selected_motorista_db_id=None; self.motoristas_treeview.selection_remove(self.motoristas_treeview.selection())
        self.update_motorista_btn.config(state=tk.DISABLED); self.remove_motorista_btn.config(state=tk.DISABLED)
        self.log_result("Campos do motorista limpos.")

    def _add_motorista_gui(self):
        data = {name: widget.get().strip() if isinstance(widget, ttk.Entry) else \
                    (widget.get(1.0, tk.END).strip() if isinstance(widget, scrolledtext.ScrolledText) else widget.get())
                for name, widget in self.motorista_form_widgets.items()}
        if not data['nome_motorista_entry'] or not data['cnh_motorista_entry']: messagebox.showerror("Erro", "Nome e CNH são obrigatórios."); return
        val_cnh = data['val_cnh_motorista_entry'] if data['val_cnh_motorista_entry'] != "YYYY-MM-DD" else None
        
        motorista_id = db_manager.adicionar_motorista_db( 
            data['nome_motorista_entry'], data['cnh_motorista_entry'], data['cat_cnh_motorista_combo'],
            val_cnh, data['tel_motorista_entry'], data['email_motorista_entry'],
            data['estado_motorista_combo'], data['obs_motorista_text'])
        if motorista_id: self.log_result(f"Motorista '{data['nome_motorista_entry']}' adicionado."); self._load_motoristas_gui(); self._clear_motorista_fields_gui()
        else: messagebox.showerror("Erro BD", "Falha ao adicionar motorista (verifique CNH/Email únicos).")

    def _update_motorista_gui(self):
        if not self.selected_motorista_db_id: messagebox.showerror("Erro", "Nenhum motorista selecionado."); return
        data_to_update = {
            "nome_completo": self.motorista_form_widgets['nome_motorista_entry'].get().strip(),
            "cnh": self.motorista_form_widgets['cnh_motorista_entry'].get().strip(),
            "categoria_cnh": self.motorista_form_widgets['cat_cnh_motorista_combo'].get(),
            "telefone": self.motorista_form_widgets['tel_motorista_entry'].get().strip(),
            "email": self.motorista_form_widgets['email_motorista_entry'].get().strip(),
            "estado": self.motorista_form_widgets['estado_motorista_combo'].get(),
            "observacoes": self.motorista_form_widgets['obs_motorista_text'].get(1.0, tk.END).strip()
        }
        if not data_to_update["nome_completo"] or not data_to_update["cnh"]: messagebox.showerror("Erro", "Nome e CNH são obrigatórios."); return
        val_cnh_str = self.motorista_form_widgets['val_cnh_motorista_entry'].get().strip()
        data_to_update["validade_cnh"] = val_cnh_str if val_cnh_str and val_cnh_str != "YYYY-MM-DD" else None
        
        if db_manager.atualizar_motorista_db(self.selected_motorista_db_id, data_to_update): 
            self.log_result(f"Motorista ID {self.selected_motorista_db_id} atualizado."); self._load_motoristas_gui(); self._clear_motorista_fields_gui()
        else: messagebox.showerror("Erro BD", "Falha ao atualizar motorista.")

    def _remove_motorista_gui(self):
        if not self.selected_motorista_db_id: messagebox.showerror("Erro", "Nenhum motorista selecionado."); return
        nome = self.motorista_form_widgets['nome_motorista_entry'].get()
        if messagebox.askyesno("Confirmar", f"Remover motorista {nome} (ID:{self.selected_motorista_db_id})?"):
            if db_manager.remover_motorista_db(self.selected_motorista_db_id): 
                self.log_result(f"Motorista ID {self.selected_motorista_db_id} removido."); self._load_motoristas_gui(); self._clear_motorista_fields_gui()
            else: messagebox.showerror("Erro BD", "Falha ao remover motorista.")

    def _load_cargas_gui(self):
        for i in self.cargas_treeview.get_children(): self.cargas_treeview.delete(i)
        cargas_data = db_manager.obter_todas_cargas_db_detalhado() 
        if cargas_data is None: messagebox.showerror("Erro BD", "Falha ao carregar cargas."); return
        for c in cargas_data:
            self.cargas_treeview.insert("", tk.END, values=(
                c['id'], c.get('descricao',''), c.get('nome_ponto_origem',''), c.get('nome_ponto_destino',''),
                c.get('estado',''), c.get('matricula_camiao','N/A'), c.get('nome_motorista','N/A')
            ))
        self.log_result(f"{len(cargas_data)} cargas carregadas.")
        self._update_entrega_form_combos() 

    def _on_carga_select(self, event=None):
        sel = self.cargas_treeview.selection()
        if not sel: self._clear_carga_fields_gui(); self.selected_carga_db_id=None; return
        self.selected_carga_db_id = self.cargas_treeview.item(sel[0])['values'][0]
        carga_data = db_manager.obter_carga_por_id_db(self.selected_carga_db_id) 
        if not carga_data: messagebox.showerror("Erro BD", "Carga não encontrada."); self._clear_carga_fields_gui(); return

        self.carga_form_widgets['desc_carga_entry'].delete(0,tk.END); self.carga_form_widgets['desc_carga_entry'].insert(0, carga_data.get('descricao',''))
        self.carga_form_widgets['tipo_carga_combo'].set(carga_data.get('tipo_carga','') if carga_data.get('tipo_carga','') in TIPOS_CARGA else (TIPOS_CARGA[0] if TIPOS_CARGA else ""))
        self.carga_form_widgets['peso_carga_entry'].delete(0,tk.END); self.carga_form_widgets['peso_carga_entry'].insert(0, str(carga_data.get('peso_kg','0.0') or ''))
        self.carga_form_widgets['volume_carga_entry'].delete(0,tk.END); self.carga_form_widgets['volume_carga_entry'].insert(0, str(carga_data.get('volume_m3','0.0') or ''))
        self.carga_form_widgets['cliente_carga_entry'].delete(0,tk.END); self.carga_form_widgets['cliente_carga_entry'].insert(0, carga_data.get('cliente_nome',''))
        
        dt_c_str = str(carga_data.get('data_prevista_coleta','YYYY-MM-DD')or "YYYY-MM-DD"); self.carga_form_widgets['dt_coleta_carga_entry'].delete(0,tk.END); self.carga_form_widgets['dt_coleta_carga_entry'].insert(0, dt_c_str)
        self._add_placeholder(None, self.carga_form_widgets['dt_coleta_carga_entry'], "YYYY-MM-DD") if dt_c_str == "YYYY-MM-DD" else self.carga_form_widgets['dt_coleta_carga_entry'].config(foreground="black")
        dt_e_str = str(carga_data.get('data_prevista_entrega','YYYY-MM-DD')or "YYYY-MM-DD"); self.carga_form_widgets['dt_entrega_carga_entry'].delete(0,tk.END); self.carga_form_widgets['dt_entrega_carga_entry'].insert(0, dt_e_str)
        self._add_placeholder(None, self.carga_form_widgets['dt_entrega_carga_entry'], "YYYY-MM-DD") if dt_e_str == "YYYY-MM-DD" else self.carga_form_widgets['dt_entrega_carga_entry'].config(foreground="black")

        self.carga_form_widgets['estado_carga_combo'].set(carga_data.get('estado','') if carga_data.get('estado','') in ESTADOS_CARGA else (ESTADOS_CARGA[0] if ESTADOS_CARGA else ""))
        self.carga_form_widgets['obs_carga_text'].delete(1.0,tk.END); self.carga_form_widgets['obs_carga_text'].insert(tk.END, carga_data.get('observacoes',''))

        p_o_id, p_d_id = carga_data.get('ponto_origem_id'), carga_data.get('ponto_destino_id')
        f_nodes = self._get_formatted_node_list_gui()
        o_val = next((fn for n_id, fn in [(self.node_attributes[n.split(" (")[0]]['id'], n) for n in f_nodes if n.split(" (")[0] in self.node_attributes] if n_id == p_o_id), "")
        self.carga_form_widgets['origem_carga_combo'].set(o_val)
        d_val = next((fn for n_id, fn in [(self.node_attributes[n.split(" (")[0]]['id'], n) for n in f_nodes if n.split(" (")[0] in self.node_attributes] if n_id == p_d_id), "")
        self.carga_form_widgets['destino_carga_combo'].set(d_val)

        c_id, m_id = carga_data.get('camiao_atribuido_id'), carga_data.get('motorista_atribuido_id')
        c_val = next((c for c in self.carga_form_widgets['camiao_carga_combo']['values'] if f"ID:{c_id}" in c), "Nenhum")
        self.carga_form_widgets['camiao_carga_combo'].set(c_val)
        m_val = next((m for m in self.carga_form_widgets['motorista_carga_combo']['values'] if f"ID:{m_id}" in m), "Nenhum")
        self.carga_form_widgets['motorista_carga_combo'].set(m_val)
        self.update_carga_btn.config(state=tk.NORMAL); self.remove_carga_btn.config(state=tk.NORMAL)

    def _clear_carga_fields_gui(self):
        for name, widget in self.carga_form_widgets.items():
            if isinstance(widget, ttk.Entry):
                widget.delete(0, tk.END)
                if "dt_" in name: self._add_placeholder(None, widget, "YYYY-MM-DD")
            elif isinstance(widget, ttk.Combobox):
                default_val = ""
                if name in ['camiao_carga_combo', 'motorista_carga_combo']: default_val = "Nenhum"
                elif widget['values']: default_val = widget['values'][0]
                widget.set(default_val)
            elif isinstance(widget, scrolledtext.ScrolledText): widget.delete(1.0, tk.END)
        self.selected_carga_db_id=None; self.cargas_treeview.selection_remove(self.cargas_treeview.selection())
        self.update_carga_btn.config(state=tk.DISABLED); self.remove_carga_btn.config(state=tk.DISABLED)
        self.log_result("Campos da carga limpos.")

    def _add_carga_gui(self):
        data = {name: widget.get().strip() if isinstance(widget, ttk.Entry) else \
                    (widget.get(1.0, tk.END).strip() if isinstance(widget, scrolledtext.ScrolledText) else widget.get())
                for name, widget in self.carga_form_widgets.items()}
        if not data['desc_carga_entry'] or not data['origem_carga_combo'] or not data['destino_carga_combo']:
            messagebox.showerror("Erro", "Descrição, Origem e Destino obrigatórios."); return
        
        p_o_id = self.node_attributes[data['origem_carga_combo'].split(" (")[0]]['id']
        p_d_id = self.node_attributes[data['destino_carga_combo'].split(" (")[0]]['id']
        peso = float(data['peso_carga_entry']) if data['peso_carga_entry'] else None
        vol = float(data['volume_carga_entry']) if data['volume_carga_entry'] else None
        dt_col = data['dt_coleta_carga_entry'] if data['dt_coleta_carga_entry'] != "YYYY-MM-DD" else None
        dt_ent = data['dt_entrega_carga_entry'] if data['dt_entrega_carga_entry'] != "YYYY-MM-DD" else None
        cam_id = int(data['camiao_carga_combo'].split("ID:")[-1]) if data['camiao_carga_combo'] != "Nenhum" else None
        mot_id = int(data['motorista_carga_combo'].split("ID:")[-1]) if data['motorista_carga_combo'] != "Nenhum" else None

        carga_id = db_manager.adicionar_carga_db( 
            data['desc_carga_entry'], data['tipo_carga_combo'], peso, vol, p_o_id, p_d_id,
            data['cliente_carga_entry'], dt_col, dt_ent, data['estado_carga_combo'],
            cam_id, mot_id, data['obs_carga_text'] )
        if carga_id: self.log_result(f"Carga '{data['desc_carga_entry']}' adicionada."); self._load_cargas_gui(); self._clear_carga_fields_gui()
        else: messagebox.showerror("Erro BD", "Falha ao adicionar carga.")

    def _update_carga_gui(self):
        if not self.selected_carga_db_id: messagebox.showerror("Erro", "Nenhuma carga selecionada."); return
        data_to_update = {
            "descricao": self.carga_form_widgets['desc_carga_entry'].get().strip(),
            "tipo_carga": self.carga_form_widgets['tipo_carga_combo'].get(),
            "cliente_nome": self.carga_form_widgets['cliente_carga_entry'].get().strip(),
            "estado": self.carga_form_widgets['estado_carga_combo'].get(),
            "observacoes": self.carga_form_widgets['obs_carga_text'].get(1.0, tk.END).strip()
        }
        if not data_to_update["descricao"]: messagebox.showerror("Erro", "Descrição obrigatória."); return
        
        orig_combo_val = self.carga_form_widgets['origem_carga_combo'].get()
        dest_combo_val = self.carga_form_widgets['destino_carga_combo'].get()
        if not orig_combo_val or not dest_combo_val: messagebox.showerror("Erro", "Origem e Destino são obrigatórios."); return
        data_to_update["ponto_origem_id"] = self.node_attributes[orig_combo_val.split(" (")[0]]['id']
        data_to_update["ponto_destino_id"] = self.node_attributes[dest_combo_val.split(" (")[0]]['id']
        
        data_to_update["peso_kg"] = float(self.carga_form_widgets['peso_carga_entry'].get()) if self.carga_form_widgets['peso_carga_entry'].get() else None
        data_to_update["volume_m3"] = float(self.carga_form_widgets['volume_carga_entry'].get()) if self.carga_form_widgets['volume_carga_entry'].get() else None
        dt_col_str = self.carga_form_widgets['dt_coleta_carga_entry'].get(); data_to_update["data_prevista_coleta"] = dt_col_str if dt_col_str != "YYYY-MM-DD" else None
        dt_ent_str = self.carga_form_widgets['dt_entrega_carga_entry'].get(); data_to_update["data_prevista_entrega"] = dt_ent_str if dt_ent_str != "YYYY-MM-DD" else None
        data_to_update["camiao_atribuido_id"] = int(self.carga_form_widgets['camiao_carga_combo'].get().split("ID:")[-1]) if self.carga_form_widgets['camiao_carga_combo'].get() != "Nenhum" else None
        data_to_update["motorista_atribuido_id"] = int(self.carga_form_widgets['motorista_carga_combo'].get().split("ID:")[-1]) if self.carga_form_widgets['motorista_carga_combo'].get() != "Nenhum" else None

        if db_manager.atualizar_carga_db(self.selected_carga_db_id, data_to_update): 
            self.log_result(f"Carga ID {self.selected_carga_db_id} atualizada."); self._load_cargas_gui(); self._clear_carga_fields_gui()
        else: messagebox.showerror("Erro BD", "Falha ao atualizar carga.")

    def _remove_carga_gui(self):
        if not self.selected_carga_db_id: messagebox.showerror("Erro", "Nenhuma carga selecionada."); return
        desc = self.carga_form_widgets['desc_carga_entry'].get()
        if messagebox.askyesno("Confirmar", f"Remover carga {desc} (ID:{self.selected_carga_db_id})?"):
            if db_manager.remover_carga_db(self.selected_carga_db_id): 
                self.log_result(f"Carga ID {self.selected_carga_db_id} removida."); self._load_cargas_gui(); self._clear_carga_fields_gui()
            else: messagebox.showerror("Erro BD", "Falha ao remover carga.")

    def _on_entrega_carga_selected(self, event=None):
        self.iniciar_entrega_btn.config(state=tk.DISABLED) 
        self.entrega_rota_details_text.config(state=tk.NORMAL); self.entrega_rota_details_text.delete(1.0, tk.END); self.entrega_rota_details_text.config(state=tk.DISABLED)
        self.redraw_canvas_gui(canvas_widget=self.entrega_map_canvas, node_attrs_override={}) 

        selected_carga_str = self.entrega_carga_combo.get()
        if not selected_carga_str:
            self.entrega_origem_label.config(text="N/A"); self.entrega_destino_label.config(text="N/A"); return
        try:
            carga_id = int(selected_carga_str.split("ID:")[1].split(" -")[0])
            carga_data = db_manager.obter_carga_por_id_db_detalhado(carga_id) 
            if carga_data:
                self.entrega_origem_label.config(text=f"{carga_data.get('nome_ponto_origem','N/A')} (ID:{carga_data.get('ponto_origem_id')})")
                self.entrega_destino_label.config(text=f"{carga_data.get('nome_ponto_destino','N/A')} (ID:{carga_data.get('ponto_destino_id')})")
                mot_id, cam_id = carga_data.get('motorista_atribuido_id'), carga_data.get('camiao_atribuido_id')
                mot_val = next((m for m in self.entrega_motorista_combo['values'] if f"ID:{mot_id}" in m), "Nenhum")
                self.entrega_motorista_combo.set(mot_val)
                cam_val = next((c for c in self.entrega_camiao_combo['values'] if f"ID:{cam_id}" in c), "Nenhum")
                self.entrega_camiao_combo.set(cam_val)
            else: self.entrega_origem_label.config(text="Erro dados carga."); self.entrega_destino_label.config(text="")
        except Exception as e: self.log_result(f"Erro seleção carga entrega: {e}"); self.entrega_origem_label.config(text="Erro"); self.entrega_destino_label.config(text="")

    def _calcular_rota_entrega_gui(self):
        self.iniciar_entrega_btn.config(state=tk.DISABLED)
        self.entrega_rota_details_text.config(state=tk.NORMAL); self.entrega_rota_details_text.delete(1.0, tk.END)
        carga_str = self.entrega_carga_combo.get()
        if not carga_str: messagebox.showerror("Erro", "Selecione uma carga."); return
        try:
            carga_id = int(carga_str.split("ID:")[1].split(" -")[0])
            carga_data = db_manager.obter_carga_por_id_db_detalhado(carga_id) 
            if not carga_data: messagebox.showerror("Erro", "Dados da carga não encontrados."); return
            o_nome, d_nome = carga_data.get('nome_ponto_origem'), carga_data.get('nome_ponto_destino')
            if not o_nome or not d_nome: messagebox.showerror("Erro", "Origem/Destino da carga não definidos."); return
            if o_nome not in self.city_graph.get_vertices() or d_nome not in self.city_graph.get_vertices():
                messagebox.showerror("Erro Grafo", f"Ponto '{o_nome}' ou '{d_nome}' não existe no grafo."); 
                self.entrega_rota_details_text.insert(tk.END, "Erro: Pontos não no grafo."); self.entrega_rota_details_text.config(state=tk.DISABLED); return
            dist, path = dijkstra(self.city_graph, o_nome, d_nome)
            if dist == math.inf:
                msg = f"Rota de '{o_nome}' para '{d_nome}' não calculada."
                self.entrega_rota_details_text.insert(tk.END, msg); messagebox.showinfo("Rota", msg)
                self.redraw_canvas_gui(canvas_widget=self.entrega_map_canvas, node_attrs_override={p:self.node_attributes[p] for p in [o_nome,d_nome] if p in self.node_attributes})
            else:
                msg = f"Rota: {' -> '.join(path)}\nDistância: {dist} km"
                self.entrega_rota_details_text.insert(tk.END, msg); messagebox.showinfo("Rota", msg)
                nodes_path_attrs = {n_name: self.node_attributes[n_name] for n_name in path if n_name in self.node_attributes}
                self.redraw_canvas_gui(highlight_path=path, canvas_widget=self.entrega_map_canvas, node_attrs_override=nodes_path_attrs)
                self.iniciar_entrega_btn.config(state=tk.NORMAL) 
        except Exception as e: self.log_result(f"Erro calc rota entrega: {e}"); messagebox.showerror("Erro", f"Erro: {e}")
        finally: self.entrega_rota_details_text.config(state=tk.DISABLED)

    def _iniciar_entrega_gui(self):
        carga_str, mot_str, cam_str = self.entrega_carga_combo.get(), self.entrega_motorista_combo.get(), self.entrega_camiao_combo.get()
        if not carga_str or mot_str == "Nenhum" or cam_str == "Nenhum":
            messagebox.showerror("Erro", "Selecione Carga, Motorista e Camião."); return
        try:
            carga_id = int(carga_str.split("ID:")[1].split(" -")[0])
            mot_id = int(mot_str.split("ID:")[-1]); cam_id = int(cam_str.split("ID:")[-1])
            db_manager.atualizar_carga_db(carga_id, {"estado": "Em Trânsito", "motorista_atribuido_id": mot_id, "camiao_atribuido_id": cam_id})
            db_manager.atualizar_motorista_db(mot_id, {"estado": "Em Rota"})
            db_manager.atualizar_camiao_db(cam_id, {"estado": "Em Rota", "localizacao_atual_ponto_id": None}) 
            self.log_result(f"Entrega Carga ID:{carga_id} iniciada (Mot:{mot_id}, Cam:{cam_id}).")
            messagebox.showinfo("Entrega Iniciada", f"Entrega Carga ID:{carga_id} iniciada.")
            self._load_all_initial_data() # Recarrega tudo para refletir estados
            self.iniciar_entrega_btn.config(state=tk.DISABLED)
            self.entrega_rota_details_text.config(state=tk.NORMAL); self.entrega_rota_details_text.delete(1.0, tk.END); self.entrega_rota_details_text.config(state=tk.DISABLED)
            self.redraw_canvas_gui(canvas_widget=self.entrega_map_canvas, node_attrs_override={})
        except Exception as e: self.log_result(f"Erro iniciar entrega: {e}"); messagebox.showerror("Erro", f"Falha: {e}")

if __name__ == "__main__":
    main_root = tk.Tk()
    app = CityGraphApp(main_root)
    main_root.mainloop()
