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

## 👾 Modo de Uso:
1. Descarga los archivos adjuntos.
2. Escribe tu código dentro de "codigo.py", o usa el código de ejemplo.
3. Ejecuta el siguiente comando:

```
python3 analizador_lexico.py codigo.py
```

Los resultados del analizador léxico se guardan en el archivo de salida "resultado_lexico.txt"

Como ejemplo prueba tenemos:

Codigo.py
```
def contains(items:[int ,]
```

resultado_lexico.txt
```
<1,24> Error sintactico: se encontro: “,”; se esperaba: “]”.
```
