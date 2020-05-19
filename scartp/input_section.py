from kivy.app import App
from kivy.uix.gridlayout import GridLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from .pdf_document_widget import PDFDocumentWidget


class InputSection(BoxLayout):
 
    def __init__(self, **kwargs):
        super(InputSection, self).__init__(**kwargs)
        self.orientation = 'vertical'
        self.add_widget(ConceptWidget())
        self.add_widget(ConceptWidget())
        self.add_widget(ConceptWidget())

class ConceptWidget(GridLayout):
    def __init__(self, **kwargs):
        super(GridLayout, self).__init__(**kwargs)
        self.row = 1
        self.add_widget(Label(text='User Name'))
        self.username = TextInput(multiline=False)
        self.add_widget(self.username)
        self.add_widget(Label(text='password'))
        self.password = TextInput(password=True, multiline=False)
        self.add_widget(self.password)