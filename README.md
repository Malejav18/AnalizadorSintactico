# 🗂️ Analizador Sintáctico en Python

Integrantes:

- Eduardo Hincapie 
- Josh Lopez 
- Miguel Suarez 
- Maria Alejandra Vargas

El objetivo para este proyecto es tomar un código fuente escrito en python y realizar un análisis sintáctico sobre dicho código. 

Se implementa un programa en Python que recibe un archivo py como entrada y devuelve un archivo txt con el análisis léxico del mismo como salida.

## 🧷 Requerimientos

### Dependencias necesarias

- **Python** (versión 3 o superior)


## 💥 Características

### ✅ Funcionalidades compatibles

Este proyecto admite las siguientes características básicas de Python:

* Asignaciones de variables
* Condicionales (`if`, `else`, `elif`)
* Bucles (`for`, `while`)
* Funciones definidas por el usuario
* Operaciones matemáticas simples
* Listas, diccionarios y tuplas como `x = (1, 2)`
* Uso de `print` para mostrar resultados
* Sentencias de control: `break`, `pass`, `continue`
* Manejo de excepciones: `try`, `except`, `else`, `finally`
* Encadenamiento de métodos: `obj.metodo().metodo2()`
* Uso del constructor `__init__` y `self` en clases
* Acceso a atributos y métodos con notación de punto (`obj.metodo()`, `obj.id`)
* Manejo de cadenas de texto (strings)
* Operadores compuestos (como `+=`, `-=`, etc.)
* Uso de `set()` para crear conjuntos
* Clases simples con `class`, `self` y `__init__`


### ❌ Funcionalidades no compatibles

Las siguientes características **no están soportadas** actualmente:

* Evaluación directa de expresiones como `2 + 3`
* Cadenas formateadas con `f""` (f-strings)
* Listas por comprensión, como: `[x for x in arr if x % 2 == 0]`
* Uso de `super().__init__()` en clases (POO avanzada)
* Uso de `__init__` funciona, pero no puede llamarse directamente


## 👾 Modo de Uso:
1. Descarga los archivos adjuntos.
2. Escribe tu código dentro de "codigo.py", o usa el código de ejemplo.
3. Ejecuta el siguiente comando para el analizador léxico:

```
python3 analizador_lexico.py codigo.py
```

4. Ejecuta el siguiente comando para el analizador sintáctico: 
Como ejemplo prueba tenemos:

```
python3 analizador_sintactico.py codigo.py
```

Codigo.py
```
def contains(items:[int ,]
```

Los resultados del analizador léxico se guardan en el archivo de salida "resultado_lexico.txt"

resultado_lexico.txt
```
<1,24> Error sintactico: se encontro: “,”; se esperaba: “]”.
```
