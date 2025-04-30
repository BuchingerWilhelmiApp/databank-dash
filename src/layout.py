from dash import html, dcc
import dash_mantine_components as dmc
import pandas as pd 
# from utils import param_categories
from callback_register import data
config={
    "displayModeBar": True,
    'displaylogo': False,
    "modeBarButtonsToRemove" :[
        "toImage","zoom2d", "pan2d","lasso2d", "zoomIn2d", "zoomOut2d", "autoScale2d", "resetScale2d",
        "hoverClosestCartesian", "hoverCompareCartesian", "toggleSpikelines", "resetViews"
    ],
}

seen = set()
LIST_STUDIES = [study for study in sorted(data.study.dropna().unique())]
LIST_PARAMETERS = [param for param in sorted(data.variable.dropna().dropna().unique())]

study_selected = "genesis"
parameter_selected = "LDL [mg/dL]"
PARAMETERS_in_selected_study = list(data.query("study == @study_selected").variable.dropna().unique())
STUDIES_with_selected_parameter = list(data.query("variable == @parameter_selected").study.unique())

def layout():
    return dmc.MantineProvider([ html.Div(
        [
            html.Img(src="assets/BW_logo.svg", alt="BW_logo", id = "logo"),
            dmc.Space(h=20), 
            dcc.Store(id="studies-with-parameter-store", data=[]), 
            html.Div(id='style-trigger-div', style={'display': 'none'}),

            html.Div([], className="header-container"),
            
            html.Div([
                html.Div([
                dmc.Select(
                    label="Select one study", 
                    id='dropdown-studies',
                    data=STUDIES_with_selected_parameter,
                    value="genesis",
                    searchable=True, 
                    allowDeselect=False,
                    clearable=False

                ),
                ], id = "div-test"), 

                dmc.Select(
                    label="Select one parameter", 
                    id='dropdown-parameters',
                    data=PARAMETERS_in_selected_study,
                    value="LDL [mg/dL]",
                    # searchable=True, 
                    allowDeselect=False,
                    clearable=False, 
            withScrollArea=True,

                ),
                
                dcc.Graph(id='graph-1', config=config),
                dmc.Text(
                    """Over 500 parameters are available in total, measured in around 3,000 participants. 
                    Some parameters appear in several studies, while others, more specific, 
                    are present in only one.""",                    
                    size="sm",
                )
                
            ])
        ]
    )
])