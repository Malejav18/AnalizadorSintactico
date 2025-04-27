from collections import defaultdict
import re

# Definición de los patrones de tokens para el lexer
TOKEN_REGEX = [
    ('TRUE', r'True'),
    ('FALSE', r'False'),
    ('IMPORT', r'import'),
    ('AS', r'as'),
    ('FROM', r'from'),  
    ("DEF", r"def"),
    ('IF', r'if'),
    ('ELIF', r'elif'),
    ('ELSE', r'else'),        
    ('WHILE', r'while'),
    ('FOR', r'for'),
    ("IN", r"in"),
    ('RANGE', r'range'),
    ('RETURN', r'return'),
    ('PRINT', r'print'),
    ('CLASS', r'class'),
    ('EQEQ', r'=='),      
    ('NOTEQ', r'!='),     
    ('LE', r'<='),        
    ('GE', r'>='),
    ('PLUS_ASSIGN', r'\+='),
    ('MINUS_ASSIGN', r'-='),
    ('MUL_ASSIGN', r'\*='),  
    ('DIV_ASSIGN', r'/='),
    ('LT', r'<'),        
    ('GT', r'>'),
    ('NUM', r'\d+'),
    ('NOT', r'not'),
    ('AND', r'and'),
    ('OR', r'or'),
    ('ID', r"[a-zA-Z_][a-zA-Z_0-9]*"), # ID después de palabras reservadas
    ('PLUS', r'\+'),
    ('MINUS', r'-'),
    ('MUL', r'\*'),
    ('DIV', r'/'),
    ('MOD', r'%'),
    ('LPAREN', r'\('),
    ('RPAREN', r'\)'),
    ('LSQUARE', r'\['),    # Llaves y corchetes
    ('RSQUARE', r'\]'),
    ('LBRACE', r'\{'),
    ('RBRACE', r'\}'),
    ('EQUAL', r'='),
    ('COLON', r':'),
    ("COMMA", r","),
    ('SKIP', r'[ \t]+'),    
]


# Lexer: Convierte el código fuente en una lista de tokens
def lexer(code):
    tokens = []
    i = 0
    while i < len(code):
        match = None
        for token_type, regex in TOKEN_REGEX:
            pattern = re.compile(regex)
            match = pattern.match(code, i)
            if match:
                value = match.group(0)
                if token_type != 'SKIP':  # Ignorar espacios y tabulaciones
                    tokens.append((token_type, value))
                i = match.end()  # Avanzar el índice
                break
        if not match:
            raise SyntaxError(f"Caracter inesperado: {code[i]}")
    tokens.append(('EOF', '$'))  # Agregar marcador de fin de entrada
    return tokens
# Gramática de la producción
productions = {
    'stmt': [['assign_stmt'], ['def_stmt'], ['if_stmt'], ['return_stmt'], ['while_stmt'], ['for_stmt'], ['print_stmt'], ['import_stmt'], ['class_stmt']],  # stmt → assign_stmt | def_stmt | if_stmt | return_stmt
    'def_stmt': [['DEF', 'ID', 'LPAREN', 'param_list', 'RPAREN', 'COLON', 'stmt']],  # Definición de función
    "param_list": [["ID", "param_list_rest"],[]], # param_list → ID param_list_rest | ε
    "param_list_rest": [["COMMA", "ID", "param_list_rest"], []], # param_list_rest → , ID param_list_rest | ε
    'return_stmt': [['RETURN', 'expr']],  # Instrucción de retorno
    'print_stmt': [['PRINT', 'LPAREN', 'expr', 'RPAREN']],  # Sentencia de impresión
    'import_stmt': [['IMPORT', 'id_list'], ['FROM', 'ID', 'IMPORT', 'id_list']],  # Instrucción de importación
    'class_stmt': [['CLASS', 'ID', 'class_body']],
    'class_body': [
        ['COLON', 'stmt'],  # class_body → : stmt
        ['LPAREN', 'ID', 'RPAREN', 'COLON', 'stmt']  # class_body → ( ID ) : stmt
    ],
    'id_list': [['ID', 'id_list_rest']],
    'id_list_rest': [['COMMA', 'ID', 'id_list_rest'], ['AS', 'ID'], []],
    'assign_stmt': [['ID', 'assign_op', 'expr'],[]],
    'assign_op': [
        ['EQUAL'],
        ['PLUS_ASSIGN'],
        ['MINUS_ASSIGN'],
        ['MUL_ASSIGN'],
        ['DIV_ASSIGN'],
        ['LT'],
        ['GT'],
        ['MOD']
    ],
    'mod_op':[['expr', 'MOD', 'expr']],
    'if_stmt': [['IF', 'condition', 'COLON', 'stmt', 'if_tail']],  # luego del IF ejecuta un stmt (otra asignación o un if anidado)
    'if_tail': [['ELIF', 'condition', 'COLON', 'stmt', 'if_tail'], ['ELSE', 'COLON', 'stmt']],  
    'while_stmt': [['WHILE', 'condition', 'COLON', 'stmt']],  # Instrucción while
    'for_stmt': [['FOR', 'ID', 'IN', 'loop_iterable', 'COLON', 'stmt']],  # Instrucción for
    'loop_iterable': [['RANGE', 'LPAREN', 'num_list', 'RPAREN'], ['LSQUARE', 'num_list', 'RSQUARE'], ['ID']],  # Rango de números o ID
    'num_list': [['NUM', 'num_list_rest'],  []],
    'num_list_rest': [['COMMA', 'NUM', 'num_list_rest'],[]],
    'dict': [['pair', 'dict_rest'], []],  # Un diccionario puede ser un par de clave:valor seguido de más pares
    'dict_rest': [['COMMA', 'pair', 'dict_rest'], []],  # dict_rest → , pair dict_rest | ε
    'pair': [['ID', 'COLON', 'expr']],  # par → ID: expr (clave: valor)
    'condition': [['expr', 'comp_op', 'expr'], ['LPAREN', 'expr', 'comp_op', 'expr', 'RPAREN']],
    'comp_op': [['EQEQ'], ['NOTEQ'], ['LT'], ['GT'], ['LE'], ['GE']],
    'expr': [['term', 'expr_']],
    'expr_': [['PLUS', 'term', 'expr_'], 
              ['MINUS', 'term', 'expr_'],
              ['AND', 'term', 'expr_'],  
              ['OR', 'term', 'expr_'],   
              []],
    'term': [['factor', 'term_']],
    'term_': [['MUL', 'factor', 'term_'], ['DIV', 'factor', 'term_'], []],
    'factor': [['LPAREN', 'expr', 'RPAREN'], ['ID', 'factor_tail'], ['LSQUARE', 'num_list', 'RSQUARE'], ['LBRACE', 'dict', 'RBRACE'],  ['NUM'], ['TRUE'], ['FALSE'], ['NOT', 'factor']],  # factor → ( expr ) | ID | NUM | { dict } | [ num_list ] | True | False
    'factor_tail': [
        ['LSQUARE', 'num_list', 'RSQUARE'],  # Acceso a posición de arreglo
        ['LPAREN', 'arg_list', 'RPAREN'],  # Llamada a función
        []  # ε (solo ID)
    ],
    'arg_list': [['expr', 'arg_list_rest'], []],  # Lista de argumentos
    'arg_list_rest': [['COMMA', 'expr', 'arg_list_rest'], []],  # Lista de argumentos separados por comas
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
        return self.tokens[self.pos][0]  # Obtener el tipo del token actual

    def debug(self, action):
        print(f"[PILA: {self.stack} | TOKEN: {self.tokens[self.pos]}] -> {action}")

    def parse(self):
        while self.stack:
            top = self.stack.pop()  # Obtener el símbolo en la cima de la pila
            tok = self.current_token()

            if top == 'ε':  # Ignorar ε
                self.debug("Ignorar ε")
                continue
            elif top not in non_terminals:  # Si es un terminal
                if top == tok:
                    self.debug(f"Consumir '{tok}'")
                    self.pos += 1
                else:
                    self.debug(f"❌ Error: esperado {top}, encontrado {tok}")
                    return False
            else:  # Si es un no terminal
                rule = self.table.get(top, {}).get(tok)
                if rule is None:
                    self.debug(f"❌ Error: sin regla para ({top}, {tok})")
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

        return self.current_token() == 'EOF'  # Verificar si se consumió toda la entrada

# Código de entrada
code = "x=x%2"  # Ejemplo de código a analizar
tokens = lexer(code)  # Convertir el código en tokens

first = compute_first()  # Calcular FIRST
for token_type, _ in TOKEN_REGEX:
    if token_type != 'SKIP':
        first[token_type] = {token_type}
first['EOF'] = {'EOF'}

follow = compute_follow(first)  # Calcular FOLLOW
table = build_predict_table(first, follow)  # Construir la tabla predictiva

# Crear el intérprete y analizar
parser = LL1Interpreter(tokens, table)
print("\n🔍 Parsing...\n")
accepted = parser.parse()

if accepted:
    print("\n✔ Cadena aceptada")
else:
    print("\n❌ Cadena rechazada")
