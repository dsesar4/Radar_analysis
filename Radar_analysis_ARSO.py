import pandas as pd
import urllib.request
import time
import matplotlib.pyplot as plt
import numpy as np
from PIL import Image

from pylab import rcParams
rcParams['figure.figsize'] = 10, 10

ARSO_possible_reflections = [[8,90,254],[0,140,254],[0,174,253],[0,200,254],[4,216,131],[66,235,66],[108,249,0],[184,250,0], [249,250,0], [254,198,0], [254,132,0], [255,62,1], [211,0,0], [181,3,3], [203,0,204]]
df3 = pd.DataFrame(ARSO_possible_reflections, columns = ['r','g','b'])

print('\nWelcome to ARSO-Lisca radar analysis! This analysis is suitable only for periods after'\
      ' 23.6.2014. Please enter following parameters:')
a = int(input('Area for analysis (0-Zagreb surroundings, 1-Central Croatia, 2-Gorski kotar, 3-Istra): '))
year = int(input('Year: '))
month = int(input('Month: '))
day = int(input('Day: '))
hour = int(input('Hour to start from: '))
minute = int(input('Minute to start from (multiple od 10): '))
iterations = int(input('Number of wanted frames (ex. 6 frames = 1 hour, 12 frames = 2 hours): '))
print('\nThank you! Now please wait for analysis to finish...')

hour_start = hour
minute_start = minute

areas = [[540,360,650,450],[520,250,750,510],[350,430,500,570],[200,460,350,640]]
   
x_rain = [[0 for i in range(areas[a][2]-areas[a][0])] for j in range(areas[a][3]-areas[a][1])] 
x_shower = [[0 for i in range(areas[a][2]-areas[a][0])] for j in range(areas[a][3]-areas[a][1])] 
x_thunderstorm = [[0 for i in range(areas[a][2]-areas[a][0])] for j in range(areas[a][3]-areas[a][1])] 
x_severe_storm = [[0 for i in range(areas[a][2]-areas[a][0])] for j in range(areas[a][3]-areas[a][1])] 

k = 0

while (k <= iterations):
    
    minute_querry = minute
    hour_querry = hour
    day_querry = day
    month_querry = month
    
    if (minute//10 == 0):
        minute_querry = '0' + str(minute)
    if (hour // 10 == 0):
        hour_querry = '0' + str(hour)
    if (day // 10 == 0):
        day_querry = '0' + str(day) 
    if (month // 10 == 0):
        month_querry = '0' + str(month)
        
    urllib.request.urlretrieve('http://radarska.meteocenter.eu/{year}-{month}-{day}-{hour}-{minute}.gif'\
                               .format(year = year, month = month_querry, day = day_querry, hour = hour_querry, minute = minute_querry), "lisca-stat.gif")
    
    im = Image.open("lisca-stat.gif")
    rgb_im = im.convert('RGB') 
    
    i = 0
    j = 0

    for i in range (areas[a][0],areas[a][2]):
        for j in range (areas[a][1],areas[a][3]):
            r, g, b = rgb_im.getpixel((i, j))
            if ((r == df3['r'][0] or r == df3['r'][1] or r == df3['r'][2] or r == df3['r'][3]\
                 or r == df3['r'][4] or r == df3['r'][5] or r == df3['r'][6]) and (g in df3['g'].values)):
                x_rain[j - areas[a][1]][i - areas[a][0]] = x_rain[j - areas[a][1]][i - areas[a][0]] + 1
            elif ((r == df3['r'][7] or r == df3['r'][8] or r == df3['r'][9]) and (g in df3['g'].values)):
                x_shower[j - areas[a][1]][i - areas[a][0]] = x_shower[j - areas[a][1]][i - areas[a][0]] + 1
            elif ((r == df3['r'][10] or r == df3['r'][11]) and (g in df3['g'].values)):
                x_thunderstorm[j - areas[a][1]][i - areas[a][0]] = x_thunderstorm[j - areas[a][1]][i - areas[a][0]] + 1
            elif ((r == df3['r'][12] or r == df3['r'][13] or r == df3['r'][14]) and (g in df3['g'].values)):
                x_severe_storm[j - areas[a][1]][i - areas[a][0]] = x_severe_storm[j - areas[a][1]][i - areas[a][0]] + 1
    
    if (minute == 50):
        minute = 0
        if (hour == 23):
            hour = 0
            if (day == 31):
                day = 1
                month = month + 1
            else:
                day = day + 1
        else:
            hour = hour + 1
    else:
        minute = minute + 10
    
    k = k + 1    
                
    time.sleep(1) 
    
template = Image.open("template_arso.gif")
template = template.crop((areas[a][0],areas[a][1],areas[a][2],areas[a][3]))

def transparent_cmap(cmap, N = 255):
    mycmap = cmap
    mycmap._init()
    mycmap._lut[:,-1] = np.linspace(0, 1, N + 4)
    return mycmap

mycmap = transparent_cmap(plt.cm.rainbow)

w, h = template.size
y, x = np.mgrid[0:h, 0:w]

rain = np.ravel(x_rain)
shower = np.ravel(x_shower)
thunderstorm = np.ravel(x_thunderstorm)
severe_storm = np.ravel(x_severe_storm)

if (minute_start//10 == 0):
        minute_start = '0' + str(minute_start)
        
        
fig1, ax1 = plt.subplots(1, 1)

ax1.imshow(template)
cb1 = ax1.contourf(x, y, rain.reshape(x.shape[0], y.shape[1]), max(rain) + 1, cmap=mycmap, alpha = 0.55)
plt.colorbar(cb1)
plt.title('{day}.{month}.{year}, {start_hour}:{start_minute}-{end_hour}:{end_minute} UTC\n 1-5 mm/h'\
          .format(day = day, month = month, year = year, start_hour = hour_start,\
          start_minute = minute_start, end_hour = hour_querry, end_minute = minute_querry), fontsize = 22)
ax1.set_xlabel('Weak to moderate rain', fontsize = 22)
plt.show()

fig2, ax2 = plt.subplots(1, 1)

ax2.imshow(template)
cb2 = ax2.contourf(x, y, shower.reshape(x.shape[0], y.shape[1]), max(shower) + 1, cmap=mycmap, alpha = 0.55)
plt.colorbar(cb2)
plt.title('{day}.{month}.{year}, {start_hour}:{start_minute}-{end_hour}:{end_minute} UTC\n 5-15 mm/h'\
          .format(day = day, month = month, year = year, start_hour = hour_start,\
          start_minute = minute_start, end_hour = hour_querry, end_minute = minute_querry), fontsize = 22)
ax2.set_xlabel('Moderate rain or showers, thunder possible', fontsize = 22)
plt.show()

fig3, ax3 = plt.subplots(1, 1)

ax3.imshow(template)
cb3 = ax3.contourf(x, y, thunderstorm.reshape(x.shape[0], y.shape[1]), max(thunderstorm) + 1, cmap=mycmap, alpha = 0.55)
plt.colorbar(cb3)
plt.title('{day}.{month}.{year}, {start_hour}:{start_minute}-{end_hour}:{end_minute} UTC\n 15-50 mm/h'\
          .format(day = day, month = month, year = year, start_hour = hour_start,\
          start_minute = minute_start, end_hour = hour_querry, end_minute = minute_querry), fontsize = 22)
ax3.set_xlabel('Heavy rain, thunderstorms', fontsize = 22)
plt.show()

fig4, ax4 = plt.subplots(1, 1)

ax4.imshow(template)
cb4 = ax4.contourf(x, y, severe_storm.reshape(x.shape[0], y.shape[1]), max(severe_storm) + 1, cmap=mycmap, alpha = 0.55)
plt.colorbar(cb4)
plt.title('{day}.{month}.{year}, {start_hour}:{start_minute}-{end_hour}:{end_minute} UTC\n 50+ mm/h'\
          .format(day = day, month = month, year = year, start_hour = hour_start,\
          start_minute = minute_start, end_hour = hour_querry, end_minute = minute_querry), fontsize = 22)
ax4.set_xlabel('Extreme rain, severe storms', fontsize = 22)
plt.show()
    
