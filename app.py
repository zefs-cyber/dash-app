from dash import Dash, html, dcc, Input, Output
import plotly
from plotly.subplots import make_subplots
import plotly.graph_objects as go
import plotly.express as px

import pandas as pd

layout = plotly.graph_objs.Layout(
    paper_bgcolor='rgba(0,0,0,0)',
    plot_bgcolor='rgba(0,0,0,0)',
    font_color="white"
)

app = Dash(__name__)
server = app.server

df = pd.read_excel("dashboard.xlsx")
def success(outcome):
    if outcome == "Success":
        return 1
    else:
        return 0
def failure(outcome):
    if outcome == "Failure":
        return 1
    else:
        return 0


df["Success"] = df.Outcome.apply(success)
df["Failure"] = df.Outcome.apply(failure)


number_of_calls = df.groupby("Date")["Country"].count()
number_of_success_calls = df.groupby("Date")["Success"].sum()
number_of_failure_calls = df.groupby("Date")["Failure"].sum()

ratio_success_overall = number_of_success_calls / number_of_calls * 100

failed_success_timeout = df.groupby("Outcome")["Outcome"].count()

number_of_calls_by_state = df.groupby("State")["Success"].count()
number_of_calls_by_state_success = df.groupby("State")["Success"].sum()
number_of_calls_by_state_failure = df.groupby("State")["Failure"].sum()
number_of_calls_by_state_total = number_of_calls_by_state_success + number_of_calls_by_state_failure

number_of_calls_by_state_ratio = (number_of_calls_by_state_success / number_of_calls_by_state * 100).sort_values(ascending=False)

success_time_out = df[df["Success"] == 1].groupby("Time_Period")["Success"].count().sort_index()

#A
fig = go.Figure()
fig.add_trace(go.Scatter(x=number_of_calls.index, y=number_of_calls.values,
                    mode='lines+markers',
                    name='Overall calls '))
fig.add_trace(go.Scatter(x=number_of_success_calls.index, y=number_of_success_calls.values,
                    mode='lines+markers',
                    name='Number of successful calls'))
fig.add_trace(go.Scatter(x=number_of_failure_calls.index, y=number_of_failure_calls.values,
                    mode='lines+markers', 
                    name='Number of failed calls'))
fig.add_trace(go.Scatter(x=ratio_success_overall.index, y=ratio_success_overall.values,
                    mode='lines+markers', 
                    name='Ratio of successful calls to overall'))
fig["layout"]["title"] =  "Number of calls as a function of date"
fig["layout"]["xaxis"]["title"] =  "Date"
fig["layout"]["yaxis"]["title"] = "Number of calls"
fig["layout"]["legend_title"] = "Options"

fig._layout = layout


#B
fig1 = go.Figure()

fig1.add_trace(go.Bar(x=number_of_calls_by_state_success.index, y=number_of_calls_by_state_success.values,
                    name='Successful calls'))

fig1.add_trace(go.Bar(x=number_of_calls_by_state_failure.index, y=number_of_calls_by_state_failure.values, 
                    name='Failed calls'))

fig1.add_trace(go.Bar(x=number_of_calls_by_state_total.index, y=number_of_calls_by_state_total.values,
                    name='Total calls'))


fig1["layout"]["title"] = "Failed/successful calls"
fig1["layout"]["xaxis"]["title"] = "State"
fig1["layout"]["yaxis"]["title"] = "Number of calls"
fig1["layout"]["legend_title"] = "Options"
fig1._layout = layout

#C
fig2 = go.Figure(data=[go.Pie(labels = failed_success_timeout.index, values = failed_success_timeout.values)])
fig2["layout"]["title"] = "Failure/Success/Timeout"
fig2["layout"]["legend_title"] = "Call outcome"
fig2._layout = layout


#D
fig3 = go.Figure()
ratio = list(number_of_calls_by_state_success.values/number_of_calls_by_state_total.values)
fig3.add_trace(go.Bar(x=number_of_calls_by_state_success.index, y= ratio,
                    name=f'Success(Success/total) ratio for state'))

fig3["layout"]["title"] = f"Most successfull state in terms of success ratio is {number_of_calls_by_state_success.index[ratio[ratio.index(max(ratio))]]}"
fig3["layout"]["xaxis"]["title"] = "State"
fig3["layout"]["yaxis"]["title"] = "Ratio"
fig3._layout = layout


#F
fig5 = make_subplots(rows=1, cols=2, 
    column_widths=[0.5, 0.5],specs=[[{"type": "pie"}, {"type": "pie"}]],
    subplot_titles=("Calls per state", "Successfull calls per state"))
fig5.add_trace(row=1, col=1,
    trace=go.Pie(labels=number_of_calls_by_state.index, values=number_of_calls_by_state.values, hole=0.5)) 
fig5.add_trace(row=1, col=2,
    trace=go.Pie(labels=number_of_calls_by_state_success.index, values=number_of_calls_by_state_success.values, hole=0.5))


fig5.update_traces(textposition='inside')
fig5.update_layout(uniformtext_minsize=12, uniformtext_mode='hide')
fig5.update_layout(layout)

#E

X = list(set(df['Time_Period']))
success = [df[df['Time_Period'] == i][df['Outcome']=='Success']['Outcome'].count() for i in X]
failure = [df[df['Time_Period'] == i][df['Outcome']=='Failure']['Outcome'].count() for i in X]
time_out = [df[df['Time_Period'] == i][df['Outcome']=='Time out']['Outcome'].count() for i in X]


fig4 = go.Figure()
fig4.add_trace(go.Bar(x=X, y=success,
                    name='Successful calls'))
fig4.add_trace(go.Bar(x=X, y=failure,
                    name='Failure calls'))
fig4.add_trace(go.Bar(x=X, y=time_out,
                    name='Time out calls'))

fig4["layout"]["title"] = "Call outcomes by Time period"
fig4["layout"]["xaxis"]["title"] = "Time"
fig4["layout"]["yaxis"]["title"] = "Number of calls"
fig4["layout"]["legend_title"] = "Options"
fig4._layout = layout

app.layout=html.Div([
    html.Div("Dashboard", className='neon-text'),
    html.H4("Task 1"),
    html.P('We want to see this data in a graph with a time series legend. Then we want to see in the same graph the ratio of success /total calls as a function of date'),
    dcc.Graph(figure=fig),
    html.H4("Task 2"),
    html.P('We want to see another graph that presents the success and failure by State in the form of a bar graph.'),
    dcc.Graph(figure=fig1),
    html.H4("Task 3"),
    html.P('We want to see a piechart that displays failure-success-timeout as a percentage'),
    dcc.Graph(figure=fig2),
    html.H4("Task 4"),
    html.P('We want to see at the end which state was the most successful in share ratios'),
    dcc.Graph(figure =fig3),
    html.H4("Task 5"),
    html.P('We also want to see a double piechart that displays the total number of actions/ State and number of success / state.'),
    dcc.Graph(figure =fig5),
    html.H4("Task 6"),
    html.P('We want to know the number of succes by Time_Period (be careful with the ordering)'),
    dcc.Graph(figure = fig4)

])

if __name__ == "__main__":
    app.run_server("0.0.0.0", debug = False, port=int(os.environ.get('PORT',8000)))
