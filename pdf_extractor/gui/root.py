from tkinter import *
from tkinter import filedialog
from tkinter import messagebox
from tkinter import ttk
from pdf_extractor.gui.concept import Concept
from pdf_extractor.gui.controller import Controller
from collections import OrderedDict
import os
import logging

class ExtractorGui:

    def __init__(self, root):
        logging.basicConfig(filename='.\\app.log', filemode='a',format='%(asctime)s - %(levelname)s: %(message)s', level=logging.DEBUG)
        self.logger = logging.getLogger()
        try:
            self.controller = Controller(self.logger)
            self.concepts_keys = self.controller.get_concepts_keys()
            self.concepts_labels = self.controller.get_concepts_labels()
            self.root = root
            self.root.title('PDF Extractor')
            self.root.protocol("WM_DELETE_WINDOW", self._on_close)
            self.root.geometry('1300x768')
            # self.root.maxsize(height = 1000, width = 630)
            self.btn_frame = ttk.Frame(self.root)
            self.btn_frame.grid(row = 0, column = 0,columnspan = 5,pady=10, padx=10,sticky='W')
            self.label_frame = ttk.Frame(self.root)
            self.label_frame.grid(row=1, column =0, columnspan =5, pady= 10, padx=10, sticky='w')
            self.concept_frame = ttk.Frame(self.root)
            self.concept_frame.grid(row = 2, column = 0, rowspan =10, columnspan = 8,sticky='W')
            self.config_frame = ttk.LabelFrame(self.root, text = 'Configurazione')
            self.config_frame.grid(row = 2, column = 9, columnspan = 2, rowspan = 2, padx=20, sticky='ns')
            self.error_frame = ttk.Frame(self.root)
            self.error_frame.grid(row = 4, column = 11)
            #concepts
            self.concept_frame.grid_rowconfigure(0, weight=1)
            self.concept_frame.grid_columnconfigure(0, weight=1)
            self.canvas = Canvas(self.concept_frame)
            self.canvas.grid(row = 0, column = 0, rowspan =10,columnspan = 5,sticky='news')
            self.scrollbar = Scrollbar(self.concept_frame, orient='vertical', command=self.canvas.yview)
            self.scrollbar.grid(row=0, column  = 5, rowspan=10, sticky='ns')
            self.canvas.configure(yscrollcommand = self.scrollbar.set,height = 668, width = 900)
            self.inner_frame= Frame(self.canvas)
            self.canvas.create_window((0,0), window=self.inner_frame, anchor = 'nw')
            self.inner_frame.bind("<Configure>", self._on_frame_configure)
            self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)
            #configuration
            self.abi_lbl = Label(self.config_frame, text = 'Codice ABI', font=('Arial', 12, 'normal'), padx=10 )
            self.abi_lbl.grid(row = 0, column =0, sticky = 'w', padx=10, pady=10)
            self.abi_var = StringVar()
            self.abi_entry = Entry(self.config_frame, textvariable = self.abi_var)
            self.abi_entry.grid(row = 0, column = 1,padx=10)
            self.date_lbl = Label(self.config_frame, text = 'Data', font=('Arial', 12, 'normal'), padx=10 )
            self.date_lbl.grid(row = 1, column =0, sticky = 'w', padx=10, pady=10)
            self.date_var = StringVar()
            self.date_entry = Entry(self.config_frame, textvariable = self.date_var)
            self.date_entry.grid(row = 1, column = 1,padx=10)
            self.op_lbl = Label(self.config_frame, text = 'Op', font=('Arial', 12, 'normal'), padx=10 )
            self.op_lbl.grid(row = 2, column =0, sticky = 'w', padx=10, pady=10)
            self.op_var = StringVar()
            self.op_entry = Entry(self.config_frame, textvariable = self.op_var)
            self.op_entry.grid(row = 2, column = 1,padx=10)
            #buttons
            self.choose_btn = ttk.Button(self.btn_frame,text='Choose file', command = self._choose)
            self.choose_btn.grid(row=0, column = 0,sticky='W')
            self.save_btn  = ttk.Button(self.btn_frame,text='Save', command=self._save)
            self.save_btn.grid(row=0, column = 1,sticky='W')
            self.load_btn = ttk.Button(self.btn_frame, text='Load', command=self._load)
            self.load_btn.grid(row=0, column = 2)
            self.extract_btn = ttk.Button(self.btn_frame,text='Extract', command = self._extract)
            self.extract_btn.grid(row=0, column = 3,sticky='W')
            self.export_btn  = ttk.Button(self.root,text='Export', command = self._export)
            self.export_btn.grid(row=4, column = 9,sticky='W', padx=20)
            #errors
            self.export_error_label = Label(self.error_frame, text="Error during export", foreground="red")
            self.extraction_error_label = Label(self.error_frame, text="Error during extraction", foreground="red")
            #file label
            self.file_label_var = StringVar()
            self.file_label = Label(self.label_frame, textvariable = self.file_label_var, font=('Arial', 12, 'normal'), padx=10 )
            #concepts
            self.concepts = {}
            for i,key in enumerate(self.concepts_keys):
                self.concepts[key] = Concept(self.inner_frame, row=i, label=self.concepts_labels[key], canvas=self.canvas, canvas_command= self._on_mousewheel, logger = self.logger)
            self.logger.info(f"{len(self.concepts.keys())} concepts have been added to gui")
            self.temp_pdfname = ''
            self.pdfname = ''
            self.filename = ''
            self.changed_conpets = False
        except Exception:
            self.logger.exception("error in main loop")

    def _on_frame_configure(self,event):
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))
    
    def _on_mousewheel(self, event):
        self.canvas.yview_scroll(int(-1*(event.delta/120)), "units")

    def _extract(self):
        if self.pdfname and self.pdfname != self.temp_pdfname:
            answer = messagebox.askyesno("Attenzione", "Stai cercando di estrarre dati da un nuovo pdf, vuoi continuare?")
            if answer:
                self._extract_impl()
        else:
            self._extract_impl()
    
    def _extract_impl(self):
        self.extraction_error_label.grid_remove()
        try:
            pdfname = self.temp_pdfname.replace('/','\\')
            res = self.controller.extract(pdfname)
            self._set_results(res)
            os.startfile(pdfname.replace('.pdf','') + ' - evidenziato.pdf')
            self.pdfname = pdfname
            self.changed_conpets = True
        except Exception:
            self.logger.exception(f"excetion during extraction")
            self.extraction_error_label.grid(row=2, column=1)

    def _set_results(self,res):
        if res:
            for key in res:
                try:
                    self.concepts[key].set_results(res[key])
                except Exception:
                    self.logger.exception("exception occurred")
    
    def _set_states(self, states):
        for key in states:
            try:
                self.concepts[key].set_state(states[key])
            except Exception:
                self.logger.exception("exception occurred")
    
    def _choose(self):
        self.temp_pdfname = filedialog.askopenfilename(initialdir = "C:\\",title = "Seleziona file",filetypes = (("pdf files","*.pdf"),('All files', '*')))
        if self.temp_pdfname:
            self.file_label_var.set('File scelto: ' + os.path.basename(os.path.normpath(self.temp_pdfname)))
            self.file_label.grid(row=0, column = 0, columnspan = 4)
            self.logger.info(f"file chosen with name: {self.file_label_var.get()}")

    def _save(self):
        try:
            if self.pdfname:
                filename = self.filename if self.filename else filedialog.asksaveasfilename(initialdir = "C:\\",title = "Selva stato della macchina",filetypes = (("json files","*.json"),('All files', '*')))      
                states = {}
                for key in self.concepts:
                    states[key] = self.concepts[key].get_state()
                self.changed_conpets = False
                self.controller.save_state(filename, states, self.pdfname)
                self.filename = filename
                self.logger.info("state of machine saved on file {filename}")
        except Exception:
            self.logger.exception("exception during save")
    
    def _load(self):
        fn = filedialog.askopenfilename(initialdir = "C:\\",title = "Seleziona file",filetypes = (("json files","*.json"),('All files', '*')))
        if fn:
            content = self.controller.load_state(fn)
            self.pdfname = content[2]
            self._set_results(content[0])
            self._set_states(content[1])
            self.filename = fn
            self.file_label_var.set('File scelto: ' + os.path.basename(os.path.normpath(self.pdfname)))
            self.file_label.grid(row=0, column = 0, columnspan = 4)
    
    def _export(self):
        self.export_error_label.grid_remove()
        try:
            if not self.pdfname:
                messagebox.askokcancel('Attenzione',"Non c'è nulla da esportare")
                return
            error_mex = ''
            uncofirmed_values = False 
            missing_config = []
            export_content = OrderedDict()
            export_content['Op'] = self.op_var.get() if self.op_var.get() else None
            export_content['CompanyId'] = self.abi_var.get() if self.abi_var.get() else None
            export_content['ReferenceDate'] = self.date_var.get() if self.date_var.get() else None
            for key in export_content:
                if export_content[key] is None:
                    missing_config.append(key)
            for key in self.concepts:
                concept = self.concepts[key]
                if not concept.is_confirmed():
                    uncofirmed_values = True
                export_content[key] = concept.get_value()
            error_mex = ''
            if uncofirmed_values: 
                error_mex += 'Hai valori non confermati.'
            if missing_config:
                if error_mex:
                    error_mex += 'Inoltre '
                error_mex += 'Hai omesso i seguenti valori: '
                for el in missing_config:
                    error_mex += el +', '
            if error_mex:
                answer = messagebox.askyesno('Attenzione', error_mex + 'Sicuro di voler esportare comunque?')
                if not answer:
                    return
            filename = ''
            ans = messagebox.askyesno("Nuovo File","Desideri utilizzare un file già esistente?")
            if ans:
                filename = filedialog.askopenfilename(initialdir = "C:\\",title = "Selva stato della macchina",filetypes = (("xlsx files","*.xlsx"),('All files', '*')))
            else:
                filename = filedialog.asksaveasfilename(initialdir = "C:\\",title = "Selva stato della macchina",filetypes = (("xlsx files","*.xlsx"),('All files', '*')))
            self.controller.export(export_content, filename)
        except Exception:
            self.logger.exception("error during export")
            self.export_error_label.grid(row=1, column=1)
            

    def _unsaved_changes(self):
        if self.pdfname:
            for key in self.concepts:
                if not self.concepts[key].is_saved():
                    return True 
            return self.changed_conpets
        else:
            return False
    
    def _on_close(self):
        if self._unsaved_changes():
            answer = messagebox.askyesnocancel("Esci", "Hai delle modifiche non salvate, vuoi salvarle?")
            if answer:
                self._save()
                self.root.destroy()
            elif answer is None:
                pass
            else:
                self.root.destroy()
        else:
            self.root.destroy()


root = Tk()
root_gui = ExtractorGui(root)
root.mainloop()
        