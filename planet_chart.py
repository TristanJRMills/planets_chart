"""
planet_chart.py
Tristan Mills (www.mills.science)
Created: September 12, 2017
Last Modified: October 5, 2017
License: MIT License
Python version 2.7.13
    matplotlib version 1.4.3
    numpy version 1.10.0b1
    pyephem version 3.7.6

This program saves and displays a planet chart for the given year. The lines represent rise and set times for each
planet, in between which the planets are visible in the night sky. Location is set using latitude/longitude variables,
as is the year.

Limitations:
Currently does not convert times into local timezones; times are measured by hours from midnight UTC
Cannot perform calculations within a few degrees of poles
Does not display the moon or its phases, which could impact viewing
Does not include leap days

"""
# # # Inputs and Imports # # #

# ############################# #
# Location and Time Preferences #
latitude = 43.475085
longitude = -80.552901
year = 2017
# ^ User customizable!          #
# ############################# #

import ephem
from numpy import arange
from numpy.ma import masked_outside
from matplotlib import pyplot as plt
from math import floor, pi

# # # Functions # # #


# handles the creation and formatting of rise and set arrays for a given body
def get_planet_times(body, times, obs, time_difference):
    # used for graphing at times between noons, and centering the graph at around midnight
    midnight = -time_difference  # time in UTC that midnight occurs at location
    noon = (-time_difference + 12) % 24  # time in UTC that noon occurs at location

    # create and add times to rise and set arrays, for each day of the year
    body_rise_times = []
    body_set_times = []
    for time in times:
        obs.date = time
        body_rise_times.append(get_body_rise(body, time, obs, noon))
        body_set_times.append(get_body_set(body, time, obs, noon))

    # lists are returned as masked arrays to avoid wrap around lines when plotting
    return masked_outside(body_rise_times, (midnight + 10), (midnight - 10)), masked_outside(body_set_times, (midnight + 10), (midnight - 10))


# returns the time and date of previous rising
def get_body_rise(planet, date, obs, noon):
    obs.date = date
    # return no value when there is not a rise within 24 hours
    try:
        rising = obs.next_rising(planet).triple()[2]
    except:
        return
    rising = (rising - floor(rising)) * 24.
    if rising > noon:
        return rising - 24
    else:
        return rising


# returns the time and date of next setting
def get_body_set(planet, date, obs, min_time):
    obs.date = date
    # return no value when there is not a set within 24 hours
    try:
        setting = obs.next_setting(planet).triple()[2]
    except:
        return
    setting = (setting - floor(setting)) * 24.
    if setting > min_time:
        return setting - 24
    else:
        return setting


# # # Main Program # # #

# error when longitude is -180, which is equivalent to +180
if longitude == -180.0:
    longitude = 180.0

# out of bounds location data handling
if -180 > longitude or longitude > 180:
    raise ValueError('Longitude must be between -180 and +180 in units of degrees')
if -90 > latitude or latitude > 90:
    raise ValueError('Latitude must be between -180 and +180 in units of degrees')

# dealing with timezones, an approximate solution for something not straightforward in python
time_diff = int(longitude / 15)

# creating the observing site
observing_site = ephem.Observer()
observing_site.pressure = 0
observing_site.horizon = '0'
observing_site.lat = latitude * pi / 180.
observing_site.lon = longitude * pi / 180.

# load planet data using pyephem
sun = ephem.Sun()
me = ephem.Mercury()
v = ephem.Venus()
m = ephem.Mars()
j = ephem.Jupiter()
s = ephem.Saturn()
u = ephem.Uranus()
n = ephem.Neptune()

# create array times which holds all dates of year (does not include leap days)
count = 0
month = 1
current_year = year
time_array = []
days_in_month = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
cumulative_days = 0
while current_year == year:
    time = count * 24 * 60
    day = (floor(time / 60 / 24) - cumulative_days) % days_in_month[month-1] + 1
    if (time / 60 / 24 - cumulative_days) % days_in_month[month-1] == 0 and count > 1:
        cumulative_days += days_in_month[month-1]
        month += 1
        day = 1
    if month > 12:
        break
    if day >= 10:
        time_array.append(str(current_year) + '/' + str(int(month)) + '/' + str(int(day)))
    else:
        time_array.append(str(current_year) + '/' + str(int(month)) + '/0' + str(int(day)))
    count += 1

# get rise and set masked arrays
sun_rise_times, sun_set_times = get_planet_times(sun, time_array, observing_site, time_diff)
mercury_rise_times, mercury_set_times = get_planet_times(me, time_array, observing_site, time_diff)
venus_rise_times, venus_set_times = get_planet_times(v, time_array, observing_site, time_diff)
mars_rise_times, mars_set_times = get_planet_times(m, time_array, observing_site, time_diff)
jupiter_rise_times, jupiter_set_times = get_planet_times(j, time_array, observing_site, time_diff)
saturn_rise_times, saturn_set_times = get_planet_times(s, time_array, observing_site, time_diff)
uranus_rise_times, uranus_set_times = get_planet_times(u, time_array, observing_site, time_diff)
neptune_rise_times, neptune_set_times = get_planet_times(n, time_array, observing_site, time_diff)

# astronomical twilight occurs when sun is past 18 degrees below the horizon
observing_site.horizon = '-18'
sun_twilight_rise_times, sun_twilight_set_times = get_planet_times(sun, time_array, observing_site, time_diff)

# set up plotting
fg_color = 'white'
bg_color = 'black'
grid_color = '#1D1D1D'

fig = plt.figure(1, facecolor=bg_color, edgecolor=fg_color)
axes = plt.axes((0.1, 0.1, 0.8, 0.8), axisbg=bg_color)

# plot the rises and sets throughout the year, sets are marked with dashed lines
plt.plot(sun_rise_times, arange(0, len(sun_rise_times)), label="Sun Rise", color="white")
plt.plot(sun_set_times, arange(0, len(sun_set_times)), '--', label="Sun Set", color="white")
plt.plot(sun_twilight_rise_times, arange(0, len(sun_twilight_rise_times)), label="Sun Rise", color="grey")
plt.plot(sun_twilight_set_times, arange(0, len(sun_twilight_set_times)), '--', label="Sun Set", color="grey")
plt.plot(mercury_rise_times, arange(0, len(mercury_rise_times)), label="Mercury Rise", color="brown")
plt.plot(mercury_set_times, arange(0, len(mercury_set_times)), '--', label="Mercury Set", color="brown")
plt.plot(venus_rise_times, arange(0, len(venus_rise_times)), label="Venus Rise", color="yellow")
plt.plot(venus_set_times, arange(0, len(venus_set_times)), '--', label="Venus Set", color="yellow")
plt.plot(mars_rise_times, arange(0, len(mars_rise_times)), label="Mars Rise", color="red")
plt.plot(mars_set_times, arange(0, len(mars_set_times)), '--', label="Mars Set", color="red")
plt.plot(jupiter_rise_times, arange(0, len(jupiter_rise_times)), label="Jupiter Rise", color="orange")
plt.plot(jupiter_set_times, arange(0, len(jupiter_set_times)), '--', label="Jupiter Set", color="orange")
plt.plot(saturn_rise_times, arange(0, len(saturn_rise_times)), label="Saturn Rise", color="pink")
plt.plot(saturn_set_times, arange(0, len(saturn_set_times)), '--', label="Saturn Set", color="pink")
plt.plot(uranus_rise_times, arange(0, len(uranus_rise_times)), label="Uranus Rise", color="blue")
plt.plot(uranus_set_times, arange(0, len(uranus_set_times)), '--', label="Uranus Set", color="blue")
plt.plot(neptune_rise_times, arange(0, len(neptune_rise_times)), label="Neptune Rise", color="purple")
plt.plot(neptune_set_times, arange(0, len(neptune_set_times)), '--', label="Neptune Set", color="purple")

# formatting the axes
axes.xaxis.set_tick_params(color=fg_color, labelcolor=fg_color)
axes.yaxis.set_tick_params(color=fg_color, labelcolor=fg_color)
axes.set_ylim([0, 365])
if -time_diff > 0:
    axes.set_xlim([-time_diff - 10, -time_diff + 10])
else:
    axes.set_xlim([-time_diff + 10, -time_diff - 10])
# unsure of cause, x axis becomes reversed for longitudes greater than -15 degrees and must be reversed again
if longitude > -15:
    plt.gca().invert_xaxis()

# formatting the grid and spine
for spine in axes.spines.values():
    spine.set_color(fg_color)
axes.grid(color=grid_color, linestyle='-', linewidth=1)
axes.set_axisbelow(True)

# titles, labels, and legend
plt.title('Planet Rise and Set Times Over ' + str(year), color=fg_color)
plt.xlabel('Hours from Midnight UTC', color=fg_color)
plt.ylabel('Day of Year', color=fg_color)

legend = axes.legend(loc='center left', bbox_to_anchor=(1, 0.5))
legend.get_frame().set_facecolor(bg_color)
legend.get_frame().set_edgecolor(fg_color)
for text in legend.get_texts():
    text.set_color(fg_color)

# save figure
fig.savefig('planet_chart_' + str(year), facecolor=bg_color, bbox_extra_artists=(legend,), bbox_inches='tight')
# plt.show()