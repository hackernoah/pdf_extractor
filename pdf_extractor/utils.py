import string 

punctuation = '!"#$&\'()*+./:;<=>?@[\\]^_`{|}~'

def is_int(txt):
    try:
        conv = txt.translate(str.maketrans("","", punctuation)).replace(',','.')
        int(conv)
        return True
    except:
        return False 

def to_int(txt):
    negative = True if has_parenthesis(txt) else False
    conv = txt.translate(str.maketrans("","", punctuation)).replace(',','.')
    return int(conv) if not negative else 0 - int(conv)

def is_float(txt):
    try:
        conv = txt.translate(str.maketrans("","", punctuation)).replace(',','.')
        float(conv)
        return True
    except:
        return False

def to_float(txt):
    negative = True if has_parenthesis(txt) else False
    conv = txt.translate(str.maketrans("","", punctuation)).replace(',','.')
    return float(conv) if not negative else 0.0 - float(conv)

def is_percentage(txt):
    if '%' in txt:
        try:
            conv = txt.translate(str.maketrans("","", punctuation)).replace(',','.')
            float(conv.replace('%',''))
            return True 
        except:
            return False 
    else:
        return False

def to_percentage(txt):
    negative = True if has_parenthesis(txt) else False
    clean = delete_parenthesis(txt).replace('%','')
    output = to_float(clean) / 100
    return 0 - output if negative else output

def has_parenthesis(txt):
    if txt[0] == '(' and txt[-1] == ')':
        return True 
    else:
        False 

def delete_parenthesis(txt):
    return txt.replace('(','').replace(')','')


STOPWORDS = ['ad', 'al', 'allo', 'ai', 'agli', 'all', 'agl', 'alla', 'alle', 'con', 'col', 'coi', 'da', 'dal', 'dallo', 'dai', 'dagli', 'dall', 'dagl', 'dalla', 'dalle', 'di', 'del', 'dello', 'dei', 'degli', 'dell', 'degl', 'della', 'delle', 'in', 'nel', 'nello', 'nei', 'negli', 'nell', 'negl', 'nella', 'nelle', 'su', 'sul', 'sullo', 'sui', 'sugli', 'sull', 'sugl', 'sulla', 'sulle', 'per', 'tra', 'contro', 'io', 'tu', 'lui', 'lei', 'noi', 'voi', 'loro', 'mio', 'mia', 'miei', 'mie', 'tuo', 'tua', 'tuoi', 'tue', 'suo', 'sua', 'suoi', 'sue', 'nostro', 'nostra', 'nostri', 'nostre', 'vostro', 'vostra', 'vostri', 'vostre', 'mi', 'ti', 'ci', 'vi', 'lo', 'la', 'li', 'le', 'gli', 'ne', 'il', 'un', 'uno', 'una', 'ma', 'ed', 'se', 'perché', 'anche', 'come', 'dov', 'dove', 'che', 'chi', 'cui', 'non', 'più', 'quale', 'quanto', 'quanti', 'quanta', 'quante', 'quello', 'quelli', 'quella', 'quelle', 'questo', 'questi', 'questa', 'queste', 'si', 'tutto', 'tutti', 'a', 'c', 'e', 'i', 'l', 'o', 'ho', 'hai', 'ha', 'abbiamo', 'avete', 'hanno', 'abbia', 'abbiate', 'abbiano', 'avrò', 'avrai', 'avrà', 'avremo', 'avrete', 'avranno', 'avrei', 'avresti', 'avrebbe', 'avremmo', 'avreste', 'avrebbero', 'avevo', 'avevi', 'aveva', 'avevamo', 'avevate', 'avevano', 'ebbi', 'avesti', 'ebbe', 'avemmo', 'aveste', 'ebbero', 'avessi', 'avesse', 'avessimo', 'avessero', 'avendo', 'avuto', 'avuta', 'avuti', 'avute', 'sono', 'sei', 'è', 'siamo', 'siete', 'sia', 'siate', 'siano', 'sarò', 'sarai', 'sarà', 'saremo', 'sarete', 'saranno', 'sarei', 'saresti', 'sarebbe', 'saremmo', 'sareste', 'sarebbero', 'ero', 'eri', 'era', 'eravamo', 'eravate', 'erano', 'fui', 'fosti', 'fu', 'fummo', 'foste', 'furono', 'fossi', 'fosse', 'fossimo', 'fossero', 'essendo', 'faccio', 'fai', 'facciamo', 'fanno', 'faccia', 'facciate', 'facciano', 'farò', 'farai', 'farà', 'faremo', 'farete', 'faranno', 'farei', 'faresti', 'farebbe', 'faremmo', 'fareste', 'farebbero', 'facevo', 'facevi', 'faceva', 'facevamo', 'facevate', 'facevano', 'feci', 'facesti', 'fece', 'facemmo', 'faceste', 'fecero', 'facessi', 'facesse', 'facessimo', 'facessero', 'facendo', 'sto', 'stai', 'sta', 'stiamo', 'stanno', 'stia', 'stiate', 'stiano', 'starò', 'starai', 'starà', 'staremo', 'starete', 'staranno', 'starei', 'staresti', 'starebbe', 'staremmo', 'stareste', 'starebbero', 'stavo', 'stavi', 'stava', 'stavamo', 'stavate', 'stavano', 'stetti', 'stesti', 'stette', 'stemmo', 'steste', 'stettero', 'stessi', 'stesse', 'stessimo', 'stessero', 'stando']