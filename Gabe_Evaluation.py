import matplotlib as mlp
import easygui
import matplotlib.pyplot as plt
from matplotlib.widgets import Cursor
import numpy as np
import pandas as pd
import os


def offlineEventDetection(archiveFreq):

    # ============================= Parameters =================================
    slew_window = 203      # window for calculating slew
    point_separation = 5        # gap between two slew points to be compared
    slew_diff_thresh = 0.00000628         # slew diff between two slew points separated by "point_separation"
    series_over = 15  # the number of times in a row that slew_diff_thresh is exceeded
    event_thresh = 0.00005       # deviation of slew at the point when series over is reached

    fore_point = point_separation - 1
    # ==========================================================================

    Freq = archiveFreq
    events = []
    over = 0
    check = 0
    sum_ts = []
    sum_freq = []
    sum_tsfreq = []
    sum_ts2 = []
    slew = []
    intercept = []
    line = []
    ts_ph = np.linspace(0, len(Freq), len(Freq))
    Dif_slew = []
    uf = 0
    of = 0

    for j in range(slew_window, len(Freq)):
        sum_ts.append(np.sum(ts_ph[j - slew_window:j]))
        sum_freq.append(np.sum(Freq[j - slew_window:j]))
        sum_tsfreq.append(np.sum(ts_ph[j - slew_window:j] * Freq[j - slew_window:j]))
        sum_ts2.append(np.sum(ts_ph[j - slew_window:j] * ts_ph[j - slew_window:j]))
        slew.append((slew_window * sum_tsfreq[j-slew_window] - sum_ts[j-slew_window] * sum_freq[j-slew_window]) / (slew_window * sum_ts2[j-slew_window] - sum_ts[j-slew_window] * sum_ts[j-slew_window]))
        intercept.append((sum_freq[j-slew_window] - slew[j-slew_window] * sum_ts[j-slew_window]) / slew_window)
        line.append(slew[j-slew_window] * ts_ph[j-slew_window] + intercept[j-slew_window])

        if j >= slew_window and j < (slew_window + point_separation):
            continue

        Dif_slew.append(abs(slew[j-slew_window] - slew[(j-slew_window) - fore_point]))

        if len(Dif_slew) == 1:
            continue

        if Dif_slew[(j - slew_window) - point_separation] > slew_diff_thresh and Dif_slew[((j-slew_window) - point_separation) - 1] > slew_diff_thresh:
            over = over + 1
            check = 0
        else:
            check += 1

        if check == 2:
            over = 0

        if over >= series_over and abs(slew[j - slew_window] - 0.00) >= event_thresh:
            events.append(j)

    return events, slew


# ========================  GETTING DATA FROM CSV FILES  ==============================

#now use easygui library to open window so user can select event files to test with

Archive_filePath = easygui.fileopenbox("Select input CSV File,then press open", "", filetypes= "*.csv",multiple=True)
RTAC_filePath = easygui.fileopenbox("Select output CSV File,then press open", "", filetypes= "*.csv",multiple=True)

is_event2 = []
is_event3 = []

for j in range(len(Archive_filePath)):
    RTAC_TimeArr = []
    Archive_FreqArr = []
    RTAC_FreqArr = []
    Archive_SlewArr = []
    Archive_SlewVal = []
    ArchiveSeriesEvents = []
    Archive_FileSlewArr =[]
    RTAC_SlewArr = []
    RTAC_slewVal = []
    RTAC_SeriesEventArr = []
    RTACEventLine = np.nan

    df = pd.read_csv(Archive_filePath[j], encoding='cp1252', low_memory=False)
    df2 = pd.read_csv(RTAC_filePath[j], encoding='cp1252', low_memory=False)

    i = 0
    for i, row in df.iterrows():

        Archive_FreqArr.append(df.iloc[i, 1])
        Archive_FileSlewArr.append(df.iloc[i, 8])

    length = len(Archive_FreqArr)
    # for i in range(17999):
    #     if i > length:
    #         Archive_FreqArr.append(60)

    ts_ph = np.linspace(0, len(Archive_FreqArr), len(Archive_FreqArr))
    # Archive_SlewArr = slew_calc(228, ts_ph, Archive_FreqArr, Archive_filePath[j])


    for i, row in df2.iterrows():
        RTAC_FreqArr.append(df2.iloc[i, 1])
        RTAC_SlewVal = df2.iloc[i, 2]

        # checks for string characters in slew
        RTAC_SlewVal = str(RTAC_SlewVal)
        if RTAC_SlewVal[-1].isdigit() == False:
            RTAC_SlewVal = RTAC_SlewVal[:-1]
        RTAC_SlewArr.append(float(RTAC_SlewVal))
        #
        RTAC_SeriesEventArr.append(df2.iloc[i,3])

    for i in range(len(RTAC_FreqArr)):
        if i > length:
            RTAC_FreqArr.pop(length)

    # for i in range(228-1):
    #     Archive_SlewArr.insert(0, 0)
    #     RTAC_SlewArr.insert(0, 0)


    # for i in range(len(Archive_FileSlewArr)):
    #     Archive_FileSlewArr[i] = Archive_FileSlewArr[i]/100


# ==================  OFFLINE EVENT DETECTION  ============================
    offlineSlew = []

    ArchiveSeriesEvents, offlineSlew = offlineEventDetection(Archive_FreqArr)

    if len(ArchiveSeriesEvents) > 0:
        is_event2.append(True)
    else:
        is_event2.append(False)

# ==================  ONLINE EVENT DETECTION  =============================

    RTACEventLine = []
    for i in range(len(RTAC_SeriesEventArr)):
        if (i > 500) & (RTAC_SeriesEventArr[i] == 1.0) & (i < length - 500):  # ignore first 300 indexes and last 200, find first series event, break to ignore any after that
            RTACEventLine.append(i)

    if len(RTACEventLine) > 0:
        is_event3.append(True)
    else:
        is_event3.append(False)

# ================== PLOTTING ONLINE VS ONLINE FREQUENCY AND DETECTION TIMES =======================

    print(RTAC_SlewVal)

    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 6))
    title = 'Archive Data ' + Archive_filePath[j]
    # Define Archive Frequency graph
    ax1.plot(Archive_FreqArr, color='k', lw=1)
    ax1.set_ylim(59.85, 60.15)
    ax1.title.set_text(title)
    ax1.set_ylabel('Frequency (Hz)')
    ax1.grid(True, color='k', linestyle=':')
    RTAC_Title = 'Rtac Data ' + RTAC_filePath[j]
    if len(ArchiveSeriesEvents) > 0:
        eventLine1 = ArchiveSeriesEvents[0]
        ax1.vlines(x=[eventLine1], ymin=0, ymax=70, ls='--', color='r')
    print(ArchiveSeriesEvents)
    print(RTACEventLine)

    # Define cursor for finding the start of event
    cursor1 = Cursor(ax1, horizOn=False, vertOn=True, useblit=True)

    # ax2.plot(Archive_SlewArr)
    # Define RTAC frequency graph7
    ax2.plot(RTAC_FreqArr, color='r', lw=1)
    ax2.set_ylim(59.85, 60.15)
    ax2.title.set_text(RTAC_Title)
    ax2.set_ylabel('Frequency (Hz)')
    ax2.grid(True, color='k', linestyle=':')

    if len(RTACEventLine) > 0:
        eventLine2 = RTACEventLine[0]
        ax2.vlines(x=[eventLine2], ymin=0, ymax=70,
                   ls='--', color='r')  # this is vertical line showing where RTAC event flag is seen

    # Define cursor for finding the start of event
    # cursor2 = Cursor(ax2, horizOn=False, vertOn=True, useblit=True)
    #
    # Inception = []
    # def onclick(event):
    #     global Inception
    #     Inception = int(event.xdata)
    #     print(Inception)
    #     dt = (RTACEventLine - Inception) / 30
    #     print('dt: ',dt)
    #
    # fig.canvas.mpl_connect('button_press_event', onclick)

    # print('\nOffline events detected: ', is_event2)
    # print('Online events detected: ', is_event3)

    dir_Path = "Z:\Test results\Output tests\Plots"
    my_file = 'graph' + str(j) + '.png'

    fig.savefig(os.path.join(dir_Path, my_file))



    plt.show()



# ====================== Evaluation code =======================================

# home_dir=r'E:\Study\Engineering\MS USA\Power Engineering Lab\Fresp\2021 algo\\'     # Project home dir
human_valid='Z:\Human Validation - 20.csv'        # human validation file containing expert assessment
df3 = pd.read_csv(human_valid)       # read human validation .csv
name = df3['Name']        # read first column with names of original freq files
is_eventH = df3['Is_event']       # read last column that consists of event assessment i.e. True/False
print('\nOffline events detected: ', is_event2)
print('Online events detected: ', is_event3)
print(is_eventH)
# Paths for original frequency files
files_path=r'Z:\20 File Set'


# print('\nOffline events detected: ', is_event2)
# print('Online events detected: ', is_event3)
print('\n\n===== Offline Evaluation =====')
TP=0
TN=0
FP=0
FN=0
for i in range(len(is_event2)):
    if is_event2[i] == is_eventH[i] and is_event2[i] == True:
        TP=TP+1
    elif is_event2[i] == is_eventH[i] and is_event2[i] == False:
        TN=TN+1
    elif is_event2[i] != is_eventH[i] and is_event2[i] == True:
        FP=FP+1
    elif is_event2[i] != is_eventH[i] and is_event2[i] == False:
        FN=FN+1


totalexample = TP + FP + FN + TN
print("TP = {}\nFP = {}\nFN = {}\nTN = {}\nTotal examples = {}".format(TP, FP, FN, TN, totalexample))
Accuracy = round(((TP + TN) / totalexample) * 100)
if TP == 0 and FN == 0:
    FN = totalexample
Sensitivity = (TP / (TP + FN)) * 100
if TP == 0 and FP == 0:
    FP = totalexample
Precision = round((TP / (TP + FP)) * 100)
if TN == 0 and FP == 0:
    FP = totalexample
Specificity = round((TN / (TN + FP)) * 100)
FDR = round((FP / (FP + TP)) * 100)
# calculating the F scores
print('Accuracy:',Accuracy)
print('Sensitivity:',Sensitivity)
print('Precision:',Precision)
print('Specificity:',Specificity)
print('FDR:',FDR)


# print(detect)             # print the sample at which event is detected in each file
# print(is_event2)           # print event classification by the algorithm
# print(list(is_eventH))        # print event classification by the human experts
# end = time.time()
# print('Time elapsed:', end-start)


print('\n\n===== Online Evaluation =====')
TP=0
TN=0
FP=0
FN=0
for i in range(len(is_event2)):
    if is_event3[i] == is_eventH[i] and is_event3[i] == True:
        TP=TP+1
    elif is_event3[i] == is_eventH[i] and is_event3[i] == False:
        TN=TN+1
    elif is_event3[i] != is_eventH[i] and is_event3[i] == True:
        FP=FP+1
    elif is_event3[i] != is_eventH[i] and is_event3[i] == False:
        FN=FN+1


totalexample = TP + FP + FN + TN
print("TP = {}\nFP = {}\nFN = {}\nTN = {}\nTotal examples = {}".format(TP, FP, FN, TN, totalexample))
Accuracy = round(((TP + TN) / totalexample) * 100)
if TP == 0 and FN == 0:
    FN = totalexample
Sensitivity = (TP / (TP + FN)) * 100
if TP == 0 and FP == 0:
    FP = totalexample
Precision = round((TP / (TP + FP)) * 100)
if TN == 0 and FP == 0:
    FP = totalexample
Specificity = round((TN / (TN + FP)) * 100)
FDR = round((FP / (FP + TP)) * 100)
# calculating the F scores
print('Accuracy:',Accuracy)
print('Sensitivity:',Sensitivity)
print('Precision:',Precision)
print('Specificity:',Specificity)
print('FDR:',FDR)

# print(detect)             # print the sample at which event is detected in each file
# print(is_event2)           # print event classification by the algorithm
# print(list(is_eventH))        # print event classification by the human experts
# end = time.time()
# print('Time elapsed:', end-start)