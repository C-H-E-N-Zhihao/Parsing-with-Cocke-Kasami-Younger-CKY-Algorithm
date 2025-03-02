from algoritmes import *

def main(grammar, simbol_inicial, word, problema_base = False, ext1 = False, ext2 = False):
    """
    input: gramàtica, símbol incial, paraula i  el problema que es vol tractar. problema_base, ext1 i ext2 
           són booleans per determinar el problema que es vol resoldre. Depenent del problema, la gramàtica 
           tindrà un aspecte o altre.
    output: si és problema_base o ext1, l'output serà un booleà que determina si la paraula pot ser generada
            per la gramàtica. En cas de l'ext2 hi haurà, a més, la probabilitat de poder ser creat.
    """

    # en el problema base, la gramàtica està en CNF i es demana si word pot ser creada per grammar
    if problema_base:
        return CKY(grammar, simbol_inicial).algorithm(word)
    
    # en l'extensió 1, la gramàtica no cal estar en CNF
    elif ext1:
        g_fnc, genera_paraula_buida = FNC(grammar,simbol_inicial).CFG2CNF(print_grammar=True)
        if word == ['ε']:
            return genera_paraula_buida
        else:
            return CKY(g_fnc, simbol_inicial).algorithm(word)
    
    
    elif ext2:
        return PCKY(grammar, simbol_inicial).algorithm(word)

if __name__ == '__main__':
    with open('Principal_test_input.inp', 'r', encoding='utf-8') as file:
        proves = int(file.readline())
        grammar = dict()
        output = []
        for _ in range(proves):
            grammar = dict()
            file.readline()
            regles = int(file.readline())
            for _ in range(regles):
                line = file.readline().split()
                grammar[line[0]] = []
                elem = []
                for x,dreta in enumerate(line[2:]):
                    if dreta == '|':
                        grammar[line[0]].append(tuple(elem))
                        elem  = []
                    elif x == len(line[2:])-1:
                        elem.append(dreta)
                        grammar[line[0]].append(tuple(elem))
                    else:
                        elem.append(dreta)
            word = file.readline().split()[1:]
            init_simb = file.readline().split()[1]
            output.append(str(main(grammar, init_simb, word, problema_base=True, ext1 = False, ext2 = False)))


    with open('Principal_test_output.cor', 'w') as f_sortida:
        for elem in output:
            f_sortida.write(elem)
            f_sortida.write('\n')



