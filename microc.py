"""
MicroC Pre-Compilador
Universidad Mesoamericana - Ingeniería en Sistemas
Curso: Autómatas y Lenguajes - 2026
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import os
import re
from collections import defaultdict, deque
from dataclasses import dataclass


# ──────────────────────────────────────────────
#  Colores y fuentes (tema oscuro tipo IDE)
# ──────────────────────────────────────────────
BG_DARK   = "#1e1e1e"
BG_EDITOR = "#252526"
BG_OUTPUT = "#1a1a2e"
FG_WHITE  = "#d4d4d4"
FG_GREEN  = "#4ec94e"
FG_YELLOW = "#dcdcaa"
FG_BLUE   = "#569cd6"
FG_RED    = "#f44747"
FG_GRAY   = "#808080"
ACCENT    = "#007acc"
MENUBAR   = "#2d2d30"
FONT_CODE = ("Consolas", 11)
FONT_UI   = ("Segoe UI", 10)
FONT_TITLE= ("Segoe UI", 10, "bold")

KEYWORDS = {
    "if", "else", "while", "for", "return", "int", "float", "void", "char"
}


@dataclass(frozen=True)
class Automaton:
    states: set[int]
    start_state: int
    accept_states: set[int]
    transitions: dict[int, list[tuple[str | None, int]]]
    alphabet: tuple[str, ...] = ()


@dataclass(frozen=True)
class TokenSpec:
    name: str
    informal: str
    regex: str
    afn: Automaton
    dfa: Automaton
    notes: str = ""


def transition_count(automaton: Automaton) -> int:
    return sum(len(targets) for targets in automaton.transitions.values())


def epsilon_closure(states: set[int], transitions: dict[int, list[tuple[str | None, int]]]) -> frozenset[int]:
    pending = list(states)
    closure = set(states)
    while pending:
        state = pending.pop()
        for symbol, target in transitions.get(state, []):
            if symbol is None and target not in closure:
                closure.add(target)
                pending.append(target)
    return frozenset(closure)


def move(states: frozenset[int], symbol: str, transitions: dict[int, list[tuple[str | None, int]]]) -> set[int]:
    targets: set[int] = set()
    for state in states:
        for edge_symbol, target in transitions.get(state, []):
            if edge_symbol == symbol:
                targets.add(target)
    return targets


def determinize(afn: Automaton) -> Automaton:
    start_subset = epsilon_closure({afn.start_state}, afn.transitions)
    subset_to_state = {start_subset: 0}
    queue = deque([start_subset])
    dfa_transitions: dict[int, list[tuple[str, int]]] = defaultdict(list)
    accept_states: set[int] = set()

    while queue:
        subset = queue.popleft()
        current_state = subset_to_state[subset]

        if afn.accept_states.intersection(subset):
            accept_states.add(current_state)

        for symbol in afn.alphabet:
            target_subset = epsilon_closure(move(subset, symbol, afn.transitions), afn.transitions)
            if not target_subset:
                continue
            if target_subset not in subset_to_state:
                subset_to_state[target_subset] = len(subset_to_state)
                queue.append(target_subset)
            dfa_transitions[current_state].append((symbol, subset_to_state[target_subset]))

    return Automaton(
        states=set(subset_to_state.values()),
        start_state=0,
        accept_states=accept_states,
        transitions=dict(dfa_transitions),
        alphabet=afn.alphabet,
    )


def build_literal_trie(words: list[str], name: str) -> TokenSpec:
    transitions: dict[int, list[tuple[str, int]]] = defaultdict(list)
    next_state = 1
    node_state: dict[str, int] = {"": 0}
    accept_states: set[int] = set()

    for word in sorted(words):
        prefix = ""
        current_state = 0
        for char in word:
            new_prefix = prefix + char
            if new_prefix not in node_state:
                node_state[new_prefix] = next_state
                transitions[current_state].append((char, next_state))
                next_state += 1
            current_state = node_state[new_prefix]
            prefix = new_prefix
        accept_states.add(current_state)

    afn = Automaton(
        states=set(range(next_state)),
        start_state=0,
        accept_states=accept_states,
        transitions=dict(transitions),
        alphabet=tuple(sorted({char for word in words for char in word})),
    )
    return TokenSpec(
        name=name,
        informal="Palabras reservadas del lenguaje: if, else, while, for, return, int, float, void, char.",
        regex=r"(if|else|while|for|return|int|float|void|char)",
        afn=afn,
        dfa=determinize(afn),
        notes="Se reconoce antes que ID para evitar ambigüedad.",
    )


def build_simple_token_spec(
    name: str,
    informal: str,
    regex: str,
    alphabet: tuple[str, ...],
    transitions: dict[int, list[tuple[str | None, int]]],
    accept_states: set[int],
    notes: str = "",
) -> TokenSpec:
    states = set(transitions.keys()) | {0}
    for edges in transitions.values():
        for _, target in edges:
            states.add(target)
    afn = Automaton(
        states=states,
        start_state=0,
        accept_states=accept_states,
        transitions=transitions,
        alphabet=alphabet,
    )
    return TokenSpec(
        name=name,
        informal=informal,
        regex=regex,
        afn=afn,
        dfa=determinize(afn),
        notes=notes,
    )


TOKEN_SPECS = {
    "KW": build_literal_trie(sorted(KEYWORDS), "KW"),
    "ID": build_simple_token_spec(
        name="ID",
        informal="Identificadores que inician con letra o guion bajo y continúan con letras, dígitos o guion bajo.",
        regex=r"[A-Za-z_][A-Za-z0-9_]*",
        alphabet=("LETTER_OR_UNDERSCORE", "ALNUM_OR_UNDERSCORE"),
        transitions={
            0: [("LETTER_OR_UNDERSCORE", 1)],
            1: [("ALNUM_OR_UNDERSCORE", 1)],
        },
        accept_states={1},
    ),
    "NUM": build_simple_token_spec(
        name="NUM",
        informal="Numeros enteros no negativos. Solo 0 o secuencias que no empiezan con 0.",
        regex=r"(0|[1-9][0-9]*)",
        alphabet=("ZERO", "NONZERO", "DIGIT"),
        transitions={
            0: [("ZERO", 1), ("NONZERO", 2)],
            2: [("DIGIT", 2)],
        },
        accept_states={1, 2},
        notes="La forma -0 no se acepta como numero; '-' se tokeniza como operador.",
    ),
    "OP": build_simple_token_spec(
        name="OP",
        informal="Operadores aritmeticos basicos.",
        regex=r"[\+\-\*/=]",
        alphabet=("+", "-", "*", "/", "="),
        transitions={
            0: [("+", 1), ("-", 1), ("*", 1), ("/", 1), ("=", 1)],
        },
        accept_states={1},
    ),
    "DELIM": build_simple_token_spec(
        name="DELIM",
        informal="Delimitadores y separadores basicos.",
        regex=r"[\(\)\{\};,]",
        alphabet=("(", ")", "{", "}", ";", ","),
        transitions={
            0: [("(", 1), (")", 1), ("{", 1), ("}", 1), (";", 1), (",", 1)],
        },
        accept_states={1},
    ),
    "LINE_COMMENT": build_simple_token_spec(
        name="LINE_COMMENT",
        informal="Comentario de linea que inicia con // y termina en salto de linea o fin de archivo.",
        regex=r"//[^\n]*",
        alphabet=("/", "ANY_EXCEPT_NEWLINE"),
        transitions={
            0: [("/", 1)],
            1: [("/", 2)],
            2: [("ANY_EXCEPT_NEWLINE", 2), ("/", 2)],
        },
        accept_states={2},
    ),
    "BLOCK_COMMENT": build_simple_token_spec(
        name="BLOCK_COMMENT",
        informal="Comentario de bloque delimitado por /* y */.",
        regex=r"/\*[\s\S]*?\*/",
        alphabet=("/", "*", "OTHER"),
        transitions={
            0: [("/", 1)],
            1: [("*", 2)],
            2: [("/", 2), ("OTHER", 2), ("*", 3)],
            3: [("*", 3), ("OTHER", 2), ("/", 4)],
        },
        accept_states={4},
        notes="El AFD cierra en la primera aparicion valida de */.",
    ),
}


TOKEN_RULES = [
    ("WHITESPACE", re.compile(r"[ \t\r\n]+")),
    ("BLOCK_COMMENT", re.compile(r"/\*[\s\S]*?\*/")),
    ("LINE_COMMENT", re.compile(r"//[^\n]*")),
    ("KW", re.compile(r"\b(?:if|else|while|for|return|int|float|void|char)\b")),
    ("ID", re.compile(r"[A-Za-z_][A-Za-z0-9_]*")),
    ("NUM", re.compile(r"0|[1-9][0-9]*")),
    ("STRING", re.compile(r'"([^"\\]|\\.)*"')),
    ("OP", re.compile(r"[+\-*/=]")),
    ("DELIM", re.compile(r"[(){};,]")),
]

BLOCK_COMMENT_PATTERN = dict(TOKEN_RULES)["BLOCK_COMMENT"]


def advance_position(lexeme: str, line: int, column: int) -> tuple[int, int]:
    for char in lexeme:
        if char == "\n":
            line += 1
            column = 1
        else:
            column += 1
    return line, column


def lexical_analysis(source: str) -> tuple[list[dict], list[dict], dict]:
    tokens: list[dict] = []
    errors: list[dict] = []
    pos = 0
    line = 1
    column = 1
    skipped_comments = 0

    while pos < len(source):
        if source.startswith("/*", pos):
            block_match = BLOCK_COMMENT_PATTERN.match(source, pos)
            if not block_match:
                errors.append({
                    "line": line,
                    "column": column,
                    "char": "/*",
                    "message": "Comentario de bloque sin cerrar",
                })
                break

        match = None
        token_name = None

        for name, pattern in TOKEN_RULES:
            current = pattern.match(source, pos)
            if current:
                match = current
                token_name = name
                break

        if not match:
            errors.append({
                "line": line,
                "column": column,
                "char": source[pos],
                "message": f"Símbolo no reconocido: {source[pos]!r}",
            })
            pos += 1
            column += 1
            continue

        lexeme = match.group(0)
        start_line = line
        start_column = column
        line, column = advance_position(lexeme, line, column)
        pos = match.end()

        if token_name == "WHITESPACE":
            continue

        if token_name in {"LINE_COMMENT", "BLOCK_COMMENT"}:
            skipped_comments += 1
            continue

        tokens.append({
            "type": token_name,
            "lexeme": lexeme,
            "line": start_line,
            "column": start_column,
        })

    summary = {
        "total_tokens": len(tokens),
        "errors": len(errors),
        "comments": skipped_comments,
        "distinct_token_types": len({token["type"] for token in tokens}),
    }
    return tokens, errors, summary


def render_automaton(automaton: Automaton) -> str:
    lines = [
        f"Inicio: q{automaton.start_state}",
        "Aceptacion: " + ", ".join(f"q{state}" for state in sorted(automaton.accept_states)),
        "Transiciones:",
    ]
    for state in sorted(automaton.states):
        edges = automaton.transitions.get(state, [])
        if not edges:
            lines.append(f"  q{state} -- sin salidas")
            continue
        for symbol, target in edges:
            label = "ε" if symbol is None else symbol
            lines.append(f"  q{state} --{label}--> q{target}")
    return "\n".join(lines)


def format_token_specs() -> str:
    lines = [
        "1. Definicion formal del lenguaje lexico",
        "",
    ]
    order = ["KW", "ID", "NUM", "OP", "DELIM", "LINE_COMMENT", "BLOCK_COMMENT"]
    for name in order:
        spec = TOKEN_SPECS[name]
        lines.extend([
            f"[{spec.name}]",
            f"Definicion informal: {spec.informal}",
            f"Expresion regular: {spec.regex}",
            f"AFN  -> estados: {len(spec.afn.states)}, transiciones: {transition_count(spec.afn)}",
            render_automaton(spec.afn),
            f"AFD  -> estados: {len(spec.dfa.states)}, transiciones: {transition_count(spec.dfa)}",
            render_automaton(spec.dfa),
        ])
        if spec.notes:
            lines.append(f"Nota de diseno: {spec.notes}")
        lines.append("")
    return "\n".join(lines)


def format_token_table(tokens: list[dict]) -> str:
    if not tokens:
        return "No se generaron tokens.\n"

    header = f"{'#':<4}{'Token':<12}{'Lexema':<18}{'Linea':<8}{'Columna':<8}\n"
    rows = [header, "-" * 52 + "\n"]
    for index, token in enumerate(tokens, start=1):
        rows.append(
            f"{index:<4}{token['type']:<12}{token['lexeme']:<18}{token['line']:<8}{token['column']:<8}\n"
        )
    return "".join(rows)


def format_errors(errors: list[dict]) -> str:
    if not errors:
        return "Sin errores lexicos.\n"

    lines = ["Errores lexicos detectados:\n"]
    for error in errors:
        lines.append(
            f"- Linea {error['line']}, columna {error['column']}: "
            f"{error['message']}\n"
        )
    return "".join(lines)


def format_analysis(summary: dict) -> str:
    required_specs = [TOKEN_SPECS[name] for name in (
        "KW", "ID", "NUM", "OP", "DELIM", "LINE_COMMENT", "BLOCK_COMMENT"
    )]
    total_afn_states = sum(len(spec.afn.states) for spec in required_specs)
    total_afd_states = sum(len(spec.dfa.states) for spec in required_specs)
    total_afn_transitions = sum(transition_count(spec.afn) for spec in required_specs)
    total_afd_transitions = sum(transition_count(spec.dfa) for spec in required_specs)

    lines = [
        "5. Evaluacion del diseno",
        "",
        f"Tokens reconocidos: {summary['total_tokens']}",
        f"Comentarios ignorados: {summary['comments']}",
        f"Tipos de token usados: {summary['distinct_token_types']}",
        f"Errores lexicos: {summary['errors']}",
        "",
        "Analisis estructural global",
        f"- AFN total aproximado: {total_afn_states} estados, {total_afn_transitions} transiciones",
        f"- AFD total aproximado: {total_afd_states} estados, {total_afd_transitions} transiciones",
        "",
        "Conclusiones de investigacion",
        "- Expresiones regulares con prefijos compartidos, como KW, generan automatas mas grandes que ID u OP.",
        "- Separar comentarios en automatas propios mejora la claridad del diseno y evita mezclar reglas complejas con tokens simples.",
        "- El paso de AFN a AFD reduce la no determinacion, pero puede aumentar o reorganizar estados segun el patron.",
        "- Evitar ambiguedades, como confundir KW con ID, reduce backtracking conceptual y simplifica el analizador.",
        "- Restricciones como NUM = 0|[1-9][0-9]* mejoran precision y previenen cadenas no deseadas como 007.",
        "",
        "Preguntas de investigacion respondidas",
        "- La forma de la ER influye directamente en el tamano del automata: mas alternativas y prefijos, mas estados.",
        "- Muchos automatas pequenos son mas faciles de explicar y mantener; luego pueden integrarse en un analizador unificado.",
        "- Errores comunes: usar patrones demasiado generales, no priorizar KW sobre ID y no limitar correctamente comentarios.",
        "- Al pasar de AFN a AFD se eliminan decisiones simultaneas, lo que favorece la ejecucion del lexer.",
        "- La eficiencia depende del orden de reconocimiento, la ausencia de ambiguedad y la simplicidad de las ER.",
    ]
    return "\n".join(lines) + "\n"


class MicroCCompiler:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("MicroC Compiler - [Sin título]")
        self.root.geometry("1100x680")
        self.root.minsize(800, 500)
        self.root.configure(bg=BG_DARK)

        # Estado interno
        self.current_file: str | None = None   # ruta del archivo actual
        self.is_modified: bool = False          # cambios sin guardar
        self.is_new_file: bool = True           # si es archivo nuevo o abierto

        self._build_menu()
        self._build_toolbar()
        self._build_body()
        self._build_statusbar()

        # Interceptar cierre de ventana
        self.root.protocol("WM_DELETE_WINDOW", self._salir)

    # ──────────────────────────────────────────
    #  Construcción de la interfaz
    # ──────────────────────────────────────────

    def _build_menu(self):
        """Barra de menú principal."""
        menubar = tk.Menu(self.root, bg=MENUBAR, fg=FG_WHITE,
                          activebackground=ACCENT, activeforeground=FG_WHITE,
                          relief="flat", borderwidth=0)
        self.root.config(menu=menubar)

        # ── Archivo ──
        archivo_menu = tk.Menu(menubar, tearoff=0, bg=MENUBAR, fg=FG_WHITE,
                               activebackground=ACCENT, activeforeground=FG_WHITE)
        archivo_menu.add_command(label="Nuevo        Ctrl+N", command=self._nuevo)
        archivo_menu.add_command(label="Abrir...     Ctrl+A", command=self._abrir)
        archivo_menu.add_command(label="Guardar      Ctrl+G", command=self._guardar)
        archivo_menu.add_command(label="Guardar como...",     command=self._guardar_como)
        archivo_menu.add_separator()
        archivo_menu.add_command(label="Salir        Alt+F4", command=self._salir)
        menubar.add_cascade(label="Archivo", menu=archivo_menu)

        # ── Editar ──
        editar_menu = tk.Menu(menubar, tearoff=0, bg=MENUBAR, fg=FG_WHITE,
                              activebackground=ACCENT, activeforeground=FG_WHITE)
        editar_menu.add_command(label="Habilitar edición", command=self._editar)
        editar_menu.add_separator()
        editar_menu.add_command(label="Copiar   Ctrl+C",
                                command=lambda: self.editor.event_generate("<<Copy>>"))
        editar_menu.add_command(label="Pegar    Ctrl+V",
                                command=lambda: self.editor.event_generate("<<Paste>>"))
        editar_menu.add_command(label="Cortar   Ctrl+X",
                                command=lambda: self.editor.event_generate("<<Cut>>"))
        editar_menu.add_separator()
        editar_menu.add_command(label="Seleccionar todo",
                                command=lambda: self._select_all())
        menubar.add_cascade(label="Editar", menu=editar_menu)

        # ── Compilar ──
        compilar_menu = tk.Menu(menubar, tearoff=0, bg=MENUBAR, fg=FG_WHITE,
                                activebackground=ACCENT, activeforeground=FG_WHITE)
        compilar_menu.add_command(label="Compilar   F5", command=self._compilar)
        menubar.add_cascade(label="Compilar", menu=compilar_menu)

        # ── Ayuda ──
        ayuda_menu = tk.Menu(menubar, tearoff=0, bg=MENUBAR, fg=FG_WHITE,
                             activebackground=ACCENT, activeforeground=FG_WHITE)
        ayuda_menu.add_command(label="Documentación", command=self._ayuda)
        ayuda_menu.add_command(label="Acerca de...",  command=self._acerca_de)
        menubar.add_cascade(label="Ayuda", menu=ayuda_menu)

        # Atajos de teclado
        self.root.bind("<Control-n>", lambda e: self._nuevo())
        self.root.bind("<Control-a>", lambda e: self._abrir())
        self.root.bind("<Control-g>", lambda e: self._guardar())
        self.root.bind("<F5>",        lambda e: self._compilar())

    def _build_toolbar(self):
        """Barra de herramientas con botones."""
        toolbar = tk.Frame(self.root, bg=MENUBAR, pady=4, padx=6)
        toolbar.pack(side="top", fill="x")

        btn_cfg = dict(bg="#3c3c3c", fg=FG_WHITE, relief="flat",
                       activebackground=ACCENT, activeforeground=FG_WHITE,
                       font=FONT_UI, padx=10, pady=3, cursor="hand2", bd=0)

        buttons = [
            ("🆕 Nuevo",    self._nuevo),
            ("📂 Abrir",    self._abrir),
            ("💾 Guardar",  self._guardar),
            ("✏️ Editar",   self._editar),
            ("⚙️ Compilar", self._compilar),
            ("❓ Ayuda",    self._ayuda),
            ("🚪 Salir",    self._salir),
        ]

        for label, cmd in buttons:
            btn = tk.Button(toolbar, text=label, command=cmd, **btn_cfg)
            btn.pack(side="left", padx=2)
            # Efecto hover
            btn.bind("<Enter>", lambda e, b=btn: b.config(bg=ACCENT))
            btn.bind("<Leave>", lambda e, b=btn: b.config(bg="#3c3c3c"))

    def _build_body(self):
        """Área principal: editor (izq) + output (der)."""
        # PanedWindow horizontal
        paned = tk.PanedWindow(self.root, orient="horizontal",
                               bg=BG_DARK, sashwidth=5, sashrelief="flat",
                               sashpad=2)
        paned.pack(fill="both", expand=True, padx=6, pady=4)

        # ── Panel izquierdo: Editor ──
        left_frame = tk.Frame(paned, bg=BG_DARK)
        paned.add(left_frame, minsize=300)

        lbl_editor = tk.Label(left_frame, text=" 📝 Código MicroC",
                              bg="#007acc", fg=FG_WHITE, font=FONT_TITLE,
                              anchor="w", padx=6, pady=3)
        lbl_editor.pack(fill="x")

        # Frame para números de línea + editor
        edit_container = tk.Frame(left_frame, bg=BG_EDITOR)
        edit_container.pack(fill="both", expand=True)

        self.line_numbers = tk.Text(edit_container, width=4, bg="#1e1e1e",
                                    fg=FG_GRAY, font=FONT_CODE, state="disabled",
                                    relief="flat", padx=4, pady=6,
                                    selectbackground="#1e1e1e")
        self.line_numbers.pack(side="left", fill="y")

        self.editor = scrolledtext.ScrolledText(
            edit_container, wrap="none", bg=BG_EDITOR, fg=FG_WHITE,
            insertbackground=FG_WHITE, font=FONT_CODE, relief="flat",
            padx=8, pady=6, state="disabled",
            selectbackground="#264f78", undo=True
        )
        self.editor.pack(side="left", fill="both", expand=True)

        # Actualizar números de línea al escribir
        self.editor.bind("<KeyRelease>", self._on_key_release)
        self.editor.bind("<ButtonRelease>", self._on_key_release)

        # ── Panel derecho: Output ──
        right_frame = tk.Frame(paned, bg=BG_DARK)
        paned.add(right_frame, minsize=250)

        lbl_output = tk.Label(right_frame, text=" 📋 Resultados de Compilación",
                              bg="#16825d", fg=FG_WHITE, font=FONT_TITLE,
                              anchor="w", padx=6, pady=3)
        lbl_output.pack(fill="x")

        self.output = scrolledtext.ScrolledText(
            right_frame, wrap="word", bg=BG_OUTPUT, fg=FG_GREEN,
            insertbackground=FG_WHITE, font=FONT_CODE, relief="flat",
            padx=8, pady=6, state="disabled"
        )
        self.output.pack(fill="both", expand=True)

        # Tags de color para el output
        self.output.tag_config("error",   foreground=FG_RED)
        self.output.tag_config("success", foreground=FG_GREEN)
        self.output.tag_config("info",    foreground=FG_BLUE)
        self.output.tag_config("warning", foreground=FG_YELLOW)
        self.output.tag_config("gray",    foreground=FG_GRAY)

        # Inicializar números de línea
        self._update_line_numbers()

    def _build_statusbar(self):
        """Barra de estado inferior."""
        status_frame = tk.Frame(self.root, bg="#007acc", pady=2)
        status_frame.pack(side="bottom", fill="x")

        self.status_var = tk.StringVar(value="  Listo  |  Nuevo archivo")
        status_lbl = tk.Label(status_frame, textvariable=self.status_var,
                              bg="#007acc", fg=FG_WHITE, font=FONT_UI, anchor="w")
        status_lbl.pack(side="left", padx=8)

        self.cursor_var = tk.StringVar(value="Ln 1, Col 1")
        cursor_lbl = tk.Label(status_frame, textvariable=self.cursor_var,
                              bg="#007acc", fg=FG_WHITE, font=FONT_UI, anchor="e")
        cursor_lbl.pack(side="right", padx=8)

    # ──────────────────────────────────────────
    #  Helpers de UI
    # ──────────────────────────────────────────

    def _set_editor_state(self, editable: bool):
        state = "normal" if editable else "disabled"
        self.editor.config(state=state)

    def _write_output(self, text: str, tag: str = ""):
        self.output.config(state="normal")
        self.output.delete("1.0", "end")
        if tag:
            self.output.insert("end", text, tag)
        else:
            self.output.insert("end", text)
        self.output.config(state="disabled")

    def _append_output(self, text: str, tag: str = ""):
        self.output.config(state="normal")
        self.output.insert("end", text, tag)
        self.output.see("end")
        self.output.config(state="disabled")

    def _update_title(self):
        name = os.path.basename(self.current_file) if self.current_file else "[Sin título]"
        mod  = " •" if self.is_modified else ""
        path = self.current_file if self.current_file else "Nuevo archivo"
        self.root.title(f"MicroC Compiler - {path}{mod}")
        self.status_var.set(f"  {'Modificado' if self.is_modified else 'Guardado'}  |  {name}")

    def _update_line_numbers(self):
        self.line_numbers.config(state="normal")
        self.line_numbers.delete("1.0", "end")
        content = self.editor.get("1.0", "end-1c")
        lines   = content.count("\n") + 1
        numbers = "\n".join(str(i) for i in range(1, lines + 1))
        self.line_numbers.insert("1.0", numbers)
        self.line_numbers.config(state="disabled")

    def _on_key_release(self, event=None):
        self._update_line_numbers()
        # Cursor position
        pos = self.editor.index("insert").split(".")
        self.cursor_var.set(f"Ln {pos[0]}, Col {int(pos[1])+1}")
        # Marcar como modificado
        if not self.is_modified:
            self.is_modified = True
            self._update_title()

    def _select_all(self):
        self.editor.tag_add("sel", "1.0", "end")

    # ──────────────────────────────────────────
    #  Acciones principales (botones / menú)
    # ──────────────────────────────────────────

    def _nuevo(self):
        """Crear nuevo archivo en blanco."""
        if self.is_modified:
            resp = messagebox.askyesnocancel(
                "Guardar cambios",
                "Hay cambios sin guardar. ¿Desea guardar antes de crear un nuevo archivo?")
            if resp is None:
                return        # Cancelar
            if resp:
                self._guardar()

        self._set_editor_state(True)
        self.editor.delete("1.0", "end")
        self.current_file = None
        self.is_new_file  = True
        self.is_modified  = False
        self._update_title()
        self._update_line_numbers()
        self._write_output("─── Nuevo archivo creado. Listo para escribir. ───\n", "info")
        self.editor.focus_set()

    def _abrir(self):
        """Abrir archivo *.C (modo solo lectura hasta presionar Editar)."""
        if self.is_modified:
            resp = messagebox.askyesnocancel(
                "Guardar cambios",
                "Hay cambios sin guardar. ¿Desea guardar antes de abrir otro archivo?")
            if resp is None:
                return
            if resp:
                self._guardar()

        filepath = filedialog.askopenfilename(
            title="Abrir archivo MicroC",
            filetypes=[("Archivos C", "*.c *.C"), ("Todos los archivos", "*.*")])

        if not filepath:
            return

        try:
            with open(filepath, "r", encoding="utf-8") as f:
                content = f.read()

            self._set_editor_state(True)
            self.editor.delete("1.0", "end")
            self.editor.insert("1.0", content)
            self._set_editor_state(False)   # Solo lectura hasta [Editar]

            self.current_file = filepath
            self.is_new_file  = False
            self.is_modified  = False
            self._update_title()
            self._update_line_numbers()
            self._write_output(
                f"─── Archivo abierto (solo lectura) ───\n"
                f"📂 {filepath}\n\n"
                "Presione [Editar] para habilitar la edición.\n", "info")

        except Exception as e:
            messagebox.showerror("Error al abrir", str(e))

    def _guardar(self):
        """Guardar archivo (diálogo si es nuevo, sobreescribir si ya existe)."""
        if self.is_new_file or self.current_file is None:
            self._guardar_como()
        else:
            self._escribir_archivo(self.current_file)

    def _guardar_como(self):
        """Guardar con nombre (siempre muestra diálogo)."""
        filepath = filedialog.asksaveasfilename(
            title="Guardar archivo MicroC",
            defaultextension=".c",
            filetypes=[("Archivos C", "*.c *.C"), ("Todos los archivos", "*.*")])

        if filepath:
            self._escribir_archivo(filepath)
            self.current_file = filepath
            self.is_new_file  = False

    def _escribir_archivo(self, filepath: str):
        try:
            content = self.editor.get("1.0", "end-1c")
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(content)
            self.is_modified = False
            self._update_title()
            self._write_output(
                f"─── Archivo guardado exitosamente ───\n💾 {filepath}\n", "success")
        except Exception as e:
            messagebox.showerror("Error al guardar", str(e))

    def _editar(self):
        """Habilitar edición del archivo abierto."""
        self._set_editor_state(True)
        self._write_output(
            "─── Modo edición habilitado ✏️ ───\n"
            "El archivo ahora puede ser editado.\n", "warning")
        self.editor.focus_set()

    def _compilar(self):
        """Ejecutar analisis lexico y mostrar reporte academico."""
        content = self.editor.get("1.0", "end-1c").strip()
        if not content:
            self._write_output("⚠️ No hay codigo para analizar.\n", "warning")
            return

        self.output.config(state="normal")
        self.output.delete("1.0", "end")
        self._append_output("══════════════════════════════════════\n", "gray")
        self._append_output("   MicroC Compiler v1.0\n", "info")
        self._append_output("══════════════════════════════════════\n", "gray")
        self._append_output("⏳ Iniciando analisis lexico...\n\n", "info")

        archivo = self.current_file if self.current_file else "[Sin título]"
        self._append_output(f"📄 Archivo: {archivo}\n", "gray")
        self._append_output(f"📏 Líneas : {content.count(chr(10))+1}\n\n", "gray")

        tokens, errors, summary = lexical_analysis(content)

        if errors:
            self._append_output("Resultado: codigo con errores lexicos.\n\n", "error")
        else:
            self._append_output("Resultado: analisis completado sin errores lexicos.\n\n", "success")

        self._append_output(format_token_specs(), "info")
        self._append_output("\n3. Simulacion de cadenas\n\n", "info")
        self._append_output(format_token_table(tokens), "success" if not errors else "")
        self._append_output("\n4. Reporte de errores\n\n", "warning")
        self._append_output(format_errors(errors), "error" if errors else "success")
        self._append_output("\n", "")
        self._append_output(format_analysis(summary), "info")
        self._append_output("\n══════════════════════════════════════\n", "gray")

    def _ayuda(self):
        """Mostrar documentacion de uso y alcance del analizador."""
        ayuda_win = tk.Toplevel(self.root)
        ayuda_win.title("Ayuda - MicroC Compiler")
        ayuda_win.geometry("560x400")
        ayuda_win.configure(bg=BG_DARK)
        ayuda_win.resizable(False, False)

        tk.Label(ayuda_win, text="📖 Documentación MicroC",
                 bg=BG_DARK, fg=FG_WHITE, font=("Segoe UI", 14, "bold"),
                 pady=16).pack()

        texto = (
            "MicroC Pre-Compilador — Universidad Mesoamericana\n"
            "Curso: Autómatas y Lenguajes  |  2026\n\n"
            "OBJETIVO:\n"
            "  Analizar lexicamente codigo fuente usando expresiones\n"
            "  regulares y una representacion academica de AFN y AFD.\n\n"
            "TOKENS PRINCIPALES DEL PROYECTO:\n"
            "  KW, ID, NUM, OP, DELIM, comentarios de linea y bloque.\n"
            "  Adicionalmente se admite STRING como apoyo para ejemplos.\n\n"
            "ATAJOS DE TECLADO:\n"
            "  Ctrl + N   →   Nuevo archivo\n"
            "  Ctrl + A   →   Abrir archivo\n"
            "  Ctrl + G   →   Guardar\n"
            "  F5         →   Compilar\n\n"
            "BOTONES:\n"
            "  [Nuevo]    Crear archivo en blanco (modo edición)\n"
            "  [Abrir]    Cargar archivo *.C (solo lectura)\n"
            "  [Guardar]  Guardar archivo actual\n"
            "  [Editar]   Habilitar edición del archivo abierto\n"
            "  [Compilar] Ejecutar analisis lexico y reporte AFN/AFD\n"
            "  [Ayuda]    Mostrar esta ventana\n"
            "  [Salir]    Cerrar la aplicación\n\n"
            "SALIDA DEL ANALISIS:\n"
            "  1. Definicion formal de tokens\n"
            "  2. Diagramas textuales de AFN y AFD\n"
            "  3. Tabla de tokens reconocidos\n"
            "  4. Reporte de errores lexicos\n"
            "  5. Evaluacion del diseno"
        )

        txt = scrolledtext.ScrolledText(ayuda_win, bg=BG_EDITOR, fg=FG_WHITE,
                                        font=FONT_CODE, relief="flat",
                                        padx=16, pady=12, state="normal")
        txt.pack(fill="both", expand=True, padx=12, pady=(0, 12))
        txt.insert("1.0", texto)
        txt.config(state="disabled")

    def _acerca_de(self):
        messagebox.showinfo(
            "Acerca de MicroC",
            "MicroC Pre-Compilador\n"
            "Universidad Mesoamericana\n"
            "Facultad de Ingeniería — Ing. Sistemas\n"
            "Curso: Autómatas y Lenguajes\n"
            "Catedrático: Ing. Baudilio Boteo\n\n"
            "Version 2.0  •  2026\n"
            "Analizador lexico con ER, AFN y AFD")

    def _salir(self):
        """Cerrar la aplicación con confirmación si hay cambios sin guardar."""
        if self.is_modified:
            resp = messagebox.askyesnocancel(
                "Salir",
                "Hay cambios sin guardar.\n¿Desea guardar antes de salir?")
            if resp is None:
                return          # Cancelar cierre
            if resp:
                self._guardar()
        self.root.destroy()


# ──────────────────────────────────────────────
#  Entry point
# ──────────────────────────────────────────────
if __name__ == "__main__":
    root = tk.Tk()
    try:
        root.iconbitmap("microc.ico")  # opcional, si tienes ícono
    except Exception:
        pass
    app = MicroCCompiler(root)
    root.mainloop()
