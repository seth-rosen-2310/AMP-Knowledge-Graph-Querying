# AMP-Knowledge-Graph-Querying
AMPhionQA was built as a system to allow for Natural Language querying of knowledge graphs by converting questions into SPARQL queries. It was meant for submission and demonstrations at conferences in 2023 and as such many of the dependencies are now outdated.


The basic pipeline takes a natural language query from the user, looks for similar questions in the elasticsearch index, uses an LLM to convert the question to intermediate representation, converts the IR to SPARQL by resolving NL labels to URIs (IDs), and finally executes the SPARQL and returns results to the user. 
