# Import necessary libraries and create Flask object
# I will use websockets for instant updates vs. polling
from flask import Flask, request, render_template
from flask_socketio import SocketIO, emit, send 
import ast, time
app = Flask(__name__)
socketio = SocketIO(app)

# Simple array to store most recent calculations
# Keep in memory
calculations = []

# Homepage route
@app.route('/') 
def home():
    return render_template('index.html')

###############################################
# Events for socket.io
###############################################

# For a connection, emit our DS of known calculations
@socketio.on('connect', namespace='/calculator')
def connect():
	for item in calculations:
		emit('fill_calculations', item) 

# User disconnected
@socketio.on('disconnect', namespace='/calculator')
def disconnect():
    print('Client disconnected')

# Websocket event for storing data in our DS
# And broadcasting new calculation to all users
@socketio.on('to_calculate', namespace='/calculator')
def to_calculate(message):
	# We keep our local stack small, but we leave
	# a bit of a buffer (we strip the table to 10)
	# most recent entries client-side
	global calculations
	if(len(calculations) > 20):
		calculations = calculations[5:]
	calculations.append({
		'time': time.time(),
		'expression': message['expression'],
		'answer':  message['result']
		})
	# Send the new calcuation to all connected WS clients
	emit('fill_calculations', calculations[-1], broadcast=True)
