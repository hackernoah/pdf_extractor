import openpyxl
from openpyxl.worksheet.merge import MergedCell
import os
import json
import re
import collections
import string

class CertificateParser:

    def __init__(self ):
        self.table_content = []
        self.other_content = []
        self.tables = []
        self.max_row = 0
        #tracciato da prendere da un file esterno e inserire inizializzazione di constants in metodo
        self.tracciato = ["Issuer",	("Isin Code","ISIN Code"), "CFI Code", ("Underlying","Underlying Shares"),"Type of Certificate", ("Underlying ISIN","ISIN of Share"),	"Strike","Issue date", ("Expiry date","Exercise Settlement Date"), "Parity",	"Nominal Value",	("Quantity","No. of Securities issued"),"Exercise Type",	"Option Type","Exercise Lot",	"Marketing name",	"Price of Underlying",	("Reference Price","Issue Priceper Security"),	"Underlying currency",	"Euro-Hedged",	"1st Barrier",	"Barrier Observation",	"2nd Strike",	"2nd Barrier",	"Autocallability",	"Observation Autocallability",	"Participation %",	"Fee %",	"Long/Short",	"Bonus/Strike%",	"Cap",	"Floor",	"Coupon",	"Protection",	"Specialist Code",	"Quote Type",	"RFE Activation",	"Denomination Currency",	"Trading Currency",	"Settlement Currency",	"Settlement System",	"Leverage Number",	"Restrike %",	"Final Valuation Date",	"Professional",	"KID web link",	"Distribution Type",	"Type of Underlying",	"ACEPI Type",	"Instrument Name",	"Minimum Lot",	"Start Trading Date",	"Last Trading Date",	"Size Obligation",	"Threshold Profile ID",	"First Semaphore",	"First Error Description",	"FISN",	"Multiplier"	"File PDF"]
        self.constants = {}
        for el in self.tracciato:
            if type(el) is not tuple:
                self.constants[el] = ''
    
    def extract_content(self,sheet):
        vertical = sheet.max_row
        horizontal = sheet.max_column
        isin = re.compile(r'\b([A-Z]{2})((?![A-Z]{10}\b)[A-Z0-9]{6,10})\b')
        for row in range(1,vertical):
            data = []
            table = False
            merged = True if type(sheet.cell(row=row + 1, column = 1)) == MergedCell else False
            for col in range(1,horizontal):
                if merged:
                    val1 = self.check_regex(sheet.cell(row=row, column = col).value,isin)
                    val2 = self.check_regex(sheet.cell(row=row + 1, column = col).value,isin)
                    val = (val1,val2) if val1 and val2 else val1
                    if val:
                        data.append(val)
                else:
                    val = sheet.cell(row=row, column = col).value
                    if val:
                        data.append(self.check_regex(val,isin))
            data = [e for e in data if e]
            contains = False
            if len(data) > 6:
                for elem in self.table_content:
                    if data[0].find(elem[0]) >= 0:
                        contains = True
                if not contains:
                    self.table_content.append(data)
            else:
                self.other_content.append(data)

    def get_tabular_data(self):
        indexes = []
        width = 0
        n_rows = 0
        for row in self.table_content:
            new_width = len(row)
            if new_width != width:
                self.max_row = n_rows if n_rows > self.max_row else self.max_row
                n_rows = 0
                indexes.append({})
                self.tables.append({})
                for i,el in enumerate(row):
                    # print(el)
                    el = self.clean(el)
                    if el not in self.tables[-1]:
                        self.tables[-1][el] = []
                    indexes[-1][i] = el 
                width = new_width
            else:
                rows = []
                if tuple in [type(e) for e in row]:
                    row1 = []
                    row2 = []
                    for el in row:
                        if type(el) is tuple:
                            row1.append(el[0])
                            row2.append(el[1])
                        else:
                            row1.append(el)
                            row2.append(el)
                    rows.append(row1)
                    rows.append(row2)
                else:
                    rows.append(row)
                for row in rows:
                    for i,el in enumerate(row):
                        if i == 0 and el in self.tables[-1][indexes[-1][0]]:
                            break
                        else:
                            self.tables[-1][indexes[-1][i]].append((n_rows,el))
                    n_rows = n_rows + 1
        for t in self.tables:
            for key in list(t.keys()):
                if not len(t[key]):
                    t.pop(key)

    def find_join(self):
        join_info = []
        tables = enumerate(self.tables)
        for i,table in tables:
            for j in range(i+1,len(list(tables))):
                for key in table:
                    for  k in self.tables[j]:
                        if not (set(table[key]) - set(self.tables[j][k])):
                            join_info.append((i,j,key,k))
        return join_info

    def join_tables(self, table1, table2, col1, col2):
        new_table = {**self.tables[table1]}
        for key in self.tables[table2]:
            new_table[key] = []

        for i,el in self.tables[table1][col1]:
            for j,e in self.tables[table2][col2]:
                if e.replace('\n','').replace(' ','') == el.replace('\n','').replace(' ',''):
                    for key in self.tables[table2]:
                        for k,elem in self.tables[table2][key]:
                            if k == j:
                                new_table[key].append((i,elem))
        self.tables = new_table


                    
    # da individuare automaticamente le colonne e le tabelle da unire
    # def join_tables(self, col1 = "Underlying Shares", col2 = "Share Company"):
    #     new_table = {**self.tables[0]}
    #     for key in self.tables[1]:
    #         new_table[key] = []

    #     for i,el in self.tables[0][col1]:
    #         for j,e in self.tables[1][col2]:
    #             if e.replace('\n','').replace(' ','') == el.replace('\n','').replace(' ',''):
    #                 for key in self.tables[1]:
    #                     for k,elem in self.tables[1][key]:
    #                         if k == j:
    #                             new_table[key].append((i,elem))
    #     self.tables = new_table

    def save_to_file(self, path):
        wb = openpyxl.load_workbook(path) if os.path.isfile(path) else openpyxl.Workbook()
        sheet = wb.active
        progress = sheet.max_row

        for i,el in enumerate(self.tracciato):
            connection = True if type(el) is tuple else False
            col = el[0] if connection else el 
            key = el[1] if connection else el
            sheet.cell(row=1, column=i + 1 ).value = col 
            if key in self.tables:
                for k,el in self.tables[key]:
                    sheet.cell(row = k + 2, column = i + 1).value = el
            else:
                if self.constants[key]:
                    for k in range(self.max_row):
                        sheet.cell(row = k + 2,column = i + 1 ).value = self.constants[key]
        wb.save(path)


    def create_import(self,input_path = '.\\input\\excel1.xlsx', output_path='.\\output\\import.xlsx'):
        self.reset()
        wb = openpyxl.load_workbook(input_path) if os.path.isfile(input_path) else openpyxl.Workbook()
        sheet = wb.active
        self.extract_content(sheet)
        self.get_tabular_data()
        join_info = self.find_join()
        if join_info:
            print(join_info)
            for info in join_info:
                self.join_tables(*info)
        self.get_constants()
        self.save_to_file(output_path)

    def get_constants(self):
        for key in self.constants:
            for row in self.other_content:
                for el in row:
                    out = str(el).translate(str.maketrans("","", string.punctuation))
                    if str(key).lower() == str(out).lower():
                        self.constants[key] = row[-1] 
                        break
    

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

    def reset(self):
        self.table_content = []
        self.other_content = []
        self.tables = []
        self.max_row = 0
        #tracciato da prendere da un file esterno e inserire inizializzazione di constants in metodo
        self.tracciato = ["Issuer",	("Isin Code","ISIN Code"), "CFI Code", ("Underlying","Underlying Shares"),"Type of Certificate", ("Underlying ISIN","ISIN of Share"),	"Strike","Issue date", ("Expiry date","Exercise Settlement Date"), "Parity",	"Nominal Value",	("Quantity","No. of Securities issued"),"Exercise Type",	"Option Type","Exercise Lot",	"Marketing name",	"Price of Underlying",	("Reference Price","Issue Priceper Security"),	"Underlying currency",	"Euro-Hedged",	"1st Barrier",	"Barrier Observation",	"2nd Strike",	"2nd Barrier",	"Autocallability",	"Observation Autocallability",	"Participation %",	"Fee %",	"Long/Short",	"Bonus/Strike%",	"Cap",	"Floor",	"Coupon",	"Protection",	"Specialist Code",	"Quote Type",	"RFE Activation",	"Denomination Currency",	"Trading Currency",	"Settlement Currency",	"Settlement System",	"Leverage Number",	"Restrike %",	"Final Valuation Date",	"Professional",	"KID web link",	"Distribution Type",	"Type of Underlying",	"ACEPI Type",	"Instrument Name",	"Minimum Lot",	"Start Trading Date",	"Last Trading Date",	"Size Obligation",	"Threshold Profile ID",	"First Semaphore",	"First Error Description",	"FISN",	"Multiplier"	"File PDF"]
        self.constants = {}
        for el in self.tracciato:
            if type(el) is not tuple:
                self.constants[el] = ''


