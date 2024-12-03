

"""Assessed Value"""

# import shiny
# import pandas as pd
# import altair as alt
# from shiny import App, render, ui, reactive
# import geopandas as gpd
# import numpy as np
# import shinywidgets as sw
# import plotly.express as px

# from shared import app_dir, merged_gdf, fc_gdf

# # Preprocess data
# merged_gdf['certified_tot_mean'] = pd.to_numeric(merged_gdf['certified_tot_mean'], errors='coerce').fillna(0)

# # Define the UI
# app_ui = ui.page_sidebar(
#     ui.sidebar(
#         ui.input_select(
#             id="year_select_1",
#             label="Select Year 1:",
#             choices=[str(year) for year in sorted(merged_gdf["year"].unique())],
#             selected=str(merged_gdf["year"].min()),
#         ),
#         ui.input_select(
#             id="year_select_2",
#             label="Select Year 2:",
#             choices=[str(year) for year in sorted(merged_gdf["year"].unique())],
#             selected=str(merged_gdf["year"].max()),
#         ),
#         ui.input_select(
#             id="pri_neigh",
#             label="Neighborhood:",
#             choices=sorted(merged_gdf['pri_neigh'].unique().tolist())
#         ),
#         ui.input_select(
#             id="choropleth_year",
#             label="Select Year for Map:",
#             choices=[str(year) for year in sorted(merged_gdf["year"].unique())],
#             selected=str(merged_gdf["year"].max()),
#         ),
#         ui.output_text("selected_neighborhood"),
#     ),
#     ui.layout_column_wrap(
#         ui.card(
#             ui.card_header("Top 10 Neighborhoods with Greatest Differences"),
#             ui.output_table("top_diff_table"),
#             width="100px",
#             height="150px",
#             style="font-size: 12px;",
#         ),
#         ui.card(
#             ui.card_header("Assessed Value by Neighborhood"),
#             sw.output_widget("reactive_plot"),
#             width="100px",
#             height="150px",
#         ),
#         ui.card(
#             ui.card_header("Map for Selected Year"),
#             sw.output_widget("choropleth_map"),
#             width="200px",
#             height="100px",
#         )
#     )
# )

# # Define the Server
# def server(input, output, session):
#     @reactive.calc
#     def filter_neighborhood_data():
#         selected_neighborhood = input.pri_neigh()
#         filtered_data = merged_gdf[merged_gdf['pri_neigh'] == selected_neighborhood]
#         if filtered_data.empty:
#             return pd.DataFrame({'year': [], 'certified_tot_mean': []})
#         return filtered_data.groupby('year', as_index=False)['certified_tot_mean'].mean()

#     @reactive.calc
#     def agg_full():
#         agg_merged = merged_gdf.groupby('year', as_index=False)['certified_tot_mean'].mean()
#         return agg_merged

#     @reactive.calc
#     def choropleth_data():
#         try:
#             selected_year = int(input.choropleth_year())
#             filtered_data = merged_gdf[merged_gdf['year'] == selected_year]
#             if filtered_data.empty:
#                 return pd.DataFrame()  # Return empty dataframe for no data
#             filtered_data['certified_tot_mean'] = pd.to_numeric(
#                 filtered_data['certified_tot_mean'], errors='coerce'
#             ).fillna(0)
#             return filtered_data
#         except Exception as e:
#             print(f"Error in choropleth_data: {e}")
#             return pd.DataFrame()

#     @reactive.calc
#     def diff_data():
#         year1 = int(input.year_select_1())
#         year2 = int(input.year_select_2())
    
#         data_year1 = merged_gdf[merged_gdf["year"] == year1].groupby("pri_neigh")["certified_tot_mean"].mean().reset_index()
#         data_year1 = data_year1.rename(columns={"certified_tot_mean": "value_year1"})
    
#         data_year2 = merged_gdf[merged_gdf["year"] == year2].groupby("pri_neigh")["certified_tot_mean"].mean().reset_index()
#         data_year2 = data_year2.rename(columns={"certified_tot_mean": "value_year2"})
    
#         merged = pd.merge(data_year1, data_year2, on="pri_neigh", how="inner")
#         merged["difference"] = abs(merged["value_year2"] - merged["value_year1"])
#         merged = merged.sort_values(by="difference", ascending=False)
    
#         merged["value_year1"] = merged["value_year1"].round().astype(int)
#         merged["value_year2"] = merged["value_year2"].round().astype(int)
#         merged["difference"] = merged["difference"].round().astype(int)
    
#         return merged.head(10)

#     @output(id="top_diff_table")
#     @render.table
#     def top_diff_table():
#         data = diff_data()
#         if data.empty:
#             return pd.DataFrame(columns=["Neighborhood", "Value (Year 1)", "Value (Year 2)", "Difference"])
#         return data.rename(
#             columns={
#                 "pri_neigh": "Neighborhood",
#                 "value_year1": f"Value ({input.year_select_1()})",
#                 "value_year2": f"Value ({input.year_select_2()})",
#                 "difference": "Difference",
#             }
#         )

#     @output(id="reactive_plot")
#     @sw.render_altair
#     def _():
#         filtered_data = filter_neighborhood_data()  

#         reactive_chart = alt.Chart(filtered_data).mark_line().encode(
#             x=alt.X('year:O', title='Year'),
#             y=alt.Y('certified_tot_mean:Q', 
#                     title='Assessed Value',
#                     axis=alt.Axis(format='.1f'),
#                     scale=alt.Scale(domain=[0, 200000])),  
#             tooltip=[
#                 alt.Tooltip('year:O', title='Year'),
#                 alt.Tooltip('certified_tot_mean:Q', format='.2f', title='Certified Total')
#             ],
#         ).properties(
#             title=f"Assessed Value by Year for {input.pri_neigh()}",
#             width=275,
#             height=175
#         )


#         agg_merged = agg_full() 
#         static_line = alt.Chart(agg_merged).mark_line(color='lightblue', strokeDash=[5, 4]).encode(
#             x=alt.X('year:O', title='Year'),
#             y=alt.Y('certified_tot_mean:Q', title='Assessed Value', axis=alt.Axis(format='.1f')),
#         )
#         combined_chart = static_line + reactive_chart 

#         return combined_chart

#     @output(id="choropleth_map")
#     @sw.render_plotly
#     def choropleth_map():
#         filtered_data = choropleth_data()
#         if filtered_data.empty:
#             return ""  
#         fig = px.choropleth_mapbox(
#             filtered_data,
#             geojson=filtered_data.__geo_interface__,
#             locations=filtered_data.index,
#             color="certified_tot_mean",
#             mapbox_style="carto-positron",
#             center={"lat": 41.8781, "lon": -87.6298},
#             zoom=10,
#             title=f"Choropleth Map for Year {input.choropleth_year()}",
#             hover_name="pri_neigh",  
#             hover_data={"certified_tot_mean": True},
#             range_color=[0, 150000], 
#         )

#         fig.update_layout(
#             coloraxis_colorbar=dict(
#                 tickfont=dict(size=10),  
#                 title_font=dict(size=10),  
#                 thickness=10,  
#             ),
#         )

#         return fig

#     @output(id="selected_neighborhood")
#     @render.text
#     def selected_neighborhood():
#         return f""

# app = App(app_ui, server)


"""foreclosure """

# import shiny
import pandas as pd
import altair as alt
from shiny import App, render, ui, reactive
import geopandas as gpd
import numpy as np
import shinywidgets as sw
import plotly.express as px

from shared import app_dir, fc_gdf

# Preprocess data
fc_gdf['num_foreclosure_in_half_mile_past_5_years_mean'] = pd.to_numeric(
    fc_gdf['num_foreclosure_in_half_mile_past_5_years_mean'], errors='coerce').fillna(0)

# Clean and convert the `year` column
fc_gdf = fc_gdf[fc_gdf['year'].notna()]  # Drop rows where year is NaN
fc_gdf['year'] = fc_gdf['year'].astype(float).round().astype(int)  # Convert to integer after rounding

# Define the UI
app_ui = ui.page_sidebar(
    ui.sidebar(
        ui.input_select(
            id="year_select_1",
            label="Select Year 1:",
            choices=[str(year) for year in sorted(fc_gdf["year"].unique())],
            selected=str(fc_gdf["year"].min()),
        ),
        ui.input_select(
            id="year_select_2",
            label="Select Year 2:",
            choices=[str(year) for year in sorted(fc_gdf["year"].unique())],
            selected=str(fc_gdf["year"].max()),
        ),
        ui.input_select(
            id="pri_neigh",
            label="Neighborhood:",
            choices=sorted(fc_gdf['pri_neigh'].unique().tolist())
        ),
        ui.input_select(
            id="choropleth_year",
            label="Select Year for Map:",
            choices=[str(year) for year in sorted(fc_gdf["year"].unique())],
            selected=str(fc_gdf["year"].max()),
        ),
        ui.output_text("selected_neighborhood"),
    ),
    ui.layout_column_wrap(
        ui.card(
            ui.card_header("Top 10 Neighborhoods with Greatest Differences"),
            ui.output_table("top_diff_table"),
            width="100px",
            height="150px",
            style="font-size: 12px;",
        ),
        ui.card(
            ui.card_header("Foreclosures by Neighborhood"),
            sw.output_widget("reactive_plot"),
            width="100px",
            height="150px",
        ),
        ui.card(
            ui.card_header("Map for Selected Year"),
            sw.output_widget("choropleth_map"),
            width="200px",
            height="100px",
        )
    )
)

# Define the Server
def server(input, output, session):
    @reactive.calc
    def filter_neighborhood_data():
        selected_neighborhood = input.pri_neigh()
        filtered_data = fc_gdf[fc_gdf['pri_neigh'] == selected_neighborhood]
        if filtered_data.empty:
            return pd.DataFrame({'year': [], 'num_foreclosure_in_half_mile_past_5_years_mean': []})
        return filtered_data.groupby('year', as_index=False)['num_foreclosure_in_half_mile_past_5_years_mean'].mean()

    @reactive.calc
    def agg_full():
        agg_fc = fc_gdf.groupby('year', as_index=False)['num_foreclosure_in_half_mile_past_5_years_mean'].mean()
        return agg_fc

    @reactive.calc
    def choropleth_data():
        try:
            selected_year = int(input.choropleth_year())
            filtered_data = fc_gdf[fc_gdf['year'] == selected_year]
            if filtered_data.empty:
                return pd.DataFrame()  # Return empty dataframe for no data
            filtered_data['num_foreclosure_in_half_mile_past_5_years_mean'] = pd.to_numeric(
                filtered_data['num_foreclosure_in_half_mile_past_5_years_mean'], errors='coerce'
            ).fillna(0)
            return filtered_data
        except Exception as e:
            print(f"Error in choropleth_data: {e}")
            return pd.DataFrame()

    @reactive.calc
    def diff_data():
        year1 = int(input.year_select_1())
        year2 = int(input.year_select_2())
    
        data_year1 = fc_gdf[fc_gdf["year"] == year1].groupby("pri_neigh")[
            "num_foreclosure_in_half_mile_past_5_years_mean"].mean().reset_index()
        data_year1 = data_year1.rename(columns={"num_foreclosure_in_half_mile_past_5_years_mean": "value_year1"})
    
        data_year2 = fc_gdf[fc_gdf["year"] == year2].groupby("pri_neigh")[
            "num_foreclosure_in_half_mile_past_5_years_mean"].mean().reset_index()
        data_year2 = data_year2.rename(columns={"num_foreclosure_in_half_mile_past_5_years_mean": "value_year2"})
    
        merged = pd.merge(data_year1, data_year2, on="pri_neigh", how="inner")
        merged["difference"] = abs(merged["value_year2"] - merged["value_year1"])
        merged = merged.sort_values(by="difference", ascending=False)
    
        merged["value_year1"] = merged["value_year1"].round(2)
        merged["value_year2"] = merged["value_year2"].round(2)
        merged["difference"] = merged["difference"].round(2)
    
        return merged.head(10)

    @output(id="top_diff_table")
    @render.table
    def top_diff_table():
        data = diff_data()
        if data.empty:
            return pd.DataFrame(columns=["Neighborhood", "Value (Year 1)", "Value (Year 2)", "Difference"])
        return data.rename(
            columns={
                "pri_neigh": "Neighborhood",
                "value_year1": f"Value ({input.year_select_1()})",
                "value_year2": f"Value ({input.year_select_2()})",
                "difference": "Difference",
            }
        )

    @output(id="reactive_plot")
    @sw.render_altair
    def reactive_plot():
        filtered_data = filter_neighborhood_data()
        reactive_chart = alt.Chart(filtered_data).mark_line().encode(
            x=alt.X('year:O', title='Year'),
            y=alt.Y('num_foreclosure_in_half_mile_past_5_years_mean:Q', 
                    title='Foreclosures',
                    axis=alt.Axis(format='.1f'),
                    scale=alt.Scale(domain=[0, 200])),  
            tooltip=[
                alt.Tooltip('year:O', title='Year'),
                alt.Tooltip('num_foreclosure_in_half_mile_past_5_years_mean:Q', format='.2f', title='Foreclosures')
            ],
        ).properties(
            title=f"Foreclosures by Year for {input.pri_neigh()}",
            width=275,
            height=175
        )
        agg_fc = agg_full() 
        static_line = alt.Chart(agg_fc).mark_line(color='lightblue', strokeDash=[5, 4]).encode(
            x=alt.X('year:O', title='Year'),
            y=alt.Y('num_foreclosure_in_half_mile_past_5_years_mean:Q', title='Foreclosures', axis=alt.Axis(format='.1f')),
        )
        combined_chart = static_line + reactive_chart
        return combined_chart

    @output(id="choropleth_map")
    @sw.render_plotly
    def choropleth_map():
        filtered_data = choropleth_data()
        if filtered_data.empty:
            return ""  
        fig = px.choropleth_mapbox(
            filtered_data,
            geojson=filtered_data.__geo_interface__,
            locations=filtered_data.index,
            color="num_foreclosure_in_half_mile_past_5_years_mean",
            mapbox_style="carto-positron",
            center={"lat": 41.8781, "lon": -87.6298},
            zoom=10,
            title=f"Choropleth Map for Year {input.choropleth_year()}",
            hover_name="pri_neigh",  
            hover_data={"num_foreclosure_in_half_mile_past_5_years_mean": True},
            range_color=[0, filtered_data["num_foreclosure_in_half_mile_past_5_years_mean"].max()],
        )

        fig.update_layout(
            coloraxis_colorbar=dict(
                tickfont=dict(size=10),  
                title_font=dict(size=10),  
                thickness=10,  
            ),
            margin={"r": 0, "t": 40, "l": 0, "b": 0},  # Remove default margins
            width=500,  # Set a wider width
            height=600,  # Optional: Adjust height as needed
        )

        return fig



    @output(id="selected_neighborhood")
    @render.text
    def selected_neighborhood():
        return f""

app = App(app_ui, server)
