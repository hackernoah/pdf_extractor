from tabula import read_pdf
from pdf_extractor.engine.table_extractor import TableExtractor
from pdf_extractor.engine.text_extractor import TextExtractor
from pdf_extractor.excel_adapter import read_concepts
from pdf_extractor.utils import is_float,is_int,is_percentage
import openpyxl
from collections import OrderedDict
import string
from PyPDF2 import PdfFileReader
import os


class ExtractionEngine:
	def __init__(self, concepts = None):
		self.txtext = None
		self.tblext = TableExtractor()
		self.concepts = concepts if concepts else read_concepts()
		self.tblext.train(concepts)
		print(os.getcwd())
		os.environ['TABULA_JAR'] = os.getcwd() + "\\tabula-1.0.3-jar-with-dependencies.jar"

	def extract_values(self,filename):
		tables = self._get_tables(filename)
		res = self.tblext.find_results(tables)
		return self._format_results(res)
		
	def _get_tables(self, filename):
		self.txtext = TextExtractor(filename)
		t = [] 
		for i in range(self._get_num_pages(filename)):
			try:
				p = read_pdf(filename, pages = f'{i}', pandas_options = {'header' : None})
				if p:
					page = self.txtext.get_page(i)
					cols = [el for el in page if self.txtext.validate_date(el)]
					for table in p:
						t.append((i,table,cols))
			except Exception:
				pass
		return t
	
	def _get_num_pages(self, filename):
		reader = PdfFileReader(open(filename, 'rb'))
		return reader.getNumPages()
	
	def _format_results(self,results):
		formatted = OrderedDict()
		for key in results:
			formatted[key] = []
			findings = results[key]
			for info in findings:
				if info[0]:
					page = info[1].translate(str.maketrans("","", "{}"))
					strings = info[3]
					for i in range(1,len(strings)):
						formatted[key].append((page, self._convert_string(str(strings[i]))))
		return formatted
	
	def _convert_string(self,txt):
		if is_int(txt) or is_percentage(txt) or is_float(txt):
			return txt
		else:
			return 'text line'
		
			

		
