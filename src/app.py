from dash import Dash, _dash_renderer
import layout
import callback_register


# not needed with dash >3.0.0
_dash_renderer._set_react_version("18.2.0")


app = Dash(__name__,suppress_callback_exceptions=True, 
           meta_tags = [{"name": "viewport",
                        "content": "width=device-width, initial-scale=1.0, maximum-scale=5, minimum-scale=0.5"}],
            external_stylesheets=["https://use.fontawesome.com/releases/v5.15.4/css/all.css"])
app.layout = layout.layout

# Register callbacks from callbacks.py
callback_register.register_callbacks(app)

app.run(
    host = "0.0.0.0", 
    debug = True, 
    port = 8060
)