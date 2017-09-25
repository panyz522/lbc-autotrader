import plotly.plotly as py
import plotly.graph_objs as go
import json, numpy

def draw():
    with open('./keys.json') as f:
        keys = json.load(f)
    py.sign_in('panyz522', keys['plotly']['key'])

    N = 100
    data_x = numpy.linspace(0,1,N)
    data_y = numpy.random.randn(N) + 30

    trace = go.Scatter(x = data_x, y = data_y, mode = 'lines', name = 'test-data')
    data = [trace]
    layout = go.Layout(title='Test Plot', 
                       xaxis = dict(title = 'xvalue',
                                    zeroline = False,
                                    showline = True), 
                       yaxis = dict(title = 'yvalue', 
                                    zeroline = False,
                                    showline = True,
                                    rangemode = "tozero"), 
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