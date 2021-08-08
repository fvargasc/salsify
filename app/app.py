import os
from flask import Flask, Response
from http import HTTPStatus
from functools import lru_cache
from line_index import get_line_text, LineDoesNotExistException

LINE_CACHE_SIZE_MAX = int(os.environ.get('LINE_CACHE_SIZE_MAX', 64)) # max entries in the cache

# Set up the flask application
app = Flask(__name__)


# Single route that responds with a specified line of text
@app.route('/lines/<line_index>', methods=['GET'])
# applied a cache decorator to set up caching for this resource. Chose LRU strategy.
@lru_cache(maxsize=LINE_CACHE_SIZE_MAX)
def products_resource(line_index):
    try:
        line_text = get_line_text(int(line_index))

    except (LineDoesNotExistException, ValueError):
        return Response(status=HTTPStatus.REQUEST_ENTITY_TOO_LARGE)
        # Responds with status code 413, as requested in the challenge.
        # This doesn't make sense in the given context, but I'll leave it as-is.
        # 403 or 404 would be better suited for the set purpose.

    return Response(
        response=line_text,
        status=HTTPStatus.OK,  # Status 200 OK
        content_type='text/plain;charset=ASCII')


def main():
    # starts the development web server
    app.run(debug=True, use_reloader=True)


# Main routine is run when this script is executed directly
if __name__ == '__main__':
    main()
