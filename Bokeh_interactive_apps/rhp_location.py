# futures: add in strike zone

# Perform necessary imports
from bokeh.io import curdoc, show
from bokeh.models import ColumnDataSource, CustomJS, Slider, HoverTool, CategoricalColorMapper, WheelZoomTool, PanTool
from bokeh.plotting import figure, ColumnDataSource
from bokeh.palettes import brewer, Spectral9, Spectral11
hover = HoverTool()

from collections import Counter
import datetime
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import datetime

import os, sys
sys.path.append('/Users/joelelster/Python_projects/pybaseball/pybaseball/')

from statcast import statcast # not sure if needed but works


# Code Block

# Goal: Looking at  pitches by RHP using x and z break colored by pitch type, sliders by count


### Make the ColumnDataSource: source - using raw statcast data
raw_data = pd.read_csv('./Resources/statcast_raw')

# setting index to events, filtering out strikeouts, pitches that were classified, and right handed pitchers
data = raw_data[pd.notnull(raw_data['pitch_name'])]
data = data[data.p_throws == 'R']


# Now creating the source
source = ColumnDataSource(data={
    'x'       : data['plate_x'],
    'y'       : data['plate_z'],
    'player_name' : data['player_name'],
    'pitch_name' : data['pitch_name'],
    'date' : data['game_date'],
    'inning' : data['inning'],
    'desc' : data['des'],
    'strikes' : data['strikes'],
    'balls' : data['balls'],
    'description': data['description']
    
})

# Creating colormapper - creating list of unqiue pitches, and grabbing same length of colors (think need to limit colors)
pitch_list = data.pitch_name.unique().tolist()
color_mapper = CategoricalColorMapper(factors = pitch_list, palette = Spectral11[0:len(pitch_list)])

# specifying axis min/max
x_min, x_max = min(data.plate_x), max(data.plate_x)
y_min, y_max = min(data.plate_z), max(data.plate_z)

# Create the figure: p -title, axis labels, height/width, and tools (hovertool
p = figure(title='X/Z Location for Pitches by RHP',x_axis_label='Horizontal Location', y_axis_label='Vertical Location',
           plot_height=400, plot_width=700, x_range=(x_min, x_max), y_range=(y_min, y_max),
           tools=[WheelZoomTool(), PanTool(),HoverTool(tooltips=[('Pitcher','@player_name'), ('Pitch Type', '@pitch_name'),('Date', '@date'), ('Inning', '@inning'), ('Play', '@desc'),
                            ('Balls', '@balls'),('Strikes', '@strikes'), ('Outcome', '@description')]) 
                                      ])

# Add a circle glyph to the figure p, color by colormapper above
p.circle(x='x', y='y', color=dict(field='pitch_name', transform=color_mapper), legend='pitch_name', source=source)


# trying slider
# Import the necessary modules
from bokeh.layouts import widgetbox, row
from bokeh.models import Slider

# define data - all strikeout pitches
data = raw_data.set_index('events')
data = data[data.p_throws == 'R']
data = data.set_index('balls')

# Define the callback function: update_plot - based on balls in count
def update_plot(attr, old, new):
    # set the `yr` name to `slider.value` and `source.data = new_data`
    data = raw_data[pd.notnull(raw_data['pitch_name'])]
    data = data[data.p_throws == 'R']
    balls = slider_balls.value
    strikes = slider_strikes.value
    new_data = {
        'x'       : data[(data.balls == balls) & (data.strikes == strikes)].plate_x,
        'y'       : data[(data.balls == balls) & (data.strikes == strikes)].plate_z,
        'player_name' : data[(data.balls == balls) & (data.strikes == strikes)]['player_name'],
        'pitch_name' : data[(data.balls == balls) & (data.strikes == strikes)]['pitch_name'],
        'date' : data[(data.balls == balls) & (data.strikes == strikes)]['game_date'],
        'inning' : data[(data.balls == balls) & (data.strikes == strikes)]['inning'],
        'desc' : data[(data.balls == balls) & (data.strikes == strikes)]['des'],
        'strikes' : data[(data.balls == balls) & (data.strikes == strikes)]['strikes'],
        'balls' : data[(data.balls == balls) & (data.strikes == strikes)]['balls'],
        'description': data[(data.balls == balls) & (data.strikes == strikes)]['description']
    }
    # renaming title
    p.title.text = 'X/Z Location for Pitches by RHP when count is {0} - {1}'.format(balls, strikes)    
    # updating source
    source.data = new_data
   
    # printing data in terminal
    print('Balls: ',balls, ' Strikes: ',strikes)
    c = (Counter(new_data['pitch_name']))
    print([(key, round(100 * value/sum(c.values()),3)) for (key, value) in c.items()])


# Make a slider object: slider_balls
slider_balls = Slider(start=0, end=3, step=1,value=0,title='Balls in AB')

# Attach the callback to the 'value' property of slider
slider_balls.on_change('value', update_plot)

# Make a slider object: slider_strikes
slider_strikes = Slider(start=0, end=2, step=1,value=0,title='Strikes in AB')

# Attach the callback to the 'value' property of slider
slider_strikes.on_change('value', update_plot)

# Make a row layout of widgetbox(slider) and plot and add it to the current document
layout = row(widgetbox(slider_balls, slider_strikes), p)
curdoc().add_root(layout)



