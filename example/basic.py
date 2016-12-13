import flask
import tempfile
import flask_sqlalchemy
import flask_praetorian

db = flask_sqlalchemy.SQLAlchemy()
guard = flask_praetorian.Praetorian()


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.Text, unique=True)
    password = db.Column(db.Text)
    roles = db.Column(db.Text)

    @property
    def rolenames(self):
        try:
            return self.roles.split(',')
        except:
            return []

    @classmethod
    def lookup(cls, username):
        return cls.query.filter_by(username=username).one_or_none()

    @classmethod
    def identify(cls, id):
        return cls.query.get(id)


app = flask.Flask(__name__)
app.debug = True
app.config['SECRET_KEY'] = 'top secret'

guard.init_app(app, User)

local_database = tempfile.NamedTemporaryFile(prefix='local', suffix='.db')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///{}'.format(local_database)
db.init_app(app)
with app.app_context():
    db.create_all()
    db.session.add(User(
        username='TheDude',
        password=guard.encrypt_password('abides'),
    ))
    db.session.add(User(
        username='Walter',
        password=guard.encrypt_password('calmerthanyouare'),
        roles='admin'
    ))
    db.session.add(User(
        username='Donnie',
        password=guard.encrypt_password('iamthewalrus'),
        roles='operator'
    ))
    db.session.add(User(
        username='Maude',
        password=guard.encrypt_password('andthorough'),
        roles='operator,admin'
    ))
    db.session.commit()


@app.route('/')
def root():
    return 'root endpoint'


@app.route('/protected')
@flask_praetorian.auth_required()
def protected():
    return 'protected endpoint'


@app.route('/protected_admin_required')
@flask_praetorian.auth_required()
@flask_praetorian.roles_required('admin')
def protected_admin_required():
    return 'protected_admin_required endpoint'


@app.route('/protected_admin_accepted')
@flask_praetorian.auth_required()
@flask_praetorian.roles_accepted('admin', 'operator')
def protected_admin_and_operator_accepted():
    return 'protected_admin_accepted endpoint'


if __name__ == '__main__':
    app.run()
