


# """Assessed Value"""

# import shiny
# import pandas as pd
# import altair as alt
# from shiny import App, render, ui, reactive
# import geopandas as gpd
# import numpy as np
# import shinywidgets as sw
# import plotly.express as px
# import plotly.graph_objects as go


# from shared import app_dir, merged_gdf, fc_gdf, ps_gdf

# # Preprocess data
# merged_gdf['certified_tot_mean'] = pd.to_numeric(merged_gdf['certified_tot_mean'], errors='coerce').fillna(0)

# fc_gdf['num_foreclosure_in_half_mile_past_5_years_mean'] = pd.to_numeric(
#     fc_gdf['num_foreclosure_in_half_mile_past_5_years_mean'], errors='coerce').fillna(0)

# # Clean and convert the `year` column
# fc_gdf = fc_gdf[fc_gdf['fc_year'].notna()]  # Drop rows where year is NaN
# fc_gdf['fc_year'] = fc_gdf['fc_year'].astype(float).round().astype(int) 

# page1 = ui.page_sidebar(
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
#     ),
#     ui.layout_column_wrap(
#         ui.card(
#             ui.card_header("Top 10 Neighborhoods with Greatest Differences"),
#             ui.output_table("av_top_diff_table"),
#             width="100px",
#             height="150px",
#             style="font-size: 12px;",
#         ),
#         ui.card(
#             ui.card_header("Assessed Value by Neighborhood"),
#             sw.output_widget("av_reactive_plot"),
#             width="100px",
#             height="150px",
#         ),
#         ui.card(
#             ui.card_header("Map for Selected Year"),
#             sw.output_widget("av_choropleth_map"),
#             width="200px",
#             height="100px",
#         )
#     )
# )

# # Define page 2 UI with unique input IDs
# page2 = ui.page_sidebar(
#     ui.sidebar(
#         ui.input_select(
#             id="year_select_1_page2",  # Unique ID for page 2
#             label="Select Year 1:",
#             choices=[str(year) for year in sorted(fc_gdf["fc_year"].unique())],
#             selected=str(fc_gdf["fc_year"].min()),
#         ),
#         ui.input_select(
#             id="year_select_2_page2",  # Unique ID for page 2
#             label="Select Year 2:",
#             choices=[str(year) for year in sorted(fc_gdf["fc_year"].unique())],
#             selected=str(fc_gdf["fc_year"].max()),
#         ),
#         ui.input_select(
#             id="pri_neigh_page2",  # Unique ID for page 2
#             label="Neighborhood:",
#             choices=sorted(fc_gdf['fc_pri_neigh'].unique().tolist())
#         ),
#         ui.input_select(
#             id="choropleth_year_page2",  # Unique ID for page 2
#             label="Select Year for Map:",
#             choices=[str(year) for year in sorted(fc_gdf["fc_year"].unique())],
#             selected=str(fc_gdf["fc_year"].max()),
#         ),
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

# # Define the app UI with navigation
# app_ui = ui.page_navbar(
#     ui.nav_spacer(),  # Optional: for better navbar alignment
#     ui.nav_panel("Assessed Value", page1),
#     ui.nav_panel("Foreclosure", page2),
#     title="Property as an Indicator for Gentrification",  # Update this if needed
# )


# # Server logic for Page 1
# def server(input, output, session):
#     # Reactive calculation for filtering neighborhood data (Page 1)
#     @reactive.calc
#     def av_filter_neighborhood_data():
#         av_selected_neighborhood = input.pri_neigh()  # Use updated ID for Page 1
#         av_filtered_data = merged_gdf[merged_gdf['pri_neigh'] == av_selected_neighborhood]
#         if av_filtered_data.empty:
#             return pd.DataFrame({'year': [], 'certified_tot_mean': []})
#         return av_filtered_data.groupby('year', as_index=False)['certified_tot_mean'].mean()

#     # Reactive calculation for aggregated data (Page 1)
#     @reactive.calc
#     def av_agg_full():
#         agg_merged = merged_gdf.groupby('year', as_index=False)['certified_tot_mean'].mean()
#         return agg_merged

#     # Reactive calculation for choropleth data (Page 1)
#     @reactive.calc
#     def av_choropleth_data():
#         try:
#             av_selected_year = int(input.choropleth_year())
#             av_filtered_data = merged_gdf[merged_gdf['year'] == av_selected_year]
#             if av_filtered_data.empty:
#                 return pd.DataFrame()  # Return empty dataframe for no data
#             av_filtered_data['certified_tot_mean'] = pd.to_numeric(
#                 av_filtered_data['certified_tot_mean'], errors='coerce'
#             ).fillna(0)
#             return av_filtered_data
#         except Exception as e:
#             print(f"Error in choropleth_data: {e}")
#             return pd.DataFrame()

#     # Reactive calculation for differences between years (Page 1)
#     @reactive.calc
#     def av_diff_data():
#         av_year1 = int(input.year_select_1())
#         av_year2 = int(input.year_select_2())
    
#         av_data_year1 = merged_gdf[merged_gdf["year"] == av_year1].groupby("pri_neigh")["certified_tot_mean"].mean().reset_index()
#         av_data_year1 = av_data_year1.rename(columns={"certified_tot_mean": "value_year1"})
    
#         av_data_year2 = merged_gdf[merged_gdf["year"] == av_year2].groupby("pri_neigh")["certified_tot_mean"].mean().reset_index()
#         av_data_year2 = av_data_year2.rename(columns={"certified_tot_mean": "value_year2"})
    
#         av_merged = pd.merge(av_data_year1, av_data_year2, on="pri_neigh", how="inner")
#         av_merged["difference"] = abs(av_merged["value_year2"] - av_merged["value_year1"])
#         av_merged = av_merged.sort_values(by="difference", ascending=False)
    
#         av_merged["value_year1"] = av_merged["value_year1"].round(2)
#         av_merged["value_year2"] = av_merged["value_year2"].round(2)
#         av_merged["difference"] = av_merged["difference"].round(2)
    
#         return av_merged.head(10)

#     # Output for the table showing the differences between years (Page 1)
#     @output(id="av_top_diff_table")
#     @render.table
#     def av_top_diff_table():
#         av_data = av_diff_data()
#         if av_data.empty:
#             return pd.DataFrame(columns=["Neighborhood", "Value (Year 1)", "Value (Year 2)", "Difference"])
#         return av_data.rename(
#             columns={
#                 "pri_neigh": "Neighborhood",
#                 "value_year1": f"Value ({input.year_select_1()})",
#                 "value_year2": f"Value ({input.year_select_2()})",
#                 "difference": "Difference",
#             }
#         )

#     # Output for the Altair plot (assessed value by neighborhood, Page 1)
#     @output(id="av_reactive_plot")
#     @sw.render_altair
#     def av_reactive_plot():
#         av_filtered_data = av_filter_neighborhood_data()
#         if av_filtered_data.empty:
#             return alt.Chart().mark_text().encode(
#                 text=alt.value('No Data Available')
#             ).properties(width=275, height=175)

#         av_reactive_chart = alt.Chart(av_filtered_data).mark_line().encode(
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

#         agg_merged = av_agg_full() 
#         av_static_line = alt.Chart(agg_merged).mark_line(color='lightblue', strokeDash=[5, 4]).encode(
#             x=alt.X('year:O', title='Year'),
#             y=alt.Y('certified_tot_mean:Q', title='Assessed Value', axis=alt.Axis(format='.1f')),
#         )
#         av_combined_chart = av_static_line + av_reactive_chart
#         return av_combined_chart

#     # Output for the choropleth map (Page 1)
        
#     @output(id="av_choropleth_map")
#     @sw.render_plotly
#     def av_choropleth_map():
#         av_filtered_data = av_choropleth_data()
#         if av_filtered_data.empty:
#             return ""  
#         av_fig = px.choropleth_mapbox(
#             av_filtered_data,
#             geojson=av_filtered_data.__geo_interface__,
#             locations=av_filtered_data.index,
#             color="certified_tot_mean",
#             mapbox_style="carto-positron",
#             center={"lat": 41.8781, "lon": -87.6298},
#             zoom=10,
#             title=f"Choropleth Map for Year {input.choropleth_year()}",
#             hover_name="pri_neigh",  
#             hover_data={"certified_tot_mean": True},
#             range_color=[0, 150000], 
#         )

#         av_fig.update_layout(
#             coloraxis_colorbar=dict(
#                 tickfont=dict(size=10),  
#                 title_font=dict(size=10),  
#                 thickness=10,  
#             ),
#         )

#         return av_fig


#     @reactive.calc
#     def fc_filter_neighborhood_data():
#         fc_selected_neighborhood = input.pri_neigh_page2()  
#         fc_filtered_data = fc_gdf[fc_gdf['fc_pri_neigh'] == fc_selected_neighborhood]
#         if fc_filtered_data.empty:
#             return pd.DataFrame({'fc_year': [], 'num_foreclosure_in_half_mile_past_5_years_mean': []})
#         return fc_filtered_data.groupby('fc_year', as_index=False)['num_foreclosure_in_half_mile_past_5_years_mean'].mean()

#     @reactive.calc
#     def fc_agg_full():
#         agg_fc = fc_gdf.groupby('fc_year', as_index=False)['num_foreclosure_in_half_mile_past_5_years_mean'].mean()
#         return agg_fc

#     @reactive.calc
#     def fc_choropleth_data():
#         try:
#             fc_selected_year = int(input.choropleth_year_page2())  # Use updated ID for page2
#             fc_filtered_data = fc_gdf[fc_gdf['fc_year'] == fc_selected_year]
#             if fc_filtered_data.empty:
#                 return pd.DataFrame()  
#             fc_filtered_data['num_foreclosure_in_half_mile_past_5_years_mean'] = pd.to_numeric(
#                 fc_filtered_data['num_foreclosure_in_half_mile_past_5_years_mean'], errors='coerce'
#             ).fillna(0)
#             return fc_filtered_data
#         except Exception as e:
#             print(f"Error in choropleth_data: {e}")
#             return pd.DataFrame()

#     @reactive.calc
#     def fc_diff_data():
#         fc_year1 = int(input.year_select_1_page2())  
#         fc_year2 = int(input.year_select_2_page2())  
    
#         fc_data_year1 = fc_gdf[fc_gdf["fc_year"] == fc_year1].groupby("fc_pri_neigh")[
#             "num_foreclosure_in_half_mile_past_5_years_mean"].mean().reset_index()
#         fc_data_year1 = fc_data_year1.rename(columns={"num_foreclosure_in_half_mile_past_5_years_mean": "value_year1"})
    
#         fc_data_year2 = fc_gdf[fc_gdf["fc_year"] == fc_year2].groupby("fc_pri_neigh")[
#             "num_foreclosure_in_half_mile_past_5_years_mean"].mean().reset_index()
#         fc_data_year2 = fc_data_year2.rename(columns={"num_foreclosure_in_half_mile_past_5_years_mean": "value_year2"})
    
#         fc_merged = pd.merge(fc_data_year1, fc_data_year2, on="fc_pri_neigh", how="inner")
#         fc_merged["difference"] = abs(fc_merged["value_year2"] - fc_merged["value_year1"])
#         fc_merged = fc_merged.sort_values(by="difference", ascending=False)
    
#         fc_merged["value_year1"] = fc_merged["value_year1"].round(2)
#         fc_merged["value_year2"] = fc_merged["value_year2"].round(2)
#         fc_merged["difference"] = fc_merged["difference"].round(2)
    
#         return fc_merged.head(10)

#     @output(id="fc_top_diff_table")
#     @render.table
#     def fc_top_diff_table():
#         fc_data = fc_diff_data()
#         if fc_data.empty:
#             return pd.DataFrame(columns=["Neighborhood", "Value (Year 1)", "Value (Year 2)", "Difference"])
#         return fc_data.rename(
#             columns={
#                 "fc_pri_neigh": "Neighborhood",
#                 "value_year1": f"Value ({input.year_select_1_page2()})",  
#                 "value_year2": f"Value ({input.year_select_2_page2()})",  
#                 "difference": "Difference",
#             }
#         )

#     @output(id="fc_reactive_plot")
#     @sw.render_altair
#     def fc_reactive_plot():
#         fc_filtered_data = fc_filter_neighborhood_data()
#         fc_reactive_chart = alt.Chart(fc_filtered_data).mark_line().encode(
#             x=alt.X('fc_year:O', title='Year'),
#             y=alt.Y('num_foreclosure_in_half_mile_past_5_years_mean:Q', 
#                     title='Foreclosures',
#                     axis=alt.Axis(format='.1f'),
#                     scale=alt.Scale(domain=[0, 200])),  
#             tooltip=[
#                 alt.Tooltip('fc_year:O', title='Year'),
#                 alt.Tooltip('num_foreclosure_in_half_mile_past_5_years_mean:Q', format='.2f', title='Foreclosures')
#             ],
#         ).properties(
#             title=f"Foreclosures by Year for {input.pri_neigh_page2()}",  
#             width=275,
#             height=175
#         )
#         agg_fc = fc_agg_full() 
#         fc_static_line = alt.Chart(agg_fc).mark_line(color='lightblue', strokeDash=[5, 4]).encode(
#             x=alt.X('fc_year:O', title='Year'),
#             y=alt.Y('num_foreclosure_in_half_mile_past_5_years_mean:Q', title='Foreclosures', axis=alt.Axis(format='.1f')),
#         )
#         fc_combined_chart = fc_static_line + fc_reactive_chart
#         return fc_combined_chart

#     @output(id="fc_choropleth_map")
#     @sw.render_plotly
#     def fc_choropleth_map():
#         fc_filtered_data = fc_choropleth_data()
        
#         if fc_filtered_data.empty:
#             return ""  

#     @output(id="fc_choropleth_map")
#     @sw.render_plotly
#     def fc_choropleth_map():
#         fc_filtered_data = fc_choropleth_data()
        
#         if fc_filtered_data.empty:
#             return ""  


#         fc_fig = px.choropleth_mapbox(
#             fc_filtered_data,
#             geojson=fc_filtered_data.set_geometry('fc_geometry').__geo_interface__,  
#             locations=fc_filtered_data.index,
#             color="num_foreclosure_in_half_mile_past_5_years_mean",  
#             mapbox_style="carto-positron",
#             center={"lat": 41.8781, "lon": -87.6298},
#             zoom=10,
#             title=f"Choropleth Map for Year {input.choropleth_year_page2()}",
#             hover_name="fc_pri_neigh", 
#             hover_data={"num_foreclosure_in_half_mile_past_5_years_mean": "foreclosures"},  
#             range_color=[0, fc_filtered_data["num_foreclosure_in_half_mile_past_5_years_mean"].max()],
#         )


#         fc_fig.update_layout(
#             coloraxis_colorbar=dict(
#                 title="Foreclosures",  
#                 tickfont=dict(size=10),  
#                 title_font=dict(size=10),  
#                 thickness=10,  
#             ),
#         )

#         return fc_fig


# app = App(app_ui, server)

import shiny
import pandas as pd
import altair as alt
from shiny import App, render, ui, reactive
import geopandas as gpd
import numpy as np
import shinywidgets as sw
import plotly.express as px
import plotly.graph_objects as go


from shared import app_dir, merged_gdf, fc_gdf, ps_gdf

# Preprocess data
merged_gdf['certified_tot_mean'] = pd.to_numeric(merged_gdf['certified_tot_mean'], errors='coerce').fillna(0)

fc_gdf['num_foreclosure_in_half_mile_past_5_years_mean'] = pd.to_numeric(
    fc_gdf['num_foreclosure_in_half_mile_past_5_years_mean'], errors='coerce').fillna(0)

# Clean and convert the `year` column
fc_gdf = fc_gdf[fc_gdf['fc_year'].notna()]  # Drop rows where year is NaN
fc_gdf['fc_year'] = fc_gdf['fc_year'].astype(float).round().astype(int) 

ps_gdf['sale_price_mean'] = pd.to_numeric(ps_gdf['sale_price_mean'], errors='coerce').fillna(0)
ps_gdf = ps_gdf[ps_gdf['ps_year'].notna()]
ps_gdf['ps_year'] = ps_gdf['ps_year'].astype(int)

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
page3 = ui.page_sidebar(
    ui.sidebar(
        ui.input_select(
            id="year_select_1_page3",
            label="Select Year 1:",
            choices=[str(year) for year in sorted(ps_gdf["ps_year"].unique())],
            selected=str(ps_gdf["ps_year"].min()),
        ),
        ui.input_select(
            id="year_select_2_page3",  # Make this ID unique
            label="Select Year 2:",
            choices=[str(year) for year in sorted(ps_gdf["ps_year"].unique())],
            selected=str(ps_gdf["ps_year"].max()),
        ),
        ui.input_select(
            id="pri_neigh_page3",
            label="Neighborhood:",
            choices=sorted(ps_gdf['ps_pri_neigh'].unique().tolist())
        ),
        ui.input_select(
            id="choropleth_year_page3",  # Make this ID unique
            label="Select Year for Map:",
            choices=[str(year) for year in sorted(ps_gdf["ps_year"].unique())],
            selected=str(ps_gdf["ps_year"].max()),
        ),
    ),
    ui.layout_column_wrap(
        ui.card(
            ui.card_header("Top 10 Neighborhoods with Greatest Differences"),
            ui.output_table("ps_top_diff_table"),
            width="100px",
            height="150px",
            style="font-size: 12px;",
        ),
        ui.card(
            ui.card_header("Parcel Sales by Neighborhood"),
            sw.output_widget("ps_reactive_plot"),
            width="100px",
            height="150px",
        ),
        ui.card(
            ui.card_header("Map for Selected Year"),
            sw.output_widget("ps_choropleth_map"),
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
    ui.nav_panel("Parcel Sales", page3),
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
        
    @output(id="av_choropleth_map")
    @sw.render_plotly
    def av_choropleth_map():
        av_filtered_data = av_choropleth_data()
        if av_filtered_data.empty:
            return ""  
        av_fig = px.choropleth_mapbox(
            av_filtered_data,
            geojson=av_filtered_data.__geo_interface__,
            locations=av_filtered_data.index,
            color="certified_tot_mean",
            mapbox_style="carto-positron",
            center={"lat": 41.8781, "lon": -87.6298},
            zoom=10,
            title=f"Choropleth Map for Year {input.choropleth_year()}",
            hover_name="pri_neigh",  
            hover_data={"certified_tot_mean": True},
            range_color=[0, 150000], 
        )

        av_fig.update_layout(
            coloraxis_colorbar=dict(
                tickfont=dict(size=10),  
                title_font=dict(size=10),  
                thickness=10,  
            ),
        )

        return av_fig


    @reactive.calc
    def fc_filter_neighborhood_data():
        fc_selected_neighborhood = input.pri_neigh_page2()  
        fc_filtered_data = fc_gdf[fc_gdf['fc_pri_neigh'] == fc_selected_neighborhood]
        if fc_filtered_data.empty:
            return pd.DataFrame({'fc_year': [], 'num_foreclosure_in_half_mile_past_5_years_mean': []})
        return fc_filtered_data.groupby('fc_year', as_index=False)['num_foreclosure_in_half_mile_past_5_years_mean'].mean()

    @reactive.calc
    def fc_agg_full():
        agg_fc = fc_gdf.groupby('fc_year', as_index=False)['num_foreclosure_in_half_mile_past_5_years_mean'].mean()
        return agg_fc

    @reactive.calc
    def fc_choropleth_data():
        try:
            fc_selected_year = int(input.choropleth_year_page2())  # Use updated ID for page2
            fc_filtered_data = fc_gdf[fc_gdf['fc_year'] == fc_selected_year]
            if fc_filtered_data.empty:
                return pd.DataFrame()  
            fc_filtered_data['num_foreclosure_in_half_mile_past_5_years_mean'] = pd.to_numeric(
                fc_filtered_data['num_foreclosure_in_half_mile_past_5_years_mean'], errors='coerce'
            ).fillna(0)
            return fc_filtered_data
        except Exception as e:
            print(f"Error in choropleth_data: {e}")
            return pd.DataFrame()

    @reactive.calc
    def fc_diff_data():
        fc_year1 = int(input.year_select_1_page2())  
        fc_year2 = int(input.year_select_2_page2())  
    
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

    @output(id="fc_top_diff_table")
    @render.table
    def fc_top_diff_table():
        fc_data = fc_diff_data()
        if fc_data.empty:
            return pd.DataFrame(columns=["Neighborhood", "Value (Year 1)", "Value (Year 2)", "Difference"])
        return fc_data.rename(
            columns={
                "fc_pri_neigh": "Neighborhood",
                "value_year1": f"Value ({input.year_select_1_page2()})",  
                "value_year2": f"Value ({input.year_select_2_page2()})",  
                "difference": "Difference",
            }
        )

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
            title=f"Foreclosures by Year for {input.pri_neigh_page2()}",  
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

    @output(id="fc_choropleth_map")
    @sw.render_plotly
    def fc_choropleth_map():
        fc_filtered_data = fc_choropleth_data()
        
        if fc_filtered_data.empty:
            return ""  

    @output(id="fc_choropleth_map")
    @sw.render_plotly
    def fc_choropleth_map():
        fc_filtered_data = fc_choropleth_data()
        
        if fc_filtered_data.empty:
            return ""  


        fc_fig = px.choropleth_mapbox(
            fc_filtered_data,
            geojson=fc_filtered_data.set_geometry('fc_geometry').__geo_interface__,  
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
                title="Foreclosures",  
                tickfont=dict(size=10),  
                title_font=dict(size=10),  
                thickness=10,  
            ),
        )

        return fc_fig
    
    
    @reactive.calc
    def ps_filter_neighborhood_data():
        ps_selected_neighborhood = input.pri_neigh_page3()  
        ps_filtered_data = ps_gdf[ps_gdf['ps_pri_neigh'] == ps_selected_neighborhood]
        if ps_filtered_data.empty:
            return pd.DataFrame({'ps_year': [], 'sale_price_mean': []})
        return ps_filtered_data.groupby('ps_year', as_index=False)['sale_price_mean'].mean()

    @reactive.calc
    def ps_agg_full():
        agg_ps = ps_gdf.groupby('ps_year', as_index=False)['sale_price_mean'].mean()
        return agg_ps

    @reactive.calc
    def ps_choropleth_data():
        try:
            ps_selected_year = int(input.choropleth_year_page3())  # Use updated ID for page2
            ps_filtered_data = ps_gdf[ps_gdf['ps_year'] == ps_selected_year]
            if ps_filtered_data.empty:
                return pd.DataFrame()  
            ps_filtered_data['sale_price_mean'] = pd.to_numeric(
                ps_filtered_data['sale_price_mean'], errors='coerce'
            ).fillna(0)
            return ps_filtered_data
        except Exception as e:
            print(f"Error in choropleth_data: {e}")
            return pd.DataFrame()  

    @reactive.calc
    def ps_diff_data():
        ps_year1 = int(input.year_select_1_page3())  # Updated ID
        ps_year2 = int(input.year_select_2_page3())  # Updated ID 
    
        ps_data_year1 = ps_gdf[ps_gdf["ps_year"] == ps_year1].groupby("ps_pri_neigh")["sale_price_mean"].mean().reset_index()
        ps_data_year1 = ps_data_year1.rename(columns={"sale_price_mean": "value_year1"})

        ps_data_year2 = ps_gdf[ps_gdf["ps_year"] == ps_year2].groupby("ps_pri_neigh")["sale_price_mean"].mean().reset_index()
        ps_data_year2 = ps_data_year2.rename(columns={"sale_price_mean": "value_year2"})

        ps_merged = pd.merge(ps_data_year1, ps_data_year2, on="ps_pri_neigh", how="inner")
        ps_merged["difference"] = abs(ps_merged["value_year2"] - ps_merged["value_year1"])
        ps_merged = ps_merged.sort_values(by="difference", ascending=False)
    
        ps_merged["value_year1"] = ps_merged["value_year1"].round(2)
        ps_merged["value_year2"] = ps_merged["value_year2"].round(2)
        ps_merged["difference"] = ps_merged["difference"].round(2)
    
        return ps_merged.head(10)

    @output(id="ps_top_diff_table")
    @render.table
    def ps_top_diff_table():
        ps_data = ps_diff_data()
        if ps_data.empty:
            return pd.DataFrame(columns=["Neighborhood", "Value (Year 1)", "Value (Year 2)", "Difference"])
        return ps_data.rename(
            columns={
                "ps_pri_neigh": "Neighborhood",
                "value_year1": f"Value ({input.year_select_1_page3()})",  
                "value_year2": f"Value ({input.year_select_2_page3()})",  
                "difference": "Difference",
            }
        )
    
    @output(id="ps_reactive_plot")
    @sw.render_altair
    def ps_reactive_plot():
        ps_filtered_data = ps_filter_neighborhood_data()
        if ps_filtered_data.empty:
            return alt.Chart().mark_text().encode(
                text=alt.value('No Data Available')
            ).properties(width=275, height=175)

        ps_reactive_chart = alt.Chart(ps_filtered_data).mark_line().encode(
            x=alt.X('ps_year:O', title='Year'),
            y=alt.Y('sale_price_mean:Q', 
                    title='Parcel Sales',
                    axis=alt.Axis(format='.1f'),
                    scale=alt.Scale(domain=[0, 2000000])),  
            tooltip=[
                alt.Tooltip('ps_year:O', title='Year'),
                alt.Tooltip('sale_price_mean:Q', format='.2f', title='Sales Price')
            ],
        ).properties(
            title=f"Parcel Sales by Year for {input.pri_neigh_page3()}",
            width=275,
            height=175
        )

        agg_merged = ps_agg_full() 
        ps_static_line = alt.Chart(agg_merged).mark_line(color='lightblue', strokeDash=[5, 4]).encode(
            x=alt.X('ps_year:O', title='Year'),
            y=alt.Y('sale_price_mean:Q', title='Sales Price', axis=alt.Axis(format='.1f')),
        )
        ps_combined_chart = ps_static_line + ps_reactive_chart
        return ps_combined_chart


    @output(id="ps_choropleth_map")
    @sw.render_plotly
    def ps_choropleth_map():
        ps_filtered_data = ps_choropleth_data()
        
        if ps_filtered_data.empty:
            return ""  

    @output(id="ps_choropleth_map")
    @sw.render_plotly
    def ps_choropleth_map():
        ps_filtered_data = ps_choropleth_data()
        
        if ps_filtered_data.empty:
            return ""  


        ps_fig = px.choropleth_mapbox(
            ps_filtered_data,
            geojson=ps_filtered_data.set_geometry('ps_geometry').__geo_interface__,  
            locations=ps_filtered_data.index,
            color="sale_price_mean",  
            mapbox_style="carto-positron",
            center={"lat": 41.8781, "lon": -87.6298},
            zoom=10,
            title=f"Choropleth Map for Year {input.choropleth_year_page2()}",
            hover_name="ps_pri_neigh", 
            hover_data={"sale_price_mean": True},  
            range_color=[0, ps_filtered_data["sale_price_mean"].max()],
            color_continuous_scale=px.colors.sequential.Plasma
        )


        ps_fig.update_layout(
            coloraxis_colorbar=dict(
                title="Sales Price",  
                tickfont=dict(size=10),  
                title_font=dict(size=10),  
                thickness=10,  
            ),
        )

        return ps_fig
    

# Create the Shiny app
app = App(app_ui, server)



"""End of FC and AS tabs"""



