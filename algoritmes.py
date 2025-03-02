############################################### PROBLEMA PRINCIPAL ##########################################

class CKY():

    def __init__(self, grammar, simbol_inicial, gen_eps = False) -> None:
        self.simbol_inicial = simbol_inicial
        self.grammar = grammar
        self.gen_eps = gen_eps

    def algorithm(self, word):
        self.grammar_inv = self.invertir_dicc(self.grammar)
        if word == ['ε']:
            return self.gen_eps
        word = [None] + word                #Per facilitar la lectura dels indexos
        self.table = {}
        for i in range(1,len(word)):        #Per inicialitzar la taula, cada clau és (i,i), i el valor és la semàntica de la paraula i
            self.table[i,i] = self.grammar_inv[(word[i],)]
        for x in range(1,len(word)-1):      #comptador de la fila on es troba 
            for i in range(1,len(word)-x):  #comptador de la columna on es troba, el primer elem de la clau de la taula
                j = i + x            #el segon elem. de la clau de la taula
                exists_i_j = False          #Comprovar si l'índex (i,j) existeix a la taula
                for k in range(i,j):
                    if (i,k) in self.table and (k+1,j) in self.table:
                        for elem1 in self.table[i,k]:
                            for elem2 in self.table[k+1,j]:  
                                if (elem1,elem2) in self.grammar_inv:    #Comprovar si dos no terminals formen un no terminal de nivell més alt
                                    if exists_i_j:
                                        self.table[i,j] = self.table[i,j].union(self.grammar_inv[(elem1,elem2)])
                                    else:
                                        self.table[i,j] = self.grammar_inv[(elem1,elem2)]
                                        exists_i_j = True
        print(self.table)
        return (1,len(word)-1) in self.table and self.simbol_inicial in self.table[1,len(word)-1]
    
    def invertir_dicc(self, dicc):
        dicc_inv = {}
        for clau, valor in dicc.items():
            for valor_i in valor:
                #Per a cada tupla, afegir-lo al dicc_inv com a clau i la clau' com a valor
                if valor_i in dicc_inv:
                    dicc_inv[valor_i].add(clau)
                else:
                    dicc_inv[valor_i] = {clau}
        return dicc_inv

############################################### EXTENSIÓ 1 ##########################################

class FNC():

    def __init__(self, grammar, simbol_inicial) -> None:
        self.original_grammar = grammar
        self.simbol_inicial = simbol_inicial

    def CFG2CNF(self, print_grammar = False) -> dict:
        import copy
        #Retorna la gramàtica en FNC
        self.grammar = copy.deepcopy(self.original_grammar)
        self.additional_S = 0       #Símbols addicionals
        self.__rem_eps()
        self.__rem_hib()
        self.__rem_unit_prod()
        self.__rem_no_bin()
        if print_grammar:
            self.__represent_grammar()
        return self.grammar, self.simbol_inicial in self.nullable

    def __represent_grammar(self):
        #Escriu a la sortida la gramàtica FNC de forma més interpretable
        for clau in self.grammar:
            print(clau, '->', end = ' ')
            for i, valor in enumerate(self.grammar[clau]):
                print(*valor, end = ' ')
                if i != len(self.grammar[clau])-1:
                    print('|', end = ' ')
            print()

    def __rem_eps(self):
        self.__TrobarProduccionsEpsilon()
        self.__TrobarNomesEpsilon()

        for clau, rules in self.grammar.items():
            for i, rule in enumerate(rules):
                if all(symbol in self.only_eps or symbol == 'ε' for symbol in rule):
                    self.grammar[clau][i] = (None, None)

        self.grammar = {clau: [tupla for tupla in llista if tupla != (None, None)] \
                            for clau, llista in self.grammar.items()}
        
        self.grammar = {clave: valores for clave, valores in self.grammar.items() if valores}

        for clau, rules in self.grammar.items():
            new_rules = []
            for rule in rules:
                pos = []
                for i, symbol in enumerate(rule):
                    if symbol in self.nullable:
                        pos.append(i)
                if pos:
                    pwset = self.__powerset(pos, 0, len(pos))
                    for x in pwset:
                        #Eliminar els símbols que tenen les posicions corresponents al x
                        regla_aux = tuple(value for idx, value in enumerate(rule) if idx not in x and not value in self.only_eps)
                        if len(regla_aux)>0 and regla_aux not in new_rules:
                            new_rules.append(regla_aux)
                elif rule not in new_rules:
                    new_rules.append(rule)
            self.grammar[clau] = new_rules

    def __rem_hib(self) -> None:
        later_change = set()    #Un conjunt per guardar els canvis que s'hauran d'efectuar al diccionari
        #Eliminar regles híbrides
        for non_terminal, rules in self.grammar.items():
            for i, rule in enumerate(rules):
                if len(rule) > 1:
                    for j, symbol in enumerate(rule):
                        if symbol not in self.grammar:
                            new_non_terminal = self.__get_new_non_terminal()
                            later_change.add((new_non_terminal, symbol))
                            later_change.add((non_terminal, i, j, new_non_terminal))

        for t in later_change:
            if len(t) == 4:     #Per eliminar una part de la regla (substituir terminal per no terminal)
                non_terminal, i, j, new_non_terminal = t
                rule = self.grammar[non_terminal][i]
                self.grammar[non_terminal][i] = rule[:j] + (new_non_terminal,) + rule[j+1:]
            elif len(t) == 2:   #Per afegir una regla que genera el no terminal substituït
                new_non_terminal, symbol = t
                if new_non_terminal not in self.grammar:
                    self.grammar[new_non_terminal] = [(symbol,)]
                else:
                    self.grammar[new_non_terminal].append((symbol,))

    def __rem_unit_prod(self) -> None:
        #Eliminar les produccions unitàries
        unit_productions = []

        for non_terminal, rules in self.grammar.items():
            for rule in rules:
                #Si la regla genera un no terminal
                if len(rule) == 1 and rule[0] in self.grammar:
                    unit_productions.append((non_terminal, rule[0]))
                    self.grammar[non_terminal].remove(rule)     #Assumint que no hi ha regles repetides

        while unit_productions:
            non_terminal, unit = unit_productions.pop()
            rules_to_add = self.grammar[unit]
            for rule in rules_to_add:
                if rule not in self.grammar[non_terminal]:
                    self.grammar[non_terminal].append(rule)
                    #Si la regla afegida genera un no terminal
                    if len(rule) == 1 and rule[0] in self.grammar:
                        unit_productions.append((non_terminal, rule[0]))
                        self.grammar[non_terminal].remove(rule)

    def __rem_no_bin(self) -> None:
        #Eliminar les regles no binàries
        new_rules = dict()      #Un diccionari auxiliar, més tard substituirà al dict actual
        
        for non_terminal, rules in self.grammar.items():
            new_rules[non_terminal] = []
            for rule in rules:
                while len(rule) > 2:
                    new_non_terminal = self.__get_new_non_terminal()
                    new_rules[new_non_terminal] = [(rule[0], rule[1])]
                    rule = (new_non_terminal,) + rule[2:]
                new_rules[non_terminal].append(rule)

        self.grammar = new_rules

    def __get_new_non_terminal(self) -> str:
        #Retorna un símbol no terminal codificat com números (Assumeix que no hi existien)
        self.additional_S += 1
        return f"{self.additional_S}"
    
    def __TrobarProduccionsEpsilon(self):
        self.nullable = {lhs for lhs, rules in self.grammar.items() if ('ε',) in rules}
        while True:
            new_nullable = set()
            for lhs, rules in self.grammar.items():
                for rule in rules:
                    if all(symbol in self.nullable for symbol in rule):
                        new_nullable.add(lhs)
            if not new_nullable - self.nullable:
                break
            self.nullable |= new_nullable

    def __TrobarNomesEpsilon(self):
        self.only_eps = {lhs for lhs, rules in self.grammar.items() if rules == [('ε',) ]}
        while True:
            new_only_eps = set()
            for lhs, rules in self.grammar.items():
                count = 0
                for rule in rules:
                    if all(symbol in self.only_eps or symbol == 'ε' for symbol in rule):
                        count +=1
                if count == len(rules):
                    new_only_eps.add(lhs)
            if not new_only_eps - self.only_eps:
                break
            self.only_eps |= new_only_eps


    def __powerset(self, conjunt, current, n_elements):
        if current == n_elements:
            return [list()]
        
        sols0 = self.__powerset(conjunt, current+1, n_elements)
        sols0 += [[conjunt[current]] + sol for sol in sols0]
        
        return sols0


############################################### EXTENSIÓ 2 ##########################################

class PCKY():

    def __init__(self, grammar, ini = 'S') -> None:
        self.ini = ini
        self.grammar = grammar

    def algorithm(self, word):
        self.grammar_inv = self.invertir_dicc(self.grammar)
        word = [None] + word                #Per facilitar la lectura dels indexos
        self.table = {}
        self                                #{(generat, i, j): prob}
        for i in range(1,len(word)):        #Per inicialitzar la taula, cada clau és (i,i), i el valor és la semàntica de la paraula i
            self.table[i,i] = self.grammar_inv[(word[i],)]
        for x in range(1,len(word)-1):      #comptador de la fila on es troba 
            for i in range(1,len(word)-x):  #comptador de la columna on es troba, el primer elem de la clau de la taula
                j = i + x            #el segon elem. de la clau de la taula
                exists_i_j = False          #Comprovar si l'índex (i,j) existeix a la taula
                for k in range(i,j):
                    if (i,k) in self.table and (k+1,j) in self.table:
                        for elem1 in self.table[i,k]:
                            for elem2 in self.table[k+1,j]:  
                                if (elem1[0],elem2[0]) in self.grammar_inv:    #Comprovar si dos no terminals formen un no terminal de nivell més alt
                                    to_mul = elem1[1]*elem2[1]
                                    if exists_i_j:
                                        self.table[i,j] = self.table[i,j].union({(s, prob * to_mul) for s, prob in self.grammar_inv[(elem1[0],elem2[0])]})
                                    else:
                                        self.table[i,j] = {(s, prob * to_mul) for s, prob in self.grammar_inv[(elem1[0],elem2[0])]}
                                        exists_i_j = True
                self.table[i,j] = self.preproc_dicc(self.table[i,j])
                
        if (1,len(word)-1) in self.table:
            final = [tupla for tupla in self.table[1,len(word)-1] if tupla[0] == 'S'][0]
            return self.ini in final[0], final[1]
        else:
            return False, 0
    
    def invertir_dicc(self, dicc):
        dicc_inv = {}
        for clau, valor in dicc.items():
            for valor_i in valor:
                new_value = (clau, valor_i[1])
                #Per a cada expressió generada, afegir-la al dicc_inv com a clau i (la clau, la prob.) com a valor
                if valor_i[0] in dicc_inv:
                    dicc_inv[valor_i[0]].add(new_value)
                else:
                    dicc_inv[valor_i[0]] = set([new_value])
        return dicc_inv
    
    def preproc_dicc(self, rules):
        #Eliminar els no terminals que generen els mateixos símbols però sense tenir la prob. màxima
        max_values = {}
        for tuple, prob in rules:
            if tuple not in max_values or prob > max_values[tuple]:
                max_values[tuple] = prob
        new_rules = set(max_values.items())
        return new_rules