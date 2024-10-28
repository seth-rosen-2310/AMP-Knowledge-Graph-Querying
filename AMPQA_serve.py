"""
This module contains the code for serving the combined QA
"""
import argparse
import json
import logging
import sys
import time

from graph_handler import *
from apiflask import APIFlask, Schema
from flask.views import MethodView
from flask import Flask, request, Response, jsonify


GRAPH, SPARQL = MODES = ['graph', 'sparql']

logger = logging.getLogger(__name__)  # pylint: disable=invalid-name

graph_service: GraphHandler


class ServerError(Exception):
    """Error class for service"""
    status_code = 400

    def __init__(self, message, status_code=None, payload=None):
        Exception.__init__(self)
        self.message = message
        if status_code is not None:
            self.status_code = status_code
        self.payload = payload

    def to_dict(self):
        error_dict = dict(self.payload or ())
        error_dict['message'] = self.message
        return error_dict


def AMPhionQA_app(app: Flask) -> Flask:
    @app.route('/AMPhion/query', methods=['POST', 'OPTIONS'])
    def graph_query() -> Response:  # pylint: disable=unused-variable
        """
        query a graph via natural language question
        """
        if request.method == "OPTIONS":
            return Response(response=graph_query.__doc__, status=200)

        data = request.get_json()
        results = graph_service.run_query(data.get('question'))

        log_blob = {"inputs": data, "outputs": results}
        logger.info("results: %s", json.dumps(log_blob))
        return jsonify(results)

    @app.route('/AMPhion/sparql', methods=['POST', 'OPTIONS'])
    def graph_sparql() -> Response:  # pylint: disable=unused-variable
        """
        generate SPARQL for a natural language question
        """
        if request.method == "OPTIONS":
            return Response(response=graph_explain.__doc__, status=200)

        data = request.get_json()
        results = graph_service.get_sparql(data.get('question'))

        log_blob = {"inputs": data, "outputs": results}
        logger.info("results: %s", json.dumps(log_blob))
        return jsonify(results)

    return app


def make_app(title: str) -> Flask:
    app = Flask(title)

    @app.errorhandler(ServerError)
    def handle_invalid_usage(error: ServerError) -> Response:  # pylint: disable=unused-variable
        response = jsonify(error.to_dict())
        response.status_code = error.status_code
        return response

    @app.route('/query', methods=['POST', 'OPTIONS'])
    def query() -> Response:  # pylint: disable=unused-variable
        """
        Return documents relevant to the question
        """
        if request.method == "OPTIONS":
            resp_message = query.__doc__ + f'''
            question: "..."
            mode: {MODES} - which service to call
            '''
            return Response(response=resp_message, status=200)

        graph_results = None
        

        data = request.get_json()
        question = data.get('question')
        mode = data.get('mode', 'both')
       

        if mode == GRAPH:
            try:
                graph_results = graph_service.query(question)
            #add error class to the utils?
            except:  #graph_utils.GraphServiceNoResultsException
                logger.exception("no result from graph service")
        if mode == SPARQL:
            try:
                sparql_results = graph_service.get_sparql(question)
            except:  #text_utils.TextServiceNoResultsException
                logger.exception("no result from SPARQL service")


        results = {}
        if graph_results:
            results['graph'] = graph_results
        if sparql_results:
            results['sparql'] = sparql_results

        log_blob = {"inputs": data, "outputs": results}
        logger.info("results: %s", json.dumps(log_blob))
        return jsonify(results)

    return app


if __name__ == '__main__':
    tic = time.time()
    parser = argparse.ArgumentParser(description='Serve up a simple model')

    parser.add_argument('-v', '--verbose', help='logging', action='store_const', dest='loglevel', const=logging.INFO)
    parser.add_argument('--title', type=str, help='change the default page title', default="Federated QA")
    parser.add_argument('--port', type=int, default=9012, help='port to serve the demo on')

    args = parser.parse_args(sys.argv[1:])
    logging.basicConfig(level=args.loglevel)

    graph_service = graphqa.GraphQAService()
    
    _app = make_app(args.title)
    _app = AMPhionQA_app(_app)
    
    _app.run(port=args.port)