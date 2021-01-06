#importing necessary libraries
import csv
import re

def process_shifts(path_to_csv):
    
    #Checking if the input is a string, however commented out due to instructions set
    #if type(path_to_csv) != str:
        #raise TypeError("Path to work_shift has to be a string.")
    
    #reading data from csv file
    excel_file = path_to_csv
    data = open(excel_file, encoding="utf-8")
    csv_data = csv.reader(data)
    data_list = list(csv_data)

    #creating the dictionary 
    work_shift_dict = {"00:00": 0., "01:00": 0., "02:00": 0., "03:00": 0., "04:00": 0., "05:00": 0., "06:00": 0., 
    "07:00": 0., "08:00": 0., "09:00": 0., "10:00": 0., "11:00": 0., "12:00": 0., "13:00": 0., "14:00": 0., "15:00": 0.
    , "16:00": 0., "17:00": 0., "18:00": 0., "19:00": 0., "20:00": 0., "21:00": 0., "22:00": 0., "23:00": 0.}

    #iterating over all the workers
    for row in data_list[1:]:
        #all data in string
        start_time = row[3]
        end_time = row[1]
        pay = row[2]
        notes = row[0]
        #list with starting and ending break times
        time_off = notes.split('-')
        #removing any letters
        counter = 0
        b = "PAM"
        for time in time_off:
            for char in b:
                time_off[counter]= time_off[counter].replace(char,"")
            counter +=1
        #converting all to 24 hour time
        counter = 0
        for time in time_off:
            if float(time)>= 1 and float(time)<=8:
                time_off[counter] = float(time) + 12.0
            counter +=1
        #grabbing first two and last two digits of time
        start_time_2 = start_time[:2]
        end_time_2 = int(end_time[:2])
        start_time_last2 = int(start_time[-2:])
        end_time_last2 = int(end_time[-2:])
        pay_int = float(pay)
        #adding pay values to the dictionary
        #accounting for minutes
        if start_time_last2 != 0:
            work_shift_dict[str(start_time_2) + ":00"] =  float(work_shift_dict[str(start_time_2) + ":00"]) + pay_int * (start_time_last2/60)
        else:
            work_shift_dict[str(start_time_2) + ":00"] =  float(work_shift_dict[str(start_time_2) + ":00"]) + pay_int

        if end_time_last2 != 0:
            work_shift_dict[str(end_time_2) + ":00"] =  float(work_shift_dict[str(end_time_2) + ":00"]) + pay_int * (end_time_last2/60)

        #accounting for the main body of pay
        for y in range(int(start_time_2) +1, end_time_2 ):
            previous = work_shift_dict[str(y) + ":00"]
            work_shift_dict[str(y) + ":00"] =  float(previous) + pay_int

        #deducting times when on break
        if (float(time_off[0])) % 1 != 0:
            previous = work_shift_dict[str(time_off[0])[:2] + ":00"]
            work_shift_dict[str(time_off[0])[:2] + ":00"] =  float(previous) - pay_int*(((float(time_off[0])) % 1) * 100/60)
        elif (float(time_off[1])) % 1 != 0:
            previous = work_shift_dict[str(time_off[0])[:2] + ":00"]
            work_shift_dict[str(time_off[0])[:2] + ":00"] =  float(previous) - pay_int*(((float(time_off[1])) % 1) * 100/60)
        else:
            for i in range(int(str(time_off[0])[:2]), int(str(time_off[1])[:2] )):
                previous = work_shift_dict[str(i) + ":00"]
                work_shift_dict[str(i) + ":00"] =  previous - pay_int

    return work_shift_dict


def process_sales(path_to_csv):
    
    #reading data from csv file
    excel_file = path_to_csv
    data = open(excel_file, encoding="utf-8")
    csv_data = csv.reader(data)
    #list of lists, each list of len 2 consisting of amount and time
    data_list = list(csv_data)[1:]

    #creating the dictionary
    trans_dict = {"00:00": 0., "01:00": 0., "02:00": 0., "03:00": 0., "04:00": 0., "05:00": 0., "06:00": 0., 
    "07:00": 0., "08:00": 0., "09:00": 0., "10:00": 0., "11:00": 0., "12:00": 0., "13:00": 0., "14:00": 0., "15:00": 0.
    , "16:00": 0., "17:00": 0., "18:00": 0., "19:00": 0., "20:00": 0., "21:00": 0., "22:00": 0., "23:00": 0.}

    #looping over all the rows
    for row in data_list:
        amount = row[0] #string
        time = row[1] #string
        hour = time[:2] #getting the hour
        hour_full = hour + ":00" #concatenating string into correct format for dict
        trans_dict[hour_full] = trans_dict[hour_full] + float(amount) #adding amount into that hour

    return trans_dict

def compute_percentage(shifts, sales):
    
    #creating the empty dictionary
    percent_dict = {"00:00": 0., "01:00": 0., "02:00": 0., "03:00": 0., "04:00": 0., "05:00": 0., "06:00": 0., 
    "07:00": 0., "08:00": 0., "09:00": 0., "10:00": 0., "11:00": 0., "12:00": 0., "13:00": 0., "14:00": 0., "15:00": 0.
    , "16:00": 0., "17:00": 0., "18:00": 0., "19:00": 0., "20:00": 0., "21:00": 0., "22:00": 0., "23:00": 0.}

    #looping over dictionary key and values
    for key, value in percent_dict.items():
        if shifts[key] == 0.:
            percent = 0.
        else:
            try:
                percent = (shifts[key] / sales[key]) * 100
            except ZeroDivisionError:
                percent = - shifts[key] #accounting for dividing by zero
        percent_dict[key] = round(percent, 2) #round to 2 decimal places
        
    return percent_dict

def best_and_worst_hour(percentages):
    
    #setting the max and min values
    max_val = 0
    min_val = 0
    index_best = 0
    index_worst = 0

    #iterating over dictionary
    for key, value in percentages.items():
        if value > max_val:
            index_best = key 
            max_val = value #update new maximum
        elif value < min_val:
            index_worst = key
            min_val = value #update new minimum
        else: 
            pass

    return [index_best, index_worst] 

