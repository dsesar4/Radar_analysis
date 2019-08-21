import pandas as pd
import urllib.request
import time
import matplotlib.pyplot as plt
import numpy as np
from PIL import Image

from pylab import rcParams
rcParams['figure.figsize'] = 10, 10

DHMZ_possible_reflections = [[0,255,255],[0,199,199],[0,146,145],[0,56,184],\
                             [0,129,0],[0,202,0],[41,255,10],[255,255,0],\
                             [237,194,0],[255,0,0],[247,0,219]]
df3 = pd.DataFrame(DHMZ_possible_reflections, columns = ['r','g','b'])

print('\nWelcome to DHMZ-Bilogora radar analysis! This analysis is suitable only for periods after'\
      ' 6.6.2019. Please enter following parameters:')
a = int(input('Area for analysis (0-Central Croatia, 1-Slavonia): '))
minute = int(input('Minute to start from (0,15,30 or 45): '))
hour = int(input('Hour to start from: '))
day = int(input('Day: '))
month = int(input('Month: '))
year = int(input('Year: '))
iterations = int(input('Number of wanted frames (ex. 4 frames = 1 hour, 8 frames = 2 hours): '))
print('\nThank you! Now please wait for analysis to finish...')


hour_start = hour
minute_start = minute
    
areas = [[105,165,250,325],[230,215,415,355]]
   
x_rain = [[0 for i in range(areas[a][2]-areas[a][0])] for j in range(areas[a][3]-areas[a][1])] 
x_shower = [[0 for i in range(areas[a][2]-areas[a][0])] for j in range(areas[a][3]-areas[a][1])] 
x_thunderstorm = [[0 for i in range(areas[a][2]-areas[a][0])] for j in range(areas[a][3]-areas[a][1])] 
x_severe_storm = [[0 for i in range(areas[a][2]-areas[a][0])] for j in range(areas[a][3]-areas[a][1])] 

k = 0

while (k <= iterations):
    minute_querry = minute + 10
    hour_querry = hour 
    day_querry = day
    month_querry = month
    
    if (hour // 10 == 0):
        hour_querry = '0' + str(hour)
    if (day // 10 == 0):
        day_querry = '0' + str(day) 
    if (month // 10 == 0):
        month_querry = '0' + str(month)
        
    urllib.request.urlretrieve('http://139.59.144.6/arhiva/bilogora_stat/{year}/{month}/{day}/bilogora_stat_{year}{month}{day}{hour}{minute}Z.png'\
                               .format(year = year, month = month_querry, day = day_querry, hour = hour_querry, minute = minute_querry), "bilogora-stat.png")
    
    im = Image.open("bilogora-stat.png")
    rgb_im = im.convert('RGB') 
    
    i = 0
    j = 0

    for i in range (areas[a][0],areas[a][2]):
        for j in range (areas[a][1],areas[a][3]):
            r, g, b = rgb_im.getpixel((i, j))
            if ((r == df3['r'][1] or r == df3['r'][2] or r == df3['r'][3] or r == df3['r'][4]) and (g in df3['g'].values)):
                x_rain[j - areas[a][1]][i - areas[a][0]] = x_rain[j - areas[a][1]][i - areas[a][0]] + 1
            elif ((r == df3['r'][5] or r == df3['r'][6]) and (g in df3['g'].values)):
                x_shower[j - areas[a][1]][i - areas[a][0]] = x_shower[j - areas[a][1]][i - areas[a][0]] + 1
            elif ((r == df3['r'][7] or r == df3['r'][8]) and (g in df3['g'].values)):
                x_thunderstorm[j - areas[a][1]][i - areas[a][0]] = x_thunderstorm[j - areas[a][1]][i - areas[a][0]] + 1
            elif ((r == df3['r'][9] or r == df3['r'][10]) and (g in df3['g'].values)):
                x_severe_storm[j - areas[a][1]][i - areas[a][0]] = x_severe_storm[j - areas[a][1]][i - areas[a][0]] + 1
    
    if (minute == 45):
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
        minute = minute + 15
    
    k = k + 1    
                
    time.sleep(1) 

i = 0
j = 0

for i in range(0,areas[a][3]-areas[a][1]):
    mask = max(x_rain[i])
    for j in range (0,areas[a][2]-areas[a][0]):
        if x_rain[i][j] == mask:
            x_rain[i][j] = 0

template = Image.open("template.png")
template = template.crop((areas[a][0],areas[a][1],areas[a][2],areas[a][3]))

def transparent_cmap(cmap, N = 255):
    mycmap = cmap
    mycmap._init()
    mycmap._lut[:,-2] = np.linspace(0, 1, N + 4)
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
        
if (minute_querry != 10):
    minute_querry = minute_querry - 10
else:
    minute_querry = '00'

fig1, ax1 = plt.subplots(1, 1)

ax1.imshow(template)
cb1 = ax1.contourf(x, y, rain.reshape(x.shape[0], y.shape[1]), 15, cmap=mycmap, alpha = 0.5)
plt.colorbar(cb1)
plt.title('{day}.{month}.{year}, {start_hour}:{start_minutes}-{end_hour}:{end_minutes} UTC\n 15-35 dBZ'\
          .format(day = day, month = month, year = year, start_hour = hour_start,\
          start_minutes = minute_start, end_hour = hour_querry, end_minutes = minute_querry), fontsize = 22)
ax1.set_xlabel('Weak to moderate rain', fontsize = 22)
plt.show()

fig2, ax2 = plt.subplots(1, 1)

ax2.imshow(template)
cb2 = ax2.contourf(x, y, shower.reshape(x.shape[0], y.shape[1]), 15, cmap=mycmap, alpha = 0.5)
plt.colorbar(cb2)
plt.title('{day}.{month}.{year}, {start_hour}:{start_minutes}-{end_hour}:{end_minutes} UTC\n 35-45 dBZ'\
          .format(day = day, month = month, year = year, start_hour = hour_start,\
          start_minutes = minute_start, end_hour = hour_querry, end_minutes = minute_querry), fontsize = 22)
ax2.set_xlabel('Moderate to heavy rain, thunder possible', fontsize = 22)
plt.show()

fig3, ax3 = plt.subplots(1, 1)

ax3.imshow(template)
cb3 = ax3.contourf(x, y, thunderstorm.reshape(x.shape[0], y.shape[1]), 15, cmap=mycmap, alpha = 0.5)
plt.colorbar(cb3)
plt.title('{day}.{month}.{year}, {start_hour}:{start_minutes}-{end_hour}:{end_minutes} UTC\n 45-55 dBZ'\
          .format(day = day, month = month, year = year, start_hour = hour_start,\
          start_minutes = minute_start, end_hour = hour_querry, end_minutes = minute_querry), fontsize = 22)
ax3.set_xlabel('Heavy rain, thunderstorms', fontsize = 22)
plt.show()

fig4, ax4 = plt.subplots(1, 1)

ax4.imshow(template)
cb4 = ax4.contourf(x, y, severe_storm.reshape(x.shape[0], y.shape[1]), 15, cmap=mycmap, alpha = 0.5)
plt.colorbar(cb4)
plt.title('{day}.{month}.{year}, {start_hour}:{start_minutes}-{end_hour}:{end_minutes} UTC\n 55+ dBZ'\
          .format(day = day, month = month, year = year, start_hour = hour_start,\
          start_minutes = minute_start, end_hour = hour_querry, end_minutes = minute_querry), fontsize = 22)
ax4.set_xlabel('Severe storms', fontsize = 22)
plt.show()












            