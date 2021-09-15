#!/usr/bin/env python
# coding: utf-8

# Katie O'SHEA


from dicompylercore import dicomparser, dvh, dvhcalc
import pydicom
from pydicom import dcmread
import numpy as np
import matplotlib.pyplot as plt
import math
from matplotlib.patches import Rectangle
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from mpldatacursor import datacursor
from tkinter import *
from tkinter import ttk
from tkinter import filedialog
from tkinter.filedialog import askopenfile 
from tkinter import messagebox
from tkinter.ttk import *
import tkcalendar
import time
from pathlib import Path
import os.path
import os
import csv
from datetime import timedelta


window = Tk()
tabControl = ttk.Notebook(window)
tab1 = ttk.Frame(tabControl)
tab2 = ttk.Frame(tabControl)

class EQD2VH:

    def __init__(self, window):
        global var

        self.window = window
        self.window.title("Welcome to EQD2VH")
        window.configure(background='whitesmoke')

        # -*- CREATING LABELS FOR TREATMENT GAP CALCULATIONS -*-
        

        #k factor of the tumour
        self.kfactor_label = Label(window, text="K Factor (Gy/day)")
        self.kfactor_label.grid(row=4, column = 0)
        self.kfactor = Entry(window, width = 5)
        self.kfactor.grid(row=4, column=0, sticky=E)

        #delay time of the tumour
        self.tdelay_label = Label(window, text="T_delay (days)")
        self.tdelay_label.grid(row=5, column = 0)
        self.tdelay = Entry(window, width = 5)
        self.tdelay.grid(row=5, column=0, sticky=E)

        #alpha beta for the ROI
        self.tumour_ab_label= Label(window, text="alpha/beta")
        self.tumour_ab_label.grid(row=6, column = 0)
        self.tumour_ab = Entry(window, width = 5)
        self.tumour_ab.grid(row=6, column=0, sticky=E)

        #fractionation for the initial plan
        self.init_frac_label= Label(window, text="Prescribed Fractions")
        self.init_frac_label.grid(row=4, column = 2, sticky = W)
        self.init_frac = Entry(window, width = 5)
        self.init_frac.grid(row=4, column=3, sticky=W)

        #number of fractions completed before treatment gap
        self.pre_gap_label= Label(window, text="Pre-Gap Fractions")
        self.pre_gap_label.grid(row=5, column = 2, sticky = W)
        self.pre_gap = Entry(window, width = 5)
        self.pre_gap.grid(row=5, column=3, sticky=W)

        #no of fractions completed after treatment gap
        self.post_gap_label= Label(window, text="Post-Gap Fractions")
        self.post_gap_label.grid(row=6, column = 2, sticky = W)
        self.post_gap = Entry(window, width = 5)
        self.post_gap.grid(row=6, column=3, sticky=W)

        #two frac days after gap
        self.twice_daily_label= Label(window, text="Twice-Daily Fractions")
        self.twice_daily_label.grid(row=7, column = 2, sticky = W)
        self.twice_daily = Entry(window, width = 5)
        self.twice_daily.grid(row=7, column=3, sticky=W)

        var = IntVar()
        ttk.Radiobutton(window, text="OAR", variable = var,  value=0).grid(row=14, column = 0, columnspan = 1)
        ttk.Radiobutton(window, text="Target Volume", variable = var, value=1).grid(row=15, column = 0, columnspan = 1)
        
        #prescribed treatment time (before gap) 
        self.init_trt_time_label = Label(window, text="Treatment Start Date")
        self.init_trt_time_label.grid(row=16, column = 0)

        init_date1 = tkcalendar.DateEntry(window, date_pattern='dd/mm/y')
        init_date1.grid(row=16,column=1)
        
        #actual treatment time (b/c of gap)
        self.gap_trt_time_label= Label(window, text="Initial Treatment End")
        self.gap_trt_time_label.grid(row=17, column = 0)

        init_date2 = tkcalendar.DateEntry(window, date_pattern='dd/mm/y')
        init_date2.grid(row=17,column=1)

        #actual treatment time (b/c of gap)
        self.gap_trt_time_label= Label(window, text="Actual Treatment End")
        self.gap_trt_time_label.grid(row=18, column = 0)

        actual_date3 = tkcalendar.DateEntry(window, date_pattern='dd/mm/y')
        actual_date3.grid(row=18,column=1)


        #buttons to upload files
        upload_dose = Button(window, text = "Upload Initial Plan Dose File(s)", command = self.dosefiles1, width = 25).grid(row=9, column=0)  
        upload_dose = Button(window, text = "Upload Revised Plan Dose File(s)", command = self.dosefiles2, width = 25).grid(row=10, column=0)
        upload_struc = Button(window, text = "Upload Structure File", command = self.structurefileGAP, width = 20).grid(row=11, column=0)

        #button to calculate the treatment gap BED
        

        dateCalc = Button(window,text='1. Calculate Treatment Times', command=lambda:[self.init_date_range(init_date1.get_date(), init_date2.get_date(), actual_date3.get_date())]).grid(row=20, column=0)
        gapBED = Button(window, text = "2. Generate DVHs", command = self.gapBED, width = 21).grid(row=21, column=0)



    # -*- FUNCTION TO UPLOAD DOSE FILES FOR PLAN 1 FOR TREATMENT GAP CALCULATIONS -*-   

    def dosefiles1(self):
        global dose_files1
            
        self.dosefiles1 = filedialog.askopenfilenames(initialdir="/", title="Select Dose Files") #select multiple RT dose files
            
        if self.dosefiles1 == '':
            tkMessageBox.showinfo(message="No file was selected")
            return
        else:
            dose_files1 = len(self.dosefiles1) #calculate number of dose files uploaded
            print(dose_files1)
            str_dosefiles1 = str(dose_files1)
            self.labelFiles1 = Label(window, text = "Plan 1 files: " + str_dosefiles1)
            self.labelFiles1.grid(row = 9, column = 1, columnspan = 2, sticky = W)


    # -*- FUNCTION TO UPLOAD DOSE FILES FOR PLAN 2 FOR TREATMENT GAP CALCULATIONS -*- 
                
    def dosefiles2(self):
        global dose_files2
            
        self.dosefiles2 = filedialog.askopenfilenames(initialdir="/", title="Select Dose Files") #select multiple RT dose files
            
        if self.dosefiles2 == '':
            tkMessageBox.showinfo(message="No file was selected")
            return
        else:
            dose_files2 = len(self.dosefiles2) #calculate number of dose files uploaded
            print(dose_files2)
            str_dosefiles2 = str(dose_files2)
            self.labelFiles2 = Label(window, text = "Plan 2 files: " + str_dosefiles2)
            self.labelFiles2.grid(row = 10, column = 1, columnspan = 2, sticky = W)
 

    # -*- FUNCTION TO UPLOAD A STRUCTURE FILE FOR TREATMENT GAP CALCULATIONS -*- 
    def structurefileGAP(self):
        global var
        self.structurefileGAP = filedialog.askopenfilename(initialdir="/", title="Select Structure File") #select RT structure file
        if self.structurefileGAP == '':
            tkMessageBox.showinfo(message="No file was selected")
            return
        else:
                
            RTStrucPathGAP = "".join(self.structurefileGAP)
            RSHead, RSTail = os.path.split(RTStrucPathGAP)
            self.labelStrucGAP = Label(window, text = " ")
            self.labelStrucGAP.grid(row = 11, column = 1, columnspan = 2)
            self.labelStrucGAP.configure(text=RSTail)
            
            rtssGAP = dicomparser.DicomParser(RTStrucPathGAP)
            RTstructuresGAP = rtssGAP.GetStructures() 
                
            #https://stackoverflow.com/questions/12117080/how-do-i-create-dictionary-from-another-dictionary

            variableGAP = StringVar(window)
            defaultGAP = 'View Structures'
            dropdownGAP = OptionMenu(window, variableGAP, *RTstructuresGAP.values())
            variableGAP.set(defaultGAP)
            dropdownGAP.grid(row = 12, column = 0, columnspan = 5) 
                
            self.key_labelGAP = Label(window, text="Structure ID")
            self.key_labelGAP.grid(row=13, column=0) 
            self.keyGAP = Entry(window, width = 5)
            self.keyGAP.grid(row=13, column=0, columnspan = 2)

    def init_date_range(self, init_start, init_stop, actual_stop): #https://stackoverflow.com/questions/66510020/select-date-range-with-tkinter
        global init_dates # If you want to use this outside of functions
        global init_diff
        global actual_diff
     
        init_dates = []
        init_diff = (init_stop-init_start).days
        actual_dates = []
        actual_diff = (actual_stop-init_start).days
        for i in range(init_diff+1):
            init_day = init_start + timedelta(days=i)
            init_dates.append(init_day)
            actual_day = init_start + timedelta(days=i)
            actual_dates.append(actual_day)
        if init_dates:
            print(init_diff) # Print it, or even make it global to access it outside this
            print(actual_diff)

        else:
            print('Make sure the end date is later than start date')

    # -*- FUNCTION TO CREATE AND PLOT THE DVHS FOR TREATMENT GAP CALCULATIONS -*-
    def gapBED(self):

        self.newWindow = Toplevel(self.window) #initiate new window for summed DVH
        self.newWindow.title("Recalculated DVH for Treatment Gap")
        

        #if val is None:
            #messagebox.showerror("Error", "Please tick OAR or Target Volume")

        #creating Plan 1 variables

        calcdvhs_init_0 = {}
        calcdvhs_init = {}
        init_EQD2 = {}
        init_lastdata = {}
        init_totaldose = 0
        calcdvhs_pre = {}
        pre_gap_EQD2 = {}
        pre_gap_lastdata = {}
        pre_gap_totaldose = 0
        vol1 = {}
        
        

        #creating Plan 2 variables
        calcdvhs_post_0 = {}
        calcdvhs_post = {}
        vol2 = {}

        data3 = {}
        data4 = {}

        post_gap_EQD2 = {}
        twice_daily_EQD2 = {}
        total_post_gap_EQD2 = {}
        post_gap_lastdata = {}
        post_gap_totaldose = 0
        RB_correct = 0
            
        init_frac = float(self.init_frac.get())
        pre_gap_frac = float(self.pre_gap.get())
        post_gap_frac = float(self.post_gap.get())
        key = float(self.keyGAP.get())
        twice_daily = float(self.twice_daily.get())

        kfactor = float(self.kfactor.get())
        init_trt_time = init_diff
        gap_trt_time = actual_diff
        delay_time = float(self.tdelay.get())
        tumour_ab = float(self.tumour_ab.get())
        ott_days = gap_trt_time - init_trt_time
        
        
        #repopulation factors for prescribed and actual treatment times
        init_RF = kfactor * (init_trt_time - delay_time)
        gap_RF = kfactor * (gap_trt_time - delay_time)


        #ratios of given dose to prescribed dose
        pre_frac_ratio = pre_gap_frac/init_frac
        post_frac_ratio = post_gap_frac/init_frac
        

        #iterating through file(s) uploaded for Initial Plan
        for i in range(0,dose_files1): 
                
            RTDosePath1 = "".join(self.dosefiles1[i]) #join the parts of file path together for each iteration
            RTHead1, RTTail1 = os.path.split(RTDosePath1) #split file path to isolate file name
            
                 
            RTStrucPathGAP = "".join(self.structurefileGAP)
            RSHead, RSTail = os.path.split(RTStrucPathGAP)
            rtssGAP = dicomparser.DicomParser(RTStrucPathGAP)
            RTstructuresGAP = rtssGAP.GetStructures()

                
            print(RTTail1) #print structure filename
            RTStruc = RSTail #rtss assigned to filename
            
            RB_correct = 1
            calcdvhs_init_0[key] = dvhcalc.get_dvh(RB_correct, RTStrucPathGAP, RTDosePath1, key)
            choice = var.get()
            if choice == 0: #OAR dose per fraction
                init_dpf = calcdvhs_init_0[key].bins/init_frac
            elif choice == 1: #Target Volume dose per fraction
                init_dpf = calcdvhs_init_0[key].bins[1:]/init_frac
                
            BED = (1 + (init_dpf/tumour_ab))

            if choice == 0: 
                RB_correct = BED/(1 + (float(2.0)/tumour_ab)) #BED for normal tissue if OAR is ticked
                calcdvhs_init[key] = dvhcalc.get_dvh(RB_correct, RTStrucPathGAP, RTDosePath1, key)
                init_EQD2[i] = np.array(calcdvhs_init[key].bins[1:])
            elif choice == 1:
                
                RB_correct = (BED - (init_RF/calcdvhs03[key].bins[1:]))/(1 + (float(2.0)/tumour_ab)) #BED for tumour tissue with repopulation factor if Target Volume is ticked
                RB_correct = np.insert(RB_correct, 0, 0)
                calcdvhs_init[key] = dvhcalc.get_dvh(RB_correct, RTStrucPathGAP, RTDosePath1, key)
                init_EQD2[i] = np.array(calcdvhs_init[key].bins[1:])

            init_lastdata = init_EQD2[i]
            init_totaldose += init_lastdata[-1]
            
            print("Initial plan DVH statistics")
            print(calcdvhs_init[key].describe())

            #calculating dose for pre-gap BED (no RF)
            init_dpf = calcdvhs_init_0[key].bins/init_frac
            BED = (1 + (init_dpf/tumour_ab))
            RB_correct = BED/(1 + (float(2.0)/tumour_ab))
            
            calcdvhs_pre[key] = dvhcalc.get_dvh(RB_correct, RTStrucPathGAP, RTDosePath1, key)
            
            pre_gap_EQD2[i] = np.array(calcdvhs_pre[key].bins[1:]) * pre_frac_ratio 
            pre_gap_lastdata = pre_gap_EQD2[i]
            pre_gap_totaldose += pre_gap_lastdata[-1]
            
            vol1[i] = calcdvhs_init[key].counts[1:] * 100 / calcdvhs_init[key].counts[0]
            vol1[i] = np.append(vol1[i], 0)

                
        y1 = vol1[0]
        
        if dose_files1 == 1:
            y1len = len(y1)
            init_x = init_lastdata
            pre_gap_x = pre_gap_lastdata
            
        else:
            for i in range (1, dose_files1):
                y1 = np.concatenate((y1, vol1[i]), axis=0)
            sorty1 = np.sort(y1)
            y1 = sorty1[::-1]
            y1len = len(y1)
            init_x = init_lastdata
            pre_gap_x = pre_gap_lastdata
            
        #iterating through files uploaded for Revised Plan
        
        for i in range(0,dose_files2): 
                
            RTDosePath2 = "".join(self.dosefiles2[i])
            RTHead2, RTTail2 = os.path.split(RTDosePath2)
                
            RTStrucPathGAP = "".join(self.structurefileGAP)
            RSHead, RSTail = os.path.split(RTStrucPathGAP)
            rtssGAP = dicomparser.DicomParser(RTStrucPathGAP)
            RTstructuresGAP = rtssGAP.GetStructures()
                
            print(RTTail2) #print filename
            RTStruc = RSTail #rtss assigned to filename
            
            #REMAINDER OF DOSE
            RB_correct = 1
            calcdvhs_post_0[key] = dvhcalc.get_dvh(RB_correct, RTStrucPathGAP, RTDosePath2, key) #obtaining physical dose to create D/N
            choice = var.get()
            if choice == 0: #OAR dose per fraction
                post_gap_dpf = (calcdvhs_post_0[key].bins/post_gap_frac)
            elif choice == 1: #PTV dose per fraction
                post_gap_dpf = (calcdvhs_post_0[key].bins[1:]/post_gap_frac)
                
            BED = 1 + (post_gap_dpf/tumour_ab)

            if choice == 0:
                RB_correct = BED/(1 + (float(2.0)/tumour_ab)) #BED for normal tissue if OAR is ticked
                calcdvhs_post[key] = dvhcalc.get_dvh(RB_correct, RTStrucPathGAP, RTDosePath2, key)
                post_gap_EQD2[i] = np.array(calcdvhs_post[key].bins[1:])
                twice_daily_EQD2[i] = np.full(len(post_gap_EQD2), (twice_daily/2)*(0.125))
                total_post_gap_EQD2[i] = np.add(post_gap_EQD2[i], twice_daily_EQD2[i])

            elif choice == 1:
                RB_correct = (BED - (gap_RF/calcdvhs04[key].bins[1:]))/(1 + (float(2.0)/tumour_ab)) #BED for tumour tissue with repopulation factor if Target Volume is ticked
                RB_correct = np.insert(RB_correct, 0, 0)
                calcdvhs_post[key] = dvhcalc.get_dvh(RB_correct, RTStrucPathGAP, RTDosePath2, key)
                total_post_gap_EQD2[i] = np.array(calcdvhs_post[key].bins[1:])
                
            post_gap_lastdata = total_post_gap_EQD2[i]
            post_gap_totaldose += post_gap_lastdata[-1]

            
            vol2[i] = calcdvhs_post[key].counts[1:] * 100 / calcdvhs_post[key].counts[0] #creating volume
            vol2[i] = np.append(vol2[i], 0)


            print("Revised plan DVH statistics")
            print(calcdvhs_post[key].describe())
                
        y2 = vol2[0]
        if dose_files2 == 1:
            y2len = len(y2)
            post_gap_x = post_gap_lastdata
        else:
            for k in range(1, dose_files2):
                y2 = np.concatenate((y2, vol2[k]), axis = 0)
            sorty2 = np.sort(y2) #sorted volume data array in ascending order
            y2 = sorty2[::-1] #volume data array reversed to descending order
            y2len = len(y2)
            post_gap_x = post_gap_lastdata
          
        #initiation of DVH window
        fig = Figure()
        ax = fig.add_subplot(111)
           
        name = RTstructuresGAP[key]['name']
        init_t = str(init_trt_time)
        act_t = str(gap_trt_time)
        ext_days = str(ott_days)
        ab = str(tumour_ab)
        
        #plot pre-gap and post-gap BED

        plan1_plot = ax.plot(pre_gap_x, y1, label = 'Pre-Gap', c = 'b')
        plan1_data = plan1_plot[0].get_data()
        plan2_plot = ax.plot(post_gap_x, y2, label = 'Post-Gap', c = 'g')
        plan2_data = plan2_plot[0].get_data()
        ax.legend()
        ax.set_title("Pre-Gap and Post-Gap DVH for " + name)
        ax.set_ylabel("Volume (%)", fontsize=14)
        ax.set_xlabel("EQD2 (Gy)", fontsize=14)
        ax.grid(True)
        ax.set_axisbelow(True)
        array = np.linspace(0, 100, 9000, endpoint=False)

        #get values from plan1 graph

        xdat1 = plan1_plot[0].get_xdata() #get x data
        fp1 = xdat1[::-1]  # reverses x values to match reversed y values in array
        ydat1 = plan1_plot[0].get_ydata() #get y data
        xp1 = ydat1[::-1]  # reverses y values from decreasng to increasing so interpolation function can work

        # get values from plan2 graph

        xdat2 = plan2_plot[0].get_xdata() #get xdata
        fp2 = xdat2[::-1]  # reverses x values to match reversed y values in array
        ydat2 = plan2_plot[0].get_ydata() #get y data
        xp2 = ydat2[::-1]  # reverses y values from decreasng to increasing so interpolation function can work

        # set volume array to use for dose interpolation
        
        inter1 = np.interp([array], xp1, fp1)  # interpolation of plan1 dose
        reshapeinter1 = np.reshape(inter1, (9000, 1))
        inter2 = np.interp([array], xp2, fp2)  # interpolation of plan2 dose
        reshapeinter2 = np.reshape(inter2, (9000, 1))
        
        # adding plan1 and plan2 dose
        xvalues = reshapeinter1 + reshapeinter2
        reshapearray = np.reshape(array, (9000, 1))  # array of specified %volume intervals

        #plot summed re-calculated DVH in seperate window

        actual_BED = plt.plot(xvalues, reshapearray, c = 'g', label = 'Revised DVH')
        actual_BED_data = actual_BED[0].get_data()
        initial_BED = plt.plot(abs(init_x), y1, c = 'b', label = 'Initial DVH')
        initial_BED_data = initial_BED[0].get_data()
        plt.legend()
        plt.title("DVHs for " + name)
        plt.suptitle("For OTT extension of " + ext_days + " days")
        #plt.subtitle("For prescribed T of " + init_t + " and actual T of " + act_t)
        
        plt.ylabel("Volume (%)", fontsize=14)
        plt.xlabel("EQD2 (Gy)" , fontsize=14)
        plt.grid(True)

        
        #SAVING INITIAL PLAN DVH TO A CSV
        with open('init_plan.csv', 'w') as myfile: 
            writer = csv.writer(myfile)
            writer.writerow(['x', 'y'])
            for i in range(len(initial_BED_data[0])): 
                writer.writerow([initial_BED_data[0][i], initial_BED_data[1][i]])

                
        #SAVING INITIAL PLAN DVH TO A CSV
        with open('comp_plan.csv', 'w') as myfile: 
            writer = csv.writer(myfile)
            writer.writerow(['x', 'y'])
            for i in range(len(actual_BED_data[0])): 
                writer.writerow([actual_BED_data[0][i], actual_BED_data[1][i]])

        #design of summed DVH
        plt.grid(color='gray', linestyle='dashed')
        datacursor()
        ax.yaxis.grid(color='gray', linestyle='dashed')
        ax.xaxis.grid(color='gray', linestyle='dashed')

        #draw summmed DVH
        canvas = FigureCanvasTkAgg(fig, master=self.newWindow)
        canvas.get_tk_widget().grid(row=10)
        canvas.draw()
        plt.show()

        #initiate toolbar for analysis
        toolbarFrame = Frame(master=self.newWindow)
        toolbarFrame.grid(row=20)
        toolbar = NavigationToolbar2Tk(canvas, toolbarFrame)
        toolbar.draw()

window.geometry("700x500")
start = EQD2VH(window)
window.mainloop()
