import openpyxl
from openpyxl.worksheet.merge import MergedCell
import os
import json
import re
import collections
import string

class CertificateParer:

    def __init__(self, path):
        input_base_path = '.\\input\\'
        output_base_path = '.\\output\\'
        path = input_base_path + "excel1.xlsx"
        wb = openpyxl.load_workbook(path) if os.path.isfile(path) else openpyxl.Workbook()
        sheet = wb.active
        table_content = []
        other_content = []

#creare classi di sta roba

def clean(txt):
    elems = txt.split()
    result = []
    stopwords = ['of','at']
    for i,el in enumerate(elems):
        if len(el) < 4 and el not in stopwords and i > 0:
            result[-1] = result[-1] + el 
        else:
            result.append(el)
    return ' '.join(result)

def check_regex(val, regex):
    result = val.replace(' ','') if re.match(regex, str(val).replace(' ','')) else val
    return result

def join(key1,key2):
    for i,elem in enumerate(data[key2]):
        new = (data[key1][i][0],data[key2][i][1])
        print(new)
        data[key2][i] = new

input_base_path = '.\\input\\'
output_base_path = '.\\output\\'
path = input_base_path + "excel1.xlsx"
wb = openpyxl.load_workbook(path) if os.path.isfile(path) else openpyxl.Workbook()
sheet = wb.active
table_content = []
other_content = []


vertical = sheet.max_row
horizontal = sheet.max_column

isin = re.compile(r'\b([A-Z]{2})((?![A-Z]{10}\b)[A-Z0-9]{6,10})\b')
for row in range(1,vertical):
    data = []
    table = False
    merged = True if type(sheet.cell(row=row + 1, column = 1)) == MergedCell else False
    for col in range(1,horizontal):
        if merged:
            val1 = check_regex(sheet.cell(row=row, column = col).value,isin)
            val2 = check_regex(sheet.cell(row=row + 1, column = col).value,isin)
            val = (val1,val2) if val1 and val2 else val1
            if val:
                data.append(val)
        else:
            val = sheet.cell(row=row, column = col).value
            if val:
                data.append(check_regex(val,isin))
    data = [e for e in data if e]
    contains = False
    if len(data) > 6:
        for elem in table_content:
            if data[0].find(elem[0]) >= 0:
                contains = True
        if not contains:
            table_content.append(data)
    else:
        other_content.append(data)

with open(output_base_path + 'content.txt','w',encoding="utf-8") as f:
    for line in table_content:
        f.write(' ; '.join([str(el) for el in line]).replace('\n','') + '\n\n')
    for line in other_content: 
        f.write(' ; '.join([str(el) for el in line]).replace('\n','') + '\n\n')

data = []
indexes = []
width = 0
j = 0
for row in table_content:
    new_width = len(row)
    if new_width != width:
        j = 0
        indexes.append({})
        data.append({})
        for i,el in enumerate(row):
            # print(el)
            el = clean(el)
            if el not in data[-1]:
                data[-1][el] = []
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
                if i == 0 and el in data[-1][indexes[-1][0]]:
                    break
                else:
                    data[-1][indexes[-1][i]].append((j,el))
            j = j + 1
print(j)

with open('tables.json','w',encoding="utf-8") as f:
    json.dump(data, f)

tracciato = ["Issuer",	("Isin Code","ISIN Code"), "CFI Code", ("Underlying","Underlying Shares"),"Type of Certificate", ("Underlying ISIN","ISIN of Share"),	"Strike","Issue date", ("Expiry date","Exercise Settlement Date"), "Parity",	"Nominal Value",	("Quantity","No. of Securities issued"),"Exercise Type",	"Option Type","Exercise Lot",	"Marketing name",	"Price of Underlying",	("Reference Price","Issue Priceper Security"),	"Underlying currency",	"Euro-Hedged",	"1st Barrier",	"Barrier Observation",	"2nd Strike",	"2nd Barrier",	"Autocallability",	"Observation Autocallability",	"Participation %",	"Fee %",	"Long/Short",	"Bonus/Strike%",	"Cap",	"Floor",	"Coupon",	"Protection",	"Specialist Code",	"Quote Type",	"RFE Activation",	"Denomination Currency",	"Trading Currency",	"Settlement Currency",	"Settlement System",	"Leverage Number",	"Restrike %",	"Final Valuation Date",	"Professional",	"KID web link",	"Distribution Type",	"Type of Underlying",	"ACEPI Type",	"Instrument Name",	"Minimum Lot",	"Start Trading Date",	"Last Trading Date",	"Size Obligation",	"Threshold Profile ID",	"First Semaphore",	"First Error Description",	"FISN",	"Multiplier"	"File PDF"]

persistent_data = {}

for el in tracciato:
    if type(el) is not tuple:
        persistent_data[el] = ''

for key in persistent_data:
    for row in other_content:
        for el in row:
            out = str(el).translate(str.maketrans("","", string.punctuation))
            if str(key).lower() == str(out).lower():
                persistent_data[key] = row[-1] 
                print(f'{out}: {row[-1]}\n')
                break

for d in data:
    for key in list(d.keys()):
        if not len(d[key]):
            d.pop(key)

new_data = {**data[0]}

col1 = "Underlying Shares"
col2 = "Share Company"


for key in data[1]:
    new_data[key] = []

#da capire automaticamente
for i,el in data[0][col1]:
    for j,e in data[1][col2]:
        if e.replace('\n','').replace(' ','') == el.replace('\n','').replace(' ',''):
            for key in data[1]:
                for k,elem in data[1][key]:
                    if k == j:
                        new_data[key].append((i,elem))


out = output_base_path + "import.xlsx"
wb = openpyxl.load_workbook(out) if os.path.isfile(out) else openpyxl.Workbook()
if "Output" in wb.sheetnames:
    wb.remove(wb["Output"])
wb.create_sheet("Output")
sheet = wb["Output"] 
progress = sheet.max_row

#da prendere automaticamente

for i,el in enumerate(tracciato):
    connection = True if type(el) is tuple else False
    col = el[0] if connection else el 
    key = el[1] if connection else el
    sheet.cell(row=1, column=i + 1 ).value = col 
    if key in new_data:
        for k,el in new_data[key]:
            sheet.cell(row = k + 2, column = i + 1).value = el
    else:
        if persistent_data[key]:
            for k in range(j):
                sheet.cell(row = k + 2,column = i + 1 ).value = persistent_data[key]


# for i,key in enumerate(new_data.keys(
v):
#     sheet.cell(row=1, column=i + 1 ).value = key 
#     for j,el in new_data[key]:
#         sheet.cell(row = j + 2, column = i + 1).value = el


wb.save(out)

