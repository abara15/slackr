"""Flask Server"""

import sys
from server import flask

# Run Server
if __name__ == "__main__":
    flask.APP.run(port=(sys.argv[1] if len(sys.argv) > 1 else 5011))
