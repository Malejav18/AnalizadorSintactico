from collections import defaultdict
import re

# Definición de los patrones de tokens para el lexer
TOKEN_REGEX = [
    ('IF', r'if'),
    ('ELIF', r'elif'),
    ('ELSE', r'else'),
    ('EQEQ', r'=='),
    ('NOTEQ', r'!='),
    ('LE', r'<='),
    ('GE', r'>='),
    ('LT', r'<'),
    ('GT', r'>'),
    ('NUM', r'\d+'),
    ('ID', r'[a-zA-Z_]\w*'),
    ('PLUS', r'\+'),
    ('MINUS', r'-'),
    ('MUL', r'\*'),
    ('DIV', r'/'),
    ('LPAREN', r'\('),
    ('RPAREN', r'\)'),
    ('EQUAL', r'='),
    ('COLON', r':'),
    ('SKIP', r'[ \t\n]+'),  # Asegurarse de que los saltos de línea y espacios sean ignorados
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
    'stmt': [['assign_stmt'], ['if_stmt']],  # stmt → assign_stmt | if_stmt
    'assign_stmt': [['ID', 'EQUAL', 'expr']],  # assign_stmt → ID = expr
    'if_stmt': [['IF', 'condition', 'COLON', 'stmt', 'elif_else']],  # if_stmt → IF condition : stmt elif_else
    'elif_else': [
        ['ELIF', 'condition', 'COLON', 'stmt', 'elif_else'],  # elif_else → ELIF condition : stmt elif_else
        ['ELSE', 'COLON', 'stmt'],  # elif_else → ELSE : stmt
        []  # elif_else → ε
    ],
    'condition': [['expr', 'comp_op', 'expr']],  # condition → expr comp_op expr
    'comp_op': [['EQEQ'], ['NOTEQ'], ['LE'], ['GE'], ['LT'], ['GT']],  # comp_op → == | != | <= | >= | < | >
    'expr': [['term', 'expr_']],  # expr → term expr_
    'expr_': [['PLUS', 'term', 'expr_'], ['MINUS', 'term', 'expr_'], []],  # expr_ → + term expr_ | - term expr_ | ε
    'term': [['factor', 'term_']],  # term → factor term_
    'term_': [['MUL', 'factor', 'term_'], ['DIV', 'factor', 'term_'], []],  # term_ → * factor term_ | / factor term_ | ε
    'factor': [['LPAREN', 'expr', 'RPAREN'], ['ID'], ['NUM']],  # factor → ( expr ) | ID | NUM
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
            # Si la regla tiene ε, agregar los elementos de FOLLOW
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
code = "if a == b: x = 1 elif a < b: x = 2 else: x = 3"
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
