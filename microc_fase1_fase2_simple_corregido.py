"""
MicroC Pre-Compilador
Universidad Mesoamericana - Ingenieria en Sistemas
Curso: Automatas y Lenguajes - 2026

Fase 1 y Fase 2
Analizador lexico simple estilo estudiante
"""

import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
import os


BG_DARK = "#1e1e1e"
BG_EDITOR = "#252526"
BG_OUTPUT = "#1a1a2e"
FG_WHITE = "#d4d4d4"
FG_GREEN = "#4ec94e"
FG_YELLOW = "#dcdcaa"
FG_BLUE = "#569cd6"
FG_RED = "#f44747"
FG_GRAY = "#808080"
ACCENT = "#007acc"
MENUBAR = "#2d2d30"
FONT_CODE = ("Consolas", 11)
FONT_UI = ("Segoe UI", 10)
FONT_TITLE = ("Segoe UI", 10, "bold")


class UnidadesLexicas:
    def __init__(self):
        self.Palabra = {
            "auto": 1,
            "break": 2,
            "case": 3,
            "char": 4,
            "const": 5,
            "continue": 6,
            "default": 7,
            "do": 8,
            "double": 9,
            "else": 10,
            "enum": 11,
            "extern": 12,
            "float": 13,
            "for": 14,
            "goto": 15,
            "if": 16,
            "int": 17,
            "long": 18,
            "register": 19,
            "return": 20,
            "short": 21,
            "signed": 22,
            "sizeof": 23,
            "static": 24,
            "struct": 25,
            "switch": 26,
            "typedef": 27,
            "union": 28,
            "unsigned": 29,
            "void": 30,
            "volatile": 31,
            "while": 32,
            "include": 33,
            "define": 34,
            "printf": 35,
            "scanf": 36,
            "main": 37,
        }

        self.Simbolo = {
            "(": 75,
            ")": 76,
            "{": 77,
            "}": 78,
            "[": 79,
            "]": 80,
            "+": 81,
            "-": 82,
            "*": 83,
            "/": 84,
            "%": 85,
            "=": 86,
            "==": 87,
            "!=": 88,
            "<": 89,
            ">": 90,
            "<=": 91,
            ";": 92,
            ">=": 93,
            "&&": 94,
            "||": 95,
            "!": 96,
            ",": 97,
            ".": 98,
            "#": 99,
            "++": 100,
            "--": 101,
            "+=": 102,
            "-=": 103,
            "*=": 104,
            "/=": 105,
            "%=": 106,
            "&": 107,
            "|": 108,
            "^": 109,
            "~": 110,
            "?": 111,
            ":": 112,
            "<<": 114,
            ">>": 115,
            "&=": 116,
            "|=": 117,
            "^=": 118,
            "->": 119,
        }

        self.TokensEspeciales = {
            "IDENTIFICADOR": 300,
            "ENTERO": 301,
            "REAL": 302,
            "STRING": 303,
            "CHAR": 304,
            "COMENTARIO_LINEA": 305,
            "COMENTARIO_BLOQUE": 306,
            "LIBRERIA": 307,
            "ERROR_SIMBOLO": -1,
            "ERROR_COMENTARIO": -2,
            "ERROR_STRING": -3,
            "ERROR_CHAR": -4,
            "ERROR_NUMERO": -5,
        }

    def GetTokenPalabra(self, Lexema):
        if Lexema in self.Palabra:
            return self.Palabra[Lexema]
        return self.TokensEspeciales["IDENTIFICADOR"]

    def GetTokenSimbolo(self, Lexema):
        if Lexema in self.Simbolo:
            return self.Simbolo[Lexema]
        return -1

    def GetTokenEspecial(self, nombre):
        return self.TokensEspeciales.get(nombre, -1)


class AnalizadorLexico:
    def __init__(self):
        self.Lista = []
        self.TablaSimbolos = []
        self.Errores = []
        self.cont = 0
        self.Linea = 1
        self.UL = UnidadesLexicas()

        self.tipos_dato = {
            "int", "float", "double", "char", "long", "short"
        }

    def GetAlfabetoAlfanumerico(self, c):
        if c.isalpha() or c == "_":
            return 1
        if c.isdigit():
            return 2
        return 0

    def GetAlfabetoNumero(self, c):
        if c.isdigit():
            return 1
        if c == ".":
            return 2
        if c in "eE":
            return 3
        if c in "+-":
            return 4
        return 0

    def GetAlfabetoSimbolo(self, c):
        simbolos = "(){}[]+-*/%=!<>&|^~?:;,.#"
        if c in simbolos:
            return 1
        return 0

    def agregar_token(self, linea, lexema, token, tipo):
        self.Lista.append({
            "linea": linea,
            "lexema": lexema,
            "token": token,
            "tipo": tipo,
        })

    def agregar_error(self, linea, lexema, mensaje, token_error=None):
        if token_error is None:
            if "bloque sin cerrar" in mensaje:
                token_error = -2
            elif "String sin cerrar" in mensaje:
                token_error = -3
            elif "Caracter sin cerrar" in mensaje:
                token_error = -4
            elif "mal formado" in mensaje:
                token_error = -5
            else:
                token_error = -1

        self.Errores.append({
            "linea": linea,
            "lexema": lexema,
            "mensaje": mensaje,
            "token": token_error,
        })

        self.agregar_token(linea, lexema, token_error, "ERROR")

    def buscar_tabla_simbolos(self, nombre):
        for item in self.TablaSimbolos:
            if item["nombre"] == nombre:
                return True
        return False

    def agregar_tabla_simbolos(self, nombre, tipo, linea):
        if not self.buscar_tabla_simbolos(nombre):
            self.TablaSimbolos.append({
                "nombre": nombre,
                "tipo": tipo,
                "linea": linea,
            })

    def IdentificadorPalabraReservada(self, Archivo):
        linea_inicio = self.Linea
        lexema = ""

        while self.cont < len(Archivo):
            c = Archivo[self.cont]

            if c.isalnum() or c == "_":
                lexema += c
                self.cont += 1
            else:
                break

        token = self.UL.GetTokenPalabra(lexema)

        if token == 300:
            self.agregar_token(linea_inicio, lexema, token, "IDENTIFICADOR")
        else:
            self.agregar_token(linea_inicio, lexema, token, "PALABRA_RESERVADA")

        return lexema

    def EnteroReal(self, Archivo):
        linea_inicio = self.Linea
        lexema = ""
        tiene_punto = False
        tiene_exponente = False
        error = False

        if self.cont < len(Archivo) and Archivo[self.cont] == "-":
            if self.cont + 1 < len(Archivo) and Archivo[self.cont + 1].isdigit():
                lexema += "-"
                self.cont += 1

        while self.cont < len(Archivo):
            c = Archivo[self.cont]

            if c.isdigit():
                lexema += c
                self.cont += 1

            elif c == ".":
                if tiene_punto or tiene_exponente:
                    error = True
                    lexema += c
                    self.cont += 1

                    while self.cont < len(Archivo) and (
                        Archivo[self.cont].isalnum() or Archivo[self.cont] == "."
                    ):
                        lexema += Archivo[self.cont]
                        self.cont += 1
                    break

                tiene_punto = True
                lexema += c
                self.cont += 1

            elif c in "eE":
                if tiene_exponente:
                    error = True
                    lexema += c
                    self.cont += 1
                    break

                tiene_exponente = True
                lexema += c
                self.cont += 1

                if self.cont < len(Archivo) and Archivo[self.cont] in "+-":
                    lexema += Archivo[self.cont]
                    self.cont += 1

                if self.cont >= len(Archivo) or not Archivo[self.cont].isdigit():
                    error = True
                    break

            else:
                break

        if (
            lexema.endswith("e") or lexema.endswith("E")
            or lexema.endswith("e+") or lexema.endswith("e-")
            or lexema.endswith("E+") or lexema.endswith("E-")
        ):
            error = True

        if error:
            self.agregar_error(
                linea_inicio,
                lexema,
                "Numero mal formado",
                self.UL.GetTokenEspecial("ERROR_NUMERO")
            )
        else:
            if tiene_punto or tiene_exponente:
                self.agregar_token(
                    linea_inicio,
                    lexema,
                    self.UL.GetTokenEspecial("REAL"),
                    "REAL"
                )
            else:
                self.agregar_token(
                    linea_inicio,
                    lexema,
                    self.UL.GetTokenEspecial("ENTERO"),
                    "ENTERO"
                )

        return lexema

    def AutomataComentario(self, Archivo):
        linea_inicio = self.Linea
        lexema = ""

        if self.cont + 1 < len(Archivo) and Archivo[self.cont:self.cont + 2] == "//":
            while self.cont < len(Archivo) and Archivo[self.cont] != "\n":
                lexema += Archivo[self.cont]
                self.cont += 1

            self.agregar_token(
                linea_inicio,
                lexema,
                self.UL.GetTokenEspecial("COMENTARIO_LINEA"),
                "COMENTARIO_LINEA"
            )
            return lexema

        if self.cont + 1 < len(Archivo) and Archivo[self.cont:self.cont + 2] == "/*":
            lexema += "/*"
            self.cont += 2
            cerrado = False

            while self.cont < len(Archivo):
                if self.cont + 1 < len(Archivo) and Archivo[self.cont:self.cont + 2] == "*/":
                    lexema += "*/"
                    self.cont += 2
                    cerrado = True
                    break

                if Archivo[self.cont] == "\n":
                    self.Linea += 1

                lexema += Archivo[self.cont]
                self.cont += 1

            if cerrado:
                self.agregar_token(
                    linea_inicio,
                    lexema,
                    self.UL.GetTokenEspecial("COMENTARIO_BLOQUE"),
                    "COMENTARIO_BLOQUE"
                )
            else:
                self.agregar_error(
                    linea_inicio,
                    lexema,
                    "Comentario de bloque sin cerrar",
                    self.UL.GetTokenEspecial("ERROR_COMENTARIO")
                )

            return lexema

        return ""

    def AutomataString(self, Archivo):
        linea_inicio = self.Linea
        lexema = "\""
        self.cont += 1
        cerrado = False

        while self.cont < len(Archivo):
            c = Archivo[self.cont]

            if c == "\n":
                self.Linea += 1
                self.cont += 1
                self.agregar_error(
                    linea_inicio,
                    lexema,
                    "String sin cerrar",
                    self.UL.GetTokenEspecial("ERROR_STRING")
                )
                return lexema

            if c == "\\" and self.cont + 1 < len(Archivo):
                lexema += c + Archivo[self.cont + 1]
                self.cont += 2
                continue

            lexema += c
            self.cont += 1

            if c == "\"":
                cerrado = True
                break

        if cerrado:
            self.agregar_token(
                linea_inicio,
                lexema,
                self.UL.GetTokenEspecial("STRING"),
                "STRING"
            )
        else:
            self.agregar_error(
                linea_inicio,
                lexema,
                "String sin cerrar",
                self.UL.GetTokenEspecial("ERROR_STRING")
            )

        return lexema

    def AutomataChar(self, Archivo):
        linea_inicio = self.Linea
        lexema = "'"
        self.cont += 1
        cerrado = False

        while self.cont < len(Archivo):
            c = Archivo[self.cont]

            if c == "\n":
                self.Linea += 1
                self.cont += 1
                self.agregar_error(
                    linea_inicio,
                    lexema,
                    "Caracter sin cerrar",
                    self.UL.GetTokenEspecial("ERROR_CHAR")
                )
                return lexema

            if c == "\\" and self.cont + 1 < len(Archivo):
                lexema += c + Archivo[self.cont + 1]
                self.cont += 2
                continue

            lexema += c
            self.cont += 1

            if c == "'":
                cerrado = True
                break

        if cerrado:
            self.agregar_token(
                linea_inicio,
                lexema,
                self.UL.GetTokenEspecial("CHAR"),
                "CHAR"
            )
        else:
            self.agregar_error(
                linea_inicio,
                lexema,
                "Caracter sin cerrar",
                self.UL.GetTokenEspecial("ERROR_CHAR")
            )

        return lexema

    def AutomataLibreria(self, Archivo):
        linea_inicio = self.Linea
        lexema = ""
        self.cont += 1
        cerrado = False

        while self.cont < len(Archivo):
            c = Archivo[self.cont]

            if c == "\n":
                self.Linea += 1
                self.agregar_error(
                    linea_inicio,
                    lexema,
                    "Libreria sin cerrar",
                    self.UL.GetTokenEspecial("ERROR_SIMBOLO")
                )
                return lexema

            if c == ">":
                self.cont += 1
                cerrado = True
                break

            lexema += c
            self.cont += 1

        if cerrado:
            self.agregar_token(
                linea_inicio,
                lexema,
                self.UL.GetTokenEspecial("LIBRERIA"),
                "LIBRERIA"
            )
        else:
            self.agregar_error(
                linea_inicio,
                lexema,
                "Libreria sin cerrar",
                self.UL.GetTokenEspecial("ERROR_SIMBOLO")
            )

        return lexema

    def leer_simbolo(self, Archivo):
        linea_inicio = self.Linea

        if self.cont + 1 < len(Archivo):
            lexema2 = Archivo[self.cont:self.cont + 2]
            if lexema2 in self.UL.Simbolo:
                self.cont += 2
                self.agregar_token(
                    linea_inicio,
                    lexema2,
                    self.UL.GetTokenSimbolo(lexema2),
                    "SIMBOLO"
                )
                return lexema2

        lexema = Archivo[self.cont]
        token = self.UL.GetTokenSimbolo(lexema)
        self.cont += 1

        if token != -1:
            self.agregar_token(linea_inicio, lexema, token, "SIMBOLO")
        else:
            self.agregar_error(
                linea_inicio,
                lexema,
                "Simbolo no permitido",
                self.UL.GetTokenEspecial("ERROR_SIMBOLO")
            )

        return lexema

    def construir_tabla_simbolos(self):
        self.TablaSimbolos = []

        TIPOS_DATO = ["int", "float", "double", "char", "long", "short"]

        lineas_con_error = set()

        for error in self.Errores:
            lineas_con_error.add(error["linea"])

        for i in range(len(self.Lista) - 1):
            actual = self.Lista[i]
            siguiente = self.Lista[i + 1]

            if actual["lexema"] in TIPOS_DATO and siguiente["token"] == 300:
                if actual["linea"] in lineas_con_error:
                    continue

                self.agregar_tabla_simbolos(
                    siguiente["lexema"],
                    actual["lexema"],
                    siguiente["linea"]
                )

    def AnalisisLexico(self, Archivo):
        self.Lista = []
        self.TablaSimbolos = []
        self.Errores = []
        self.cont = 0
        self.Linea = 1

        while self.cont < len(Archivo):
            c = Archivo[self.cont]

            if c == "\n":
                self.Linea += 1
                self.cont += 1
                continue

            if c in " \t\r":
                self.cont += 1
                continue

            if c.isalpha() or c == "_":
                self.IdentificadorPalabraReservada(Archivo)
                continue

            if c.isdigit():
                self.EnteroReal(Archivo)
                continue

            if c == "-" and self.cont + 1 < len(Archivo) and Archivo[self.cont + 1].isdigit():
                self.EnteroReal(Archivo)
                continue

            if c == "/" and self.cont + 1 < len(Archivo) and Archivo[self.cont + 1] in "/*":
                self.AutomataComentario(Archivo)
                continue

            if c == "\"":
                self.AutomataString(Archivo)
                continue

            if c == "'":
                self.AutomataChar(Archivo)
                continue

            if c == "<" and self._viene_de_include():
                self.AutomataLibreria(Archivo)
                continue

            if self.GetAlfabetoSimbolo(c):
                self.leer_simbolo(Archivo)
                continue

            self.agregar_error(
                self.Linea,
                c,
                "Simbolo no permitido",
                self.UL.GetTokenEspecial("ERROR_SIMBOLO")
            )
            self.cont += 1

        self.construir_tabla_simbolos()
        return self.Lista

    def _viene_de_include(self):
        ultimos = self.Lista[-3:]

        for item in ultimos:
            if item["lexema"] == "include":
                return True

        return False

    def ObtenerSalidaTokens(self):
        salida = ""

        for item in self.Lista:
            salida += (
                f"Linea: {item['linea']:<4} "
                f"Lexema: {item['lexema']:<20} "
                f"Token: {item['token']:<5} "
                f"Tipo: {item['tipo']}\n"
            )

        return salida

    def ObtenerSalidaTablaSimbolos(self):
        if not self.TablaSimbolos:
            return "No se encontraron variables declaradas.\n"

        salida = "nombre              | tipo       | linea\n"
        salida += "----------------------------------------\n"

        for item in self.TablaSimbolos:
            salida += (
                f"{item['nombre']:<19} | "
                f"{item['tipo']:<10} | "
                f"{item['linea']}\n"
            )

        return salida

    def ObtenerSalidaErrores(self):
        if not self.Errores:
            return "No se encontraron errores lexicos.\n"

        salida = ""

        for error in self.Errores:
            salida += (
                f"Linea: {error['linea']} | "
                f"Lexema: {error['lexema']} | "
                f"Token: {error['token']} | "
                f"Error: {error['mensaje']}\n"
            )

        return salida


class Frame:
    def __init__(self, root):
        self.root = root
        self.root.title("MicroC Compiler - [Sin titulo]")
        self.root.geometry("1100x680")
        self.root.minsize(800, 500)
        self.root.configure(bg=BG_DARK)

        self.Archivo = None
        self.is_modified = False
        self.is_new_file = True

        self._build_menu()
        self._build_toolbar()
        self._build_body()
        self._build_statusbar()

        self.root.protocol("WM_DELETE_WINDOW", self.OpcSalir_Click)

    def _build_menu(self):
        menubar = tk.Menu(
            self.root,
            bg=MENUBAR,
            fg=FG_WHITE,
            activebackground=ACCENT,
            activeforeground=FG_WHITE
        )
        self.root.config(menu=menubar)

        archivo_menu = tk.Menu(
            menubar,
            tearoff=0,
            bg=MENUBAR,
            fg=FG_WHITE,
            activebackground=ACCENT,
            activeforeground=FG_WHITE
        )

        archivo_menu.add_command(label="Nuevo        Ctrl+N", command=self.OpcNuevo_Click)
        archivo_menu.add_command(label="Abrir...     Ctrl+A", command=self.OpcAbrir_Click)
        archivo_menu.add_command(label="Guardar      Ctrl+G", command=self.OpcGuardar_Click)
        archivo_menu.add_command(label="Guardar como...", command=self.OpcGuardarComo_Click)
        archivo_menu.add_separator()
        archivo_menu.add_command(label="Salir        Alt+F4", command=self.OpcSalir_Click)
        menubar.add_cascade(label="Archivo", menu=archivo_menu)

        editar_menu = tk.Menu(
            menubar,
            tearoff=0,
            bg=MENUBAR,
            fg=FG_WHITE,
            activebackground=ACCENT,
            activeforeground=FG_WHITE
        )

        editar_menu.add_command(label="Habilitar edición", command=self.OpcEditar_Click)
        menubar.add_cascade(label="Editar", menu=editar_menu)

        compilar_menu = tk.Menu(
            menubar,
            tearoff=0,
            bg=MENUBAR,
            fg=FG_WHITE,
            activebackground=ACCENT,
            activeforeground=FG_WHITE
        )

        compilar_menu.add_command(label="Compilar   F5", command=self.OpcCompliar_Click)
        menubar.add_cascade(label="Compilar", menu=compilar_menu)

        ayuda_menu = tk.Menu(
            menubar,
            tearoff=0,
            bg=MENUBAR,
            fg=FG_WHITE,
            activebackground=ACCENT,
            activeforeground=FG_WHITE
        )

        ayuda_menu.add_command(label="Documentación", command=self.OpcAyuda_Click)
        ayuda_menu.add_command(label="Acerca de...", command=self.OpcAcercaDe_Click)
        menubar.add_cascade(label="Ayuda", menu=ayuda_menu)

        self.root.bind("<Control-n>", lambda e: self.OpcNuevo_Click())
        self.root.bind("<Control-a>", lambda e: self.OpcAbrir_Click())
        self.root.bind("<Control-g>", lambda e: self.OpcGuardar_Click())
        self.root.bind("<F5>", lambda e: self.OpcCompliar_Click())

    def _build_toolbar(self):
        toolbar = tk.Frame(self.root, bg=MENUBAR, pady=4, padx=6)
        toolbar.pack(side="top", fill="x")

        btn_cfg = dict(
            bg="#3c3c3c",
            fg=FG_WHITE,
            relief="flat",
            activebackground=ACCENT,
            activeforeground=FG_WHITE,
            font=FONT_UI,
            padx=10,
            pady=3,
            cursor="hand2",
            bd=0
        )

        buttons = [
            ("Nuevo", self.OpcNuevo_Click),
            ("Abrir", self.OpcAbrir_Click),
            ("Guardar", self.OpcGuardar_Click),
            ("Editar", self.OpcEditar_Click),
            ("Compilar", self.OpcCompliar_Click),
            ("Ayuda", self.OpcAyuda_Click),
            ("Salir", self.OpcSalir_Click),
        ]

        for label, cmd in buttons:
            btn = tk.Button(toolbar, text=label, command=cmd, **btn_cfg)
            btn.pack(side="left", padx=2)
            btn.bind("<Enter>", lambda e, b=btn: b.config(bg=ACCENT))
            btn.bind("<Leave>", lambda e, b=btn: b.config(bg="#3c3c3c"))

    def _build_body(self):
        paned = tk.PanedWindow(self.root, orient="horizontal", bg=BG_DARK, sashwidth=5)
        paned.pack(fill="both", expand=True, padx=6, pady=4)

        left_frame = tk.Frame(paned, bg=BG_DARK)
        paned.add(left_frame, minsize=300)

        lbl_editor = tk.Label(
            left_frame,
            text=" Codigo MicroC",
            bg=ACCENT,
            fg=FG_WHITE,
            font=FONT_TITLE,
            anchor="w",
            padx=6,
            pady=3
        )
        lbl_editor.pack(fill="x")

        edit_container = tk.Frame(left_frame, bg=BG_EDITOR)
        edit_container.pack(fill="both", expand=True)

        self.line_numbers = tk.Text(
            edit_container,
            width=4,
            bg="#1e1e1e",
            fg=FG_GRAY,
            font=FONT_CODE,
            state="disabled",
            relief="flat",
            padx=4,
            pady=6
        )
        self.line_numbers.pack(side="left", fill="y")

        self.editor = scrolledtext.ScrolledText(
            edit_container,
            wrap="none",
            bg=BG_EDITOR,
            fg=FG_WHITE,
            insertbackground=FG_WHITE,
            font=FONT_CODE,
            relief="flat",
            padx=8,
            pady=6,
            state="disabled",
            undo=True
        )
        self.editor.pack(side="left", fill="both", expand=True)
        self.editor.bind("<KeyRelease>", self._on_key_release)
        self.editor.bind("<ButtonRelease>", self._on_key_release)

        right_frame = tk.Frame(paned, bg=BG_DARK)
        paned.add(right_frame, minsize=250)

        lbl_output = tk.Label(
            right_frame,
            text=" Resultados de Compilacion",
            bg="#16825d",
            fg=FG_WHITE,
            font=FONT_TITLE,
            anchor="w",
            padx=6,
            pady=3
        )
        lbl_output.pack(fill="x")

        self.output = scrolledtext.ScrolledText(
            right_frame,
            wrap="word",
            bg=BG_OUTPUT,
            fg=FG_GREEN,
            insertbackground=FG_WHITE,
            font=FONT_CODE,
            relief="flat",
            padx=8,
            pady=6,
            state="disabled"
        )
        self.output.pack(fill="both", expand=True)

        self.output.tag_config("error", foreground=FG_RED)
        self.output.tag_config("success", foreground=FG_GREEN)
        self.output.tag_config("info", foreground=FG_BLUE)
        self.output.tag_config("warning", foreground=FG_YELLOW)
        self.output.tag_config("gray", foreground=FG_GRAY)

        self._update_line_numbers()

    def _build_statusbar(self):
        status_frame = tk.Frame(self.root, bg=ACCENT, pady=2)
        status_frame.pack(side="bottom", fill="x")

        self.status_var = tk.StringVar(value="Listo | Nuevo archivo")
        status_lbl = tk.Label(
            status_frame,
            textvariable=self.status_var,
            bg=ACCENT,
            fg=FG_WHITE,
            font=FONT_UI,
            anchor="w"
        )
        status_lbl.pack(side="left", padx=8)

        self.cursor_var = tk.StringVar(value="Ln 1, Col 1")
        cursor_lbl = tk.Label(
            status_frame,
            textvariable=self.cursor_var,
            bg=ACCENT,
            fg=FG_WHITE,
            font=FONT_UI,
            anchor="e"
        )
        cursor_lbl.pack(side="right", padx=8)

    def _set_editor_state(self, editable):
        if editable:
            self.editor.config(state="normal")
        else:
            self.editor.config(state="disabled")

    def _write_output(self, text, tag=""):
        self.output.config(state="normal")
        self.output.delete("1.0", "end")

        if tag:
            self.output.insert("end", text, tag)
        else:
            self.output.insert("end", text)

        self.output.config(state="disabled")

    def _append_output(self, text, tag=""):
        self.output.config(state="normal")

        if tag:
            self.output.insert("end", text, tag)
        else:
            self.output.insert("end", text)

        self.output.see("end")
        self.output.config(state="disabled")

    def _update_title(self):
        nombre = os.path.basename(self.Archivo) if self.Archivo else "[Sin titulo]"
        mod = " *" if self.is_modified else ""
        self.root.title(f"MicroC Compiler - {nombre}{mod}")

        estado = "Modificado" if self.is_modified else "Guardado"
        self.status_var.set(f"{estado} | {nombre}")

    def _update_line_numbers(self):
        self.line_numbers.config(state="normal")
        self.line_numbers.delete("1.0", "end")

        content = self.editor.get("1.0", "end-1c")
        lines = content.count("\n") + 1
        numbers = "\n".join(str(i) for i in range(1, lines + 1))

        self.line_numbers.insert("1.0", numbers)
        self.line_numbers.config(state="disabled")

    def _on_key_release(self, event=None):
        self._update_line_numbers()

        pos = self.editor.index("insert").split(".")
        self.cursor_var.set(f"Ln {pos[0]}, Col {int(pos[1]) + 1}")

        if not self.is_modified:
            self.is_modified = True
            self._update_title()

    def OpcNuevo_Click(self):
        if self.is_modified:
            resp = messagebox.askyesnocancel(
                "Guardar cambios",
                "Hay cambios sin guardar. Desea guardar?"
            )

            if resp is None:
                return

            if resp:
                self.OpcGuardar_Click()

        self._set_editor_state(True)
        self.editor.delete("1.0", "end")
        self.Archivo = None
        self.is_new_file = True
        self.is_modified = False
        self._update_title()
        self._update_line_numbers()
        self._write_output("Nuevo archivo creado.\n", "info")
        self.editor.focus_set()

    def OpcAbrir_Click(self):
        if self.is_modified:
            resp = messagebox.askyesnocancel(
                "Guardar cambios",
                "Hay cambios sin guardar. Desea guardar?"
            )

            if resp is None:
                return

            if resp:
                self.OpcGuardar_Click()

        filepath = filedialog.askopenfilename(
            title="Abrir archivo MicroC",
            filetypes=[
                ("Archivos C", "*.c *.C *.h"),
                ("Todos los archivos", "*.*")
            ]
        )

        if not filepath:
            return

        try:
            with open(filepath, "r", encoding="utf-8") as f:
                content = f.read()

            self._set_editor_state(True)
            self.editor.delete("1.0", "end")
            self.editor.insert("1.0", content)
            self._set_editor_state(False)

            self.Archivo = filepath
            self.is_new_file = False
            self.is_modified = False
            self._update_title()
            self._update_line_numbers()

            self._write_output(
                f"Archivo abierto en modo solo lectura:\n{filepath}\n"
                "Presione Editar para modificar.\n",
                "info"
            )

        except Exception as e:
            messagebox.showerror("Error al abrir", str(e))

    def OpcGuardar_Click(self):
        if self.is_new_file or self.Archivo is None:
            self.OpcGuardarComo_Click()
        else:
            self._escribir_archivo(self.Archivo)

    def OpcGuardarComo_Click(self):
        filepath = filedialog.asksaveasfilename(
            title="Guardar archivo MicroC",
            defaultextension=".c",
            filetypes=[
                ("Archivos C", "*.c *.C *.h"),
                ("Todos los archivos", "*.*")
            ]
        )

        if filepath:
            self._escribir_archivo(filepath)
            self.Archivo = filepath
            self.is_new_file = False
            self._update_title()

    def _escribir_archivo(self, filepath):
        try:
            content = self.editor.get("1.0", "end-1c")

            with open(filepath, "w", encoding="utf-8") as f:
                f.write(content)

            self.is_modified = False
            self._update_title()
            self._write_output(f"Archivo guardado:\n{filepath}\n", "success")

        except Exception as e:
            messagebox.showerror("Error al guardar", str(e))

    def OpcEditar_Click(self):
        self._set_editor_state(True)
        self._write_output("Modo edicion habilitado.\n", "warning")
        self.editor.focus_set()

    def OpcCompliar_Click(self):
        Archivo = self.editor.get("1.0", "end-1c")

        if not Archivo.strip():
            self._write_output("No hay codigo para compilar.\n", "warning")
            return

        AL = AnalizadorLexico()
        ListaToken = AL.AnalisisLexico(Archivo)

        self.output.config(state="normal")
        self.output.delete("1.0", "end")
        self.output.config(state="disabled")

        self._append_output("══════════════════════════════════════\n", "gray")
        self._append_output("   ANALISIS LEXICO MICROC - LENGUAJE C\n", "info")
        self._append_output("══════════════════════════════════════\n\n", "gray")

        self._append_output("LISTA DE TOKENS\n", "success")
        self._append_output(AL.ObtenerSalidaTokens())

        self._append_output("\nTABLA DE SIMBOLOS\n", "info")
        self._append_output(AL.ObtenerSalidaTablaSimbolos())

        self._append_output("\nERRORES LEXICOS\n", "warning")

        if AL.Errores:
            self._append_output(AL.ObtenerSalidaErrores(), "error")
        else:
            self._append_output(AL.ObtenerSalidaErrores(), "success")

        self._append_output("\nRESUMEN\n", "gray")
        self._append_output(f"Total de tokens: {len(ListaToken)}\n")
        self._append_output(
            f"Variables en tabla de simbolos: {len(AL.TablaSimbolos)}\n"
        )
        self._append_output(f"Errores lexicos: {len(AL.Errores)}\n")
        self._append_output("\nFin analisis lexico.\n", "success")

    def OpcAyuda_Click(self):
        texto = (
            "MicroC Pre-Compilador\n\n"
            "Fase 1 y Fase 2\n"
            "Lenguaje aceptado: C\n\n"
            "- Genera lista de tokens\n"
            "- Elimina espacios, tabuladores y saltos de linea durante el analisis\n"
            "- Relaciona tokens con lineas\n"
            "- Identifica lexemas simples\n"
            "- Identifica palabras reservadas de C\n"
            "- Identifica numeros enteros, reales, negativos y exponentes\n"
            "- Identifica comentarios de linea y bloque\n"
            "- Identifica strings, chars y librerias\n"
            "- Genera tabla de simbolos basica\n"
        )

        messagebox.showinfo("Ayuda", texto)

    def OpcAcercaDe_Click(self):
        messagebox.showinfo(
            "Acerca de",
            "MicroC Pre-Compilador\n"
            "Universidad Mesoamericana\n"
            "Curso: Automatas y Lenguajes\n"
            "Version Fase 1 y 2 - Lenguaje C"
        )

    def OpcSalir_Click(self):
        if self.is_modified:
            resp = messagebox.askyesnocancel(
                "Salir",
                "Hay cambios sin guardar. Desea guardar?"
            )

            if resp is None:
                return

            if resp:
                self.OpcGuardar_Click()

        self.root.destroy()


if __name__ == "__main__":
    root = tk.Tk()
    app = Frame(root)
    root.mainloop()