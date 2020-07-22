from tabula import read_pdf
from table_classificator import TableClassificator
from text_extractor import TextExtractor
import openpyxl

def read_concepts (path = 'concetti.xlsx',sheet_name = 'concepts'):
    le = openpyxl.load_workbook(path, data_only=True)
    sheet = le.get_sheet_by_name(sheet_name)
    concepts = [(sheet.cell(row = i, column = 1).value, sheet.cell(row = i, column = 2).value) for i in range(1,sheet.max_row+1) if sheet.cell(row = i, column = 1).value ]
    return dict(concepts)

conv = TextExtractor()
t = [] 
for i in range(235):
	try:
		p = read_pdf("BILANCIO SANT'ANGELO 2018.pdf", pages = f'{i}', pandas_options = {'header' : None})
		if p:
			page = conv.get_page(i)
			cols = [el for el in page if conv.validate_date(el)]
			for table in p:
				t.append((i,table,cols))
	except Exception:
		pass

concepts = read_concepts()
c = TableClassificator()
c.train(concepts)
r = c.find_results(t)

# from tkinter import Tk
# from pdfviewer import PDFViewer


# root = Tk()
# PDFViewer()
# root.mainloop()