import flask
import os


# Initialize flask app for the example
app = flask.Flask(__name__)
app.debug = True


@app.route('/')
@app.route('/basic')
def basic():
    return flask.render_template(
        'basic.html',
        scripts=os.listdir(app.static_folder),
        api_port=5000,
        access_lifespan=24*60*60,
        refresh_lifespan=30*24*60*60,
    )


@app.route('/refresh')
def refresh():
    return flask.render_template(
        'refresh.html',
        scripts=os.listdir(app.static_folder),
        api_port=5010,
        access_lifespan=30,
        refresh_lifespan=2*60,
    )


@app.route('/blacklist')
def blacklist():
    return flask.render_template(
        'blacklist.html',
        scripts=os.listdir(app.static_folder),
        api_port=5020,
        access_lifespan=10000*24*60*60,
        refresh_lifespan=10000*24*60*60,
    )


# Run the example
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5050)
