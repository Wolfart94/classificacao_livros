import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import sqlite3
import csv
from datetime import datetime

# ── Banco de Dados ────────────────────────────────────────────────────────────

DB_FILE = "biblioteca.db"

def init_db():
    con = sqlite3.connect(DB_FILE)
    cur = con.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS livros (
            id        INTEGER PRIMARY KEY AUTOINCREMENT,
            titulo    TEXT NOT NULL,
            autor     TEXT NOT NULL,
            genero    TEXT NOT NULL,
            ano       INTEGER,
            editora   TEXT,
            lido      INTEGER DEFAULT 0,
            nota      REAL,
            obs       TEXT,
            criado_em TEXT DEFAULT (datetime('now','localtime'))
        )
    """)
    con.commit()
    con.close()

def get_connection():
    return sqlite3.connect(DB_FILE)

# ── Paleta de cores ───────────────────────────────────────────────────────────

BG         = "#1e1e2e"
SURFACE    = "#2a2a3e"
ACCENT     = "#7c3aed"
ACCENT2    = "#6d28d9"
TEXT       = "#e2e8f0"
TEXT_MUTED = "#94a3b8"
SUCCESS    = "#10b981"
DANGER     = "#ef4444"
ROW_ODD    = "#252535"
ROW_EVEN   = "#2e2e42"

GENEROS = [
    "Ficção Científica", "Fantasia", "Romance", "Terror/Horror",
    "Mistério/Policial", "Aventura", "Biografia", "História",
    "Filosofia", "Ciência", "Tecnologia", "Autoajuda",
    "Negócios", "Arte", "Poesia", "Infantil", "Infanto-juvenil", "Outros"
]

# ── Janela de Cadastro/Edicao ─────────────────────────────────────────────────

def _mapear_genero(valor):
    if not valor:
        return "Outros"
    for g in GENEROS:
        if g.lower() in valor.lower() or valor.lower() in g.lower():
            return g
    return "Outros"


class JanelaCadastro(tk.Toplevel):
    def __init__(self, parent, livro=None):
        super().__init__(parent)
        self.parent = parent
        self.livro  = livro
        self.title("Editar Livro" if livro else "Cadastrar Livro")
        self.configure(bg=BG)
        self.resizable(False, False)
        self.grab_set()
        self._build()
        if livro:
            self._preencher(livro)
        self.update_idletasks()
        self._centralizar()

    def _centralizar(self):
        w, h = self.winfo_width(), self.winfo_height()
        x = self.parent.winfo_x() + (self.parent.winfo_width()  - w) // 2
        y = self.parent.winfo_y() + (self.parent.winfo_height() - h) // 2
        self.geometry("+{}+{}".format(x, y))

    def _label(self, frame, texto, row, col=0):
        tk.Label(frame, text=texto, bg=BG, fg=TEXT_MUTED,
                 font=("Segoe UI", 9)).grid(row=row, column=col, sticky="w", pady=(8,2))

    def _entry(self, frame, row, col=1, width=38):
        e = tk.Entry(frame, bg=SURFACE, fg=TEXT, insertbackground=TEXT,
                     relief="flat", font=("Segoe UI", 10), width=width,
                     highlightthickness=1, highlightbackground=ACCENT,
                     highlightcolor=ACCENT)
        e.grid(row=row, column=col, sticky="ew", padx=(8,0), pady=(8,2))
        return e

    def _build(self):
        frame = tk.Frame(self, bg=BG, padx=24, pady=20)
        frame.pack(fill="both", expand=True)

        campos = [
            ("Titulo *",    "titulo"),
            ("Autor *",     "autor"),
            ("Ano",         "ano"),
            ("Editora",     "editora"),
            ("Nota (0-10)", "nota"),
        ]

        self.vars = {}
        for i, (label, key) in enumerate(campos):
            self._label(frame, label, i*2)
            self.vars[key] = self._entry(frame, i*2)

        row_g = len(campos) * 2
        self._label(frame, "Genero *", row_g)
        self.vars["genero"] = ttk.Combobox(frame, values=GENEROS, state="readonly",
                                           font=("Segoe UI", 10), width=36)
        self.vars["genero"].grid(row=row_g, column=1, sticky="ew", padx=(8,0), pady=(8,2))
        self.vars["genero"].set(GENEROS[0])

        self.lido_var = tk.BooleanVar()
        tk.Checkbutton(frame, text="Ja li este livro", variable=self.lido_var,
                       bg=BG, fg=TEXT, selectcolor=SURFACE,
                       activebackground=BG, activeforeground=TEXT,
                       font=("Segoe UI", 10)).grid(row=row_g+1, column=1,
                       sticky="w", padx=(8,0), pady=(10,2))

        self._label(frame, "Observacoes", row_g+2)
        self.obs_text = tk.Text(frame, bg=SURFACE, fg=TEXT, insertbackground=TEXT,
                                relief="flat", font=("Segoe UI", 10),
                                width=38, height=4,
                                highlightthickness=1, highlightbackground=ACCENT,
                                highlightcolor=ACCENT)
        self.obs_text.grid(row=row_g+2, column=1, sticky="ew", padx=(8,0), pady=(8,0))

        btn_frame = tk.Frame(frame, bg=BG)
        btn_frame.grid(row=row_g+3, column=0, columnspan=2, pady=(18,0))

        tk.Button(btn_frame, text="Cancelar", command=self.destroy,
                  bg=SURFACE, fg=TEXT_MUTED, relief="flat",
                  font=("Segoe UI", 10), padx=18, pady=8,
                  cursor="hand2").pack(side="left", padx=(0,10))

        tk.Button(btn_frame, text="  Salvar  ", command=self._salvar,
                  bg=ACCENT, fg="white", relief="flat",
                  font=("Segoe UI", 10, "bold"), padx=18, pady=8,
                  cursor="hand2", activebackground=ACCENT2,
                  activeforeground="white").pack(side="left")

    def _preencher(self, livro):
        mapa = {"titulo":1,"autor":2,"genero":3,"ano":4,"editora":5,"nota":7,"obs":8}
        for key, idx in mapa.items():
            val = livro[idx]
            if val is None:
                continue
            if key == "genero":
                self.vars[key].set(val)
            elif key == "obs":
                self.obs_text.insert("1.0", val)
            else:
                self.vars[key].delete(0, "end")
                self.vars[key].insert(0, str(val))
        self.lido_var.set(bool(livro[6]))

    def _salvar(self):
        titulo  = self.vars["titulo"].get().strip()
        autor   = self.vars["autor"].get().strip()
        genero  = self.vars["genero"].get().strip()

        if not titulo or not autor or not genero:
            messagebox.showwarning("Campos obrigatorios",
                                   "Preencha Titulo, Autor e Genero.", parent=self)
            return

        ano     = self.vars["ano"].get().strip() or None
        editora = self.vars["editora"].get().strip() or None
        nota_s  = self.vars["nota"].get().strip()
        lido    = int(self.lido_var.get())
        obs     = self.obs_text.get("1.0", "end").strip() or None

        try:
            ano  = int(ano)  if ano  else None
            nota = float(nota_s) if nota_s else None
            if nota is not None and not (0 <= nota <= 10):
                raise ValueError
        except ValueError:
            messagebox.showwarning("Valor invalido",
                                   "Ano deve ser numero inteiro e Nota entre 0 e 10.", parent=self)
            return

        con = get_connection()
        cur = con.cursor()
        if self.livro:
            cur.execute("""UPDATE livros SET titulo=?,autor=?,genero=?,ano=?,editora=?,
                           lido=?,nota=?,obs=? WHERE id=?""",
                        (titulo, autor, genero, ano, editora, lido, nota, obs, self.livro[0]))
        else:
            cur.execute("""INSERT INTO livros (titulo,autor,genero,ano,editora,lido,nota,obs)
                           VALUES (?,?,?,?,?,?,?,?)""",
                        (titulo, autor, genero, ano, editora, lido, nota, obs))
        con.commit()
        con.close()
        self.parent.carregar_livros()
        self.destroy()

# ── Janela de Importacao CSV ──────────────────────────────────────────────────

class JanelaCSV(tk.Toplevel):
    """Janela de importacao de CSV com mapeamento de colunas."""

    def __init__(self, parent, rows, colunas):
        super().__init__(parent)
        self.parent  = parent
        self.rows    = rows
        self.colunas = ["(ignorar)"] + list(colunas)
        self.title("Importar CSV")
        self.configure(bg=BG)
        self.resizable(False, False)
        self.grab_set()
        self._build()
        self.update_idletasks()
        self._centralizar()

    def _centralizar(self):
        w, h = self.winfo_width(), self.winfo_height()
        x = self.parent.winfo_x() + (self.parent.winfo_width()  - w) // 2
        y = self.parent.winfo_y() + (self.parent.winfo_height() - h) // 2
        self.geometry("+{}+{}".format(x, y))

    def _lbl(self, frame, texto, row):
        tk.Label(frame, text=texto, bg=BG, fg=TEXT_MUTED,
                 font=("Segoe UI", 9)).grid(row=row, column=0, sticky="w", pady=(8,2))

    def _combo(self, frame, row, default=None):
        var = tk.StringVar(value=default or "(ignorar)")
        cb = ttk.Combobox(frame, textvariable=var, values=self.colunas,
                          state="readonly", font=("Segoe UI", 10), width=30)
        cb.grid(row=row, column=1, sticky="ew", padx=(10,0), pady=(8,2))
        return var

    def _auto_detectar(self, campo):
        """Tenta achar automaticamente a coluna do CSV para cada campo."""
        sinonimos = {
            "titulo": ["titulo", "title", "nome", "name", "livro", "book"],
            "autor":  ["autor", "author", "escritor", "writer"],
            "genero": ["genero", "genre", "categoria", "category", "tipo"],
            "ano":    ["ano", "year", "ano_publicacao", "published"],
            "editora":["editora", "publisher", "editora/publisher"],
            "lido":   ["lido", "read", "lido?", "ja lido", "concluido"],
            "nota":   ["nota", "rating", "avaliacao", "score", "pontuacao"],
            "obs":    ["obs", "observacoes", "notes", "notas", "comentarios"],
        }
        for col in self.colunas[1:]:  # skip (ignorar)
            for syn in sinonimos.get(campo, []):
                if syn in col.lower().replace(" ", "_"):
                    return col
        return "(ignorar)"

    def _build(self):
        frame = tk.Frame(self, bg=BG, padx=24, pady=20)
        frame.pack(fill="both", expand=True)

        tk.Label(frame, text="Importar CSV", bg=BG, fg=TEXT,
                 font=("Segoe UI", 13, "bold")).grid(
                 row=0, column=0, columnspan=2, sticky="w", pady=(0,4))

        info = "Arquivo com {} linha(s). Mapeie as colunas do CSV para cada campo:".format(
            len(self.rows))
        tk.Label(frame, text=info, bg=BG, fg=TEXT_MUTED,
                 font=("Segoe UI", 9)).grid(
                 row=1, column=0, columnspan=2, sticky="w", pady=(0,12))

        campos = [
            ("Titulo *",    "titulo"),
            ("Autor *",     "autor"),
            ("Genero",      "genero"),
            ("Ano",         "ano"),
            ("Editora",     "editora"),
            ("Lido",        "lido"),
            ("Nota",        "nota"),
            ("Observacoes", "obs"),
        ]

        self.map_vars = {}
        for i, (label, key) in enumerate(campos):
            self._lbl(frame, label, 2 + i)
            self.map_vars[key] = self._combo(frame, 2 + i,
                                             default=self._auto_detectar(key))

        # Opcao duplicatas
        self.skip_dup = tk.BooleanVar(value=True)
        tk.Checkbutton(frame,
                       text="Ignorar livros ja cadastrados (mesmo titulo + autor)",
                       variable=self.skip_dup, bg=BG, fg=TEXT,
                       selectcolor=SURFACE, activebackground=BG,
                       font=("Segoe UI", 10)).grid(
                       row=2+len(campos), column=0, columnspan=2,
                       sticky="w", pady=(14,0))

        self.lbl_status = tk.Label(frame, text="", bg=BG, fg=TEXT_MUTED,
                                   font=("Segoe UI", 9))
        self.lbl_status.grid(row=3+len(campos), column=0, columnspan=2,
                             sticky="w", pady=(6,0))

        btn_frame = tk.Frame(frame, bg=BG)
        btn_frame.grid(row=4+len(campos), column=0, columnspan=2, pady=(14,0))

        tk.Button(btn_frame, text="Cancelar", command=self.destroy,
                  bg=SURFACE, fg=TEXT_MUTED, relief="flat",
                  font=("Segoe UI", 10), padx=18, pady=8,
                  cursor="hand2").pack(side="left", padx=(0,10))

        self.btn_imp = tk.Button(btn_frame, text="  Importar  ",
                  command=self._importar,
                  bg=ACCENT, fg="white", relief="flat",
                  font=("Segoe UI", 10, "bold"), padx=18, pady=8,
                  cursor="hand2", activebackground=ACCENT2,
                  activeforeground="white")
        self.btn_imp.pack(side="left")

    def _get_val(self, row, campo):
        col = self.map_vars[campo].get()
        if col == "(ignorar)":
            return None
        return row.get(col, "").strip() or None

    def _importar(self):
        titulo_col = self.map_vars["titulo"].get()
        autor_col  = self.map_vars["autor"].get()

        if titulo_col == "(ignorar)" or autor_col == "(ignorar)":
            messagebox.showwarning("Campos obrigatorios",
                                   "Mapeie pelo menos Titulo e Autor.", parent=self)
            return

        self.btn_imp.config(state="disabled", text="Importando...")
        self.lbl_status.config(text="Processando...", fg=TEXT_MUTED)
        self.update()

        con = get_connection()
        inseridos = 0
        ignorados = 0
        erros     = 0

        for row in self.rows:
            titulo = (row.get(titulo_col) or "").strip()
            autor  = (row.get(autor_col)  or "").strip()
            if not titulo or not autor:
                erros += 1
                continue

            if self.skip_dup.get():
                existe = con.execute(
                    "SELECT 1 FROM livros WHERE LOWER(titulo)=LOWER(?) AND LOWER(autor)=LOWER(?)",
                    (titulo, autor)
                ).fetchone()
                if existe:
                    ignorados += 1
                    continue

            genero_raw = self._get_val(row, "genero")
            genero = _mapear_genero(genero_raw) if genero_raw else "Outros"

            ano_raw = self._get_val(row, "ano")
            try:
                ano = int(ano_raw) if ano_raw else None
            except ValueError:
                ano = None

            editora = self._get_val(row, "editora")

            lido_raw = self._get_val(row, "lido")
            if lido_raw:
                lido = 1 if lido_raw.lower() in ("sim", "yes", "true", "1", "x", "v") else 0
            else:
                lido = 0

            nota_raw = self._get_val(row, "nota")
            try:
                nota = float(nota_raw.replace(",", ".")) if nota_raw else None
                if nota is not None and not (0 <= nota <= 10):
                    nota = None
            except (ValueError, AttributeError):
                nota = None

            obs = self._get_val(row, "obs")

            con.execute(
                "INSERT INTO livros (titulo,autor,genero,ano,editora,lido,nota,obs) VALUES (?,?,?,?,?,?,?,?)",
                (titulo, autor, genero, ano, editora, lido, nota, obs)
            )
            inseridos += 1

        con.commit()
        con.close()

        msg = "{} livro(s) importado(s)!".format(inseridos)
        if ignorados:
            msg += "  ({} duplicado(s) ignorado(s))".format(ignorados)
        if erros:
            msg += "  ({} linha(s) sem titulo/autor ignorada(s))".format(erros)

        self.lbl_status.config(text=msg, fg=SUCCESS)
        self.btn_imp.config(state="normal", text="  Importar  ")
        self.parent.carregar_livros()


# ── Aplicacao Principal ───────────────────────────────────────────────────────

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Minha Biblioteca")
        self.geometry("1100x680")
        self.configure(bg=BG)
        self.minsize(900, 560)
        init_db()
        self._style()
        self._build()
        self.carregar_livros()

    def _style(self):
        s = ttk.Style(self)
        s.theme_use("clam")
        s.configure("Treeview",
                     background=ROW_ODD, foreground=TEXT,
                     fieldbackground=ROW_ODD, rowheight=28,
                     font=("Segoe UI", 10), borderwidth=0)
        s.configure("Treeview.Heading",
                     background=SURFACE, foreground=TEXT,
                     font=("Segoe UI", 10, "bold"), relief="flat")
        s.map("Treeview",
              background=[("selected", ACCENT)],
              foreground=[("selected", "white")])
        s.map("Treeview.Heading", background=[("active", ACCENT2)])
        s.configure("TCombobox", fieldbackground=SURFACE, background=SURFACE,
                    foreground=TEXT, selectbackground=ACCENT)
        s.map("TCombobox", fieldbackground=[("readonly", SURFACE)],
              foreground=[("readonly", TEXT)])
        s.configure("Vertical.TScrollbar", background=SURFACE,
                    troughcolor=BG, arrowcolor=TEXT_MUTED)

    def _build(self):
        # Barra superior
        top = tk.Frame(self, bg=SURFACE, pady=12, padx=20)
        top.pack(fill="x")

        tk.Label(top, text="Minha Biblioteca", bg=SURFACE, fg=TEXT,
                 font=("Segoe UI", 16, "bold")).pack(side="left")

        self.lbl_total = tk.Label(top, text="", bg=SURFACE, fg=TEXT_MUTED,
                                  font=("Segoe UI", 10))
        self.lbl_total.pack(side="left", padx=20)

        tk.Button(top, text="+ Cadastrar Livro", command=self._novo,
                  bg=ACCENT, fg="white", relief="flat",
                  font=("Segoe UI", 10, "bold"), padx=14, pady=6,
                  cursor="hand2", activebackground=ACCENT2,
                  activeforeground="white").pack(side="right")

        tk.Button(top, text="Exportar CSV", command=self._exportar,
                  bg=SURFACE, fg=TEXT, relief="flat",
                  font=("Segoe UI", 10), padx=14, pady=6,
                  cursor="hand2").pack(side="right", padx=8)


        tk.Button(top, text="Importar CSV", command=self._importar_csv,
                  bg=SURFACE, fg=TEXT, relief="flat",
                  font=("Segoe UI", 10), padx=14, pady=6,
                  cursor="hand2").pack(side="right", padx=(0,4))

        # Barra de filtros
        filt = tk.Frame(self, bg=BG, pady=12, padx=20)
        filt.pack(fill="x")

        tk.Label(filt, text="Buscar:", bg=BG, fg=TEXT_MUTED,
                 font=("Segoe UI", 10)).pack(side="left")

        self.busca_var = tk.StringVar()
        self.busca_var.trace_add("write", lambda *_: self.carregar_livros())
        tk.Entry(filt, textvariable=self.busca_var,
                 bg=SURFACE, fg=TEXT, insertbackground=TEXT,
                 relief="flat", font=("Segoe UI", 10), width=28,
                 highlightthickness=1, highlightbackground=ACCENT,
                 highlightcolor=ACCENT).pack(side="left", padx=(6,18))

        tk.Label(filt, text="Genero:", bg=BG, fg=TEXT_MUTED,
                 font=("Segoe UI", 10)).pack(side="left")

        self.genero_var = tk.StringVar(value="Todos")
        cb = ttk.Combobox(filt, textvariable=self.genero_var,
                          values=["Todos"] + GENEROS,
                          state="readonly", font=("Segoe UI", 10), width=20)
        cb.pack(side="left", padx=(6,18))
        cb.bind("<<ComboboxSelected>>", lambda _: self.carregar_livros())

        tk.Label(filt, text="Lido:", bg=BG, fg=TEXT_MUTED,
                 font=("Segoe UI", 10)).pack(side="left")

        self.lido_var = tk.StringVar(value="Todos")
        cb2 = ttk.Combobox(filt, textvariable=self.lido_var,
                            values=["Todos", "Sim", "Nao"],
                            state="readonly", font=("Segoe UI", 10), width=8)
        cb2.pack(side="left", padx=(6,0))
        cb2.bind("<<ComboboxSelected>>", lambda _: self.carregar_livros())

        # Tabela
        table_frame = tk.Frame(self, bg=BG)
        table_frame.pack(fill="both", expand=True, padx=20, pady=(0,10))

        cols = ("titulo","autor","genero","ano","editora","lido","nota")
        self.tree = ttk.Treeview(table_frame, columns=cols, show="headings",
                                  selectmode="browse")

        headers = {
            "titulo":  ("Titulo",  280),
            "autor":   ("Autor",   200),
            "genero":  ("Genero",  150),
            "ano":     ("Ano",      60),
            "editora": ("Editora", 140),
            "lido":    ("Lido",     55),
            "nota":    ("Nota",     55),
        }
        for col, (h, w) in headers.items():
            self.tree.heading(col, text=h,
                              command=lambda c=col: self._ordenar(c))
            self.tree.column(col, width=w, minwidth=40,
                             anchor="center" if col in ("ano","lido","nota") else "w")

        self.tree.tag_configure("odd",  background=ROW_ODD)
        self.tree.tag_configure("even", background=ROW_EVEN)
        self.tree.tag_configure("lido", foreground=SUCCESS)

        scroll = ttk.Scrollbar(table_frame, orient="vertical",
                               command=self.tree.yview)
        self.tree.configure(yscrollcommand=scroll.set)
        self.tree.pack(side="left", fill="both", expand=True)
        scroll.pack(side="right", fill="y")

        self.tree.bind("<Double-1>",  self._editar)
        self.tree.bind("<Delete>",    self._deletar)
        self.tree.bind("<BackSpace>", self._deletar)

        # Barra de acoes
        bot = tk.Frame(self, bg=SURFACE, pady=8, padx=20)
        bot.pack(fill="x")

        tk.Label(bot, text="Double-click para editar  |  Delete para remover",
                 bg=SURFACE, fg=TEXT_MUTED, font=("Segoe UI", 9)).pack(side="left")

        tk.Button(bot, text="Editar", command=self._editar,
                  bg=SURFACE, fg=TEXT, relief="flat",
                  font=("Segoe UI", 9), padx=10, pady=4,
                  cursor="hand2").pack(side="right", padx=4)

        tk.Button(bot, text="Remover", command=self._deletar,
                  bg=SURFACE, fg=DANGER, relief="flat",
                  font=("Segoe UI", 9), padx=10, pady=4,
                  cursor="hand2").pack(side="right")

        self._sort_col = None
        self._sort_rev = False

    # ── Dados ─────────────────────────────────────────────────────────────────

    def carregar_livros(self):
        busca  = self.busca_var.get().strip()
        genero = self.genero_var.get()
        lido   = self.lido_var.get()

        query  = "SELECT * FROM livros WHERE 1=1"
        params = []

        if busca:
            query += " AND (titulo LIKE ? OR autor LIKE ? OR editora LIKE ?)"
            p = "%{}%".format(busca)
            params += [p, p, p]

        if genero != "Todos":
            query += " AND genero=?"
            params.append(genero)

        if lido == "Sim":
            query += " AND lido=1"
        elif lido == "Nao":
            query += " AND lido=0"

        if self._sort_col:
            query += " ORDER BY {} {}".format(
                self._sort_col, "DESC" if self._sort_rev else "ASC")
        else:
            query += " ORDER BY titulo ASC"

        con = get_connection()
        rows = con.execute(query, params).fetchall()
        con.close()

        self._livros = rows
        self.tree.delete(*self.tree.get_children())

        for i, r in enumerate(rows):
            nota_str = "{:.1f}".format(r[7]) if r[7] is not None else "-"
            lido_str = "v" if r[6] else "-"
            tag = ("even" if i % 2 == 0 else "odd",)
            if r[6]:
                tag = ("lido",) + tag
            self.tree.insert("", "end", iid=str(r[0]),
                             values=(r[1], r[2], r[3], r[4] or "-",
                                     r[5] or "-", lido_str, nota_str),
                             tags=tag)

        total = len(rows)
        lidos = sum(1 for r in rows if r[6])
        self.lbl_total.config(
            text="{} livro{}  |  {} lido{}".format(
                total, "s" if total != 1 else "",
                lidos, "s" if lidos != 1 else "")
        )

    def _livro_selecionado(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showinfo("Selecione", "Selecione um livro na lista.")
            return None
        lid = int(sel[0])
        con = get_connection()
        row = con.execute("SELECT * FROM livros WHERE id=?", (lid,)).fetchone()
        con.close()
        return row

    def _novo(self):
        JanelaCadastro(self)


    def _importar_csv(self):
        path = filedialog.askopenfilename(
            title="Selecionar arquivo CSV",
            filetypes=[("CSV", "*.csv"), ("Todos", "*.*")]
        )
        if not path:
            return

        # Detectar encoding
        for enc in ("utf-8-sig", "utf-8", "latin-1", "cp1252"):
            try:
                with open(path, newline="", encoding=enc) as f:
                    sample = f.read(1024)
                encoding = enc
                break
            except UnicodeDecodeError:
                continue

        try:
            with open(path, newline="", encoding=encoding) as f:
                reader = csv.DictReader(f)
                colunas = reader.fieldnames or []
                rows = list(reader)
        except Exception as e:
            messagebox.showerror("Erro ao ler CSV",
                                 "Nao foi possivel abrir o arquivo:\n{}".format(str(e)))
            return

        if not rows:
            messagebox.showwarning("CSV vazio", "O arquivo nao contem linhas de dados.")
            return

        JanelaCSV(self, rows, colunas)

    def _editar(self, event=None):
        livro = self._livro_selecionado()
        if livro:
            JanelaCadastro(self, livro)

    def _deletar(self, event=None):
        livro = self._livro_selecionado()
        if not livro:
            return
        if messagebox.askyesno("Confirmar", 'Remover "{}"?'.format(livro[1]), parent=self):
            con = get_connection()
            con.execute("DELETE FROM livros WHERE id=?", (livro[0],))
            con.commit()
            con.close()
            self.carregar_livros()

    def _ordenar(self, col):
        if self._sort_col == col:
            self._sort_rev = not self._sort_rev
        else:
            self._sort_col = col
            self._sort_rev = False
        self.carregar_livros()

    def _exportar(self):
        path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV", "*.csv")],
            initialfile="biblioteca_{}.csv".format(
                datetime.now().strftime("%Y%m%d_%H%M"))
        )
        if not path:
            return
        con = get_connection()
        rows = con.execute(
            "SELECT titulo,autor,genero,ano,editora,lido,nota,obs,criado_em "
            "FROM livros ORDER BY titulo").fetchall()
        con.close()
        with open(path, "w", newline="", encoding="utf-8-sig") as f:
            w = csv.writer(f)
            w.writerow(["Titulo","Autor","Genero","Ano","Editora",
                        "Lido","Nota","Observacoes","Cadastrado em"])
            for r in rows:
                w.writerow([r[0], r[1], r[2], r[3] or "", r[4] or "",
                            "Sim" if r[5] else "Nao",
                            r[6] if r[6] is not None else "", r[7] or "", r[8]])
        messagebox.showinfo("Exportado", "Arquivo salvo em:\n{}".format(path))

# ── Iniciar ───────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    App().mainloop()
