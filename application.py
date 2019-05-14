"""
Demo Flask application to test the operation of Flask with socket.io

Aim is to create a webpage that is constantly updated with random numbers from a background python process.

30th May 2014

===================

Updated 13th April 2018

+ Upgraded code to Python 3
+ Used Python3 SocketIO implementation
+ Updated CDN Javascript and CSS sources

"""

# Start with a basic flask app webpage.
from flask_socketio import SocketIO, emit
from flask import Flask, render_template, url_for, copy_current_request_context
from random import random
from time import sleep
from threading import Thread, Event

import xlrd
from numpy import median

file_loc = "C:/Users/jonas/OneDrive/Desktop/FinalCapstone/jona13.xlsx"
workbook = xlrd.open_workbook(file_loc)
sheet = workbook.sheet_by_index(0)


__author__ = 'slynn'

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
app.config['DEBUG'] = True

#turn the flask app into a socketio app
socketio = SocketIO(app)

#random number Generator Thread
thread = Thread()
thread_stop_event = Event()

class RandomThread(Thread):
    def __init__(self):
        self.delay = 1
        super(RandomThread, self).__init__()
        

    def randomNumberGenerator(self):

        """
        EYE BROW HELPER CLASS
        """
        def check_rest_b(row_start):
            #assume it's a brow raise, then have disqualifiers
            result = 1

            #check next 50 rows
            row_finish = row_start + 50

            #if no rows left, say end is end of sheet
            if(row_finish >= sheet.nrows):
                row_finish = sheet.nrows

            #contain list of next 80 points
            clench_window = []

            #check 50 rows from start for channel 1
            for i in range(row_start, row_finish):
                clench_window.append(sheet.cell_value(i,0))

            #if peak goes too high, not a clench
            if max(clench_window) > 1000:
                result = 0

            return result
        
        """
        CLENCH HELPER CLASS
        """       
        def check_rest_c(row_start):
            #CHECK THE NEXT 80 POINTS --------------------------
            #assume it's a clench, then have disqualifiers
            result = 1

            row_finish = row_start + 80

            #contain list of next 80 points
            clench_window = []

            for i in range(row_start, row_finish):
                clench_window.append(sheet.cell_value(i,1))

            #if peak goes too high, not a clench
            if max(clench_window) > 250:
                #print("i=", i, " .. max too high for clench")
                result = 0

            #if peak goes too low, not a clench
            if min(clench_window) < -250:
                result = 0

            #CHECK THE PREVIOUS 80 POINTS ------------------------
            row_previous = row_start - 80

            #contain list of next 80 points
            clench_window_prev = []

            for i in range(row_previous, row_start):
                clench_window_prev.append(sheet.cell_value(i,1))

            #if peak goes too high, not a clench
            if max(clench_window_prev) > 250:
                #print("i=", i, " .. max too high for clench")
                result = 0

            return result
        
        """
        Generate a random number every 1 second and emit to a socketio instance (broadcast)
        Ideally to be run in a separate thread?
        """
        #infinite loop of magical random numbers
        #print("Making random numbers")
        #while not thread_stop_event.isSet():
        #start blink detect
        blink_counter = 0
        brow_counter = 0
        clench_counter = 0

        hitblink = False
        hitbrow = False
        hitclench = False

        hit_relaxblink = 0
        hit_relaxbrow = 0
        hit_relaxclench = 0

        pause_counter = 0
        pause_counter2 = 0
        pause_counter3 = 0
        pause = False
        
        #read through all rows
        for i in range(sheet.nrows):
            blink=0
            brow=0
            clench=0
            
            if i%200==0: #pause every 200 points - 1 sec
                sleep(self.delay)
            else:
                sleep(0)
            
            """
            EYE BLINK
            """
            if sheet.cell_value(i, 0) > 1500 and pause_counter > 200:
                blink=1
                pause_counter = 0
                blink_counter = blink_counter + 1
                number=i/200
                socketio.emit('newnumber', {'number': number,'blink':blink,'brow':brow,'clench':clench}, namespace='/test')
                print("i = ", i)
                print("Blink at time ", i / 200)
            else:
                sleep(0)
            
            """
            EYE BROW
            """
            if sheet.cell_value(i, 0) < 1000 and sheet.cell_value(i, 1) > 1000 and pause_counter2 > 200:
                if check_rest_b(i) == 1:
                    brow=1
                    pause_counter2 = 0
                    brow_counter = brow_counter + 1
                    number=i/200
                    socketio.emit('newnumber', {'number': number,'blink':blink,'brow':brow,'clench':clench}, namespace='/test')
                    print("i = ", i)
                    print("Brow raise at time ", i / 200)
                else:
                    """do nothing, it's not a brow raise"""
            else:
                sleep(0)
            
            """
            JAW CLENCH
            """       
            #if threshold reached, check that there are 5 small peaks above 0 within 80 points
            #if threshold, check next 80 points.. are they all below 500 and are there 5 above 0?
            if sheet.cell_value(i, 0) < 500 \
                    and sheet.cell_value(i, 1) < 500 \
                    and sheet.cell_value(i,1) > 100\
                    and pause == False:

                #check the next 80 rows of values
                #if a clench, then pause for 300 points
                if(check_rest_c(i)) == 1:
                    clench=1
                    clench_counter = clench_counter + 1
                    pause = True
                    number=i/200
                    socketio.emit('newnumber', {'number': number,'blink':blink,'brow':brow,'clench':clench}, namespace='/test')
                    print("i = ", i)
                    print("Clench at time ", i / 200)
                    print(pause_counter3)

            elif pause == True and pause_counter3 >= 300:
                pause_counter3 = 0
                print(pause_counter3)
                pause = False

            #if pause is True and pause_counter < 300, increment pause_counter
            elif pause == True and pause_counter3 <300:
                pause_counter3 = pause_counter3 + 1

            #otherwise, do nothing
            else:
                sleep(0)   
            
            
            number=0
            socketio.emit('newnumber', {'number': number,'blink':blink,'brow':brow,'clench':clench}, namespace='/test')
                #always increment pause counter
            pause_counter += 1   
            pause_counter2 += 1   
            #end blink detect
            
            #sleep(self.delay)
        #end infinite loop
    def run(self):
        self.randomNumberGenerator()


@app.route('/')
def index():
    #only by sending this page first will the client be connected to the socketio instance
    return render_template('index.html')

@socketio.on('connect', namespace='/test')
def test_connect():
    # need visibility of the global thread object
    global thread
    print('Client connected')

    #Start the random number generator thread only if the thread has not been started before.
    if not thread.isAlive():
        print("Starting Thread")
        thread = RandomThread()
        thread.start()

@socketio.on('disconnect', namespace='/test')
def test_disconnect():
    print('Client disconnected')


if __name__ == '__main__':
    socketio.run(app)
