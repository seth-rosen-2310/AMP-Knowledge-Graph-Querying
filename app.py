"""
This module contains the code for serving the combined QA
"""
import argparse
import json
import logging
import sys
import time

from graph_handler import *
from apiflask import APIFlask, Schema, abort
from apiflask.fields import String, Dict, List
from flask.views import MethodView
from flask import Flask, request, Response, jsonify


app = APIFlask(__name__, title='AMPhion API', version='1.0', docs_path='/openapi/docs')

#logger = logging.getLogger(__name__)  # pylint: disable=invalid-name

graph_service = GraphHandler()

    
    
app.config['DESCRIPTION'] = """
AMPhionQA is a system that allows for natural language querying of knowledge graphs. The two return options for user queries are retults from the Wisecube AI biomedical knowledge graph or the SPARQL query that can be used to answer the users question. 


"""    
    
# app.config['CONTACT'] = {
#     'name': '',
#     'url': '',
#     'email': ''
# }

# # openapi.info.license
# app.config['LICENSE'] = {
#     'name': '',
#     'url': ''
# }

# # openapi.info.termsOfService
# app.config['TERMS_OF_SERVICE'] = ''

app.config['TAGS'] = [
    {'name': 'Query', 'description': 'The description of the **Query** tag.'},
    {'name': 'SPARQL', 'description': 'The description of the **SPARQL** tag.'}
]

# # openapi.servers
# app.config['SERVERS'] = [
#     {
#         'name': 'Development Server',
#         'url': 'http://localhost:5000'
#     }
# #        ,
# #     {
# #         'name': 'Production Server',
# #         'url': 'http://api.example.com'
# #     },
# #     {
# #         'name': 'Testing Server',
# #         'url': 'http://test.example.com'
# #     }
# ]
    
# # openapi.externalDocs
# app.config['EXTERNAL_DOCS'] = {
#     'description': 'Find more info here',
#     'url': 'https://apiflask.com/docs'
# }


class QueryIn(Schema):
    question = String(required=True)
    
class QueryOut(Schema):
    results = List(String())
    
class SparqlOut(Schema):
    results = String()


@app.post('/AMPhion/query')
@app.input(QueryIn)
@app.output(QueryOut)
@app.doc(tags=['Query'])
def graph_query(json_data):
    """
    query a graph via natural language question
    """

    data = request.get_json()
    results = graph_service.run_query(data.get('question'))

#     log_blob = {"inputs": data, "outputs": results}
#     logger.info("results: %s", json.dumps(log_blob))
    return jsonify(results)

@app.post('/AMPhion/sparql')
@app.input(QueryIn)
@app.output(SparqlOut)
@app.doc(tags=['SPARQL'])
def graph_sparql(json_data):
    """
    generate SPARQL for a natural language question
    """

    data = request.get_json()
    results = graph_service.get_sparql(data.get('question'))

#     log_blob = {"inputs": data, "outputs": results}
#     logger.info("results: %s", json.dumps(log_blob))
    return jsonify(results)


