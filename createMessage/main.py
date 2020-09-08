"""
Public facing createMessage web service.
"""
import logging
import os
import urllib.parse

import flask
import flask_restful
import flask_restful.reqparse
import requests


app = flask.Flask(__name__)
api = flask_restful.Api(app)
app.logger.setLevel(logging.INFO)


class Messages(flask_restful.Resource):
    request_parser = flask_restful.reqparse.RequestParser(bundle_errors=True)
    for key in ("title", "content", "sender", "url"):
        request_parser.add_argument(key, location="json", required=True)

    def put(self):
        args = self.request_parser.parse_args(strict=True)
        response = requests.put(db_messages_path, json=args)
        if response.status_code == 400:
            # Let error messages through for bad requests
            return {"message": response.json()["message"]}, 400
        response.raise_for_status()
        return response.json(), 200


db_messages_path = urllib.parse.urljoin(os.environ["DATABASE_URL"], "/messages")
api.add_resource(Messages, "/messages")
