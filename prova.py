from tabula import read_pdf
from table_classificator import TableClassificator
from text_extractor import TextExtractor
import openpyxl


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