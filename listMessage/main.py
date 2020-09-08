"""
Public facing listMessages web service.
"""
import logging
import os
import urllib.parse

import dicttoxml
import flask
import flask_restful
import flask_restful.reqparse
import requests


app = flask.Flask(__name__)
api = flask_restful.Api(app)
app.logger.setLevel(logging.INFO)


class Messages(flask_restful.Resource):
    version_parser = flask_restful.reqparse.RequestParser(bundle_errors=True)
    version_parser.add_argument("version", choices=(1, 2), type=int, location="args", required=True)

    format_parser = version_parser.copy()
    format_parser.add_argument("format", choices=("json", "xml"), location="args", required=True)

    def get(self):
        db_response = requests.get(db_messages_path)
        db_response.raise_for_status()
        all_messages = db_response.json()

        response = None
        args = self.version_parser.parse_args()
        if args.version == 1:
            # Version 1 returns only 3 fields of each message
            response = [{k: row[k] for k in ("title", "content", "sender")} for row in all_messages]
        elif args.version == 2:
            args = self.format_parser.parse_args()
            # Version 2 allows different format for returned results
            if args.format == "json":
                response = all_messages
            elif args.format == "xml":
                response = flask.make_response(dicttoxml.dicttoxml(all_messages), 200)
                response.headers["Content-Type"] = "application/xml"
                return response
        return response, 200



db_messages_path = urllib.parse.urljoin(os.environ["DATABASE_URL"], "/messages")
api.add_resource(Messages, "/messages")
