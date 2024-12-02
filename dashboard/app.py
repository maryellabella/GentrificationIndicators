# import shiny
# import pandas as pd 
# import altair as alt
# from shiny import App, render, ui, reactive
# import geopandas as gpd
# import numpy as np
# import shinywidgets as sw
# from shinywidgets import render_altair, output_widget
# import matplotlib.pyplot as plt

# import tempfile


# from shared import app_dir, merged_gdf

# app_ui = ui.page_sidebar(
#     ui.sidebar(
#         ui.input_select(
#             id='pri_neigh',
#             label='Neighborhood:',
#             choices=sorted(merged_gdf['pri_neigh'].unique().tolist())
#         ),
#         ui.input_select(
#             id='year_select',
#             label='Year:',
#             choices=[str(year) for year in sorted(merged_gdf['year'].unique())],
#             selected=str(merged_gdf['year'].max())  
#         ),
#         ui.output_text('selected_neighborhood')
#     ),
#     ui.layout_column_wrap(
#         ui.card(
#             ui.card_header("Average Assessed Value by Year"),
#             sw.output_widget('static_plot'),
#             width="100px", 
#             height="150px"   
#         ),
#         ui.card(
#             ui.card_header("Assessed Value by Neighborhood"),
#             sw.output_widget('reactive_plot'),
#             width="100px", 
#             height="150px",   
#         ),
#         ui.card(
#             ui.card_header("Map for Selected Year"),
#             ui.output_image('choropleth_map'),
#             width="200px", 
#             height="100px",  
#         )
#     )
# )

# def server(input, output, session):

#     @reactive.calc
#     def agg_full():
#         agg_merged = merged_gdf.groupby('year', as_index=False)['certified_tot_mean'].mean()
#         return agg_merged

#     @reactive.calc
#     def filter_neighborhood_data():
#         selected_neighborhood = input.pri_neigh()
#         filtered_data = merged_gdf[merged_gdf['pri_neigh'] == selected_neighborhood]
#         agg_filtered = filtered_data.groupby('year', as_index=False)['certified_tot_mean'].mean()
#         return agg_filtered

#     @reactive.calc
#     def choropleth_data():
#         selected_year = int(input.year_select())
#         filtered_data = merged_gdf[merged_gdf['year'] == selected_year]
#         filtered_data['certified_tot_mean'] = pd.to_numeric(filtered_data['certified_tot_mean'], errors='coerce')
#         return filtered_data

#     @output(id="static_plot")
#     @sw.render_altair
#     def _():
#         agg_merged = agg_full() 
#         static_chart = alt.Chart(agg_merged).mark_line().encode(
#             x=alt.X('year:O', title='Year'),
#             y=alt.Y('certified_tot_mean:Q',
#                     title='Assessed Value (Thousands)',
#                     axis=alt.Axis(format='.1f')),
#             tooltip=[alt.Tooltip('year:O', title='Year'),
#                      alt.Tooltip('certified_tot_mean:Q', format='.2f', title='Certified Total')],
#         ).properties(
#             title="Assessed Value Average by Year",
#             width=300,
#             height=150
#         )
#         return static_chart

#     @output(id="reactive_plot")
#     @sw.render_altair
#     def _():
#         filtered_data = filter_neighborhood_data()  

#         reactive_chart = alt.Chart(filtered_data).mark_line().encode(
#             x=alt.X('year:O', title='Year'),
#             y=alt.Y('certified_tot_mean:Q', 
#                     title='Assessed Value (Thousands)',
#                     axis=alt.Axis(format='.1f'),
#                     scale=alt.Scale(domain=[0, 700])),  
#             tooltip=[
#                 alt.Tooltip('year:O', title='Year'),
#                 alt.Tooltip('certified_tot_mean:Q', format='.2f', title='Certified Total')
#             ],
#         ).properties(
#             title=f"Assessed Value by Year for {input.pri_neigh()}",
#             width=300,
#             height=200
#         )


#         agg_merged = agg_full() 
#         static_line = alt.Chart(agg_merged).mark_line(color='lightblue', strokeDash=[5, 4]).encode(
#             x=alt.X('year:O', title='Year'),
#             y=alt.Y('certified_tot_mean:Q', title='Assessed Value (Thousands)', axis=alt.Axis(format='.1f')),
#         )
#         combined_chart = static_line + reactive_chart 

#         return combined_chart



#     @output(id="choropleth_map")
#     @render.image
#     def _():
#         filtered_data = choropleth_data()  

#         vmin, vmax = 0, 700  

#         fig, ax = plt.subplots(figsize=(6, 4))

#         filtered_data.plot(column='certified_tot_mean', ax=ax, legend=False,
#                            cmap='Blues', edgecolor='lightgray', linewidth=0.5,
#                            vmin=vmin, vmax=vmax,  
#                            )

#         cbar = ax.get_figure().colorbar(ax.collections[0], ax=ax, orientation='vertical', shrink=0.6)
#         cbar.ax.tick_params(labelsize=6)  
#         cbar.set_label("Assessed Value Total (Thousands)", fontsize=8)  
#         ax.set_title(f"Assessed Value for Year {int(input.year_select())}")
#         ax.set_xticks([])  
#         ax.set_yticks([])  

#         with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as tmpfile:
#             image_path = tmpfile.name
#             fig.savefig(image_path, bbox_inches='tight')  
#             plt.close(fig)

#         return {"src": image_path}

#     @output(id="selected_neighborhood")
#     @render.text
#     def _():
#         return ""
    



# app = App(app_ui, server)

# import shiny
# import pandas as pd
# from shiny import App, render, ui, reactive
# import shinywidgets as sw

# from shared import app_dir, merged_gdf

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
#     ),
#     ui.layout_column_wrap(
#         ui.card(
#             ui.card_header("Top 10 Neighborhoods with Greatest Differences"),
#             ui.output_table("top_diff_table"),
#             width="100px",
#             height="150px",
#         )
#     ),
# )

# # Define the Server
# def server(input, output, session):
#     @reactive.calc
#     def diff_data():
#         # Extract selected years
#         year1 = int(input.year_select_1())
#         year2 = int(input.year_select_2())
        
#         # Filter data for the selected years
#         data_year1 = merged_gdf[merged_gdf["year"] == year1][
#             ["pri_neigh", "certified_tot_mean"]
#         ].rename(columns={"certified_tot_mean": "value_year1"})
#         data_year2 = merged_gdf[merged_gdf["year"] == year2][
#             ["pri_neigh", "certified_tot_mean"]
#         ].rename(columns={"certified_tot_mean": "value_year2"})
        
#         # Merge data for both years
#         merged = pd.merge(data_year1, data_year2, on="pri_neigh", how="inner")
        
#         # Calculate the difference
#         merged["difference"] = abs(merged["value_year2"] - merged["value_year1"])
        
#         # Sort by greatest difference
#         merged = merged.sort_values(by="difference", ascending=False)
        
#         return merged

#     @output
#     @render.table
#     def top_diff_table():
#         # Get the data and select the top 10 rows
#         data = diff_data()
#         top10 = data.head(10).copy()
        
#         # Format the table
#         top10 = top10.rename(
#             columns={
#                 "pri_neigh": "Neighborhood",
#                 "value_year1": f"Value ({input.year_select_1()})",
#                 "value_year2": f"Value ({input.year_select_2()})",
#                 "difference": "Difference",
#             }
#         )
        
#         return top10

# # Create the App
# app = App(app_ui, server)

# import shiny
# import pandas as pd
# import altair as alt
# from shiny import App, render, ui, reactive
# import geopandas as gpd
# import numpy as np
# import shinywidgets as sw
# import plotly.express as px

# from shared import app_dir, merged_gdf

# # Preprocess data
# merged_gdf['certified_tot_mean'] = pd.to_numeric(merged_gdf['certified_tot_mean'], errors='coerce').fillna(0)

# # Define the UI
# app_ui = ui.page_sidebar(
#     ui.sidebar(
#         ui.input_select(
#             id="pri_neigh",
#             label="Neighborhood:",
#             choices=sorted(merged_gdf['pri_neigh'].unique().tolist())
#         ),
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
#         ui.output_text('selected_neighborhood'),
#     ),
#     ui.layout_column_wrap(
#         ui.card(
#             ui.card_header("Top 10 Neighborhoods with Greatest Differences"),
#             ui.output_table("top_diff_table"),
#             width="100px",
#             height="150px",
#         ),
#         ui.card(
#             ui.card_header("Assessed Value by Neighborhood"),
#             sw.output_widget('reactive_plot'),
#             width="100px",
#             height="150px",
#         ),
#         ui.card(
#             ui.card_header("Map for Selected Year"),
#             sw.output_widget('choropleth_map'),
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
#         agg_filtered = filtered_data.groupby('year', as_index=False)['certified_tot_mean'].mean()
#         return agg_filtered

#     @reactive.calc
#     def choropleth_data():
#         selected_year = int(input.year_select_1())  # Use year_select_1 for map
#         filtered_data = merged_gdf[merged_gdf['year'] == selected_year]
#         filtered_data['certified_tot_mean'] = pd.to_numeric(filtered_data['certified_tot_mean'], errors='coerce')
#         return filtered_data

#     @reactive.calc
#     def diff_data():
#         # Extract selected years
#         year1 = int(input.year_select_1())
#         year2 = int(input.year_select_2())
        
#         # Filter data for the selected years
#         data_year1 = merged_gdf[merged_gdf["year"] == year1][
#             ["pri_neigh", "certified_tot_mean"]
#         ].rename(columns={"certified_tot_mean": "value_year1"})
#         data_year2 = merged_gdf[merged_gdf["year"] == year2][
#             ["pri_neigh", "certified_tot_mean"]
#         ].rename(columns={"certified_tot_mean": "value_year2"})
        
#         # Merge data for both years
#         merged = pd.merge(data_year1, data_year2, on="pri_neigh", how="inner")
        
#         # Calculate the difference
#         merged["difference"] = abs(merged["value_year2"] - merged["value_year1"])
        
#         # Remove duplicates and sort by greatest difference
#         merged = merged.drop_duplicates(subset=["pri_neigh"]).sort_values(by="difference", ascending=False)
        
#         return merged

#     @output(id="top_diff_table")
#     @render.table
#     def top_diff_table():
#         # Get the data and select the top 10 rows
#         data = diff_data()
#         top10 = data.head(10).copy()
        
#         # Format the table
#         top10 = top10.rename(
#             columns={
#                 "pri_neigh": "Neighborhood",
#                 "value_year1": f"Value ({input.year_select_1()})",
#                 "value_year2": f"Value ({input.year_select_2()})",
#                 "difference": "Difference",
#             }
#         )
#         return top10

#     @output(id="reactive_plot")
#     @sw.render_altair
#     def reactive_plot():
#         filtered_data = filter_neighborhood_data()
#         reactive_chart = alt.Chart(filtered_data).mark_line().encode(
#             x=alt.X('year:O', title='Year'),
#             y=alt.Y('certified_tot_mean:Q', 
#                     title='Assessed Value (Thousands)',
#                     axis=alt.Axis(format='.1f'),
#                     scale=alt.Scale(domain=[0, 700])),  
#             tooltip=[
#                 alt.Tooltip('year:O', title='Year'),
#                 alt.Tooltip('certified_tot_mean:Q', format='.2f', title='Certified Total')
#             ],
#         ).properties(
#             title=f"Assessed Value by Year for {input.pri_neigh()}",
#             width=300,
#             height=200
#         )
#         return reactive_chart

#     @output(id="choropleth_map")
#     @sw.render_plotly
#     def choropleth_map():
#         filtered_data = choropleth_data()
#         avg_assessed_value = filtered_data["certified_tot_mean"].mean()

#         fig = px.choropleth_mapbox(
#             filtered_data,
#             geojson=filtered_data.__geo_interface__,
#             locations=filtered_data.index,
#             color="certified_tot_mean",
#             mapbox_style="carto-positron",
#             center={"lat": 41.8781, "lon": -87.6298},
#             zoom=10,
#             title="Choropleth Map for Assessed Values",
#         )

#         fig.add_shape(
#             type="line",
#             x0=0,
#             x1=1,
#             xref="paper",
#             y0=avg_assessed_value,
#             y1=avg_assessed_value,
#             line=dict(color="gray", width=2, dash="dot"),
#         )

#         return fig

# app = App(app_ui, server)

# Define the Server

import shiny
import pandas as pd
import altair as alt
from shiny import App, render, ui, reactive
import geopandas as gpd
import numpy as np
import shinywidgets as sw
import plotly.express as px

from shared import app_dir, merged_gdf

# Preprocess data
merged_gdf['certified_tot_mean'] = pd.to_numeric(merged_gdf['certified_tot_mean'], errors='coerce').fillna(0)

# Define the UI
app_ui = ui.page_sidebar(
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
            ui.card_header("Assessed Value by Neighborhood"),
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
        filtered_data = merged_gdf[merged_gdf['pri_neigh'] == selected_neighborhood]
        if filtered_data.empty:
            return pd.DataFrame({'year': [], 'certified_tot_mean': []})
        return filtered_data.groupby('year', as_index=False)['certified_tot_mean'].mean()

    @reactive.calc
    def agg_full():
        agg_merged = merged_gdf.groupby('year', as_index=False)['certified_tot_mean'].mean()
        return agg_merged

    @reactive.calc
    def choropleth_data():
        try:
            selected_year = int(input.choropleth_year())
            filtered_data = merged_gdf[merged_gdf['year'] == selected_year]
            if filtered_data.empty:
                return pd.DataFrame()  # Return empty dataframe for no data
            filtered_data['certified_tot_mean'] = pd.to_numeric(
                filtered_data['certified_tot_mean'], errors='coerce'
            ).fillna(0)
            return filtered_data
        except Exception as e:
            print(f"Error in choropleth_data: {e}")
            return pd.DataFrame()

    @reactive.calc
    def diff_data():
        year1 = int(input.year_select_1())
        year2 = int(input.year_select_2())
    
        data_year1 = merged_gdf[merged_gdf["year"] == year1].groupby("pri_neigh")["certified_tot_mean"].mean().reset_index()
        data_year1 = data_year1.rename(columns={"certified_tot_mean": "value_year1"})
    
        data_year2 = merged_gdf[merged_gdf["year"] == year2].groupby("pri_neigh")["certified_tot_mean"].mean().reset_index()
        data_year2 = data_year2.rename(columns={"certified_tot_mean": "value_year2"})
    
        merged = pd.merge(data_year1, data_year2, on="pri_neigh", how="inner")
        merged["difference"] = abs(merged["value_year2"] - merged["value_year1"])
        merged = merged.sort_values(by="difference", ascending=False)
    
        merged["value_year1"] = merged["value_year1"].round().astype(int)
        merged["value_year2"] = merged["value_year2"].round().astype(int)
        merged["difference"] = merged["difference"].round().astype(int)
    
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
    def _():
        filtered_data = filter_neighborhood_data()  

        reactive_chart = alt.Chart(filtered_data).mark_line().encode(
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


        agg_merged = agg_full() 
        static_line = alt.Chart(agg_merged).mark_line(color='lightblue', strokeDash=[5, 4]).encode(
            x=alt.X('year:O', title='Year'),
            y=alt.Y('certified_tot_mean:Q', title='Assessed Value', axis=alt.Axis(format='.1f')),
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
            color="certified_tot_mean",
            mapbox_style="carto-positron",
            center={"lat": 41.8781, "lon": -87.6298},
            zoom=10,
            title=f"Choropleth Map for Year {input.choropleth_year()}",
            hover_name="pri_neigh",  
            hover_data={"certified_tot_mean": True},
            range_color=[0, 150000], 
        )

        fig.update_layout(
            coloraxis_colorbar=dict(
                tickfont=dict(size=10),  
                title_font=dict(size=10),  
                thickness=10,  
            ),
        )

        return fig

    @output(id="selected_neighborhood")
    @render.text
    def selected_neighborhood():
        return f""

app = App(app_ui, server)

