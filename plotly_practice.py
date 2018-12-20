import plotly.plotly as py
import plotly.graph_objs as go

mapbox_access_token = 'pk.eyJ1Ijoiam9uYXRoYW4yMiIsImEiOiJjanBvaDUzMWIwZHR3NDJ0MjE3bW45NGY3In0.YOHrWTwlilxEX4UG06Dr1A'

data = [
    go.Scattermapbox(
        lat=['45.5017'],
        lon=['-73.5673'],
        mode='markers',
        marker=dict(
            size=14
        ),
        text=['Montreal'],
    )
]

layout = go.Layout(
    autosize=True,
    hovermode='closest',
    mapbox=dict(
        accesstoken=mapbox_access_token,
        bearing=0,
        center=dict(
            lat=45,
            lon=-73
        ),
        pitch=0,
        zoom=5
    ),
)

fig = dict(data=data, layout=layout)

py.plot(fig, filename='Montreal Mapbox', world_readable=True)