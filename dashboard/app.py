

"""Assessed Value"""

import shiny
import pandas as pd
import altair as alt
from shiny import App, render, ui, reactive
import geopandas as gpd
import numpy as np
import shinywidgets as sw
import plotly.express as px
import plotly.graph_objects as go


from shared import app_dir, merged_gdf, fc_gdf

# Preprocess data
merged_gdf['certified_tot_mean'] = pd.to_numeric(merged_gdf['certified_tot_mean'], errors='coerce').fillna(0)

fc_gdf['num_foreclosure_in_half_mile_past_5_years_mean'] = pd.to_numeric(
    fc_gdf['num_foreclosure_in_half_mile_past_5_years_mean'], errors='coerce').fillna(0)

# Clean and convert the `year` column
fc_gdf = fc_gdf[fc_gdf['fc_year'].notna()]  # Drop rows where year is NaN
fc_gdf['fc_year'] = fc_gdf['fc_year'].astype(float).round().astype(int) 

page1 = ui.page_sidebar(
    ui.sidebar(
        ui.input_select(
            id="year_select_1",
            label="Select Year 1:",
            choices=[str(year) for year in sorted(merged_gdf["year"].unique())],
            selected=str(merged_gdf["year"].min()),
        ),
        ui.input_select(
            id="year_select_2",
            label="Select Year 2:",
            choices=[str(year) for year in sorted(merged_gdf["year"].unique())],
            selected=str(merged_gdf["year"].max()),
        ),
        ui.input_select(
            id="pri_neigh",
            label="Neighborhood:",
            choices=sorted(merged_gdf['pri_neigh'].unique().tolist())
        ),
        ui.input_select(
            id="choropleth_year",
            label="Select Year for Map:",
            choices=[str(year) for year in sorted(merged_gdf["year"].unique())],
            selected=str(merged_gdf["year"].max()),
        ),
    ),
    ui.layout_column_wrap(
        ui.card(
            ui.card_header("Top 10 Neighborhoods with Greatest Differences"),
            ui.output_table("av_top_diff_table"),
            width="100px",
            height="150px",
            style="font-size: 12px;",
        ),
        ui.card(
            ui.card_header("Assessed Value by Neighborhood"),
            sw.output_widget("av_reactive_plot"),
            width="100px",
            height="150px",
        ),
        ui.card(
            ui.card_header("Map for Selected Year"),
            sw.output_widget("av_choropleth_map"),
            width="200px",
            height="100px",
        )
    )
)

# Define page 2 UI with unique input IDs
page2 = ui.page_sidebar(
    ui.sidebar(
        ui.input_select(
            id="year_select_1_page2",  # Unique ID for page 2
            label="Select Year 1:",
            choices=[str(year) for year in sorted(fc_gdf["fc_year"].unique())],
            selected=str(fc_gdf["fc_year"].min()),
        ),
        ui.input_select(
            id="year_select_2_page2",  # Unique ID for page 2
            label="Select Year 2:",
            choices=[str(year) for year in sorted(fc_gdf["fc_year"].unique())],
            selected=str(fc_gdf["fc_year"].max()),
        ),
        ui.input_select(
            id="pri_neigh_page2",  # Unique ID for page 2
            label="Neighborhood:",
            choices=sorted(fc_gdf['fc_pri_neigh'].unique().tolist())
        ),
        ui.input_select(
            id="choropleth_year_page2",  # Unique ID for page 2
            label="Select Year for Map:",
            choices=[str(year) for year in sorted(fc_gdf["fc_year"].unique())],
            selected=str(fc_gdf["fc_year"].max()),
        ),
        ui.output_text("fc_selected_neighborhood"),
    ),
    ui.layout_column_wrap(
        ui.card(
            ui.card_header("Top 10 Neighborhoods with Greatest Differences"),
            ui.output_table("fc_top_diff_table"),
            width="100px",
            height="150px",
            style="font-size: 12px;",
        ),
        ui.card(
            ui.card_header("Foreclosures by Neighborhood"),
            sw.output_widget("fc_reactive_plot"),
            width="100px",
            height="150px",
        ),
        ui.card(
            ui.card_header("Map for Selected Year"),
            sw.output_widget("fc_choropleth_map"),
            width="200px",
            height="100px",
        )
    )
)

# Define the app UI with navigation
app_ui = ui.page_navbar(
    ui.nav_spacer(),  # Optional: for better navbar alignment
    ui.nav_panel("Assessed Value", page1),
    ui.nav_panel("Foreclosure", page2),
    title="Property as an Indicator for Gentrification",  # Update this if needed
)


# Server logic for Page 1
def server(input, output, session):
    # Reactive calculation for filtering neighborhood data (Page 1)
    @reactive.calc
    def av_filter_neighborhood_data():
        av_selected_neighborhood = input.pri_neigh()  # Use updated ID for Page 1
        av_filtered_data = merged_gdf[merged_gdf['pri_neigh'] == av_selected_neighborhood]
        if av_filtered_data.empty:
            return pd.DataFrame({'year': [], 'certified_tot_mean': []})
        return av_filtered_data.groupby('year', as_index=False)['certified_tot_mean'].mean()

    # Reactive calculation for aggregated data (Page 1)
    @reactive.calc
    def av_agg_full():
        agg_merged = merged_gdf.groupby('year', as_index=False)['certified_tot_mean'].mean()
        return agg_merged

    # Reactive calculation for choropleth data (Page 1)
    @reactive.calc
    def av_choropleth_data():
        try:
            av_selected_year = int(input.choropleth_year())
            av_filtered_data = merged_gdf[merged_gdf['year'] == av_selected_year]
            if av_filtered_data.empty:
                return pd.DataFrame()  # Return empty dataframe for no data
            av_filtered_data['certified_tot_mean'] = pd.to_numeric(
                av_filtered_data['certified_tot_mean'], errors='coerce'
            ).fillna(0)
            return av_filtered_data
        except Exception as e:
            print(f"Error in choropleth_data: {e}")
            return pd.DataFrame()

    # Reactive calculation for differences between years (Page 1)
    @reactive.calc
    def av_diff_data():
        av_year1 = int(input.year_select_1())
        av_year2 = int(input.year_select_2())
    
        av_data_year1 = merged_gdf[merged_gdf["year"] == av_year1].groupby("pri_neigh")["certified_tot_mean"].mean().reset_index()
        av_data_year1 = av_data_year1.rename(columns={"certified_tot_mean": "value_year1"})
    
        av_data_year2 = merged_gdf[merged_gdf["year"] == av_year2].groupby("pri_neigh")["certified_tot_mean"].mean().reset_index()
        av_data_year2 = av_data_year2.rename(columns={"certified_tot_mean": "value_year2"})
    
        av_merged = pd.merge(av_data_year1, av_data_year2, on="pri_neigh", how="inner")
        av_merged["difference"] = abs(av_merged["value_year2"] - av_merged["value_year1"])
        av_merged = av_merged.sort_values(by="difference", ascending=False)
    
        av_merged["value_year1"] = av_merged["value_year1"].round(2)
        av_merged["value_year2"] = av_merged["value_year2"].round(2)
        av_merged["difference"] = av_merged["difference"].round(2)
    
        return av_merged.head(10)

    # Output for the table showing the differences between years (Page 1)
    @output(id="av_top_diff_table")
    @render.table
    def av_top_diff_table():
        av_data = av_diff_data()
        if av_data.empty:
            return pd.DataFrame(columns=["Neighborhood", "Value (Year 1)", "Value (Year 2)", "Difference"])
        return av_data.rename(
            columns={
                "pri_neigh": "Neighborhood",
                "value_year1": f"Value ({input.year_select_1()})",
                "value_year2": f"Value ({input.year_select_2()})",
                "difference": "Difference",
            }
        )

    # Output for the Altair plot (assessed value by neighborhood, Page 1)
    @output(id="av_reactive_plot")
    @sw.render_altair
    def av_reactive_plot():
        av_filtered_data = av_filter_neighborhood_data()
        if av_filtered_data.empty:
            return alt.Chart().mark_text().encode(
                text=alt.value('No Data Available')
            ).properties(width=275, height=175)

        av_reactive_chart = alt.Chart(av_filtered_data).mark_line().encode(
            x=alt.X('year:O', title='Year'),
            y=alt.Y('certified_tot_mean:Q', 
                    title='Assessed Value',
                    axis=alt.Axis(format='.1f'),
                    scale=alt.Scale(domain=[0, 200000])),  
            tooltip=[
                alt.Tooltip('year:O', title='Year'),
                alt.Tooltip('certified_tot_mean:Q', format='.2f', title='Certified Total')
            ],
        ).properties(
            title=f"Assessed Value by Year for {input.pri_neigh()}",
            width=275,
            height=175
        )

        agg_merged = av_agg_full() 
        av_static_line = alt.Chart(agg_merged).mark_line(color='lightblue', strokeDash=[5, 4]).encode(
            x=alt.X('year:O', title='Year'),
            y=alt.Y('certified_tot_mean:Q', title='Assessed Value', axis=alt.Axis(format='.1f')),
        )
        av_combined_chart = av_static_line + av_reactive_chart
        return av_combined_chart

    # Output for the choropleth map (Page 1)
    @output(id="choropleth_map")
    @sw.render_plotly
    def av_choropleth_map():
        av_filtered_data = av_choropleth_data()
        
        if av_filtered_data.empty:
            # Return an empty map if no data
            av_fig = px.scatter_mapbox(
                geojson={"type": "FeatureCollection", "features": []},  # Empty geojson
                locations=[],
                color=[],
                mapbox_style="carto-positron",
                center={"lat": 41.8781, "lon": -87.6298},
                zoom=10,
                title=f"Choropleth Map for Year {input.choropleth_year()}",  # Use updated ID for Page 1
            )
            return av_fig
        
        # If data is available, render the choropleth map
    @output(id="av_choropleth_map")
    @sw.render_plotly
    def av_choropleth_map():
        av_filtered_data = av_choropleth_data()  # Get the filtered data for the choropleth
        
        # Check if the filtered data is empty
        if av_filtered_data.empty:
            # Return an empty map if no data is available
            av_fig = px.scatter_mapbox(
                geojson={"type": "FeatureCollection", "features": []},  # Empty geojson
                locations=[],
                color=[],
                mapbox_style="carto-positron",
                center={"lat": 41.8781, "lon": -87.6298},  # Chicago as default center
                zoom=10,
                title=f"Choropleth Map for Year {input.choropleth_year()}",  # Use updated ID for page 1
            )
            return av_fig
        
        # If data is available, generate the choropleth map
        av_fig = px.choropleth_mapbox(
            av_filtered_data,
            geojson=av_filtered_data.__geo_interface__,  # Use the geojson interface of the filtered data
            locations=av_filtered_data.index,  # Use the DataFrame index for locations
            color="certified_tot_mean",  # The column to be used for coloring the map
            mapbox_style="carto-positron",
            center={"lat": 41.8781, "lon": -87.6298},  # Chicago as default center
            zoom=10,
            title=f"Choropleth Map for Year {input.choropleth_year()}",  # Use updated ID for page 1
            hover_name="pri_neigh",  # Show neighborhood names on hover
            hover_data={"certified_tot_mean": True},  # Show the value of certified_tot_mean on hover
            range_color=[0, av_filtered_data["certified_tot_mean"].max()],  # Set the color range
        )
        
        # Update layout of the map
        av_fig.update_layout(
            coloraxis_colorbar=dict(
                tickfont=dict(size=10),  # Set font size for colorbar ticks
                title_font=dict(size=10),  # Set font size for colorbar title
                thickness=10,  # Set thickness for the colorbar
            ),
            margin={"r": 0, "t": 40, "l": 0, "b": 0},  # Remove default margins
            width=500,  # Set a custom width for the map
            height=600,  # Set a custom height for the map
        )

        return av_fig

# app = App(app_ui, server)



    @reactive.calc
    def fc_filter_neighborhood_data():
        fc_selected_neighborhood = input.pri_neigh_page2()  # Use updated ID for page2
        fc_filtered_data = fc_gdf[fc_gdf['fc_pri_neigh'] == fc_selected_neighborhood]
        if fc_filtered_data.empty:
            return pd.DataFrame({'fc_year': [], 'num_foreclosure_in_half_mile_past_5_years_mean': []})
        return fc_filtered_data.groupby('fc_year', as_index=False)['num_foreclosure_in_half_mile_past_5_years_mean'].mean()

    @reactive.calc
    def fc_agg_full():
        agg_fc = fc_gdf.groupby('fc_year', as_index=False)['num_foreclosure_in_half_mile_past_5_years_mean'].mean()
        return agg_fc

    # Adjusted function for choropleth data with page2's unique input ID
    @reactive.calc
    def fc_choropleth_data():
        try:
            fc_selected_year = int(input.choropleth_year_page2())  # Use updated ID for page2
            fc_filtered_data = fc_gdf[fc_gdf['fc_year'] == fc_selected_year]
            if fc_filtered_data.empty:
                return pd.DataFrame()  # Return empty dataframe for no data
            fc_filtered_data['num_foreclosure_in_half_mile_past_5_years_mean'] = pd.to_numeric(
                fc_filtered_data['num_foreclosure_in_half_mile_past_5_years_mean'], errors='coerce'
            ).fillna(0)
            return fc_filtered_data
        except Exception as e:
            print(f"Error in choropleth_data: {e}")
            return pd.DataFrame()

    # Adjusted function to calculate differences between years with page2's unique IDs
    @reactive.calc
    def fc_diff_data():
        fc_year1 = int(input.year_select_1_page2())  # Use updated ID for page2
        fc_year2 = int(input.year_select_2_page2())  # Use updated ID for page2
    
        fc_data_year1 = fc_gdf[fc_gdf["fc_year"] == fc_year1].groupby("fc_pri_neigh")[
            "num_foreclosure_in_half_mile_past_5_years_mean"].mean().reset_index()
        fc_data_year1 = fc_data_year1.rename(columns={"num_foreclosure_in_half_mile_past_5_years_mean": "value_year1"})
    
        fc_data_year2 = fc_gdf[fc_gdf["fc_year"] == fc_year2].groupby("fc_pri_neigh")[
            "num_foreclosure_in_half_mile_past_5_years_mean"].mean().reset_index()
        fc_data_year2 = fc_data_year2.rename(columns={"num_foreclosure_in_half_mile_past_5_years_mean": "value_year2"})
    
        fc_merged = pd.merge(fc_data_year1, fc_data_year2, on="fc_pri_neigh", how="inner")
        fc_merged["difference"] = abs(fc_merged["value_year2"] - fc_merged["value_year1"])
        fc_merged = fc_merged.sort_values(by="difference", ascending=False)
    
        fc_merged["value_year1"] = fc_merged["value_year1"].round(2)
        fc_merged["value_year2"] = fc_merged["value_year2"].round(2)
        fc_merged["difference"] = fc_merged["difference"].round(2)
    
        return fc_merged.head(10)

    # Output for the table showing the differences between years (with updated IDs)
    @output(id="fc_top_diff_table")
    @render.table
    def fc_top_diff_table():
        fc_data = fc_diff_data()
        if fc_data.empty:
            return pd.DataFrame(columns=["Neighborhood", "Value (Year 1)", "Value (Year 2)", "Difference"])
        return fc_data.rename(
            columns={
                "fc_pri_neigh": "Neighborhood",
                "value_year1": f"Value ({input.year_select_1_page2()})",  # Use updated ID for page2
                "value_year2": f"Value ({input.year_select_2_page2()})",  # Use updated ID for page2
                "difference": "Difference",
            }
        )

    # Output for the Altair plot (foreclosures by neighborhood, using updated IDs)
    @output(id="fc_reactive_plot")
    @sw.render_altair
    def fc_reactive_plot():
        fc_filtered_data = fc_filter_neighborhood_data()
        fc_reactive_chart = alt.Chart(fc_filtered_data).mark_line().encode(
            x=alt.X('fc_year:O', title='Year'),
            y=alt.Y('num_foreclosure_in_half_mile_past_5_years_mean:Q', 
                    title='Foreclosures',
                    axis=alt.Axis(format='.1f'),
                    scale=alt.Scale(domain=[0, 200])),  
            tooltip=[
                alt.Tooltip('fc_year:O', title='Year'),
                alt.Tooltip('num_foreclosure_in_half_mile_past_5_years_mean:Q', format='.2f', title='Foreclosures')
            ],
        ).properties(
            title=f"Foreclosures by Year for {input.pri_neigh_page2()}",  # Use updated ID for page2
            width=275,
            height=175
        )
        agg_fc = fc_agg_full() 
        fc_static_line = alt.Chart(agg_fc).mark_line(color='lightblue', strokeDash=[5, 4]).encode(
            x=alt.X('fc_year:O', title='Year'),
            y=alt.Y('num_foreclosure_in_half_mile_past_5_years_mean:Q', title='Foreclosures', axis=alt.Axis(format='.1f')),
        )
        fc_combined_chart = fc_static_line + fc_reactive_chart
        return fc_combined_chart

    # Output for the choropleth map (using updated ID for page2)
    @output(id="fc_choropleth_map")
    @sw.render_plotly
    def fc_choropleth_map():
        fc_filtered_data = fc_choropleth_data()
        
        if fc_filtered_data.empty:
            fc_fig = px.scatter_mapbox(
                geojson={"type": "FeatureCollection", "features": []},  
                locations=[],
                color=[],
                mapbox_style="carto-positron",
                center={"lat": 41.8781, "lon": -87.6298},
                zoom=10,
                title=f"Choropleth Map for Year {input.choropleth_year_page2()}",  # Use updated ID for page2
            )
            return fc_fig
        

        fc_fig = px.choropleth_mapbox(
            fc_filtered_data,
            geojson=fc_filtered_data.set_geometry('fc_geometry').__geo_interface__,  # Use the 'fc_geometry' column
            locations=fc_filtered_data.index,
            color="num_foreclosure_in_half_mile_past_5_years_mean",
            mapbox_style="carto-positron",
            center={"lat": 41.8781, "lon": -87.6298},
            zoom=10,
            title=f"Choropleth Map for Year {input.choropleth_year_page2()}",  
            hover_name="fc_pri_neigh",  
            hover_data={"num_foreclosure_in_half_mile_past_5_years_mean": True},
            range_color=[0, fc_filtered_data["num_foreclosure_in_half_mile_past_5_years_mean"].max()],
        )

        fc_fig.update_layout(
            coloraxis_colorbar=dict(
                tickfont=dict(size=10),  
                title_font=dict(size=10),  
                thickness=10,  
            ),
            margin={"r": 0, "t": 40, "l": 0, "b": 0},  
            width=500,  
            height=600,  
        )

        return fc_fig

    @output(id="fc_selected_neighborhood")
    @render.text
    def selected_neighborhood():
        return f""


app = App(app_ui, server)





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


# foreclosure

# # import shiny
# import pandas as pd
# import altair as alt
# from shiny import App, render, ui, reactive
# import geopandas as gpd
# import numpy as np
# import shinywidgets as sw
# import plotly.express as px

# from shared import app_dir, fc_gdf

# Preprocess data
# fc_gdf['num_foreclosure_in_half_mile_past_5_years_mean'] = pd.to_numeric(
#     fc_gdf['num_foreclosure_in_half_mile_past_5_years_mean'], errors='coerce').fillna(0)

# # Clean and convert the `year` column
# fc_gdf = fc_gdf[fc_gdf['year'].notna()]  # Drop rows where year is NaN
# fc_gdf['year'] = fc_gdf['year'].astype(float).round().astype(int)  # Convert to integer after rounding

# Define the UI
# app_ui = ui.page_sidebar(
#     ui.sidebar(
#         ui.input_select(
#             id="year_select_1",
#             label="Select Year 1:",
#             choices=[str(year) for year in sorted(fc_gdf["year"].unique())],
#             selected=str(fc_gdf["year"].min()),
#         ),
#         ui.input_select(
#             id="year_select_2",
#             label="Select Year 2:",
#             choices=[str(year) for year in sorted(fc_gdf["year"].unique())],
#             selected=str(fc_gdf["year"].max()),
#         ),
#         ui.input_select(
#             id="pri_neigh",
#             label="Neighborhood:",
#             choices=sorted(fc_gdf['pri_neigh'].unique().tolist())
#         ),
#         ui.input_select(
#             id="choropleth_year",
#             label="Select Year for Map:",
#             choices=[str(year) for year in sorted(fc_gdf["year"].unique())],
#             selected=str(fc_gdf["year"].max()),
#         ),
#         ui.output_text("fc_selected_neighborhood"),
#     ),
#     ui.layout_column_wrap(
#         ui.card(
#             ui.card_header("Top 10 Neighborhoods with Greatest Differences"),
#             ui.output_table("fc_top_diff_table"),
#             width="100px",
#             height="150px",
#             style="font-size: 12px;",
#         ),
#         ui.card(
#             ui.card_header("Foreclosures by Neighborhood"),
#             sw.output_widget("fc_reactive_plot"),
#             width="100px",
#             height="150px",
#         ),
#         ui.card(
#             ui.card_header("Map for Selected Year"),
#             sw.output_widget("fc_choropleth_map"),
#             width="200px",
#             height="100px",
#         )
#     )
# )

# Define the Server
    # Adjusted function to filter neighborhood data based on page2's unique ID