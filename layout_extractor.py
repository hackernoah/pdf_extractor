import pdfminer
from pdfminer.pdfparser import PDFParser
from pdfminer.pdfdocument import PDFDocument
from pdfminer.pdfpage import PDFPage
from pdfminer.pdfinterp import PDFResourceManager
from pdfminer.pdfinterp import PDFPageInterpreter
from pdfminer.layout import LTTextBoxHorizontal
from io import StringIO
from pdfminer.layout import LAParams
from pdfminer.converter import TextConverter, PDFPageAggregator
import itertools 
import datetime

class LayoutExtractor:

	date_separators = ['/','-','.']

	def __init__(self, file = "BILANCIO SANT'ANGELO 2018.pdf"):
		self.document = open(file, 'rb')
		#Create resource manager
		self.rsrcmgr = PDFResourceManager()
		# Set parameters for analysis.
		self.laparams = LAParams()
		# Create a PDF page aggregator object.
		self.device = PDFPageAggregator(self.rsrcmgr, laparams=self.laparams)
		self.interpreter = PDFPageInterpreter(self.rsrcmgr, self.device)
		# for page in PDFPage.get_pages(self.document):
		# 	self.interpreter.process_page(page)
		# 	# receive the LTPage object for the page.
		# 	layout = self.device.get_result()
		# 	for element in layout:
		# 		if isinstance(element, LTTextBoxHorizontal):
		# 			print(element.get_text())
				
		
	def get_page(self, index):
		gen = PDFPage.get_pages(self.document)
		page = next(itertools.islice(gen, index, None))
		self.interpreter.process_page(page)
		layout = self.device.get_result()
		return layout

	# def get_pages(self):
	# 	for page in PDFPage.create_pages(self.document):
	# 		self.interpreter.process_page(page)
	# 	pages = self.output.getvalue().splitlines()
	# 	return pages

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


le = LayoutExtractor()

