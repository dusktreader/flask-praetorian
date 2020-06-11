import flask
import tempfile
import flask_praetorian
import flask_cors
import mongoengine
from mongoengine import Document, fields, DoesNotExist, signals
from bson.json_util import loads, dumps

db = mongoengine
db.connect("praetorian", host="localhost", port=27017)

guard = flask_praetorian.Praetorian()
cors = flask_cors.CORS()

class RoleException(Exception):
    pass

allowed_roles = ['admin', 'operator']

class User(Document):
    '''
    This is a small sample of a User class that persists to MongoDB.

    The following docker-compose.yml snippet can be used for testing. 
    Please do not use in production.

    version: "3.2"
    services:
    mongo:
        image: mongo:latest
        container_name: "mongo"
        restart: always
        ports:
        - 27017:27017

    '''

    username = fields.StringField(required=True, unique=True)
    password = fields.StringField(required=True)
    roles = fields.StringField()
    is_active = fields.BooleanField(default=True)

    @classmethod
    def lookup(cls, username):
        try:
            return User.objects(username=username).get()
        except DoesNotExist:
            return None

    @classmethod
    def identify(cls, id):
        try:
            return User.objects(id=loads(id)).get()
        except DoesNotExist:
            return None

    @property
    def rolenames(self):
        try:
            roles = self.roles.split(',') 
            if set(roles).issubset(set(allowed_roles)):
                return roles
            else:
                raise RoleException
        except RoleException:            
            return []

    @property
    def identity(self):
        return dumps(self.id)

    def is_valid(self):
        return self.is_active

def update_modified(sender, document):
    try:
        print(document.save())
    except:
        pass

signals.post_init.connect(update_modified)

# Initialize flask app for the example
app = flask.Flask(__name__)
app.debug = True
app.config['SECRET_KEY'] = 'top secret'
app.config['JWT_ACCESS_LIFESPAN'] = {'hours': 24}
app.config['JWT_REFRESH_LIFESPAN'] = {'days': 30}

# Initialize the flask-praetorian instance for the app
guard.init_app(app, User)

# Initializes CORS so that the api_tool can talk to the example app
cors.init_app(app)

User(username="TheDude", password=guard.hash_password('abides'), roles='')
User(username="Walter", password=guard.hash_password('calmerthanyouare'), roles='admin')
User(username="Donnie", password=guard.hash_password('iamthewalrus'), roles='admin')
User(username="Maude", password=guard.hash_password('andthorough'), roles='operator,admin')

# Set up some routes for the example
@app.route('/login', methods=['POST'])
def login():
    """
    Logs a user in by parsing a POST request containing user credentials and
    issuing a JWT token.
    .. example::
       $ curl http://localhost:5000/login -X POST \
         -d '{"username":"Walter","password":"calmerthanyouare"}'
    """
    req = flask.request.get_json(force=True)
    username = req.get('username', None)
    password = req.get('password', None)
    user = guard.authenticate(username, password)
    ret = {'access_token': guard.encode_jwt_token(user)}
    return (flask.jsonify(ret), 200)


@app.route('/protected')
@flask_praetorian.auth_required
def protected():
    """
    A protected endpoint. The auth_required decorator will require a header
    containing a valid JWT
    .. example::
       $ curl http://localhost:5000/protected -X GET \
         -H "Authorization: Bearer <your_token>"
    """
    return flask.jsonify(message='protected endpoint (allowed user {})'.format(
        flask_praetorian.current_user().username,
    ))


@app.route('/protected_admin_required')
@flask_praetorian.roles_required('admin')
def protected_admin_required():
    """
    A protected endpoint that requires a role. The roles_required decorator
    will require that the supplied JWT includes the required roles
    .. example::
       $ curl http://localhost:5000/protected_admin_required -X GET \
          -H "Authorization: Bearer <your_token>"
    """
    return flask.jsonify(
        message='protected_admin_required endpoint (allowed user {})'.format(
            flask_praetorian.current_user().username,
        )
    )


@app.route('/protected_operator_accepted')
@flask_praetorian.roles_accepted('operator', 'admin')
def protected_operator_accepted():
    """
    A protected endpoint that accepts any of the listed roles. The
    roles_accepted decorator will require that the supplied JWT includes at
    least one of the accepted roles
    .. example::
       $ curl http://localhost/protected_operator_accepted -X GET \
         -H "Authorization: Bearer <your_token>"
    """
    return flask.jsonify(
        message='protected_operator_accepted endpoint (allowed usr {})'.format(
            flask_praetorian.current_user().username,
        )
    )

# Run the example
if __name__ == '__main__':
    # app.run(host='0.0.0.0', port=5000)
    app.run(debug=True)
