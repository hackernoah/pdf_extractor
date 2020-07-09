import fitz
from tkinter import messagebox

class TextHighlighter:
    def __init__(self,filename, logger):
        self.doc = fitz.open(filename)
        self.filename = filename

    def highlight_text(self,page_number, text):
        try:
            page = self.doc[page_number]
            text_instances = page.searchFor(str(text))
            for inst in text_instances:
                highlight = page.addHighlightAnnot(inst)
        except Exception:
            self.logger.exception(f"exception during highligth at page {page_number} of text: {text}")
            
    
    def save(self):
        while(True):
            try:
                self.doc.save(self.filename.replace('.pdf','') + ' - evidenziato.pdf',garbage=4, deflate=True, clean=True)
                return
            except Exception:
                self.logger.exception("error while saving highligthed file")
                answer = messagebox.askokcancel("Attenzione", "chiudi il pdf evidenziato per poter salvare quello creato dall'estrazione più recente")
                