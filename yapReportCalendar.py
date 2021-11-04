
import sys
from datetime import *
from tkinter import *
from tkcalendar import *

today = date.today()
todays_year = today.strftime("%Y")
todays_month = today.strftime("%m")
todays_day = today.strftime("%d")
global mydate

def getDate():
    global mydate
    # Create a GUI window
    root = Tk()
    root.title("CALENDAR")
    #root.iconbitmap('')
    root.geometry("600x400")
   
    cal = Calendar(root,selectmode ="day",year=int(todays_year), month=int(todays_month),day=int(todays_day))
    cal.pack(pady=20)
    mydate='02/12/1966'

    def grab_date():
            global mydate 
            mydate = cal.get_date()
            my_label.config(text=mydate) 
            print(mydate)
            root.destroy()

    my_button = Button(root, text="Pick Month", command=grab_date)
    my_button.pack(pady=20)

    my_label = Label(root, text="")
    my_label.pack(pady=20)
 
    # Create a label for showing the content of the calendar
    #cal_year = Label(root, text = cal, font = "Consolas 10 bold")
 
    # grid method is used for placing
    # the widgets at respective positions
    # in table like structure.
    #cal_year.grid(row = 5, column = 1, padx = 20)
     
    # start the GUI
    root.mainloop()
    try:
        dt_object = datetime.strptime(mydate,"%m/%d/%y")
        monthStr = dt_object.strftime("%Y") + "-" + dt_object.strftime("%m")
        return monthStr
    except ValueError:
        print("Date not selected, to give the Month: Exiting .....")
        sys.exit()




    
