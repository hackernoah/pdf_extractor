from tkinter import *
from tkinter import messagebox
from tkinter import ttk
from pdf_extractor.utils import is_float,is_int,is_percentage,to_float,to_int, has_parenthesis, delete_parenthesis, to_percentage

class Concept:

    def __init__(self, root, row = 0, column = 0, label = 'N/A' ):
        self.root = root
        self.label = label
        self.row = row
        # self.position = {
        #     'row': row, 
        #     'column': column
        # }
        # self.frame = ttk.Frame(self.root)
        # self.frame.grid(**self.position, columnspan = 5, pady=10)
        self.field_lbl = Label(self.root, text = self.label, font=('Arial', 12, 'normal'), justify='left')
        self.field_lbl.grid(row = self.row, column =0,sticky='nw') 
        self.options_lst = Listbox(self.root, height = 4, width = 25,font=('Arial', 12, 'normal') )
        self.options_lst.grid(row = self.row, column = 1, columnspan =2, pady=10)
        self.options_lst_scrollbar = Scrollbar(self.root, orient=VERTICAL, command = self.options_lst.yview)
        self.options_lst_scrollbar.grid(row = self.row, column=3, sticky='ns')
        self.options_lst.configure(yscrollcommand= self.options_lst_scrollbar.set)
        self.options_lst.bind('<Double-Button>', self._selection)
        self.options_lst.bind("<MouseWheel>", self._on_mousewheel)
        self.multiply_button = ttk.Button(self.root,text = 'x1000',command= self._multiply )
        self.multiply_button.grid(row = self.row, column = 4)
        self.multiply_button.configure(width=5)
        self.value_var = StringVar()
        self.value_entry = Entry(self.root, textvariable = self.value_var)
        self.value_entry.grid(row = self.row, column = 5)
        self.divide_button = ttk.Button(self.root,text = '/1000', command= self._divide )
        self.divide_button.grid(row = self.row, column = 6)
        self.divide_button.configure(width=5)
        self.confirm_var = IntVar()
        self.confirm_check = Checkbutton(self.root, text='Confirm', variable=self.confirm_var, command=self._confirm)
        self.confirm_check.grid(row=self.row, column = 7)
        self.values = []
        self.selected_index = -1
        self.saved_state =  None
    
    def _on_mousewheel(self, event):
        self.options_lst.yview_scroll(int(-1*(event.delta/12000)), "units")
    
    def set_results(self,results):
        self.values = results
        self.options_lst.delete(0,END)
        for value in self.values:
            self.options_lst.insert(END, str(value[0]) + ' ' + str(value[1]))
    
    def get_state(self,save=True):
        state = [self.value_var.get(), self.confirm_var.get()]
        if save:
            self.saved_state = state
        return state
    
    def set_state(self, state):
        if state:
            self.value_var.set(state[0])
            self.confirm_var.set(state[1])
            self.get_state()
            self._confirm()
    
    def is_saved(self):
        cur_state = self.get_state(save=False)
        if not self.saved_state:
            if not cur_state[0] and not cur_state[1]:
                return True
            else:
                return False
        else:
            if cur_state[0] != self.saved_state[0] or cur_state[1] != self.saved_state[1]:
                return False 
            else:
                return True
    
    def is_confirmed(self):
        return True if self.confirm_var.get() else False

    def get_value(self):
        if self.is_confirmed():
            value = self.value_var.get()
            if is_int(value):
                return to_int(value)
            elif is_float(value):
                return to_float(value)
            elif is_percentage(value):
                return to_percentage(value)
            else:
                return None
        else:
            return None
            
    
    def _selection(self, event):
        selection = self.options_lst.curselection()
        if selection:
            self.value_entry.delete(0,END)
            self.value_entry.insert(END, self.values[selection[0]][1])

    def _multiply(self):
        value = self.value_var.get()
        new_value = 0
        if is_percentage(value):
            return
        elif is_int(value):
            if has_parenthesis(value):
                temp_value = delete_parenthesis(value)
                new_value = temp_value + '.000' if '.' in temp_value else str(to_int(temp_value) * 1000).replace('-','')
                new_value = '(' + new_value + ')'
            else:
                new_value = value + '.000' if '.' in value else to_int(value) * 1000
        elif is_float(value):
            if has_parenthesis(value):
                temp_value = delete_parenthesis(value)
                temp_value = str(to_float(temp_value) * 1000.0).replace('.',',').replace('-','')
                new_value = '(' + temp_value + ')'
            else:
                new_value = str(to_float(value) * 1000.0).replace('.',',')
        self.value_entry.delete(0,END)
        self.value_entry.insert(END,new_value)

    def _divide(self):
        value = self.value_var.get()
        new_value = 0
        if is_percentage(value):
            return 
        elif is_int(value):
            if has_parenthesis(value):
                temp_value = delete_parenthesis(value)
                new_value = ''.join([temp_value[i] for i in range(len(temp_value) - 4)]) if '.' in temp_value else str(to_int(temp_value) / 1000)
                new_value = '(' + new_value + ')'
            else:
                new_value = ''.join([value[i] for i in range(len(value) - 4)]) if '.' in value else to_int(value) / 1000
        elif is_float(value):
            if has_parenthesis(value):
                temp_value = delete_parenthesis(value)
                temp_value = str(to_float(temp_value) / 1000.0).replace('.',',')
                new_value = '(' + temp_value + ')'
            else:
                new_value = str(to_float(value) / 1000.0).replace('.',',')
        self.value_entry.delete(0,END)
        self.value_entry.insert(END,new_value)

    def _confirm(self):
        if self.confirm_var.get():
            self.value_entry.configure(state=DISABLED)
        else:
            self.value_entry.configure(state=NORMAL)