"""
Internal database web service.
"""
import logging
import os
import urllib.parse

import flask
import flask_restful
import flask_restful.reqparse
import requests

from . import backend


app = flask.Flask(__name__)
api = flask_restful.Api(app)
app.logger.setLevel(logging.INFO)


db_cli = flask.cli.AppGroup("db")
@db_cli.command("init")
def init_db():
    backend.reset_table()
    app.logger.info("Created new database at '%s'", backend.DATABASE_PATH)

app.cli.add_command(db_cli)


def url_is_valid(url):
    res = urllib.parse.urlparse(url)
    return bool(res.scheme and res.netloc)


class Messages(flask_restful.Resource):
    keys = ("title", "content", "sender", "url")

    request_parser = flask_restful.reqparse.RequestParser(bundle_errors=True)
    for key in keys:
        request_parser.add_argument(key, location="json", required=True)

    def get(self):
        return list(backend.get_all_messages()), 200

    def put(self):
        args = self.request_parser.parse_args(strict=True)
        if not url_is_valid(args.url):
            app.logger.warning("Ignoring PUT message due to invalid url '%s'", args.url)
            return {"message": "invalid url"}, 400
        message_id = backend.create_message(*[args[k] for k in self.keys])
        return {"created_id": message_id}, 201


api.add_resource(Messages, "/messages")
