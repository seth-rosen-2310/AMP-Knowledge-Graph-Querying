#graph_config

#These are set as environment variables. Could set them here for local use/user.
#GRAPH_USER = ""
#GRAPH_PASSWORD = ""
#API_KEY = ""

#Elasticsearch URLs for searching corresponding index - not active / need to be set       
GRAPH_URL = ""
PREDICATE_URL = ""
PROMPT_URL = ""

#query structure needed for entity linking when triple doesn't have a predicate
ENT_START = '''
        {
        "query": {
            
            "bool":{ 
                "should": [
                {
            "multi_match" : {
            "query" : "'''

ENT_END = '''",
            "fields":     ["label", "aliases"],
            "operator":   "or" 
            }
        }
        ]
        }},
        "_source": ["qid", "label", "predicates","in_predicates", "out_predicates", "degree", "aliases"]
        }
        '''

PRED_START = '''
    {
      "query": {
           "bool":{
               "should": [
            {
        "multi_match" : {
          "query" : "'''

PRED_END = '''",
          "fields":     ["label", "aliases"],
          "operator":   "or" 
        }
      }
      ]
       }},
       "_source": ["label", "pid", "occurrences"]
    }
    '''
#query structure needed for entity linking when triple does have a predicate
ENT_PRED_START = '''
        {
        "query": {
            
            "bool":{
            "filter": {
            "terms" : { "predicates.raw" : ["'''

ENT_PRED_MID = '''"] }
        }, 
                "should": [
                {
            "multi_match" : {
            "query" : "'''

ENT_PRED_END = '''",
            "fields":     ["label", "aliases"],
            "operator":   "or" 
            }
        }
        ]
        }},
        "_source": ["qid", "label", "predicates","in_predicates", "out_predicates", "degree", "aliases"]
        }
        '''
    
#query structure needed for modular prompting
PROMPT_START = '''
        {
        "query": {
            
            "bool":{ 
                "should": [
                {
            "multi_match" : {
            "query" : "'''

PROMPT_MID = '''",
            "fields":     ["question"],
            "operator":   "or" 
            }
        }
        ]
        }},
        "_source": ["question", "sbn"],
        "size":"'''

PROMPT_END = '''"
        }
        '''
#__________________________________________________________________#

#Normalization rules for some cases that frequently have issues mapping

PID_RULES = {
            "P279":"wdt:P279*",
            "P129":"wdt:P129|^wdt:P129",
            "P2293":"wdt:P2293|^wdt:P2293",
            "P2175":"wdt:P2175|^wdt:P2176",
            "P2176":"wdt:P2176|^wdt:P2175",
            "P688":"wdt:P688|^wdt:P702",
            "P702":"wdt:P702|^wdt:P688",
            "P828":"wdt:P828|^wdt:P1542",
            "P1542":"wdt:1542|^wdt:P828",
            "P31":"wdt:P31|wdt:P279"
            }

PRED_RULES = {
             "P2670":["has part(s)", "P527"],
             "P179":["part of", "P361"],
             "P6532":["symptoms and signs", "P780"],
             "P735":["has active ingredient", "P3781"],
             "P1478":["has cause", "P828"],
             "P5422":["mode of inheritance", "P1199"]
             }

PRE_LOOKUP_RULES = {
                "mode of action":"subject has role",
                "inhibits":"physically interacts with",
                "target":"physically interacts with",
                "targets":"physically interacts with",
                "primarily targets":"physically interacts with",
                "mechanism of action":"subject has role",
                "contains":"has active ingredient"
                }

#__________________________________________________________________#


LLM_PROMPT_BASE = [
        {"role": "system", "content": "You are a chatbot who's only job is to translate a given question into set builder notation using a provided format schema."},
        {"role": "user", "content": "The set builder notation schema I want you to use is:" + """
            simple query: FE ?item | {entity ~ predicate ~ ?item}
            simple and query: FE ?item | {entity ~ predicate ~ ?item} A {?item ~ predicate ~ entity}
            simple or query: FE ?item | {entity ~ predicate ~ option1} V {entity ~ predicate ~ option2}" 
            """}
        ]

LLM_BACKUP_PROMPT = [
        {"role": "system", "content": "You are a chatbot who's only job is to translate a given question into set builder notation using a provided format schema."},
        {"role": "user", "content": "The set builder notation schema I want you to use is:" + """
            simple query: FE ?var | {entity ~ predicate ~ ?var}
            simple and query: FE ?var | {entity ~ predicate ~ ?var} A {?var ~ predicate ~ entity}
            simple or query: FE ?var | {entity ~ predicate ~ option1} V {entity ~ predicate ~ option2}" 
            """},
        {"role": "user", "content": "What are the symptoms of the common cold?"},
        {"role": "assistant", "content": "FE ?var | {common cold ~ symptoms or signs ~ ?var}"},
        {"role": "user", "content": "What are the symptoms of the common cold?"},
        {"role": "assistant", "content": "FE ?var | {?x ~ subclass of ~ common cold} A {?x ~ cause and effect ~ ?var}"},
        {"role": "user", "content": "Is there a relationship between Diabetes and ADHD?"},
        {"role": "assistant", "content": "FE ?var | {Diabetes ~ ?var ~ ADHD}"},
        {"role": "user", "content": "List the components of mTOR Complex 2 (mTORC2) in humans."},
        {"role": "assistant", "content": "FE ?var | {?x ~ subclass of ~ mTORC2} A {?x ~ has parts ~ ?var} A {?var ~ found in ~ homo sapiens}"},
        {"role": "user", "content": "List diseases that Valtrex (valacyclovir) is indicated for."},
        {"role": "assistant", "content": "FE ?var | {Valtrex ~ treats ~ ?var}"},
        {"role": "user", "content": "What diseases is Velcade (bortezomib) mainly used for?"},
        {"role": "assistant", "content": "FE ?var | {Velcade ~ treats ~ ?var}"},
        {"role": "user", "content": "List 3 indications for rituximab."},
        {"role": "assistant", "content": "FE ?var | {rituximab ~ treats ~ ?var} | Limit 3"},
        {"role": "user", "content": "What are 2 drugs approved for treatment of Diabetes?"},
        {"role": "assistant", "content": "FE ?var | {?var ~ treats ~ Diabetes} | Limit 2"},
        {"role": "user", "content": "What is the mechanism of action of Eteplirsen?"},
        {"role": "assistant", "content": "FE ?var | {?var ~ subclass of ~ mode of action} A {Eteplirsen ~ subject has role ~ ?var}"},
        {"role": "user", "content": "What is the mode of action of ibalizumab?"},
        {"role": "assistant", "content": "FE ?var | {?var ~ subclass of ~ mode of action} A {ibalizumab ~ subject has role ~ ?var}"},
        {"role": "user", "content": "Can Levoxyl (levothyroxine sodium) cause insomnia?"},
        {"role": "assistant", "content": "FE ?var | {Levoxyl ~ ?var ~ insomnia}"},
        {"role": "user", "content": "What does erlotinib target?"},
        {"role": "assistant", "content": "FE ?var | {?x ~ subclass of ~ erlotinib} A {?x ~ physically interacts with ~ ?var}"},
        {"role": "user", "content": "What is targeted by lapatinib?"},
        {"role": "assistant", "content": "FE ?var | {?x ~ subclass of ~ lapatinib} A {?x ~ physically interacts with ~ ?var}"},
        {"role": "user", "content": "What is the drug target of lapatinib?"},
        {"role": "assistant", "content": "FE ?var | {?x ~ subclass of ~ lapatinib} A {?x ~ physically interacts with ~ ?var}"},
        {"role": "user", "content": "What is inhibited by the drug masitinib?"},
        {"role": "assistant", "content": "FE ?var | {?x ~ subclass of ~ masitinib} A {?x ~ physically interacts with ~ ?var}"},
        {"role": "user", "content": "Which clotting factor is inhibited by betrixaban?"},
        {"role": "assistant", "content": "FE ?var | {betrixaban ~ subject has role ~ ?var}"},
        {"role": "user", "content": "What is the effect of thapsigargin treatment?"},
        {"role": "assistant", "content": "FE ?var | {thapsigargin ~ subject has role ~ ?var}"},
        {"role": "user", "content": "Which enzyme is inhibited by ixazomib?"},
        {"role": "assistant", "content": "FE ?var | {ixazomib ~ physically interacts with ~ ?var}"},
        {"role": "user", "content": "Do mutations of AKT1 occur in meningiomas?"},
        {"role": "assistant", "content": "FE ?var | {?x ~ subclass of ~ meningioma} A {?x ~ genetic association ~ ?var}"},
        {"role": "user", "content": "Do patients with Autism Spectrum disorder present with anxiety?"},
        {"role": "assistant", "content": "FE ?var | {?x ~ subclass of ~ autism spectrum disorder} A {?x ~ symptoms and signs ~ ?var}"}, 
        {"role": "user", "content": "Are there drugs for lyme disease?"},
        {"role": "assistant", "content": "FE ?var | {lyme disease ~ drug or therapy used for treatment ~ ?var}"},
        {"role": "user", "content": "Is RPS19 expressed in the brain?"},
        {"role": "assistant", "content": "FE ?var | {RPS19 ~ expressed in ~ ?var}"},        
        {"role": "user", "content": "Where is RPS19 located in the body?"},
        {"role": "assistant", "content": "FE ?var | {RPS19 ~ expressed in ~ ?var}"},       
        {"role": "user", "content": "Has the protein SLC22A3 been associated with apoptosis??"},
        {"role": "assistant", "content": "FE ?var | {SLC22A3 ~ encodes ~ ?x} A {?x ~ biological process ~ ?var}"},      
        {"role": "user", "content": "Entresto is composed of which two drugs?"},
        {"role": "assistant", "content": "FE ?var | {Entresto ~ has active ingredient ~ ?var}"},      
        {"role": "user", "content": "What diseases are atypical neuroleptic drugs used to treat?"},
        {"role": "assistant", "content": "FE ?var | {?x ~ subclass of ~ atypical neuroleptic drugs} A {?x ~ treats ~ ?var}"},   
        {"role": "user", "content": "What proteins can venlafaxine block?"},
        {"role": "assistant", "content": "FE ?var | {venlafaxine ~ physically interacts with ~ ?var}"},  
        {"role": "user", "content": "Does nifedipine inhibit any calcium channels?"},
        {"role": "assistant", "content": "FE ?var | {nifedipine ~ physically interacts with ~ ?var}"},   
        {"role": "user", "content": "What diseases are Glecaprevir and Pibrentasvir used in treatment of?"},
        {"role": "assistant", "content": "FE ?var | {Glecaprevir/pibrentasvir ~ medical condition treated ~ ?var}"},  
        {"role": "user", "content": "Is c-met involved in  ribosomal recycling?"},
        {"role": "assistant", "content": "FE ?var | {c-met ~ physically interacts with ~ ?var}"},
        {"role": "user", "content": "What are cardinal features of the Alzheimer disease?"},
        {"role": "assistant", "content": "FE ?var | {?x ~ subclass of ~ alzheimer disease} A {?x ~ symptoms and signs ~ ?var}"},
        {"role": "user", "content": "List causative genes for Parkinson's disease?"},
        {"role": "assistant", "content": "FE ?var | {?x ~ subclass of ~ parkinson's disease} A {?x ~ genetic association ~ ?var}"},
        {"role": "user", "content": "List some of the clinical trials related to scoliosis."},
        {"role": "assistant", "content": "FE ?var | {?x ~ subclass of ~ scoliosis} A {?var ~ medical condition ~ ?x}"},
        {"role": "user", "content": "List off label uses for Lapatinib."},
        {"role": "assistant", "content": "FE ?var | {lapatinib ~ medical condition treated ~ ?var}"},
        {"role": "user", "content": "Mutations in which gene cause Schimke immune-osseous dysplasia?"},
        {"role": "assistant", "content": "FE ?var | {?x ~ subclass of ~ Schimke immune-osseous dysplasia} A {?x ~ genetic association ~ ?var}"},
        {"role": "user", "content": "Is dichlorphenamide effective for any form of paralysis?"},
        {"role": "assistant", "content": "FE ?var | {?x ~ subclass of ~ paralysis} A {?x ~ drug or therapy used for treatment ~ ?var}"},  
        {"role": "user", "content": "What drug cures hepatitis B?"},
        {"role": "assistant", "content": "FE ?var | {?x ~ subclass of ~ hepatitis B} A {?x ~ drug or therapy used for treatment ~ ?var}"},    
        {"role": "user", "content": "What fruit causes Jamaican vomiting sickness?"},
        {"role": "assistant", "content": "FE ?var | {jamaican vomiting sickness ~ has cause ~ ?var}"},     
        {"role": "user", "content": "What hand deformities do patients with Apert syndrome present with?"},
        {"role": "assistant", "content": "FE ?var | {?x ~ subclass of ~ Apert syndrome} A {?x ~ symptoms and signs ~ ?var}"}]
    
