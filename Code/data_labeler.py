import random 
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.widgets import RectangleSelector
from mpl_toolkits.basemap import Basemap
from matplotlib import gridspec
import csv

def line_select_callback(eclick, erelease):
    'eclick and erelease are the press and release events'
    global x1,y1,x2,y2
    x1, y1 = eclick.xdata, eclick.ydata
    x2, y2 = erelease.xdata, erelease.ydata

def toggle_selector(event):
    global colour
    print(' Key pressed.')
    # Good data
    if event.key in ['G', 'g'] and toggle_selector.RS.active:
        print('> Good Data selected')
        print("(%3.2f, %3.2f) --> (%3.2f, %3.2f)" % (x1, y1, x2, y2))
        colour = 'green'
        toggle_selector.RS.set_active(False) 
    # bad data
    if event.key in ['R', 'r'] and toggle_selector.RS.active:
        print('> Poor data selected')
        print("(%3.2f, %3.2f) --> (%3.2f, %3.2f)" % (x1, y1, x2, y2))
        colour = 'red'
        toggle_selector.RS.set_active(False) 

    # enable user to activate the selector again     
    if event.key in ['T', 't'] and not toggle_selector.RS.active:
        print(' RectangleSelector activated.')
        toggle_selector.RS.set_active(True)


def main():

    list_float = [1901155,1901298,1901324,1901341,1901604,1901685,1901689]

    #create empty dataframe to store user inputs
    df_main = pd.DataFrame(columns=['Feature','Float', 'Profile', 'Colour', 'x1', 'x2', 'y1', 'y2','lat', 'long'])

    # will create a data set 
    print('-----------------------------------------------')
    user = input("Enter name: ")
    #print("Welcome "+ user)
    feat = input("Feature interested: ")
    gen = input("Number of samples: ")

    print('--------- Graph Info ---------')
    print(" White dot represents the current location \n press 'g' to label data as good \n press 'r' to label data poor")

    for i in range(int(gen)):
        #select random float float 
        argo = random.choice(list_float)

        #access the random float  from database
        argo_float = pd.read_csv("/Users/vagifaliyev/Desktop/argo_database/"+str(argo)+'.csv') 

        list_prof = list(dict.fromkeys(argo_float['CYCLE_NUMBER']))

        #randomly select a profile 
        prof = random.choice(list_prof)
        
        df = argo_float.loc[argo_float['CYCLE_NUMBER'] == prof]

        # allocate the columns to specific variable names for easier access
        pres = df['PRES']
        psal = df['PSAL']
        temp = df['TEMP']
        lat = df['LATITUDE'].values[0]
        lon = df['LONGITUDE'].values[0]

        # plotting salinity graph
        fig = plt.figure(figsize=(8,4))
        gs = gridspec.GridSpec(1, 2, width_ratios=[3, 1]) 
        ax = plt.subplot(gs[0])
        # adding a low transperency line to follow the patern more easily
        plt.plot(psal, temp, alpha=0.2)
        # main fature is the scatter plot
        sc = plt.scatter(psal,temp,c=pres, cmap='hsv')
        # add colour graded bar
        cbar = plt.colorbar(sc)
        cbar.set_label('Pressure', labelpad=-40, y=1.05, rotation=0)

        plt.title(str(argo)+'_'+str(prof))
        plt.xlabel('Salinity')
        plt.ylabel('Temp')

        # enabling use of selector 
        # drawtype is 'box' or 'line' or 'none'
        toggle_selector.RS = RectangleSelector(ax, line_select_callback,
                                            drawtype='box', useblit=True,
                                            button=[1, 3],  # don't use middle button
                                            minspanx=5, minspany=5,
                                            spancoords='pixels',
                                            interactive=True)

        plt.connect('key_press_event', toggle_selector)

        # basemap mapping
        ax = plt.subplot(gs[1])

        map = Basemap(projection='cass',
                    lon_0 = lon,
                    lat_0 = lat,
                    width = 10000000,
                    height = 10000000)

        map.bluemarble()    
        map.drawcountries()
        map.drawcoastlines()
        map.drawrivers(color='#0000ff')
        
        #plot the current float point
        lons, lats = map(lon, lat)
        map.scatter(lons, lats, marker='o',color='w', zorder=5)
        
        #plot the previous points
        lons, lats = map(df_main['long'].values, df_main['lat'].values)
        map.scatter(lons, lats, marker='o',color=df_main['Colour'], zorder=5)

        ax.set_title("Lat: " + str(lat) + '\n Long: ' + str(lon))

        plt.tight_layout()
        plt.show()

        # at the end of one loop, save all the data to main dataframe
        df_main = df_main.append({'Feature': feat,'Float': argo,'Profile': prof, 
                                'Colour': colour,'x1': x1, 'x2': x2, 'y1': y1, 'y2': y2,'lat': lat, 'long':lon}, 
                                ignore_index=True)

    print('----------------------DATA COLLECTION FINISHED-------------------------')
    #print dataframe to check 
    print(df_main)
    
    #request filename
    filename = input(user+", insert file name: ")

    #save the data frame as csv
    # if file does not exist write header 
    # else it exists so append without writing the header
    with open(user+'_'+filename+'.csv', 'a') as f:
        df_main.to_csv(f, header=f.tell()==0,index=False)

    print('-----------------------CSV FILE SAVED------------------------')

#call main function
main()