"""
MicroC Pre-Compilador
Universidad Mesoamericana - Ingeniería en Sistemas
Curso: Autómatas y Lenguajes - 2026
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import os


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
        """Compilar el código (placeholder — próximas entregas)."""
        content = self.editor.get("1.0", "end-1c").strip()
        if not content:
            self._write_output("⚠️ No hay código para compilar.\n", "warning")
            return

        self.output.config(state="normal")
        self.output.delete("1.0", "end")
        self._append_output("══════════════════════════════════════\n", "gray")
        self._append_output("   MicroC Compiler v1.0\n", "info")
        self._append_output("══════════════════════════════════════\n", "gray")
        self._append_output("⏳ Iniciando compilación...\n\n", "info")

        archivo = self.current_file if self.current_file else "[Sin título]"
        self._append_output(f"📄 Archivo: {archivo}\n", "gray")
        self._append_output(f"📏 Líneas : {content.count(chr(10))+1}\n\n", "gray")
        self._append_output(
            "[Compilación en desarrollo]\n"
            "Esta función estará disponible en próximas entregas.\n", "warning")
        self._append_output("\n══════════════════════════════════════\n", "gray")

    def _ayuda(self):
        """Mostrar documentación (placeholder — próximas entregas)."""
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
            "  [Compilar] Compilar código MicroC (en desarrollo)\n"
            "  [Ayuda]    Mostrar esta ventana\n"
            "  [Salir]    Cerrar la aplicación\n\n"
            "La documentación completa estará disponible en próximas entregas."
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
            "Versión 1.0  •  2026")

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
