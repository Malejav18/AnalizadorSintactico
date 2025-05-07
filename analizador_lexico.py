import sys
from tokens_palabras import palabras_reservadas_librerias

# Definir los tokens y palabras reservadas
# Cada token tiene asociado su representación en el lenguaje.
char_tokens = {
    'tk_ejecuta': '->', 
    'tk_potencia': '**', 
    'tk_mayor_igual': '>=', 
    'tk_menor_igual': '<=', 
    'tk_igual': '==', 
    'tk_distinto': '!=', 
    'tk_mas_asig': '+=', 
    'tk_menos_asig': '-=', 
    'tk_mult_asig': '*=', 
    'tk_div_asig': '/=', 
    'tk_div_entera': '//',
    'tk_mod_asig': '%=', 
    'tk_amper_asig': '&=', 
    'tk_bar_asig': '|=', 
    'tk_hat_asig': '^=', 
    'tk_menor_menor': '<<',
    'tk_mayor_mayor': '>>',
    'tk_punto_y_coma': ';', 
    'tk_coma': ',', 
    'tk_par_izq': '(', 
    'tk_par_der': ')', 
    'tk_corchete_izq': '[', 
    'tk_corchete_der': ']', 
    'tk_llave_izq': '{', 
    'tk_llave_der': '}', 
    'tk_dos_puntos': ':', 
    'tk_or' : '|', 
    'tk_punto': '.', 
    'tk_asig': '=', 
    'tk_div': '/', 
    'tk_suma': '+', 
    'tk_resta': '-', 
    'tk_mult': '*', 
    'tk_modulo': '%', 
    'tk_mayor': '>', 
    'tk_menor': '<', 
    'tk_arroba': '@',
    'tk_arroba_asig': '@=',
    'tk_comentario': '#', 
    'tk_and': '&', 
    'tk_interrogacion': '?', 
    'tk_tilde': '~', 
    'tk_exclamacion': '!', 
    'tk_xor': '^', 
    'tk_nor': '~',
    'tk_left_shift' : '<<', 
    'tk_right_shift' : '>>',
    'tk_colon_asig' : ':=',
    'tk_left_shift_asig' : '<<=',
    'tk_right_shift_asig' : '>>=',
    'tk_pot_asig' : '**=',
    'tk_div_entera_asig' : '//=',
    'tk_ellipsis' : '...'
}


# Palabras reservadas en minúsculas
# Estas palabras tienen un significado especial en la sintaxis del lenguaje y no pueden usarse como identificadores
palabras_reservadas = {
    'range', 'object', 'False', 'None', 'True', 'and', 'as', 'assert', 'async', 'await', 'break',
    'class', 'continue', 'def', 'del', 'elif', 'else', 'except', 'finally', 'for', 'from', 'global',
    'if', 'import', 'in', 'is', 'lambda', 'nonlocal', 'not', 'or', 'pass', 'print', 'raise', 'return',
    'try', 'self', 'while', 'with', 'yield', '__init__'
}


# Tipos de datos básicos del lenguaje
# Cada tipo de dato se asocia con su palabra clave en el lenguaje
tipos_datos = {
    'int': 'int',
    'float': 'float',
    'str': 'str',
    'bool': 'bool',
    'list': 'list',
    'tuple': 'tuple',
    'dict': 'dict',
    'set': 'set'
}

def es_tab(char):
    if char == '\t':
        return True
    return False

def es_espacio(char):
    if char == ' ':
        return True
    return False

def es_comentario(char):
    if char == "#":
        return True

def es_digito(char):
    if ('0' <= char <= '9'):
        return True
    return False

def es_identificador(cadena):
    if not cadena:
        return False  # Cadena vacía
    for char in cadena:
        if not (('a' <= char <= 'z') or ('A' <= char <= 'Z') or ('0' <= char <= '9')) and char != '_':
            return False  # Solo se permiten letras minusculas y mayusculas , números y guion bajo
    return True

def es_token(char):
    if char in char_tokens.values():
        return True
    return False

def es_cadena(char):
    if char == "'" or char == '"':
        return True
    return False


def es_palabra_reservada(palabra):
    if palabra in palabras_reservadas:
        return True
    return False

def es_comentario_multilinea(linea, columna):
    return linea[columna:columna+3] == "'''" or linea[columna:columna+3] == '"""'


def analizador_lexico(codigo, salida):
    fila = 0  # Contador de filas (líneas de código)
    columna = 0  # Contador de columnas (posición en la línea)
    palabra = ''  # Variable de almacenamiento de palabra actual
    dentro_de_comentario = False # Bandera para indicar si se está en un comentario multilínea

    lineas = codigo.split('\n')  # Divide el código en líneas
    
    lista_tokens = sorted(char_tokens.items(), key=lambda x: len(x[1]), reverse=True)  # Ordena los tokens en una lista por longitud descendente

    # Abre el archivo de salida para escribir los resultados
    with open(salida, 'w', encoding='utf-8') as output_file:
        for linea in lineas: 

            # Reinicio de contadores y variables
            fila += 1  
            columna = 0  
            palabra = ''  
            
            while columna < len(linea):
                char = linea[columna]
                if dentro_de_comentario:
                    if es_comentario_multilinea(linea,columna):
                        dentro_de_comentario = False 
                    columna += 1
                    continue 
                if es_comentario_multilinea(linea,columna):
                    dentro_de_comentario = True
                    columna += 3
                    continue
                #Validacion de Tabulacion
                if es_tab(char):
                    columna += 4 # Tabulacion equivalente a 4 espacios
                    continue
                if es_espacio(char):
                    columna += 1
                    continue
                else:
                    columna += 1

                # Validacion de comentario
                if es_comentario(char):
                    break  # Ignorar el resto de la línea
                
                # Validacion de Digito
                if es_digito(char):  
                    inicio_numero = columna  # Guarda la posición inicial del número
                    while columna < len(linea) and (es_digito(linea[columna])):  # Detectar todo el número
                        columna += 1
                    output_file.write(f"<tk_entero,{linea[inicio_numero-1:columna]},{fila},{inicio_numero}>\n")  # Escribe el token numérico en el archivo
                    continue

                #Validacion de identificador
                if es_identificador(char):
                    inicio_numero = columna  # Guarda la posición inicial del identificador
                    while columna < len(linea) and es_identificador(linea[columna]):  # Detectar todo el identificador
                        columna += 1     
                    if linea[inicio_numero-1:columna] in palabras_reservadas:  # Imprimir palabra reservada
                        output_file.write(f"<{linea[inicio_numero-1:columna]},{fila},{inicio_numero}>\n")
                    elif linea[inicio_numero-1:columna] in tipos_datos:  # Imprimir tipo de dato
                        output_file.write(f"<{linea[inicio_numero-1:columna]},{fila},{inicio_numero}>\n")
                    elif linea[inicio_numero-1:columna] in palabras_reservadas_librerias:  # Imprimir tipo de dato
                        output_file.write(f"<tk_lib,{linea[inicio_numero-1:columna]},{fila},{inicio_numero}>\n")
                    else:
                        output_file.write(f"<id,{linea[inicio_numero-1:columna]},{fila},{inicio_numero}>\n")  # Imprime el token de identificador
                    continue

                
                #Validacion de Token
                if es_token(char):  # Si el carácter es un token válido
                    inicio_numero = columna
                    while columna < len(linea) and es_token(linea[columna]):  # Detectar todo el identificador
                        columna += 1  
                    tk_string = linea[inicio_numero-1:columna]
                    for nombre, simbolo in lista_tokens:
                        if tk_string.startswith(simbolo): #Detectar la subsecuencia más larga de tokens
                            output_file.write(f"<{nombre}, {fila}, {inicio_numero}>\n")  # Escribe el token en el archivo
                            columna = (inicio_numero + len(simbolo)-1)  # Actualiza la columna
                            break
            
                # Validacion de comentario multilínea
                if '"""' in linea or "'''" in linea:
                    partes = linea.split('"""') if '"""' in linea else linea.split("'''")
                    if len(partes) > 2: 
                        continue 
                    else:
                        comentario_multilinea = True
                        continue
                
                #Validacion de Cadena
                if es_cadena(char):  # Si dentro de una cadena de texto
                    while columna < len(linea) and not es_cadena(linea[columna]):
                        palabra += linea[columna]
                        columna += 1  
                    if columna >= len(linea): # Comillas sin cerrar
                        output_file.write(f">>> Error léxico(linea:{fila},posicion:{columna})\n")
                        return  # Finaliza la ejecución
                    output_file.write(f"<tk_cadena,\"{palabra}\",{fila},{(columna - len(palabra))}>\n")  # Escribe el token de cadena
                    columna += 1
                    palabra = ''  # Resetea la palabra
                    continue  # Continúa al siguiente carácter

                

                # Error Léxico por Caracter
                if not es_token(char) and not es_palabra_reservada(char) and not (('a' <= char <= 'z') or ('A' <= char <= 'Z') or ('0' <= char <= '9')) and char != '_' and char !=' ' and char !='"':
                    output_file.write(f">>> Error léxico(linea:{fila},posicion:{columna - len(palabra)})\n")
                    return  # Finaliza la ejecución

                #Error Léxico por palabra desconocida
                if char == " " or char in char_tokens.values():  # Si el carácter es un espacio o un token
                    if palabra:
                        if palabra in palabras_reservadas: # Si la palabra es una palabra reservada
                            output_file.write(f"<{palabra}, {fila}, {columna - len(palabra)}>\n")

                        elif palabra in tipos_datos: # Si la palabra es un tipo de dato
                            output_file.write(f"<{palabra},{fila},{columna - len(palabra)}>\n")
                        elif es_identificador(palabra): # Si la palabra es un identificador
                            output_file.write(f"<id, {palabra},{fila},{columna - len(palabra)}>\n")
                        else:
                            try:
                                # Intentar convertir en entero
                                numero_entero = int(palabra)
                                output_file.write(f"<numero_entero,{palabra},{fila},{columna - len(palabra)}>\n")
                            except ValueError:
                                output_file.write(f">>> Error léxico(linea:{fila},posicion:{columna - len(palabra)})\n")
                                return # Finaliza la ejecución
                        palabra = ''  # Resetea la palabra

                
            
                else:  # Ir guardando la palabra desconocida
                        palabra += char           

if len(sys.argv) != 2:
    print("Modo de Uso: python analizador_lexico.py codigo.py")
else:
    archivo_entrada = sys.argv[1]
    salida = "resultado_lexico.txt"

    try:
        with open(archivo_entrada, 'r', encoding='utf-8') as file:  # Abre el archivo de código fuente
            input_text = file.read() 

        analizador_lexico(input_text, salida) 

        #print(f"Análisis léxico completado. Resultados guardados en '{salida}'.")

    except FileNotFoundError:
        print(f"Error: El archivo '{archivo_entrada}' no se encontró.")
