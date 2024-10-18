from flask import Flask, render_template_string, redirect, url_for
from main import SpookyPi

app = Flask(__name__)
spooky_pi = SpookyPi()
is_running = False

@app.route('/')
def index():
    global is_running
    return render_template_string('''
        <!DOCTYPE html>
        <html lang="en">
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1, shrink-to-fit=no">
                <link href="https://stackpath.bootstrapcdn.com/bootstrap/4.5.2/css/bootstrap.min.css" rel="stylesheet">
                <title>Spooky Season Control</title>
            </head>
            <body class="container">
                <div class="row justify-content-center">
                    <div class="col-md-6 col-sm-8 col-12 text-center">
                        <h1 class="my-4">Spooky Season Control</h1>
                        {% if not is_running %}
                            <form action="{{ url_for('start') }}" method="post">
                                <button type="submit" class="btn btn-success btn-lg btn-block">Start</button>
                            </form>
                        {% endif %}
                        {% if is_running %}
                            <form action="{{ url_for('stop') }}" method="post">
                                <button type="submit" class="btn btn-danger btn-lg btn-block">Stop</button>
                            </form>
                        {% endif %}
                    </div>
                </div>
                <script src="https://code.jquery.com/jquery-3.5.1.slim.min.js"></script>
                <script src="https://cdn.jsdelivr.net/npm/@popperjs/core@2.5.4/dist/umd/popper.min.js"></script>
                <script src="https://stackpath.bootstrapcdn.com/bootstrap/4.5.2/js/bootstrap.min.js"></script>
            </body>
        </html>
    ''', is_running=is_running)

@app.route('/start', methods=['POST'])
def start():
    global is_running
    if not is_running:
        spooky_pi.start()
        is_running = True
    return redirect(url_for('index'))

@app.route('/stop', methods=['POST'])
def stop():
    global is_running
    if is_running:
        spooky_pi.stop()
        is_running = False
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=80)
