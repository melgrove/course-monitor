#Trying my best
from bs4 import BeautifulSoup
import requests
import time
import smtplib
import re
import ssl
import datetime
from datetime import timedelta

## How to use ##
# set up an unsecure email that you can login to from this script
# add the email and password in sender_email and sender_password
# add the email from which you want to receive the notification in receiver_email
# add the class and size to the size dict
# add the class and url to the to_monitor dict
# make sure to convert your local timezone to the school's update timezone if they are not the same
# viola!

## Program init
iterations = 0
port = 465
send_on_waitlist = True #send email if the class is waitlisted?
log = True #log requests to text file?
#init_time set to any time more than an hour before current time to trigger initial request where timer is updated from page 
init_time = (datetime.datetime.now() - timedelta(minutes=60.1)).time()

## Email init
sender_password = "example@domain.com"                   # <- CHANGE
sender_email = "example@domain.com"                      # <- CHANGE
receiver_email = "example@domain.com"                    # <- CHANGE
context = ssl.create_default_context()

## Course init
#this is an example. You can monitor an arbitrary number of classes
#the name (key) that you choose doesn't matter, however it must be the same between timer, size, and to_monitor
timer = {"Math170E1":init_time, "Math170E2":init_time}   # <- CHANGE
size = {"Math170E1":35, "Math170E2":35}                  # <- CHANGE
to_monitor = {                                           # <- CHANGE
    "Math170E1":"https://sa.ucla.edu/ro/Public/SOC/Results/ClassDetail?term_cd=20S&subj_area_cd=MATH%20%20%20&crs_catlg_no=0170E%20%20%20&class_id=262720200&class_no=%20001%20%20",
    "Math170E2":"https://sa.ucla.edu/ro/Public/SOC/Results/ClassDetail?term_cd=20S&subj_area_cd=MATH%20%20%20&crs_catlg_no=0170E%20%20%20&class_id=262720210&class_no=%20002%20%20"
}


#%%
while True:
    for k, v in to_monitor.items(): #key, value
        #The UCLA system updates every 1 hour. timedelta is set to slightly less than an hour to catch early updates
        now = (datetime.datetime.now() - timedelta(minutes=59.6)).time()
        #if it is an hour after the last update time and not edge case at midnight 
        if timer[k] < now and not (now.strftime("%p") == "PM" and timer[k].strftime("%p") == "AM"):
            #GET Request
            course = requests.get(v)
            soup = BeautifulSoup(course.text, 'html.parser')
            #Parsing Status - Specific to UCLA page
            course_table = soup.find("div", class_="row-fluid data-row enrl_mtng_info scrollable-collapse table-width2")
            course_list = str(course_table.find('div', class_='span1'))
            course_status = re.split(r'\<p\>|\<\/p\>',course_list)[1]
            #Parsing Refresh Time - Specific to UCLA page
            parsed_time = str(soup.find("div", class_="message info"))
            current_AMPM = re.search("[AP]M(?=\.)", parsed_time).group(0)
            current_time = re.search("(?<=as of )[\d:]*",parsed_time).group(0)
            current_time24 = datetime.datetime.strptime(current_time + current_AMPM,'%I:%M%p').time()
            timer[k] = current_time24 #setting timer to last update time
            #%%
            #Testing to see if class is full
            status = "Open"
            if re.search("(Closed: Class Full \(.*\))", course_status):
                status = "Closed"
            if re.search("(Closed by)", course_status):
                status = "Closed"
            if re.search("(Waitlist: Class Full \(.*\))", course_status):
                status = "Waitlist"
            #if not closed send email
            if status == "Open" or (status == "Waitlist" and send_on_waitlist == True):
                message = f"Subject: {k} is now {status}!\n\n go sign up you fool!\nText: {course_status}"
                #Sending email
                with smtplib.SMTP_SSL("smtp.gmail.com", port, context=context) as server:
                    server.login(sender_email, sender_password)
                    server.sendmail(sender_email, receiver_email, message)
                #Logging to console
                print(f"{k} is {status}!")
                print("email sent regarding %s" % k)
                if log:
                    #Logging to text file
                    file = open("%s.txt" % k,"a")
                    file.write(f"{k} Open at {status}" + str(datetime.datetime.now()) + '\n')
                    file.close()
            else:
                print(f"{k} is closed. System updated at {current_time} {current_AMPM}")
                if log:
                    #Logging to text file
                    file = open("%s.txt" % k,"a")
                    file.write("%s Closed at " % k + str(datetime.datetime.now()) + '\n')
                    file.close()
    iterations += 1
    #Logging to console
    print(f"Iteration: {iterations}, System updated at: ", end="")
    for k, v in timer.items():
        print(f"{k}: {v}", end=" | ")
    print("", end="\n")
    #Wait 5 seconds before testing time diff again
    time.sleep(5)

# Note 1: This does not send a GET request every 5 seconds! It waits until
# an hour after the last update to send a GET request. If the school system
# is slow and doesn't update after an hour the program will send a GET
# request every 5 seconds until it updates. I've been told that the UCLA
# system has an update error margin within 2 minutes.
    
# Note 2: The program runs in a while True loop so it will continue
# checking forever until you manually stop it
    
# Note 3: Scraping course data may not be allowed at your college and I
# assume no liability for one using this software in a wrongful manner.

