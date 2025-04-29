from collections import defaultdict
from analizador_lexico import *
import sys

# Gramática de la producción
productions = {
    'stmt': [['assign_stmt'], ['def_stmt'], ['if_stmt'], ['return_stmt'],
         ['while_stmt'], ['for_stmt'], ['print_stmt'], ['import_stmt'],
         ['class_stmt'], ['pass_stmt'], ['break_stmt'], ['continue_stmt'],
         ['try_stmt']],
    'pass_stmt': [['pass']],
    'break_stmt': [['break']],
    'continue_stmt': [['continue']],
    'try_stmt': [['try', 'tk_dos_puntos', 'block', 'except_clause']],
    'block': [['TAB', 'stmt_list', 'TABend']],
    'except_clause': [['except', 'tk_dos_puntos', 'block']],
    'stmt_list': [['stmt', 'NEWLINE', 'stmt_list'], []],
    'def_stmt': [['def', 'id', 'tk_par_izq', 'param_list', 'tk_par_der', 'tk_dos_puntos', 'block']],
    'if_stmt': [['if', 'condition', 'tk_dos_puntos', 'block', 'if_tail']],
    'param_list': [["typed_param", "param_list_rest"], []],
    "param_list_rest": [["tk_coma", "typed_param", "param_list_rest"], []],
    "typed_param": [["id", "tk_dos_puntos", "type_expr"], ["id"]],
    "type_expr": [["tk_corchete_izq", "type_list", "tk_corchete_der"], ["id"]],
    "type_list": [["id", "type_list_cont"]],
    "type_list_cont": [["tk_coma", "id", "type_list_cont"], []],
    'return_stmt': [['return', 'expr']],  # Instrucción de retorno
    'print_stmt': [['print', 'tk_par_izq', 'expr', 'tk_par_der']],  # Sentencia de impresión
    'import_stmt': [['import', 'id_list'], ['from', 'id', 'import', 'id_list']],  # Instrucción de importación
    'class_stmt': [['class', 'id', 'class_body']],
    'class_body': [
        ['tk_dos_puntos', 'stmt'],  # class_body → : stmt
        ['tk_par_izq', 'id', 'tk_par_der', 'tk_dos_puntos', 'stmt']  # class_body → ( ID ) : stmt
    ],
    'id_list': [['id', 'id_list_rest']],
    'id_list_rest': [['tk_coma', 'id', 'id_list_rest'], ['as', 'id'], []],
    'assign_stmt': [['id', 'assign_op', 'expr'],[]],
    'assign_op': [
        ['tk_asig'],
        ['tk_mas_asig'],
        ['tk_menos_asig'],
        ['tk_mult_asig'],
        ['tk_div_asig'],
        ['tk_menor'],
        ['tk_mayor'],
        ['tk_mod_asig']
    ],
    'mod_op':[['expr', 'tk_modulo', 'expr']],
    'if_tail': [['elif', 'condition', 'tk_dos_puntos', 'stmt', 'if_tail'], ['else', 'tk_dos_puntos', 'stmt'],[]],  
    'while_stmt': [['while', 'condition', 'tk_dos_puntos', 'stmt']],  # Instrucción while
    'for_stmt': [['for', 'id', 'in', 'loop_iterable', 'tk_dos_puntos', 'stmt']],  # Instrucción for
    'loop_iterable': [['range', 'tk_par_izq', 'num_list', 'tk_par_der'], ['tk_corchete_izq', 'num_list', 'tk_corchete_der'], ['id']],  # Rango de números o ID
    'num_list': [['num', 'num_list_rest'],  []],
    'num_list_rest': [['tk_coma', 'num', 'num_list_rest'],[]],
    'num': [['tk_entero','num_'],['tk_punto','tk_entero']],
    'num_':[['tk_punto','tk_entero'],[]],
    'dict': [['pair', 'dict_rest'], []],  # Un diccionario puede ser un par de clave:valor seguido de más pares
    'dict_rest': [['tk_coma', 'pair', 'dict_rest'], []],  # dict_rest → , pair dict_rest | ε
    'pair': [['id', 'tk_dos_puntos', 'expr']],  # par → ID: expr (clave: valor)
    'condition': [['expr', 'comp_op', 'expr'], ['tk_par_izq', 'expr', 'comp_op', 'expr', 'tk_par_der']],
    'comp_op': [['tk_igual'], ['tk_distinto'], ['tk_menor'], ['tk_mayor'], ['tk_menor_igual'], ['tk_mayor_igual']],
    'expr': [['term', 'expr_']],
    'expr_': [['tk_suma', 'term', 'expr_'], 
              ['tk_resta', 'term', 'expr_'],
              ['tk_modulo', 'term', 'expr_'], 
              ['and', 'term', 'expr_'],  
              ['or', 'term', 'expr_'],   
              []],
    'term': [['factor', 'term_']],
    'term_': [['tk_mult', 'factor', 'term_'], ['tk_div', 'factor', 'term_'], []],
    'factor': [['tk_par_izq', 'expr', 'tk_par_der'], 
           ['id', 'factor_tail'], 
           ['tk_corchete_izq', 'num_list', 'tk_corchete_der'], 
           ['tk_llave_izq', 'dict', 'tk_llave_der'],  
           ['num'], 
           ['tk_cadena'],
           ['True'], 
           ['False'], 
           ['not', 'factor']],

    'factor_tail': [
        ['tk_corchete_izq', 'num_list', 'tk_corchete_der'],  # Acceso a posición de arreglo
        ['tk_par_izq', 'arg_list', 'tk_par_der'],  # Llamada a función
        []  # ε (solo ID)
    ],
    'arg_list': [['expr', 'arg_list_rest'], []],  # Lista de argumentos
    'arg_list_rest': [['tk_coma', 'expr', 'arg_list_rest'], []],  # Lista de argumentos separados por comas
}


# Conjunto de no terminales
non_terminals = set(productions.keys())

# Cálculo del conjunto FIRST
def compute_first():
    first = defaultdict(set)

    def first_of(symbol):
        if symbol not in non_terminals:  # Si es un terminal
            return {symbol}
        result = set()
        for rule in productions[symbol]:  # Para cada regla de producción
            for sym in rule:
                f = first_of(sym)  # Calcular FIRST del símbolo
                result |= (f - {'ε'})  # Agregar todo excepto ε
                if 'ε' not in f:  # Si no contiene ε, detener
                    break
            else:
                result.add('ε')  # Si todos los símbolos tienen ε, agregar ε
        return result

    # Iterar hasta que no haya cambios
    changed = True
    while changed:
        changed = False
        for nt in non_terminals:
            before = len(first[nt])
            first[nt] |= first_of(nt)
            if len(first[nt]) > before:
                changed = True
    return dict(first)

# Cálculo del conjunto FOLLOW
def compute_follow(first):
    follow = defaultdict(set)
    follow['stmt'].add('EOF')  # Agregar EOF al FOLLOW del símbolo inicial

    changed = True
    while changed:
        changed = False
        for A, rules in productions.items():
            for rule in rules:
                for i, B in enumerate(rule):
                    if B in non_terminals:  # Si es un no terminal
                        tail = rule[i + 1:]  # Símbolos después de B
                        if tail:
                            first_tail = set()
                            for sym in tail:
                                first_tail |= (first[sym] - {'ε'})
                                if 'ε' not in first[sym]:
                                    break
                            else:
                                first_tail.add('ε')
                            before = len(follow[B])
                            follow[B] |= first_tail
                            if 'ε' in first_tail:
                                follow[B] |= follow[A]
                        else:
                            before = len(follow[B])
                            follow[B] |= follow[A]
                        if len(follow[B]) > before:
                            changed = True
    return dict(follow)

# Construcción de la tabla predictiva LL(1)
def build_predict_table(first, follow):
    table = defaultdict(dict)

    for nt, rules in productions.items():
        for rule in rules:
            # Calcular FIRST de la producción
            rule_first = set()
            for sym in rule:
                rule_first |= (first[sym] - {'ε'})
                if 'ε' not in first[sym]:
                    break
            else:
                rule_first.add('ε')

            for terminal in rule_first:
                if terminal != 'ε':
                    table[nt][terminal] = rule
            if 'ε' in rule_first:
                for terminal in follow[nt]:
                    table[nt][terminal] = rule
    return table

class LL1Interpreter:
    def __init__(self, tokens, table):
        self.tokens = tokens  # Lista de tokens
        self.table = table    # Tabla predictiva
        self.pos = 0          # Posición actual en los tokens
        self.stack = ['stmt'] # Pila inicial con el símbolo inicial

    def current_token(self):
        return (self.tokens[self.pos])  # Obtener el tipo del token actual

    def debug(self, action):
        print(f"[PILA: {self.stack} | TOKEN: {tipo_tk(self.tokens[self.pos])}] -> {action}")

    def parse(self):
        self.stack.append('EOF')  # Agregar EOF al fondo
        self.stack.append('stmt')  # Símbolo inicial válido según tu gramática

        while self.stack:
            top = self.stack.pop()
            token = self.current_token()
            tok_type = tipo_tk(token)
            lexema = token.split(',')[1].strip()
            fila, col = sacar_pos(token)

            self.debug(f"Top: {top}, Token: {tok_type}, Stack: {self.stack}")

            if top not in self.table:
                # Si top es un terminal y no coincide con el token actual, error
                if tok_type != top:
                    print(f'<{fila},{col}> Error sintactico: se encontro: “{lexema}”; se esperaba: “{top}”.')
                    return False
                else:
                    continue  # Coincide terminal con token, se consume correctamente
            elif tok_type not in self.table[top]:
                esperados = [f'"{e}"' for e in self.table[top].keys()]
                print(f'<{fila},{col}> Error sintactico: se encontro: “{lexema}”; se esperaba: {", ".join(esperados)}.')
                return False


            elif top in self.table:  # No terminal
                if tok_type not in self.table[top]:
                    esperados = [f'"{e}"' for e in self.table[top].keys()]
                    print(f'<{fila},{col}> Error sintactico: se encontro: “{lexema}”; se esperaba: {", ".join(esperados)}.')
                    return False
                rule = self.table[top][tok_type]
                self.debug(f"Aplicar regla: {top} -> {rule}")
                for sym in reversed(rule):
                    if sym != 'ε':
                        self.stack.append(sym)

            else:
                # Error: símbolo inesperado en la pila
                print(f'<{fila},{col}> Error sintactico: se encontro: “{lexema}”; se esperaba: “{top}”.')
                return False

        if tipo_tk(self.current_token()) == 'EOF':
            print("El analisis sintactico ha finalizado exitosamente.")
            return True
        else:
            fila, col = sacar_pos(self.current_token())
            lexema = self.current_token().split(',')[1].strip()
            print(f'<{fila},{col}> Error sintactico: se encontro: “{lexema}”; se esperaba: “EOF”.')
            return False

#extraer posicion de un token
def sacar_pos(token):
    x,y=token.split(",")[-2:]
    return ((int(x),int(y.rstrip(">"))))

#extraer tipo de un token 
def tipo_tk(token):
    return token.split(',')[0][1:]

#tokenizar \t y \n
def token_tab_newl(tokens):
    tabs=[1]
    for i in range(1,len(tokens)):
        print(tokens[i])
        pos=sacar_pos(tokens[i])
        if pos[0]>sacar_pos(tokens[i-1])[0]:
            tokens.insert(i,f"<NEWLINE,{pos[0]},{pos[1]}>")
            print(tokens)
            if pos[1]>tabs[-1]:
                tabs.append(pos[1])
                tokens.insert(i+1,f"<TAB,{pos[0]},{pos[1]}>")
            elif pos[1]<tabs[-1]:
                while tabs[-1]!=pos[1]:
                    tabs.pop()
                    tokens.insert(i+1,f"<TABend,{pos[0]},{pos[1]}>")                
    tokens.append(f'<EOF,{pos[0]},{pos[1]}>')
    return(tokens)
# Calcular conjuntos FIRST y FOLLOW
first = compute_first()

# Agregar entradas a FIRST manualmente para terminales (si es necesario)
for token_type in palabras_reservadas | tokens.keys() | tipos_datos.keys():
    first[token_type] = {token_type}

# Tokens especiales
first['id'] = {'id'}
first['tk_entero'] = {'tk_entero'}
first['tk_cadena'] = {'tk_cadena'}
first['TAB'] = {'TAB'}
first['TABend'] = {'TABend'}
first['NEWLINE'] = {'NEWLINE'}
first['EOF'] = {'EOF'}

follow = compute_follow(first)
table = build_predict_table(first, follow)  # ✅ ESTA es la definición de "table"


if __name__ == "__main__":
    import os
    import sys

    if len(sys.argv) != 2:
        print("Modo de Uso: python analizador_sintactico.py archivo.py")
        sys.exit(1)

    archivo_entrada = sys.argv[1]
    salida = r"C:\Users\heduu\OneDrive\Escritorio\Universidad\Quinto Semestre\Lenguajes de programación y transducción\AnalizadorSintactico-main\AnalizadorSintactico-main\resultado_lexico.txt"

    if not os.path.exists(archivo_entrada):
        print(f"Error: El archivo '{archivo_entrada}' no se encontró.")
        sys.exit(1)

    # Ejecutar análisis léxico
    try:
        with open(archivo_entrada, 'r', encoding='utf-8') as f:
            input_text = f.read()

        analizador_lexico(input_text, salida)

        if not os.path.exists(salida):
            print("❌ Error: El análisis léxico no generó el archivo de salida.")
            sys.exit(1)

    except Exception as e:
        print(f"❌ Error durante el análisis léxico: {e}")
        sys.exit(1)

    print("✅ Análisis léxico completado. Iniciando análisis sintáctico...")

    # Ejecutar análisis sintáctico
    try:
        with open(salida, 'r', encoding='utf-8') as file:
            content = file.read()

        tokens = token_tab_newl(content.splitlines())
        tokens.append('<EOF,>')

        parser = LL1Interpreter(tokens, table)

        print("\n🔍 Parsing...\n")
        accepted = parser.parse()

        if accepted:
            print("\n✔ Cadena aceptada")
        else:
            print("\n❌ Cadena rechazada")

    except Exception as e:
        print(f"❌ Error durante el análisis sintáctico: {e}")
        sys.exit(1)
