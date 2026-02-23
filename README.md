# MicroC Pre-Compilador
**Universidad Mesoamericana | Autómatas y Lenguajes 2026**

---

## 📋 Requisitos

| Herramienta | Versión mínima |
|-------------|---------------|
| Python      | 3.10+         |
| tkinter     | incluido en Python (viene por defecto) |
| VS Code     | cualquier versión reciente |

> **No necesitas instalar librerías externas.** El proyecto usa solo `tkinter` que viene incluido con Python.

---

## 🚀 Cómo ejecutar

### Opción 1 — Desde la terminal de VS Code
```bash
# 1. Abre VS Code en la carpeta del proyecto
code .

# 2. Abre la terminal integrada (Ctrl + `)

# 3. Ejecuta
python microc.py
```

### Opción 2 — Botón ▶ de VS Code
1. Abre `microc.py` en VS Code
2. Presiona `F5` o el botón ▶ (Run Python File)

---

## 📁 Estructura del proyecto
```
microc_compiler/
│
├── microc.py        ← Aplicación principal (todo en un archivo)
├── README.md        ← Este archivo
└── prueba.c         ← Archivo de prueba opcional
```

---

## 🖥️ Funciones implementadas

| Botón / Menú | Función |
|---|---|
| 🆕 **Nuevo** | Abre editor en blanco modo edición |
| 📂 **Abrir** | Carga archivo `*.C` en modo solo lectura |
| 💾 **Guardar** | Guarda el archivo (diálogo si es nuevo, sobreescribe si ya existe) |
| ✏️ **Editar** | Habilita edición del archivo abierto |
| ⚙️ **Compilar** | Placeholder — se desarrollará en próximas entregas |
| ❓ **Ayuda** | Ventana con documentación y atajos |
| 🚪 **Salir** | Cierra con aviso si hay cambios sin guardar |

---

## ⌨️ Atajos de teclado

| Atajo | Acción |
|---|---|
| `Ctrl + N` | Nuevo |
| `Ctrl + A` | Abrir |
| `Ctrl + G` | Guardar |
| `F5`       | Compilar |

---

## 📝 Archivo de prueba (prueba.c)

Puedes crear un archivo `prueba.c` con este contenido para probar la aplicación:

```c
int main() {
    int a = 5;
    int b = 10;
    int suma = a + b;

    // Mostrar resultado
    printf("La suma es: %d", suma);

    return 0;
}
```

---

## 🔧 Extensión recomendada para VS Code

Instala la extensión **Python** de Microsoft en VS Code para tener:
- Resaltado de sintaxis
- Autocompletado
- Ejecución directa con F5

---

## 🗺️ Próximas entregas
- Análisis léxico (tokenizador MicroC)
- Análisis sintáctico
- Tabla de símbolos
- Mensajes de error detallados


## 📁 Link del video
```
https://youtu.be/Z9zkh2QzElA
```