#graph query

from unidecode import unidecode
from graph_utils import *

#Run full process to query graph from NL and return results
def query_graph(question):
    """
    Returns results to be put in table
    """
    question = unidecode(question)
    prompt_examples = index_prompts(question, 10)
    prompt = modular_prompt_build(prompt_examples)
    if (len(prompt) - 2) // 2 == 0:
        prompt = LLM_BACKUP_PROMPT.copy()

    ir = build_ir(question, prompt)
    
    exp_answer, formatted_triples, formatted_labels, error_notes, variables = format_triples(ir)
    sparql = gen_sparql(exp_answer, formatted_triples, variables)
    
    try:
        results = execute_sparql_processed(sparql, variables)
    except:
        results = "Query Error: Please Try Again"

    return results


#Function to only return SPARQL for a NL question
def create_sparql(question):
    """
    Returns results to be put in table
    """
    question = unidecode(question)
    prompt_examples = index_prompts(question, 10)
    prompt = modular_prompt_build(prompt_examples)
    
    if (len(prompt) - 2) // 2 == 0:
        prompt = LLM_BACKUP_PROMPT.copy()

        
    
    ir = build_ir(question, prompt)
    
    
    exp_answer, formatted_triples, formatted_labels, error_notes, variables = format_triples(ir)
    
    sparql = gen_sparql(exp_answer, formatted_triples, variables)
    
    if formatted_triples == [] or list(set(formatted_triples)) == [None]:
        return "Failed to construct triples."
    
    return sparql

#Return raw data results from SPARQL query
def query_graph_raw(question):
    """
    Returns raw sparql results 
    """
    question = unidecode(question)
    prompt_examples = index_prompts(question, 10)
    prompt = modular_prompt_build(prompt_examples)
    if (len(prompt) - 2) // 2 == 0:
        prompt = LLM_BACKUP_PROMPT.copy()

    ir = build_ir(question, prompt)
    exp_answer, formatted_triples, formatted_labels, error_notes, variables = format_triples(ir)
    sparql = gen_sparql(exp_answer, formatted_triples, variables)
    results = execute_sparql(sparql)

    return results