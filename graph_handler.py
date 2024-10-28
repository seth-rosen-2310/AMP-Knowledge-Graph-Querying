#graph_handler

from graph_query import *

class GraphHandler():

    def run_query(self, question):
        results = query_graph(question)
        return results
    
    def get_sparql(self, question):
        results = create_sparql(question)
        return results
    
    