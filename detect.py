import xlrd
from numpy import median

file_loc = "C:/Users/jonas/OneDrive/Desktop/FinalCapstone/jona15.xlsx"
workbook = xlrd.open_workbook(file_loc)
sheet = workbook.sheet_by_index(0)
print(sheet.nrows)
print(sheet.cell_value(0, 1))

# loop to check for jaw clench
# once hits -600, ignore for 50 points
# from 3,12000 to 3,14000


# next steps..
# take median of data points for either clench or brow raise
# notice clench median will be similar bw channel 1 and 3
# notice brow raise median will be different bw 1 and 3
# take ratio of the medians.. if above threshold it's a brow raise


blink_counter = 0
brow_counter = 0
clench_counter = 0

hitblink = False
hitbrow = False
hitclench = False

hit_relaxblink = 0
hit_relaxbrow = 0
hit_relaxclench = 0


# timestamp is point number / 200
# 200 points per second

# This will always detect a blink
# blinks always over 1000 microVolts
def blink_detect():
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

    for i in range(sheet.nrows):
        if sheet.cell_value(i, 0) > 1500 and pause_counter > 200:
            pause_counter = 0
            blink_counter = blink_counter + 1

            print("i = ", i)
            print("Blink at time ", i / 200)


        #always increment pause counter
        pause_counter += 1

    print("Number of blinks is", blink_counter)


def brow_detect():
    brow_counter = 0

    pause_counter = 0

    for i in range(sheet.nrows):
        if sheet.cell_value(i, 0) < 1000 and sheet.cell_value(i, 1) > 1000 and pause_counter > 200:
            pause_counter = 0
            brow_counter = brow_counter + 1

            print("i = ", i)
            print("Brow raise at time ", i / 200)


        #always increment pause counter
        pause_counter += 1

    print("Number of brow raises is", brow_counter)


def clench_detect():
    clench_counter = 0

    pause_counter = 0

    for i in range(sheet.nrows):
        if sheet.cell_value(i, 0) < 1000 and sheet.cell_value(i, 1) > 1000 and pause_counter > 200:
            pause_counter = 0
            brow_counter = brow_counter + 1

            print("i = ", i)
            print("Brow raise at time ", i / 200)


        #always increment pause counter
        pause_counter += 1

    print("Number of brow raises is", brow_counter)


def check_rest(row_start):
    #assume it's a clench, then have disqualifiers
    result = 1

    row_finish = row_start + 80

    #contain list of next 80 points
    clench_window = []

    for i in range(row_start, row_finish):
        clench_window.append(sheet.cell_value(i,1))

    #if peak goes too high, not a clench
    if max(clench_window) > 250:
        result = 0

    #if peak goes too low, not a clench
    if min(clench_window) < -250:
        result = 0

    return result


def clench_detect():
    clench_counter = 0

    pause_counter = 0
    pause = False

    for i in range(sheet.nrows):
        #if threshold reached, check that there are 5 small peaks above 0 within 80 points
        #if threshold, check next 80 points.. are they all below 500 and are there 5 above 0?
        if sheet.cell_value(i, 0) < 500 \
                and sheet.cell_value(i, 1) < 500 \
                and sheet.cell_value(i,1) > 100\
                and pause == False:

            #check the next 80 rows of values
            #if a clench, then pause for 300 points
            if(check_rest(i)) == 1:
                clench_counter = clench_counter + 1
                pause = True
                print("i = ", i)
                print("Clench at time ", i / 200)

        elif pause == True and pause_counter >= 300:
            pause_counter = 0
            pause = False

        #if pause is True and pause_counter < 300, increment pause_counter
        elif pause == True and pause_counter <300:
            pause_counter = pause_counter + 1

        #otherwise, do nothing
        else:
            """do nothing"""

    print("Number of clenches is", clench_counter)

blink_detect()

print("-------------------------------------------------------------------------------------------")
print("-------------------------------------------------------------------------------------------")

brow_detect()
clench_detect()