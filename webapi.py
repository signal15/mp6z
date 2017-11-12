#!flask/bin/python
from shelljob import proc
from flask import Flask, request, Response

app = Flask(__name__)

@app.route('/')
def index():
    return "Hello, World!"

@app.route('/api/v1/zones', methods=['GET'])
def get_zones():
    group = proc.Group()
    group.run(['/home/pi/mp6z/mp6z.py', 'get'])

    def generator():
        while group.is_pending():
            data = group.readlines()
            for handle, lines in data:
                yield lines

    return Response(generator(), mimetype='text/plain')

@app.route('/api/v1/zones/<int:zone_id>', methods=['GET'])
def get_zone(zone_id):
    group = proc.Group()
    group.run(['/home/pi/mp6z/mp6z.py', 'get', str(zone_id)])

    def generator():
        while group.is_pending():
            data = group.readlines()
            for handle, lines in data:
                yield lines

    return Response(generator(), mimetype='text/plain')

@app.route('/api/v1/zones/<int:zone_id>', methods=['PUT'])
def set_zone(zone_id):
    cliargs = ['/home/pi/mp6z/mp6z.py', 'set', str(zone_id)]
    if 'volume' in request.json:
        cliargs.append('-v')
        cliargs.append(str(request.json.get('volume')))
    if 'balance' in request.json:
        cliargs.append('--bl')
        cliargs.append(str(request.json.get('balance')))
    if 'bass' in request.json:
        cliargs.append('-b')
        cliargs.append(str(request.json.get('bass')))
    if 'dnd' in request.json:
        cliargs.append('-d')
        cliargs.append(str(request.json.get('dnd')))
    if 'mute' in request.json:
        cliargs.append('-m')
        cliargs.append(str(request.json.get('mute')))
    if 'power' in request.json:
        cliargs.append('-p')
        cliargs.append(str(request.json.get('power')))
    if 'source' in request.json:
        cliargs.append('-s')
        cliargs.append(str(request.json.get('source')))
    if 'treble' in request.json:
        cliargs.append('-t')
        cliargs.append(str(request.json.get('treble')))
    group = proc.Group()
    group.run(cliargs)

    def generator():
        while group.is_pending():
            data = group.readlines()
            for handle, lines in data:
                yield lines

    return Response(generator(), mimetype='text/plain')
if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=5000)
