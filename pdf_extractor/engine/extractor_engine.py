from tabula import read_pdf
from pdf_extractor.engine.table_extractor import TableExtractor
from pdf_extractor.engine.text_highlighter import TextHighlighter
from pdf_extractor.excel_adapter import read_concepts
from pdf_extractor.utils import is_float,is_int,is_percentage
import openpyxl
from collections import OrderedDict
import string
from PyPDF2 import PdfFileReader
import os


class ExtractionEngine:
	def __init__(self, concepts = None, logger = None):
		self.logger =  logger
		self.tblext = TableExtractor()
		self.concepts = concepts if concepts else read_concepts()
		self.tblext.train(concepts)
		print(os.getcwd())
		os.environ['TABULA_JAR'] = os.getcwd() + "\\tabula-1.0.3-jar-with-dependencies.jar"

	def extract_values(self,filename):
		txthighlighter = TextHighlighter(filename, self.logger)
		tables = self._get_tables(filename)
		res = self.tblext.find_results(tables)
		return self._format_results(res, txthighlighter)
		
	def _get_tables(self, filename):
		t = [] 
		for i in range(1,self._get_num_pages(filename)):
			try:
				p = read_pdf(filename, pages = f'{i}', pandas_options = {'header' : None})
				if p:
					for table in p:
						t.append((i,table))
			except Exception:
				self.logger.exception(f"exception during table extraction at page {i}")
		return t
	
	def _get_num_pages(self, filename):
		reader = PdfFileReader(open(filename, 'rb'))
		return reader.getNumPages()
	
	def _format_results(self,results,highlighter):
		formatted = OrderedDict()
		for key in results:
			formatted[key] = []
			findings = results[key]
			for info in findings:
				if info[0]:
					page = info[1]
					strings = info[3]
					highlighter.highlight_text(page - 1, strings[0])
					for i in range(1,len(strings)):
						formatted[key].append((f'Page {page}: ', self._convert_string(str(strings[i]))))
		highlighter.save()
		return formatted
	
	def _convert_string(self,txt):
		if is_int(txt) or is_percentage(txt) or is_float(txt):
			return txt
		else:
			return 'text line'
		
			

		
