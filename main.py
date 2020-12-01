from flask import Flask
from src.routing import app_route

app = Flask(__name__)
app.register_blueprint(app_route)
app.secret_key = "my secret"
app.config['data'] = {}
app.config['connections'] = {}
if __name__ == '__main__':
    app.run(host = '127.0.0.1' ,debug=True,port=8080)