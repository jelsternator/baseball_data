# Perform necessary imports
from bokeh.io import curdoc, show
from bokeh.models import ColumnDataSource, CustomJS, Slider, HoverTool, CategoricalColorMapper, WheelZoomTool, PanTool
from bokeh.plotting import figure, ColumnDataSource
from bokeh.palettes import brewer, Spectral9, Spectral11
hover = HoverTool()

import datetime
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import datetime

import os, sys
sys.path.append('/Users/joelelster/Python_projects/pybaseball/pybaseball/')

from statcast import statcast # not sure if needed but works


# Code Block

# Goal: Looking at Strikeout pitches by RHP using x and z break colored by pitch type


### Make the ColumnDataSource: source - using raw statcast data
raw_data = pd.read_csv('./Resources/statcast_raw')

# setting index to events, filtering out strikeouts, pitches that were classified, and right handed pitchers
data = raw_data.set_index('events')
data = data[pd.notnull(data['pitch_name'])]
data = data[data.p_throws == 'R']
data = data.loc['strikeout']

# trying new balls with slider
data = data.set_index('balls')

# Now creating the source
source = ColumnDataSource(data={
    'x'       : data['pfx_x'],
    'y'       : data['pfx_z'],
    'player_name' : data['player_name'],
    'pitch_name' : data['pitch_name'],
    #'date' : data['game_date'],
    'inning' : data['inning'],
    'desc' : data['des']
})

# Creating colormapper - creating list of unqiue pitches, and grabbing same length of colors (think need to limit colors)
pitch_list = data.pitch_name.unique().tolist()
color_mapper = CategoricalColorMapper(factors = pitch_list, palette = Spectral11[0:len(pitch_list)])

# specifying axis min/max
x_min, x_max = min(data.pfx_x), max(data.pfx_x)
y_min, y_max = min(data.pfx_z), max(data.pfx_z)

# Create the figure: p -title, axis labels, height/width, and tools (hovertool
p = figure(title='X/Z Movement for Strikeout Pitches by RHP', x_axis_label='Horiz Movement', y_axis_label='Vertical Movement',
           plot_height=400, plot_width=700, x_range=(x_min, x_max), y_range=(y_min, y_max),
           tools=[WheelZoomTool(), PanTool(),HoverTool(tooltips=[('Pitcher','@player_name'), ('Pitch Type', '@pitch_name'), 
                                     ('Date', '@date'), ('Inning', '@inning'), ('Play', '@desc')]) 
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
data = data.loc['strikeout']
data = data.set_index('balls')

# Define the callback function: update_plot - based on balls in count
def update_plot(attr, old, new):
    # set the `yr` name to `slider.value` and `source.data = new_data`
    balls = slider.value
    new_data = {
        'x'       : data.loc[balls].pfx_x,
        'y'       : data.loc[balls]['pfx_z'],
        'player_name' : data.loc[balls]['player_name'],
        'pitch_name' : data.loc[balls]['pitch_name'],
        #'date' : data.loc[balls]['gameday_string'],
        'inning' : data.loc[balls]['inning'],
        'desc' : data.loc[balls]['des']
        }
    source.data = new_data

# Make a slider object: slider
slider = Slider(start=0, end=3, step=1,value=0,title='Balls in AB')

# Attach the callback to the 'value' property of slider
slider.on_change('value', update_plot)

# Make a row layout of widgetbox(slider) and plot and add it to the current document
layout = row(widgetbox(slider), p)
curdoc().add_root(layout)



