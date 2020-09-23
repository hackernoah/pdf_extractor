

class TableExtractor:
    
    def __init__(self):
        self.content = []
        self.input_base_path = '.\\input\\'
        self.output_base_path = '.\\output\\'
        self.path = input_base_path + "excel1.xlsx"
        self.wb = openpyxl.load_workbook(path) if os.path.isfile(path) else openpyxl.Workbook()
        self.sheet = wb.active
        pass

    def clean(self,txt):
    elems = txt.split()
    result = []
    stopwords = ['of','at']
    for i,el in enumerate(elems):
        if len(el) < 4 and el not in stopwords and i > 0:
            result[-1] = result[-1] + el 
        else:
            result.append(el)
    return ' '.join(result)

    def check_regex(self,val, regex):
        result = val.replace(' ','') if re.match(regex, str(val).replace(' ','')) else val
        return result

    def join(self,key1,key2):
        for i,elem in enumerate(data[key2]):
            new = (data[key1][i][0],data[key2][i][1])
            print(new)
            data[key2][i] = new