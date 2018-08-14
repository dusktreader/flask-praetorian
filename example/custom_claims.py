import flask
import tempfile
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
    firstname = db.Column(db.Text)
    surname = db.Column(db.Text)
    nickname = db.Column(db.Text)

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
        password=guard.encrypt_password('abides'),
        firstname='Jeffrey',
        nickname='The Dude',
        surname='Lebowski',
    ))
    db.session.add(User(
        username='Walter',
        password=guard.encrypt_password('calmerthanyouare'),
        roles='admin',
        firstname='Walter',
        surname='Sobchak',
    ))
    db.session.add(User(
        username='Donnie',
        password=guard.encrypt_password('iamthewalrus'),
        roles='operator',
        firstname='Theodore',
        nickname='Donnie',
        surname='Kerabatsos',
    ))
    db.session.add(User(
        username='Maude',
        password=guard.encrypt_password('andthorough'),
        roles='operator,admin',
        firstname='Maude',
        nickname='Maudie',
        surname='Lebowski',
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
    username = req.pop('username', None)
    password = req.pop('password', None)

    user = guard.authenticate(username, password)
    ret = {'access_token': guard.encode_jwt_token(
        user,
        firstname=user.firstname,
        nickname=user.nickname,
        surname=user.surname,
    )}

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
    custom_claims = flask_praetorian.current_custom_claims()
    firstname = custom_claims.pop('firstname', None)
    nickname = custom_claims.pop('nickname', None)
    surname = custom_claims.pop('surname', None)

    if nickname is None:
        user_string = "{} {}".format(firstname, surname)
    else:
        user_string = "{} '{}' {}".format(firstname, nickname, surname)

    return flask.jsonify(
        message="protected endpoint (allowed user {u})".format(u=user_string),
    )


# Run the example
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5030)
