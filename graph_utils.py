import SPARQLWrapper
from graph_index import *
from graph_llm import *
from graph_config import *


#Build LLM prompt from similar examples retrieved from index
def modular_prompt_build(examples):
    
    prompt = LLM_PROMPT_BASE.copy()
    for i in examples:
        u = {"role": "user", "content": i["_source"]['question']}
        a = {"role": "assistant", "content": i["_source"]['sbn']}
        prompt.append(u)
        prompt.append(a)
    return prompt

#Takes LLM output triples and formats them for SPARQL construction
def format_triples(ir):

    exp_answer, triples = split_ir(ir)
    
    formatted_triples = []
    formatted_labels = []
    error_notes = []
    variables = []
    
    if exp_answer == "LLM Error" or triples == "":
        return exp_answer, formatted_triples, formatted_labels, "LLM Error", variables
    
    if triples == []:
        return exp_answer, formatted_triples, formatted_labels, "No Triples Found, Cannot Generate SPARQL.", variables
        
    for t in triples:
        
        f_triples, f_labels, error, var = index_triples(t)
        
        formatted_triples.append(f_triples)
        formatted_labels.append(f_labels)
        error_notes.append(error)
        for x in var:
            variables.append(x)
    
    return exp_answer, formatted_triples, formatted_labels, list(set(error_notes)), list(set(variables))

#Splits intermediate representation that LLM outputs
def split_ir(ir):
    
    if "|" not in ir or "~" not in ir or "{" not in ir:
        return "LLM Error", ""
            
    ir = ir.replace('"', "")
    ir_split = ir.split(" | ")
    
    if len(ir_split) == 3:
        limit = ir[2]
        
    ex_answer = ir_split[0]
    triples = []
    if "} A {" in ir_split[1] and "} V {" in ir_split[1]:
        
        temp = ir_split[1].split("} A {")
        for i in temp:
            if "} V {" in ir_split:
                ortemp = ir_split[1].split("} V {")
                for j in ortemp:
                    triples.append(j)
            else:
                triples.append(i)

    elif "} A {" in ir_split[1]:
        
        triples = (ir_split[1].split("} A {"))
        
    elif "} V {" in ir_split[1]:
        
        triples = (ir_split[1].split("} V {"))
    else:
        triples = [ir_split[1]]
        
    return ex_answer, triples

#Predicate normalization
def handle_predicate(pid, label):
    alt_label, alt_pid = pred_rules(pid)
    if alt_label == "":
        pid = pid_rules(pid)
        return pid, label
    else:
        pid = pid_rules(alt_pid)
        label = alt_label
        return pid, label

#PID normalization
def pid_rules(predicate):
    if predicate in PID_RULES.keys():
        pid = PID_RULES.get(predicate)
    else:
        pid = "wdt:" + predicate
    
    return pid

#Predicate normalization
def pred_rules(predicate):
    predicate_label = ""
    pid = ""
    if predicate in PRED_RULES.keys():
        info = PRED_RULES.get(predicate)
        predicate_label = info[0]
        pid = info[1]
    
    return predicate_label, pid

#Predicate normalization
def pre_lookup_pred_rules(predicate):
    if predicate in PRE_LOOKUP_RULES.keys():
        return PRE_LOOKUP_RULES.get(predicate)
    else:
        return predicate

#Match natural language labels to the SPARQL IDs needed to execute against knowledge graph
def index_triples(triple):
    #split the triple into the entity/predicate parts
    t_split = triple.replace("{", "").replace("}", "").split(" ~ ")
    
    #if the split has anything other than 3 items it is incorrect
    if len(t_split) < 3 or len(t_split) > 3:
        return None, None, "Clause was not a triple.", [] 
    
    #initialize error and variables 
    error = None
    variables = []
    
    #extract the 3 labels of the triple
    p1 = t_split[0]
    p2 = pre_lookup_pred_rules(t_split[1])
    p3 = t_split[2]
    
    #set variable location flags
    flag1 = False
    flag2 = False
    flag3 = False
    
    #determine which positions have variables
    if "?" in p1:
        flag1 = True
    if "?" in p2:
        flag2 = True
    if "?" in p3:
        flag3 = True
        
    if flag1 and flag2 and flag3:
        return None, None, "No Entities or Predicates in triple", variables 
    
    elif not flag1 and not flag2 and not flag3:
        id1 = index_entities(p1, "")
        id3 = index_entities(p3, "")
        pvar = "P?" + p2.replace(" ", "_")
        variables.append(pvar)

        if len(id1) == 0 and len(id3) == 0:
            error = "Index couldn't find entities: " + p1 + ", " + p3
            return (), (), error, variables
        elif len(id1) == 0:
            error = "Index couldn't find entity: " + p1
            return (), (), error, variables
        elif len(id3) == 0:
            error = "Index couldn't find entity: " + p3
            return (), (), error, variables

        qid1 = id1[0]['_source']['qid']
        qid2 = id3[0]['_source']['qid']

        label1 = id1[0]['_source']['label']
        label2 = id3[0]['_source']['label']

        trip = ("wd:" + qid1 + " ?" + p2.replace(" ", "_") + " wd:" + qid2 + " .\n")
        label_trip = ("wd:" + label1.replace(" ", "_") + " ?" + p2.replace(" ", "_") + " wd:" + label2.replace(" ", "_") + " .\n")
        return trip, label_trip, error, variables

    #proceed with lookup 
    else:
        #lookup when predicate is the variable
        #includes checks in case it fails to find something
        if flag2:
            variables.append("P"+p2.replace(" ", "_"))
            
            if not flag1 and flag3:
                id1 = index_entities(p1, "")
                variables.append(p3)
                
                if len(id1) == 0:
                    error = "Index couldn't find entity: " + p1
                    return (), (), error, variables
                else:
                    qid1 = id1[0]['_source']['qid']
                    label1 = id1[0]['_source']['label']
                    trip = ("wd:" + qid1 + " " + p2.replace(" ", "_") + " " + p3 + " .\n")
                    label_trip = ("wd:" + label1.replace(" ", "_") + " " + p2 + " " + p3 + " .\n")
                    return trip, label_trip, error, variables
                    
            elif not flag3 and flag1:
                id3 = index_entities(p3, "")
                variables.append(p1)
                
                if len(id3) == 0:
                    error = "Index couldn't find entity: " + p3
                    return (), (), error, variables
                else:
                    qid2 = id3[0]['_source']['qid']
                    label2 = id3[0]['_source']['label']
                    trip = ( p1 + " " + p2.replace(" ", "_") + " wd:" + qid2 + " .\n")
                    label_trip = (p1 + " " + p2 + " wd:" + label2.replace(" ", "_") + " .\n")
                    return trip, label_trip, error, variables
                    
            else:
                id1 = index_entities(p1, "")
                id3 = index_entities(p3, "")
                
                
                if len(id1) == 0 and len(id3) == 0:
                    error = "Index couldn't find entities: " + p1 + ", " + p3
                    return None, None, error, variables
                elif len(id1) == 0:
                    error = "Index couldn't find entity: " + p1
                    return None, None, error, variables
                elif len(id3) == 0:
                    error = "Index couldn't find entity: " + p3
                    return None, None, error, variables
                    
                qid1 = id1[0]['_source']['qid']
                qid2 = id3[0]['_source']['qid']
                
                label1 = id1[0]['_source']['label']
                label2 = id3[0]['_source']['label']
                
                trip = ("wd:" + qid1 + " " + p2.replace(" ", "_") + " wd:" + qid2 + " .\n")
                label_trip = ("wd:" + label1.replace(" ", "_") + " " + p2 + " wd:" + label2.replace(" ", "_") + " .\n")
                return trip, label_trip, error, variables
       
        #lookup for when predicate is not the variable
        else:
           
            id2 = index_predicates(p2)
            
            if len(id2) == 0:
                error = "Index couldn't find predicate: " + p2
                return None, None, error, variables
            #when both entities are variables
            elif flag1 and flag3:
                pid, plabel = handle_predicate(id2[0]['_source']['pid'], id2[0]['_source']['label'])
                variables.append(p1)
                variables.append(p3)
                
                trip = ( p1 + " " + pid + " " + p3 + " .\n")
                label_trip = (p1 + " wdt:" + plabel.replace(" ", "_") + " " + p3 + " .\n")
                return trip, label_trip, error, variables
            else:
                #obtain pid and label following predicate rules
                
                pid, plabel = handle_predicate(id2[0]['_source']['pid'], id2[0]['_source']['label'])
                
                #if first entity not variable
                if not flag1:
                    id1_w = index_entities(p1, plabel)
                    id1_wo = index_entities(p1, "")
                    variables.append(p3)
                    
                    
                    if len(id1_wo) == 0:
                        error = "Index couldn't find entity: " + p1
                        return None, None, error, variables
                    elif len(id1_w) > 0:
                        score_w = id1_w[0]['_score']
                        label_w = id1_w[0]['_source']['label']

                        score_wo = id1_wo[0]['_score']
                        label_wo = id1_wo[0]['_source']['label']

                        scw = 5 * round(score_w/5)
                        scwo = 5 * round(score_wo/5)
                        
                        if score_wo == 0:
                            error = "Index couldn't find entity: " + p1
                            return None, None, error, variables
                        
                        elif scw >= scwo:
                            qid = id1_w[0]['_source']['qid']
                            trip = ( "wd:" + qid + " " + pid + " " + p3 + " .\n")
                            label_trip = ("wd:" + label_w.replace(" ", "_") + " wdt:" + plabel.replace(" ", "_") + " " + p3 + " .\n")
                            return trip, label_trip, error, variables
                            
                        elif score_wo > 0:
                            qid = id1_wo[0]['_source']['qid']
                            trip = ( "wd:" + qid + " " + pid + " " + p3 + " .\n")
                            label_trip = ("wd:" + label_wo.replace(" ", "_") + " wdt:" + plabel.replace(" ", "_") + " " + p3 + " .\n")
                            return trip, label_trip, error, variables
                            
                    else:
                        qid = id1_wo[0]['_source']['qid']
                        label_wo = id1_wo[0]['_source']['label']
                        trip = ( "wd:" + qid + " " + pid + " " + p3 + " .\n")
                        label_trip = ("wd:" + label_wo.replace(" ", "_") + " wdt:" + plabel.replace(" ", "_") + " " + p3 + " .\n")
                        return trip, label_trip, error, variables

                #if second entity not a variable
                else:
                    id3_w = index_entities(p3, plabel)
                    id3_wo = index_entities(p3, "")
                    variables.append(p1)
                    
                    if len(id3_wo) == 0:
                        error = "Index couldn't find entity: " + p3
                        return (), (), error, variables
                    elif len(id3_w) > 0:
                        score_w = id3_w[0]['_score']
                        label_w = id3_w[0]['_source']['label']

                        score_wo = id3_wo[0]['_score']
                        label_wo = id3_wo[0]['_source']['label']
                        
                        scw = 5 * round(score_w/5)
                        scwo = 5 * round(score_wo/5)
                        
                        if score_wo == 0:
                            error = "Index couldn't find entity: " + p3
                            return None, None, error, variables
                        
                        elif score_w >= score_wo:
                            qid = id3_w[0]['_source']['qid']
                            trip = ( p1 + " " + pid + " wd:" + qid + " .\n")
                            label_trip = (p1 + " wdt:" + plabel.replace(" ", "_") + " wd:" + label_w.replace(" ", "_") + " .\n")
                            return trip, label_trip, error, variables
                            
                        elif score_wo > 0:
                            qid = id3_wo[0]['_source']['qid']
                            trip = ( p1 + " " + pid + " wd:" + qid + " .\n")
                            label_trip = (p1 + " wdt:" + plabel.replace(" ", "_") + " wd:" + label_wo.replace(" ", "_") + " .\n")
                            return trip, label_trip, error, variables
                            
                    else:
                        qid = id3_wo[0]['_source']['qid']
                        label_wo = id3_wo[0]['_source']['label']
                        trip = ( p1 + " " + pid + " wd:" + qid + " .\n")
                        label_trip = (p1 + " wdt:" + plabel.replace(" ", "_") + " wd:" + label_wo.replace(" ", "_") + " .\n")
                        return trip, label_trip, error, variables

        return None, None, "Unexpected Error", variables
    
#Generate formal SPARQL from intermediate representation
def gen_sparql(expected_answer, ir_triples, variables):
        """
        Takes the qid and pid then puts them in the corresponding position in the sparql query.
        """
        if "FE" in expected_answer:
            
            if len(variables) == 1:
                var = variables[0]
                
                if "P?" in var:
                        var = var.replace("P?", "?")
                        query_start = "SELECT DISTINCT " + var + " " + var + "Label " + "\nWHERE {\n" 
                        query_end =  "?prop wikibase:directClaim " + var + ".\n?prop rdfs:label " + var + "Label .\nFILTER( LANG (" + var + "Label) = 'en')\n}"
                else:
                    query_start = "SELECT DISTINCT " + var + " " + var + "Label " + "\nWHERE {\n" 
                    query_end = var + " rdfs:label " + var + "Label . \nFILTER( LANG (" + var + "Label) = 'en')\n}"
                
                bulk = ""
                for i in ir_triples:
                    if i != None and i != ():
                        bulk += i
                        
                return query_start + bulk + query_end
            else:
                utils = ""
                var_labels = ""
                filters = ""
                for j in variables:
                    if "P?" in j:
                        var = j.replace("P?", "?")
                        temp =  "?prop wikibase:directClaim " + var + ".\n?prop rdfs:label " + var + "Label .\n"
                    else:
                        var = j
                        temp = j + " rdfs:label " + j + "Label .\n"
                    utils += temp
                    var_labels += var + " " + var + "Label "
                    filters += "FILTER( LANG (" + var + "Label) = 'en')\n"


                query_start = "SELECT DISTINCT " + var_labels +  "\nWHERE {\n" 

                bulk = ""
                for i in ir_triples:
                    if i != None and i != ():
                        bulk += i

                query_end = "FILTER( LANG (?varLabel) = 'en')\n}"
                return query_start + bulk + utils + filters + "}"
        else:
            
            return "Unexpected SPARQL form."

    
def execute_sparql_processed(query, variables):
        """
        Executes a query for simple questions on wikidata and returns results as processed JSON.
        """

        sparql = SPARQLWrapper.SPARQLWrapper('https://query.wikidata.org/sparql')
        sparql.setQuery(query)
        sparql.setReturnFormat(SPARQLWrapper.JSON)

        results = sparql.query().convert()

        if "ASK" in query:
            return results['boolean']
        else:
            varlist = []
            for v in variables:
                x = v.split("?")[1]
                varlist.append(x)
            #variables = [ele.replace("?", "") for ele in variables]
            variables = varlist
            processed_results = []
            for item in results['results']['bindings']:
                #print(item, '\n')
                for i in variables:

                    ilabel = i + "Label"
                    processed_results.append(item[ilabel]['value'])

        return processed_results

def execute_sparql(query):
        """
        Executes a query for simple questions on wikidata and returns results as processed JSON.
        """

        sparql = SPARQLWrapper.SPARQLWrapper('https://query.wikidata.org/sparql')
        sparql.setQuery(query)
        sparql.setReturnFormat(SPARQLWrapper.JSON)
        results = sparql.query().convert()
        
        return results