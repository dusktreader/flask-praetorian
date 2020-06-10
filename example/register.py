import tempfile
import flask
import flask_sqlalchemy
import flask_praetorian
import flask_cors

db = flask_sqlalchemy.SQLAlchemy()
guard = flask_praetorian.Praetorian()
cors = flask_cors.CORS()


# A generic user model that might be used by an app powered by flask-praetorian
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.Text, unique=True)
    password = db.Column(db.Text)
    roles = db.Column(db.Text)
    is_active = db.Column(db.Boolean, default=True, server_default='true')

    @property
    def rolenames(self):
        try:
            return self.roles.split(',')
        except Exception:
            return []

    @classmethod
    def lookup(cls, username):
        return cls.query.filter_by(username=username).one_or_none()

    @classmethod
    def identify(cls, id):
        return cls.query.get(id)

    @property
    def identity(self):
        return self.id

    def is_valid(self):
        return self.is_active


# Initialize flask app for the example
app = flask.Flask(__name__)
app.debug = True
app.config['SECRET_KEY'] = 'top secret'
app.config['JWT_ACCESS_LIFESPAN'] = {'hours': 24}
app.config['JWT_REFRESH_LIFESPAN'] = {'days': 30}

# Initialize the flask-praetorian instance for the app
guard.init_app(app, User)

# Initialize a local database for the example
local_database = tempfile.NamedTemporaryFile(prefix='local', suffix='.db')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///{}'.format(local_database)
db.init_app(app)

# Initializes CORS so that the api_tool can talk to the example app
cors.init_app(app)

# Add users for the example
with app.app_context():
    db.create_all()
    db.session.add(User(
        username='TheDude',
        password=guard.hash_password('abides'),
    ))
    db.session.add(User(
        username='Walter',
        password=guard.hash_password('calmerthanyouare'),
        roles='admin'
    ))
    db.session.add(User(
        username='Donnie',
        password=guard.hash_password('iamthewalrus'),
        roles='operator'
    ))
    db.session.add(User(
        username='Maude',
        password=guard.hash_password('andthorough'),
        roles='operator,admin'
    ))
    db.session.commit()


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
    ret = {
        'message': 'protected endpoint (allowed user {})'.format(
            flask_praetorian.current_user().username
        )
    }
    return (flask.jsonify(ret), 200)


@app.route('/register', methods=['POST'])
def register():
    """
    Registers a new user by parsing a POST request containing new user info and
    dispatching an email with a registration token

    .. example::
       $ curl http://localhost:5000/register -X POST \
         -d '{
           "username":"Brandt", \
           "password":"herlifewasinyourhands" \
           "email":"brandt@biglebowski.com"
         }'
    """
    req = flask.request.get_json(force=True)
    username = req.get('username', None)
    email = req.get('email', None)
    password = req.get('password', None)
    new_user = User(
        username=username,
        password=guard.hash_password(password),
        roles='operator',
    )
    db.session.add(new_user)
    db.session.commit()
    guard.send_registration_email(email, user=new_user)
    ret = {'message': 'successfully sent registration email to user {}'.format(
        new_user.username
    )}
    return (flask.jsonify(ret), 201)


@app.route('/finalize')
def finalize():
    """
    Finalizes a user registration with the token that they were issued in their
    registration email

    .. example::
       $ curl http://localhost:5000/finalize -X GET \
         -H "Authorization: Bearer <your_token>"
    """
    registration_token = guard.read_token_from_header()
    user = guard.get_user_from_registration_token(registration_token)
    # perform 'activation' of user here...like setting 'active' or something
    ret = {'access_token': guard.encode_jwt_token(user)}
    return (flask.jsonify(ret), 200)


# Run the example
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
