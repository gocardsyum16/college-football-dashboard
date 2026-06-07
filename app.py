#!/usr/bin/env python
# coding: utf-8

# In[5]:


import pandas as pd
from sqlalchemy import create_engine
from dash import Dash, html, dcc, Input, Output
import plotly.express as px

SUPABASE_CONNECTION = (
    "postgresql://postgres:YOURPASSWORD"
    "@db.ewbnlnslijasdjgjexpo.supabase.co:5432/postgres"
)

engine = create_engine(SUPABASE_CONNECTION)

def load_data():
    query = """
        SELECT team_name, conference, wins, losses, win_percentage
        FROM teams;
    """
    return pd.read_sql(query, engine)

app = Dash(__name__)
server = app.server

df = load_data()

app.layout = html.Div(
    style={"fontFamily": "Arial", "padding": "30px", "backgroundColor": "#f4f6f8"},
    children=[
        html.H1("SEC & Big Ten College Football Analytics Dashboard", style={"textAlign": "center"}),

        html.P(
            "Interactive dashboard connected to a Supabase PostgreSQL database.",
            style={"textAlign": "center"}
        ),

        html.Div(
            style={"backgroundColor": "white", "padding": "20px", "borderRadius": "10px", "marginBottom": "20px"},
            children=[
                html.Label("Filter by Conference"),
                dcc.Dropdown(
                    id="conference-filter",
                    options=[
                        {"label": "All Conferences", "value": "All"}
                    ] + [
                        {"label": conf, "value": conf}
                        for conf in sorted(df["conference"].dropna().unique())
                    ],
                    value="All",
                    clearable=False
                )
            ]
        ),

        html.Div(
            style={"display": "flex", "gap": "20px", "marginBottom": "20px"},
            children=[
                html.Div(
                    style={"backgroundColor": "white", "padding": "20px", "borderRadius": "10px", "flex": "1", "textAlign": "center"},
                    children=[
                        html.H3("Total Teams"),
                        html.H1(id="total-teams")
                    ]
                ),
                html.Div(
                    style={"backgroundColor": "white", "padding": "20px", "borderRadius": "10px", "flex": "1", "textAlign": "center"},
                    children=[
                        html.H3("Average Win Percentage"),
                        html.H1(id="avg-win-pct")
                    ]
                )
            ]
        ),

        html.Div(
            style={"backgroundColor": "white", "padding": "20px", "borderRadius": "10px", "marginBottom": "20px"},
            children=[
                dcc.Graph(id="wins-bar-chart")
            ]
        ),

        html.Div(
            style={"backgroundColor": "white", "padding": "20px", "borderRadius": "10px"},
            children=[
                dcc.Graph(id="wins-losses-scatter")
            ]
        )
    ]
)

@app.callback(
    Output("total-teams", "children"),
    Output("avg-win-pct", "children"),
    Output("wins-bar-chart", "figure"),
    Output("wins-losses-scatter", "figure"),
    Input("conference-filter", "value")
)
def update_dashboard(selected_conference):

    df = load_data()

    if selected_conference != "All":
        filtered_df = df[df["conference"] == selected_conference]
    else:
        filtered_df = df

    total_teams = len(filtered_df)
    avg_win_pct = round(filtered_df["win_percentage"].mean(), 3)

    bar_fig = px.bar(
        filtered_df.sort_values("wins", ascending=False),
        x="team_name",
        y="wins",
        color="conference",
        title="Wins by Team",
        labels={
            "team_name": "Team",
            "wins": "Wins",
            "conference": "Conference"
        }
    )
    bar_fig.update_layout(xaxis_tickangle=-45)

    scatter_fig = px.scatter(
        filtered_df,
        x="losses",
        y="wins",
        color="conference",
        hover_name="team_name",
        size="win_percentage",
        title="Wins vs. Losses by Team",
        labels={
            "losses": "Losses",
            "wins": "Wins",
            "conference": "Conference",
            "win_percentage": "Win Percentage"
        }
    )

    return total_teams, avg_win_pct, bar_fig, scatter_fig

if __name__ == "__main__":
    app.run(debug=True, port=8051)


# In[ ]:




