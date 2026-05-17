# MicroC Pre-Compilador

**Universidad Mesoamericana | Autómatas y Lenguajes 2026**

---

## Requisitos

| Herramienta | Versión mínima |
|-------------|----------------|
| Python | 3.10+ |
| tkinter | incluido en Python |
| VS Code | cualquier versión reciente |

No necesitas instalar librerías externas.


## Cómo ejecutar

```bash
python3 microc.py
```


## Estructura del proyecto

```text
microc_compiler/
│
├── microc.py
├── README.md
└── prueba.c
```

---

## Funciones implementadas

| Botón / Menú | Función |
|---|---|
| Nuevo | Crea archivo nuevo |
| Abrir | Abre archivo `.c` o `.h` |
| Guardar | Guarda el archivo actual |
| Guardar como | Guarda con otro nombre |
| Editar | Habilita edición |
| Compilar | Ejecuta análisis léxico |
| Ayuda | Muestra información del proyecto |
| Salir | Cierra el programa |

---

# Fase 1 implementada

- Genera lista de tokens.
- Elimina espacios en blanco durante el análisis.
- Elimina tabuladores y saltos de línea durante el análisis.
- Relaciona líneas de código con el análisis.
- Identifica lexemas simples y los relaciona con su token.

---

# Fase 2 implementada

- Identifica palabras reservadas del lenguaje C.
- Identifica números enteros.
- Identifica números reales.
- Identifica números negativos.
- Identifica números con exponente.
- Identifica comentarios de línea.
- Identifica comentarios de bloque.
- Identifica strings.
- Identifica caracteres.
- Identifica librerías.

---

# Mejoras agregadas

- Reconoce strings completos como `"Hola"`.
- Reconoce caracteres completos como `'a'`.
- Reconoce librerías completas como `stdio.h`.
- Genera tabla de símbolos dinámica.
- Muestra errores léxicos claros.
- Evita guardar variables con errores léxicos.
- Usa tokens de error separados.
- Reconoce operadores dobles y compuestos.
- Reconoce operadores aritméticos, lógicos y relacionales.
- Reconoce únicamente lenguaje C.

---

# Tabla de tokens especiales

| Token | Descripción |
|---|---|
| 300 | Identificador |
| 301 | Número entero |
| 302 | Número real |
| 303 | String |
| 304 | Char |
| 305 | Comentario de línea |
| 306 | Comentario de bloque |
| 307 | Librería |
| -1 | Símbolo no permitido |
| -2 | Comentario sin cerrar |
| -3 | String sin cerrar |
| -4 | Char sin cerrar |
| -5 | Número mal formado |

---

# Palabras reservadas reconocidas

```text
auto
break
case
char
const
continue
default
do
double
else
enum
extern
float
for
goto
if
int
long
register
return
short
signed
sizeof
static
struct
switch
typedef
union
unsigned
void
volatile
while
include
define
printf
scanf
main
```

---

# Expresiones regulares implementadas

## Palabras reservadas

```regex
(auto|break|case|char|const|continue|default|do|double|else|enum|extern|float|for|goto|if|int|long|register|return|short|signed|sizeof|static|struct|switch|typedef|union|unsigned|void|volatile|while|include|define|printf|scanf|main)
```

---

## Identificadores

```regex
[a-zA-Z_][a-zA-Z0-9_]*
```

---

## Números

```regex
-?[0-9]+(\.[0-9]+)?([eE][+-]?[0-9]+)?
```

---

## Strings

```regex
\"([^\"\\]|\\.)*\"
```

---

## Caracteres

```regex
\'([^\'\\]|\\.)\'
```

---

## Comentarios de línea

```regex
//[^\n]*
```

---

## Comentarios de bloque

```regex
/\*[\s\S]*?\*/
```

---

## Librerías

```regex
[a-zA-Z0-9_]+\.h
```

---

# Símbolos reconocidos

```text
( ) { } [ ]
+ - * / %
= == != < > <= >=
&& ||
!
,
.
#
++
--
+=
-=
*=
/=
%=
&
|
^
~
?
:
<<
>>
&=
|=
^=
->
;
```

---

# Tabla de símbolos

El programa genera una tabla de símbolos básica para variables declaradas.

Ejemplo:

```c
int a = 4;
double x = 3.14;
char letra = 'a';
```

Salida esperada:

```text
nombre              | tipo       | linea
----------------------------------------
a                   | int        | 1
x                   | double     | 2
letra               | char       | 3
```

---

# Errores léxicos detectados

- String sin cerrar.
- Caracter sin cerrar.
- Número mal formado.
- Comentario de bloque sin cerrar.
- Librería sin cerrar.
- Símbolo no permitido.

Ejemplos:

```c
double mal1 = 3.14.5;
double mal2 = 12e;
double mal3 = 12e+;
char mal4 = 'a;
/* comentario sin cerrar
```

---

# Ejemplo de archivo prueba.c

```c
#include <stdio.h>

int main() {

    int a = 4;
    double b = 3.14e10;
    char letra = 'x';

    // comentario de linea

    /*
       comentario
       de bloque
    */

    printf("Hola %d", a);

    if (a <= 10) {
        a++;
        b = b + -5;
    }

    return 0;
}
```

---

# Salida esperada del análisis

El botón **Compilar** muestra:

- Lista de tokens.
- Tabla de símbolos.
- Errores léxicos.
- Resumen del análisis.

Ejemplo:

```text
Linea: 1    Lexema: #                    Token: 99    Tipo: SIMBOLO
Linea: 1    Lexema: include              Token: 33    Tipo: PALABRA_RESERVADA
Linea: 1    Lexema: stdio.h              Token: 307   Tipo: LIBRERIA
Linea: 4    Lexema: int                  Token: 17    Tipo: PALABRA_RESERVADA
Linea: 4    Lexema: a                    Token: 300   Tipo: IDENTIFICADOR
Linea: 4    Lexema: =                    Token: 86    Tipo: SIMBOLO
Linea: 4    Lexema: 4                    Token: 301   Tipo: ENTERO
Linea: 4    Lexema: ;                    Token: 92    Tipo: SIMBOLO
```

---

# Notas importantes

Este proyecto implementa únicamente el análisis léxico.

No realiza todavía:

- Análisis sintáctico.
- Análisis semántico.
- Generación de código.
- Ejecución real del programa.

El compilador está diseñado únicamente para lenguaje C.

---

# Próximas extensiones

- Análisis sintáctico.
- Validación de estructura de instrucciones.
- Tabla de símbolos avanzada.
- Detección de variables no declaradas.
- Validación de tipos de dato.
- Análisis semántico.