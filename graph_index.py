#index
import os
import requests
from requests.auth import HTTPBasicAuth
import json
import copy

from graph_config import *

#Load env variables to access the Elasticsearch indices
GRAPH_USER = os.getenv("GRAPH_USER")
GRAPH_PASSWORD = os.getenv("GRAPH_PASSWORD")

#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#
#Simple functions that construct elasticsearch queries using templates
def generate_entity_query(entity):  
    query = ENT_START + entity + ENT_END
    return query

def generate_predicate_query(predicate):
    query = PRED_START + predicate + PRED_END
    return query

def generate_entity_predicate_query(entity, predicate):
    query = ENT_PRED_START + predicate + ENT_PRED_MID + entity + ENT_PRED_END
    return query

def generate_prompt_query(question, size):  
    query = PROMPT_START + question + PROMPT_MID + size + PROMPT_END
    return query
    
#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#
#Functions that query the relevant Elasticsearch index using the constructed templates
def index_entities(entity, predicate):
    url = GRAPH_URL
    headers = {"content-type": "application/json"}
    user = GRAPH_USER
    password = GRAPH_PASSWORD
    
    if predicate == "":
        query = generate_entity_query(entity)
    else:
        query = generate_entity_predicate_query(entity, predicate)
    r = requests.get(url, headers=headers, data=query, auth=HTTPBasicAuth(user, password))
    results = r.json()['hits']['hits']
    
    return results

def index_predicates(predicate):
    url = PREDICATE_URL
    headers = {"content-type": "application/json"}
    user = GRAPH_USER
    password = GRAPH_PASSWORD
    
    query = generate_predicate_query(predicate)
    r = requests.get(url, headers=headers, data=query, auth=HTTPBasicAuth(user, password))
    results = r.json()['hits']['hits']
    
    return results

def index_prompts(question, size):
    url = PROMPT_URL
    headers = {"content-type": "application/json"}
    user = GRAPH_USER
    password = GRAPH_PASSWORD
    
    query = generate_prompt_query(question, str(size))
    r = requests.get(url, headers=headers, data=query, auth=HTTPBasicAuth(user, password))
    results = r.json()['hits']['hits']
    
    return results