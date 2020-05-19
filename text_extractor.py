import pdfminer
from pdfminer.pdfparser import PDFParser
from pdfminer.pdfdocument import PDFDocument
from pdfminer.pdfpage import PDFPage
from pdfminer.pdfinterp import PDFResourceManager
from pdfminer.pdfinterp import PDFPageInterpreter
from io import StringIO
from pdfminer.layout import LAParams
from pdfminer.converter import TextConverter, PDFPageAggregator
import itertools 
import datetime

class TextExtractor:

	date_separators = ['/','-','.']

	def __init__(self, file):
		self.stream = open(file, 'rb')
		self.parser = PDFParser(self.stream)
		self.document = PDFDocument(self.parser)
		self.rsrmgr = PDFResourceManager()
		self.laparams = LAParams()
		self.codec = 'utf-8'
		self.output = StringIO()
		self.device = TextConverter(self.rsrmgr, self.output, laparams = self.laparams)
		self.interpreter = PDFPageInterpreter(self.rsrmgr, self.device)
		
		
	def get_page(self, index):
		gen = PDFPage.create_pages(self.document)
		page = next(itertools.islice(gen, index, None))
		self.interpreter.process_page(page)
		text = self.output.getvalue().splitlines()
		self.output.truncate(0)
		self.output.seek(0)
		return text

	def get_pages(self):
		for page in PDFPage.create_pages(self.document):
			self.interpreter.process_page(page)
		pages = self.output.getvalue().splitlines()
		return pages

	def validate_date(self,text, separators = None):
		separators = self.date_separators if not separators else self.date_separators.extend(separators)
		for separator in separators:
			if self._validate_date_separator(text,separator):
				return True 
		return False
	
	def _validate_date_separator(self,date_text, separator):
		try:
			datetime.datetime.strptime(date_text, f'%d{separator}%m{separator}%Y')
			return True
		except ValueError:
			return False
