from pdf_extractor.excel_adapter import read_concepts,export_values
from pdf_extractor.engine.extractor_engine import ExtractionEngine
import json 

class Controller:
    def __init__(self):
        self.concepts = read_concepts()
        self.engine = ExtractionEngine(concepts = self.concepts)
        self.results = None
    
    def get_concepts_keys(self):
        keys = [k for k in self.concepts.keys()]
        return keys

    def get_concepts_labels(self):
        max_len = max([len(key) for key in self.concepts.keys()])
        labels = {}
        for key in self.concepts:
            label = key + '\n'
            columns = [d for el in self.concepts[key] if el for d in el.split()]
            columns_label = ''
            line_len = 0
            for word in columns:
                if line_len < max_len:
                    columns_label += word
                    line_len += len(word)
                else:
                    columns_label += '\n'
                    line_len = 0
            labels[key] = label + columns_label
        return labels

    def extract(self, filename):
        self.results = self.engine.extract_values(filename)
        return self.results
    
    def save_state(self,filename,states, pdf):
        content = [self.results, states, pdf]
        filename = filename + '.json' if '.json' not in filename else filename
        with open(filename, 'w') as j:
            json.dump(content,j)
    
    def load_state(self, filename):
        with open(filename,'r') as j:
            content = json.load(j)
            self.results = content[0]
        return content

    def export(self, content, filename):
        filename = filename if '.xlsx' in filename else filename + '.xlsx'
        export_values(content, filename)
