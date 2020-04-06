import math 
from nltk.corpus import stopwords
import pandas as pd
class TableClassificator:
    
    def __init__(self,threshold = 0.7):
        self.concepts = {}
        self.comparison = {}
        self.results = {}
        pass

    def find_results(self, tables):
        for concept in self.concepts:
             self._find_max_similarity(concept, tables)
        return self.results


    def train(self, concepts):
        for field in concepts:
            desc = concepts[field]
            entry = {}
            entry['vocab'] = [word for word in desc.lower().split() if word not in stopwords.words('italian')]
            entry['vector'] = self._create_vector(entry['vocab'], desc)
            self.concepts[field] =entry

    def _find_max_similarity(self, concept, tables):
        max_similarity = (0,0, None)
        for page,table,cols in tables:
            n_rows = table.shape[0]
            for i in range(n_rows):
                row = table.iloc[i,:]
                row_string = self._get_row_string(row)
                row_vector = self._create_vector(self.concepts[concept]['vocab'], row_string)
                similiarity = self._cosine_similarity(self.concepts[concept]['vector'], row_vector)
                if similiarity > max_similarity[0]:
                    new_max = (similiarity,f'page: {page}',i,[el for el in row if not pd.isna(el)],cols)
                    max_similarity = new_max
        self.results[concept] = max_similarity

                
	

    def _create_vector(self,vocab, text):
        text = [word for word in text.replace("'",' ').lower().split() if word not in stopwords.words('italian')]
        vector = []
        for word in vocab:
            if word in text:
                vector.append(float(1))
            else:
                vector.append(float(0))
        return vector

    def _get_row_string(self,row):
        fields = []
        for el in row:
            if type(el) is str and not self._is_int(el.replace('.','')):
                fields.extend(el.split())
        return ' '.join(fields)

                

    def _cosine_similarity(self, vA, vB):
        dotProduct = 0.0
        normA = 0.0
        normB = 0.0
        for i in range(len(vA)):
            dotProduct += (vA[i] * vB[i])
            normA += vA[i] ** 2
            normB += vB[i] ** 2
        dividend = ( math.sqrt(normA) * math.sqrt(normB))
        if dividend:
            return dotProduct / ( math.sqrt(normA) * math.sqrt(normB))
        else:
            return float(0)

    def _is_int(self, string):
        try:
            int(string)
            return True
        except:
            return False