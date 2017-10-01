import plotly.plotly as py
import plotly.graph_objs as go
import json, numpy, os
from lbcmain.dataexplorer import DataExplorer
from lbcmain.config import Config


Config.readconfig()
Config.setpath(os.path.dirname(os.path.abspath(__file__)))

def draw():
    with open('./keys.json') as f:
        keys = json.load(f)
    py.sign_in('panyz522', keys['plotly']['key'])

    N = 100
    with DataExplorer(index = 'saved') as datafile:
        date, data_rate = datafile.get_field('rate', 'C2U')


    trace = go.Scatter(x = date, y = data_rate, mode = 'lines', name = 'test-data')
    data = [trace]
    layout = go.Layout(title='Test Plot', 
                       xaxis = dict(title = 'xvalue',
                                    zeroline = False,
                                    showline = True), 
                       yaxis = dict(title = 'yvalue', 
                                    zeroline = False,
                                    showline = True), 
                       width=800, 
                       height=640)
    fig = go.Figure(data=data, layout=layout)

    py.image.save_as(fig, filename='./doc/a-simple-plot.png')
    return True

for i in range(5):
    try:
        re = False
        re = draw()
    except Exception as e:
        print e.message
    finally:
        if re is True:
            break