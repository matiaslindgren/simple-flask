# REST API message application

Implemented in Python using Flask, with an SQLite3 database backend.

Public facing services:

* `listMessage`
    * `GET` `/messages?version=<int>&format=<str>` returns a list of all messages in the application
        * Version 1 returns a JSON list of all messages in short form, i.e. only keys `title`, `sender`, and `url`.
        * Version 2 returns a JSON or XML list of all messages in long form.
* `createMessage` - public facing service
    * `PUT` `/messages` creates a new message from `title`, `content`, `sender`, and `url` values specified in the JSON body of the request and returns an id for the created message.

Private service:

* `database`
    * `GET` `/messages` returns a JSON list of all messages in the SQL database.
    * `PUT` `/messages` creates a new message from given JSON data and returns the row id of the created message

## Setup

Tested with Python 3.7.3 on Debian 10 (buster).

```
pip install -r requirements.txt
```

## Running

The shell is assumed to be `bash`.
In addition, the `jq` JSON formatting utility is used for pretty-formatting JSON.

1. Change working directory to this repository.
2. Create a directory for the SQLite database:

        export DATABASE_DIR="$(mktemp --directory)"
3. Initialize the database:

        env FLASK_APP=database/main.py flask db init
4. Start the database service:

        env FLASK_APP=database/main.py flask run --port 5000
5. In a second terminal, start the `listMessage` service:

        env FLASK_APP=listMessage/main.py DATABASE_URL='http://127.0.0.1:5000' flask run --port 5001
6. In a third terminal, start the `createMessage` service:

        env FLASK_APP=createMessage/main.py DATABASE_URL='http://127.0.0.1:5000' flask run --port 5002

The application is now initialized and ready to serve requests.

## Examples

In a fourth terminal, check that `listMessage` returns empty lists:

        >>> curl --request GET 'http://127.0.0.1:5001/messages?version=1'
        []

        >>> curl --request GET 'http://127.0.0.1:5001/messages?version=2&format=xml'
        <?xml version="1.0" encoding="UTF-8" ?><root></root>

Now, insert some messages using the `createMessage` service:

        >>> curl --header 'Content-Type: application/json' \
            --request PUT 'http://127.0.0.1:5002/messages' \
            --data '{"title": "hello", "content": "hi, how goes it?", "sender": "bob", "url": "https://yle.fi"}'
        {"created_id": 1}

        >>> curl --header 'Content-Type: application/json' \
            --request PUT 'http://127.0.0.1:5002/messages' \
            --data '{"title": "re: hello", "content": "hi, all good here.", "sender": "alice", "url": "https://yle.fi"}'
        {"created_id": 2}

        >>> curl --header 'Content-Type: application/json' \
            --request PUT 'http://127.0.0.1:5002/messages' \
            --data '{"title": "special offer", "content": "limited time only, -50% for you", "sender": "mr. spam-king", "url": "https://example.com/spam"}'
        {"created_id": 3}

The `listMessage` service should now return non-empty lists:

        >>> curl --request GET 'http://127.0.0.1:5001/messages?version=1' | jq .
        [
          {
            "title": "hello",
            "content": "hi, how goes it?",
            "sender": "bob"
          },
          {
            "title": "re: hello",
            "content": "hi, all good here.",
            "sender": "alice"
          },
          {
            "title": "special offer",
            "content": "limited time only, -50% for you",
            "sender": "mr. spam-king"
          }
        ]

        >>> curl --request GET 'http://127.0.0.1:5001/messages?version=2&format=xml' | python3 -c 'import sys; from xml.dom.minidom import parseString; print(parseString(sys.stdin.read()).toprettyxml())'
        <?xml version="1.0" ?>
        <root>
            <item type="dict">
                <id type="int">1</id>
                <title type="str">hello</title>
                <content type="str">hi, how goes it?</content>
                <sender type="str">bob</sender>
                <url type="str">https://yle.fi</url>
            </item>
            <item type="dict">
                <id type="int">2</id>
                <title type="str">re: hello</title>
                <content type="str">hi, all good here.</content>
                <sender type="str">alice</sender>
                <url type="str">https://yle.fi</url>
            </item>
            <item type="dict">
                <id type="int">3</id>
                <title type="str">special offer</title>
                <content type="str">limited time only, -50% for you</content>
                <sender type="str">mr. spam-king</sender>
                <url type="str">https://example.com/spam</url>
            </item>
        </root>
