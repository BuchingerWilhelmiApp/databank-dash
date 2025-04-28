from dash import Input, Output, State, callback_context as ctx, ClientsideFunction, Patch
import dash
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import plotly.io as pio
from scipy.stats import zscore
import os
from dash import ctx  # ctx est un alias moderne pour callback_context
from dash import clientside_callback



def delete_outiers(values):
    z_scores = zscore(values, nan_policy='omit')
    cleaned_values = values[abs(z_scores) < 8]
    
    return cleaned_values

####################################################
metadata = pd.read_parquet("data/Masterfile-studies-anonymised.parquet").assign(
    date_arrival = lambda df : pd.to_datetime(df.date_arrival), 
)

data =(pd.read_parquet("data/Masterfile-Data.parquet")
       .assign(
            date = lambda df :pd.to_datetime(df.date), 
            date_startfast = lambda df :pd.to_datetime(df.date_startfast), 
            date_breakfast = lambda df :pd.to_datetime(df.date_breakfast), 
            is_fasting = lambda df :df.is_fasting.map({"True": True, "False": False}), 
            value = lambda df : pd.to_numeric(df.value, errors = "coerce"), 
            length_of_fasting = lambda df :pd.to_numeric(df.length_of_fasting, errors="coerce"), 
            timepoint_considered = lambda df : df.timepoint_considered.replace("nan", pd.NA)
    )
    .assign(
        meta_id = lambda df :df.record_id.astype(str) +"-"+ df.study, 
        length_of_fasting = lambda df :df.length_of_fasting.fillna(0)
    )
    .merge(metadata[["meta_id", "date_arrival", "sex"]], how = "left")
    #  .query("study == @study")
    .assign(
        nth_day = lambda dff :(dff.date-dff.date_arrival).dt.days, 
        n_measurement = lambda dff :dff.groupby(["meta_id", "variable"]).date.transform("nunique"), 
        nth_blood_draw = lambda dff :dff.groupby(["meta_id", "variable"]).date.transform("cumcount")+1
    )
    .sort_values(["meta_id", "nth_day"])
    .assign(
        time_between_lab_tmp = lambda dff : dff.groupby(["meta_id", "variable"]).date.transform("diff"), 
        time_between_lab = lambda dff : dff.groupby(["meta_id", "variable"]).time_between_lab_tmp.transform("first"), 
        )
    .drop("time_between_lab_tmp", axis =1)

)
LIST_PARAMETERS = list(data.variable.dropna().unique())
LIST_STUDIES = list(data.study.dropna().unique())
#################################################################################
def register_callbacks(app):


#div-test > div > div .m_92253aa5
#div-test > div > div .m_92253aa5
# Ajoutez ce code après avoir défini votre layout mais avant app.run_server()
    app.clientside_callback(
        """
        function(studies_list) {
            setTimeout(() => {
                document.querySelectorAll('.m_390b5f4').forEach(element => {
                    element.classList.remove('style-special');
                    element.classList.add('not-special');
                });
                
                if (studies_list && studies_list.length > 0) {
                    document.querySelectorAll('.m_390b5f4').forEach(element => {
                        const spans = element.querySelectorAll('span');
                        spans.forEach(span => {
                            if (studies_list.includes(span.textContent.trim())) {
                                element.classList.remove('not-special');
                                element.classList.add('style-special');
                            }
                        });
                    });
                }
            }, 100);  
            
            return null;  
        }
        """,
        Output('style-trigger-div', 'children'),
        Input('studies-with-parameter-store', 'data')
    )

    @app.callback(
        Output('dropdown-parameters', 'data'),
        Output('dropdown-studies', 'data'),
        Output('studies-with-parameter-store', 'data'),
        Input('dropdown-studies', 'value'),
        Input('dropdown-parameters', 'value'),
    )
    def update_both_dropdowns(study_selected, parameter_selected):
        triggered_id = ctx.triggered_id  # ctx = dash.callback_context in Dash 2+
        
        parameters_in_selected_study = list(data.query("study == @study_selected").variable.dropna().unique())
        studies_with_selected_parameter = list(data.query("variable == @parameter_selected").study.dropna().unique())
        new_stored_data = parameters_in_selected_study +studies_with_selected_parameter

        if triggered_id == 'dropdown-studies' and study_selected:
            # Mise à jour basée sur un study sélectionné
            parameters_not_in_the_study = list(set(LIST_PARAMETERS) - set(parameters_in_selected_study))
            new_parameters = parameters_in_selected_study + parameters_not_in_the_study

            new_studies = dash.no_update

        elif triggered_id == 'dropdown-parameters' and parameter_selected:
            # Mise à jour basée sur un paramètre sélectionné
            studies_without_selected_parameter = list(set(LIST_STUDIES) - set(studies_with_selected_parameter))
            new_studies = studies_with_selected_parameter + studies_without_selected_parameter

            # Les paramètres ne changent pas dans ce cas
            new_parameters = dash.no_update

        else:
            # Cas improbable (sécurité)
            return dash.no_update, dash.no_update, dash.no_update

        return new_parameters, new_studies, new_stored_data

    # @app.callback(
    #     Output('dropdown-parameters', 'data'),
    #     Output('studies-with-parameter-store', 'data', allow_duplicate=True),
    #     Input('dropdown-studies', 'value'), 
    #     State('studies-with-parameter-store', 'data'), 
    #     prevent_initial_call='initial_duplicate'
    # )
    # def update_parameters_dropdown(study_selected, stored_data):
    #     # Get parameters for the selected study
    #     parameters_in_selected_study = list(data.query("study == @study_selected").variable.dropna().unique())
    #     parameters_not_in_the_study = list(set(LIST_PARAMETERS) - set(parameters_in_selected_study))
    #     new_parameters = parameters_in_selected_study + parameters_not_in_the_study
    #     return new_parameters, stored_data + parameters_in_selected_study
        
    # @app.callback(
    #     Output('dropdown-studies', 'data'),
    #     Output('studies-with-parameter-store', 'data'),  # Nouveau output
    #     Input('dropdown-parameters', 'value'), 
    #     State('studies-with-parameter-store', 'data'), 

    # )
    # def update_studies_dropdown(parameter_selected, stored_data):
    #     studies_with_selected_parameter = list(data.query("variable == @parameter_selected").study.dropna().unique())
    #     studies_without_selected_parameter = list(set(LIST_STUDIES) - set(studies_with_selected_parameter))
    #     new_list = studies_with_selected_parameter + studies_without_selected_parameter
    #     return new_list, stored_data + studies_with_selected_parameter


    @app.callback(
        Output('graph-1', 'figure'),
        Input('dropdown-studies', 'value'), 
        Input('dropdown-parameters', 'value'),
    )
    def update_chart(selected_study, selected_parameter):
        timepoint_of_studies_dict = {
            "Detox":{"EOF": "F11 / F12", "FR30":"1M FUP"}, 
            "FastReset": {"Baseline":"Baseline","EOF": "F6", "FR30": "1M FUP"}, 
            "genesis": {"Baseline":"Baseline","EOF": "F11/F12", "FR30": "1M FUP"}, 
            "muscle": {"Baseline":"Baseline","FR90": "3M FUP", "EOF": "F10/F11"}, 
            "lipobuwi": {"Baseline":"Baseline","EOF": "F14"}, 
            "oralFast": {"Baseline":"Baseline","EOFR":"3th blood draw ~ 1, 2 or 3 <br>Days after the break of fasting", "EOF": "6-10 days of fasting"}, 
            "marbella": {"Baseline":"Baseline","EOF": "End of fasting"}, 
            "uberlingen": {"Baseline":"Baseline","EOF": "End of fasting"}
        }[selected_study]
        
        df_plot = (data
            .assign(record_id =lambda df :df.record_id.astype(int))
            .query("variable == @selected_parameter")
            .query("study==@selected_study")
            .pipe(lambda df :df.loc[df.value.isin(delete_outiers(df.value.values))])
            .assign(
                timepoint_considered = lambda df :df.timepoint_considered.replace(timepoint_of_studies_dict)
            )
            .sort_values(["record_id"])
            .dropna(subset = "value")
        )
        
        fig = (px.box(
                df_plot, x = "timepoint_considered", 
                y = "value", 
                points = False
                )
        )
        if df_plot.record_id.nunique() < 200 : 
            fig = (fig
                .add_traces(
                    list(
                        (px.line(
                            df_plot, 
                            x = "timepoint_considered", 
                            y = "value", 
                            line_group ="record_id", 
                            color = "record_id"
                        )
                        .update_traces(
                            line = dict(width=1, dash = "dot", color ="#a9a9a9"), 
                            marker = dict(color="#505050"),
                            mode = "lines+markers", 
                            connectgaps = True
                        )
                        .select_traces()
                    )
            )
            )
            
            )
        return fig.update_layout(
                template = "plotly_white", 
                yaxis_title_text= "<b>" + selected_parameter, 
                # width=1000, 
                height = 500, 
                xaxis_title_text = None
            )



        # data_graph = data.query("variable == @selected_y")
        pass
        
