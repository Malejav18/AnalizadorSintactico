from collections import defaultdict
from analizador_lexico import *
import sys

# Gramática de la producción
productions = {
    'stmts':[['stmt','stmts_','EOF']],
    'stmts_':[['stmt','stmts_'],[]],
    'stmt': [['simple_stmts'],['complx']],
    'simple_stmts':[['simple_stmt','NEWLINE']],
    'simple_stmt':[['id','assign_stmt'], ['self','assign_stmt'], ['return_stmt'], ['print_stmt'], ['import_stmt']],
    'complx': [['def', 'def_stmt'], ['if_stmt'], ['while_stmt'], ['for_stmt'], ['class_stmt'], ['try_stmt']],  # stmt → assign_stmt | def_stmt | if_stmt | return_stmt
    'def_stmt': [['def_init_stmt'], ['def_normal_stmt']],
    'def_init_stmt': [['__init__', 'tk_par_izq', 'param_list', 'tk_par_der', 'tk_dos_puntos','block']],
    'def_normal_stmt': [['id', 'tk_par_izq', 'param_list', 'tk_par_der', 'tk_dos_puntos','block']],
    "param_list": [["id", "param_structure", "param_list_rest"],["self", "param_structure", "param_list_rest"],[]],  # param_list → id param_list_rest | ε
    "param_list_rest": [["tk_coma", "param_list"], []],  # param_list_rest → , id param_list_rest | ε
    "param_structure": [["tk_dos_puntos", "param_list_complex"],[]],  # param_structure → id : tipos_datos | id : tipo_lista
    "param_list_complex": [['tipo_lista', "tk_corchete_izq",'lista_tipos_datos', "tk_corchete_der"], ["tk_corchete_izq", 'tipos_datos', "tk_corchete_der"], ["tipos_datos"], []],  # param_list_complex → id param_list_rest | ε
    "param_list_rest_2": [["tk_coma", "id", "param_list_rest_2"], []],  # param_list_rest_2 → , id param_list_rest_2 | ε
    
    "lista_tipos_datos" : [["tipos_datos", "lista_tipos_datos_rest"], []],  # lista_tipos_datos → tipos_datos lista_tipos_datos_rest | ε
    "lista_tipos_datos_rest" : [["tk_coma", "tipos_datos", "lista_tipos_datos_rest"], []],  # lista_tipos_datos_rest → , tipos_datos lista_tipos_datos_rest | ε
    'tipos_datos': [['int'], ['float'], ['str'], ['bool']],  # tipos_datos → int | float | str | bool
    'tipo_lista': [['list'], ['set'], ['dict'], ['tuple']],  # tipo_lista → list | set | dict | tuple]
    
    'return_stmt': [['return', 'expr']],  # Instrucción de retorno
    'print_stmt': [['print', 'tk_par_izq', 'print_expr', 'tk_par_der']],  # Sentencia de impresión
    'print_expr': [['expr', 'print_tail'], []],
    'print_tail': [['tk_coma', 'expr', 'print_tail'], []],
    'import_stmt': [['import', 'id_list'], ['import', 'id_list'], ['from', 'id', 'import', 'id_list']],  # Instrucción de importación

    'class_stmt': [['class', 'id', 'class_body']],
    'class_body': [
        ['tk_dos_puntos', 'block'],  # class_body → : stmt
        ['tk_par_izq', 'id', 'tk_par_der', 'tk_dos_puntos', 'block']  # class_body → ( ID ) : stmt
    ],
    'block':[['NEWLINE','TAB', 'stmts_','TABend'],['simple_stmts']],
    'id_list': [['id', 'id_list_rest']],
    'id_list_rest': [['tk_coma', 'id', 'id_list_rest'], ['as', 'id'], []],
    'assign_stmt': [['assign_op', 'expr'],['factor_tail', 'assignment']],
    'assignment': [['assign_op', 'expr'], []],  # Asignación a atributo
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
    'loop_stmt': [['simple_stmt_loop'], ['complx'], ['NEWLINE']],
    'simple_stmt_loop': [['id', 'assign_stmt'], ['return_stmt'], ['print_stmt'], ['import_stmt'], 
                        ['break'], ['continue'], ['pass']],
    'loop_block': [['NEWLINE','TAB','loop_stmts','TABend'], ['simple_stmts_loop']],
    'loop_stmts': [['loop_stmt', 'loop_stmts'], []],
    'simple_stmts_loop': [['simple_stmt_loop','NEWLINE']],
    'mod_op':[['expr', 'tk_modulo', 'expr']],
    'if_stmt': [['if', 'condition', 'tk_dos_puntos', 'loop_block', 'if_tail']],  # luego del IF ejecuta un stmt (otra asignación o un if anidado)
    'if_tail': [['elif', 'condition', 'tk_dos_puntos', 'loop_block', 'if_tail'], ['else', 'tk_dos_puntos', 'loop_block'],[]],
    'while_stmt': [['while', 'condition', 'tk_dos_puntos', 'loop_block', 'while_tail']],  # Instrucción while
    'while_tail': [['else', 'tk_dos_puntos', 'loop_block'],[]],
    'for_stmt': [['for', 'id', 'in', 'loop_iterable', 'tk_dos_puntos', 'loop_block']],  # Instrucción for
    'loop_iterable': [['range', 'tk_par_izq', 'num_list', 'tk_par_der'], ['tk_corchete_izq', 'items_array', 'tk_corchete_der'], ['id', 'factor_tail'], ['self', 'factor_tail'], ['tk_par_izq', 'items_tuple', 'tk_par_der']],  # Rango de números o ID
    
    'try_stmt': [['try', 'tk_dos_puntos', 'loop_block', 'try_stmt_tail']], # try: except: finally:
    'try_stmt_tail': [['except_stmt', 'finally_stmt']],
    'except_stmt': [['except', 'except_e', 'tk_dos_puntos', 'loop_block', 'except_try'], []],
    'except_try': [['except_stmt'], ['try_else'], []],
    'except_e': [['id'], []],
    'try_else': [['else', 'tk_dos_puntos', 'loop_block'], []],
    'finally_stmt': [['finally', 'tk_dos_puntos', 'loop_block'], []],

    'num_list': [['num', 'num_list_rest'],['id'],  []],
    'num_list_rest': [['tk_coma', 'num', 'num_list_rest'],[]],
    'num': [['tk_entero','num.'],['tk_punto','tk_entero']],
    'num.':[['tk_punto','num.num'],[]],
    'num.num':[['tk_entero'],[]],


    

    'condition': [['expr', 'condition_tail'], ['tk_par_izq','condition' 'tk_par_der'], ['True'], ['False']],
    'condition_tail': [['in', 'id'], ['comp_op', 'expr'], []],
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

    'set_dict': [['items_set'], ['items_dict'], []],  # Un conjunto puede ser una lista de elementos o un diccionario

    'items_set': [['items_rest'], []],  # Un conjunto puede ser una lista de elementos

    'items_dict': [['pair', 'dict_rest'], []],  # Un diccionario puede ser un par de clave:valor seguido de más pares
    'pair': [['tk_dos_puntos', 'expr']],  # par → ID: expr (clave: valor)
    'dict_rest': [['tk_coma', 'expr', 'pair', 'dict_rest'], []],  # dict_rest → , pair dict_rest | ε

    'items_tuple': [
        ['expr', 'items_rest'], # Mínimo 1 para ser tupla
        []
        ],
    'items_rest': [
        ['tk_coma', 'items_rest_tail'], # Más elementos en la tupla
        []
    ],
    'items_rest_tail': [
        ['expr', 'items_rest'],
        []
    ],
    'items_array': [
        ['tk_dos_puntos', 'items_dos_puntos'],
        ['expr', 'items_array_rest'], 
        []
        ],
    'items_dos_puntos': [
        ['expr'],
        [],
    ],
    'items_array_rest': [
        ['tk_coma', 'items_rest_tail'],
        ['tk_dos_puntos', 'items_array_tail'],   # text[i:j]
        []
    ],
    'items_array_tail': [
        ['expr', 'items_array_rest'],
        ['expr'],
        []
    ],
    'factor': [['tk_par_izq', 'expr', 'tk_par_der'], 
               ['id', 'factor_tail'], 
               ['self', 'factor_tail'],
               ['set_function'],
               ['list_function'],
               ['tuple_function'],
               ['tk_corchete_izq', 'items_array', 'tk_corchete_der'], 
               ['tk_llave_izq', 'expr','set_dict', 'tk_llave_der'],  
               ['num'], ['True'], ['False'], ['not', 'factor'], 
               ['tk_par_izq', 'items_tuple', 'tk_par_der'],
               ['tk_cadena']],  # factor → ( expr ) | ID | NUM | { set_dict } | [ num_list ] | True | False
    'factor_tail': [
        ['tk_corchete_izq', 'items_array', 'tk_corchete_der', 'factor_tail'],  # Acceso a posición de arreglo
        ['tk_par_izq', 'arg_list', 'tk_par_der', 'factor_tail'],  # Llamada a función
        ['tk_punto','id','factor_tail'], # llamada a atributo
        []  # ε (solo ID)
    ],
    'set_function': [['set', 'tk_par_izq', 'items', 'tk_par_der']],  # set()
    'list_function': [['list', 'tk_par_izq', 'items', 'tk_par_der']],  # list()
    'tuple_function': [['tuple', 'tk_par_izq', 'items', 'tk_par_der']],  # tuple()
    'items': [['tk_cadena'], ['tk_corchete_izq', 'items_array', 'tk_corchete_der', 'factor_tail'], ['tk_par_izq', 'arg_list', 'tk_par_der', 'factor_tail'], []],
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
    follow['stmts'].add('EOF')  # Agregar EOF al FOLLOW del símbolo inicial

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
        self.stack = ['stmts'] # Pila inicial con el símbolo inicial

    def current_token(self):
        return (self.tokens[self.pos])  # Obtener el tipo del token actual

    def debug(self, action):
        print(f"[PILA: {self.stack} | TOKEN: {tipo_tk(self.tokens[self.pos])}] -> {action}")

    def parse(self):
        while self.stack:
            top = self.stack.pop()  # Obtener el símbolo en la cima de la pila
            tok = tipo_tk(self.current_token())
            if top == 'ε':  # Ignorar ε
                self.debug("Ignorar ε")
                continue
            elif top not in non_terminals:  # Si es un terminal
                if top == tok:
                    self.debug(f"Consumir '{tok}'")
                    self.pos += 1
                else:
                    self.debug(f"❌ Error en {sacar_pos(self.current_token())}: esperado {top}, encontrado {tok}")
                    return False
            else:  # Si es un no terminal
                rule = self.table.get(top, {}).get(tok)
                if rule is None:
                    self.debug(f"❌ Error en {sacar_pos(self.current_token())}: sin regla para ({top}, {tok})")
                    return False
                self.debug(f"Aplicar: {top} → {' '.join(rule) if rule else 'ε'}")
                # Si la regla es vacía (ε), no hacemos nada
                if rule == []:
                    self.debug(f"Ignorar ε en {top}")
                    continue  # No agregar nada a la pila
                for sym in reversed(rule):  # Agregar la producción a la pila
                    self.stack.append(sym)

            # Especial para elif_else: Si estamos en el paso final de elif_else y encontramos un "elif",
            # deberíamos procesarlo, no aplicar ε
            if top == 'elif_else' and tok == 'ELIF':
                self.debug("Procesar 'elif'")
                self.stack.append('stmt')  # Agregar la producción que corresponde a la rama de elif

        return self.stack==[]  # Verificar si se consumió toda la entrada

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
    i=1
    while i < len(tokens):
        pos=sacar_pos(tokens[i])
        if pos[0]>sacar_pos(tokens[i-1])[0]:
            tokens.insert(i,f"<NEWLINE,{pos[0]},{pos[1]}>")
            if pos[1]>tabs[-1]:
                tabs.append(pos[1])
                tokens.insert(i+1,f"<TAB,{pos[0]},{pos[1]}>")
            elif pos[1]<tabs[-1]:
                while tabs[-1]!=pos[1]:
                    tabs.pop()
                    tokens.insert(i+1,f"<TABend,{pos[0]},{pos[1]}>")
        i+=1 
    tokens.append(f'<NEWLINE,{pos[0]},{pos[1]}>')
    while tabs[-1]!=1:
        tabs.pop()
        tokens.append(f"<TABend,{pos[0]},{pos[1]}>")
    tokens.append(f'<EOF,{pos[0]},{pos[1]}>')
    print(tokens)
    return(tokens)


# Código de entrada

if len(sys.argv) != 2:
    print("Modo de Uso: python 'analizador_sintactico.py' codigo.py")
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

first = compute_first()  # Calcular FIRST
for token_type in palabras_reservadas|tokens.keys()|tipos_datos.keys():
    if token_type != 'SKIP':
        first[token_type] = {token_type}
first['id'] = {'id'}
first['tk_entero'] = {'tk_entero'}
first['tk_cadena'] = {'tk_cadena'}
first['TAB'] = {'TAB'}
first['TABend'] = {'TABend'}
first['NEWLINE'] = {'NEWLINE'}
first['EOF'] = {'EOF'}

follow = compute_follow(first)  # Calcular FOLLOW
table = build_predict_table(first, follow)  # Construir la tabla predictiva

# Crear el intérprete y analizar
file =open("./resultado_lexico.txt")
content = file.read()
tokens = token_tab_newl(content.splitlines())

parser = LL1Interpreter(tokens, table)

print("\n🔍 Parsing...\n")
accepted = parser.parse()

if accepted:
    print("\n✔ Cadena aceptada")
else:
    print("\n❌ Cadena rechazada")
