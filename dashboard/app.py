import shiny
import pandas as pd 
import altair as alt
from shiny import App, render, ui, reactive
import geopandas as gpd
import numpy as np
import shinywidgets as sw
from shinywidgets import render_altair, output_widget
import matplotlib.pyplot as plt

import tempfile


from shared import app_dir, merged_gdf

app_ui = ui.page_sidebar(
    ui.sidebar(
        ui.input_select(
            id='pri_neigh',
            label='Neighborhood:',
            choices=sorted(merged_gdf['pri_neigh'].unique().tolist())
        ),
        ui.input_select(
            id='year_select',
            label='Year:',
            choices=[str(year) for year in sorted(merged_gdf['year'].unique())],
            selected=str(merged_gdf['year'].max())  
        ),
        ui.output_text('selected_neighborhood')
    ),
    ui.layout_column_wrap(
        ui.card(
            ui.card_header("Average Assessed Value by Year"),
            sw.output_widget('static_plot'),
            width="100px", 
            height="150px"   
        ),
        ui.card(
            ui.card_header("Assessed Value by Neighborhood"),
            sw.output_widget('reactive_plot'),
            width="100px", 
            height="150px",   
        ),
        ui.card(
            ui.card_header("Map for Selected Year"),
            ui.output_image('choropleth_map'),
            width="200px", 
            height="100px",  
        )
    )
)

def server(input, output, session):

    @reactive.calc
    def agg_full():
        agg_merged = merged_gdf.groupby('year', as_index=False)['certified_tot_mean'].mean()
        return agg_merged

    @reactive.calc
    def filter_neighborhood_data():
        selected_neighborhood = input.pri_neigh()
        filtered_data = merged_gdf[merged_gdf['pri_neigh'] == selected_neighborhood]
        agg_filtered = filtered_data.groupby('year', as_index=False)['certified_tot_mean'].mean()
        return agg_filtered

    @reactive.calc
    def choropleth_data():
        selected_year = int(input.year_select())
        filtered_data = merged_gdf[merged_gdf['year'] == selected_year]
        filtered_data['certified_tot_mean'] = pd.to_numeric(filtered_data['certified_tot_mean'], errors='coerce')
        return filtered_data

    @output(id="static_plot")
    @sw.render_altair
    def _():
        agg_merged = agg_full() 
        static_chart = alt.Chart(agg_merged).mark_line().encode(
            x=alt.X('year:O', title='Year'),
            y=alt.Y('certified_tot_mean:Q',
                    title='Assessed Value (Thousands)',
                    axis=alt.Axis(format='.1f')),
            tooltip=[alt.Tooltip('year:O', title='Year'),
                     alt.Tooltip('certified_tot_mean:Q', format='.2f', title='Certified Total')],
        ).properties(
            title="Assessed Value Average by Year",
            width=300,
            height=150
        )
        return static_chart

    @output(id="reactive_plot")
    @sw.render_altair
    def _():
        filtered_data = filter_neighborhood_data()  

        reactive_chart = alt.Chart(filtered_data).mark_line().encode(
            x=alt.X('year:O', title='Year'),
            y=alt.Y('certified_tot_mean:Q', 
                    title='Assessed Value (Thousands)',
                    axis=alt.Axis(format='.1f'),
                    scale=alt.Scale(domain=[0, 700])),  
            tooltip=[
                alt.Tooltip('year:O', title='Year'),
                alt.Tooltip('certified_tot_mean:Q', format='.2f', title='Certified Total')
            ],
        ).properties(
            title=f"Assessed Value by Year for {input.pri_neigh()}",
            width=300,
            height=200
        )


        agg_merged = agg_full() 
        static_line = alt.Chart(agg_merged).mark_line(color='lightblue', strokeDash=[5, 4]).encode(
            x=alt.X('year:O', title='Year'),
            y=alt.Y('certified_tot_mean:Q', title='Assessed Value (Thousands)', axis=alt.Axis(format='.1f')),
        )
        combined_chart = static_line + reactive_chart 

        return combined_chart



    @output(id="choropleth_map")
    @render.image
    def _():
        filtered_data = choropleth_data()  

        vmin, vmax = 0, 700  

        fig, ax = plt.subplots(figsize=(6, 4))

        filtered_data.plot(column='certified_tot_mean', ax=ax, legend=False,
                           cmap='Blues', edgecolor='lightgray', linewidth=0.5,
                           vmin=vmin, vmax=vmax,  
                           )

        cbar = ax.get_figure().colorbar(ax.collections[0], ax=ax, orientation='vertical', shrink=0.6)
        cbar.ax.tick_params(labelsize=6)  
        cbar.set_label("Assessed Value Total (Thousands)", fontsize=8)  
        ax.set_title(f"Assessed Value for Year {int(input.year_select())}")
        ax.set_xticks([])  
        ax.set_yticks([])  

        with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as tmpfile:
            image_path = tmpfile.name
            fig.savefig(image_path, bbox_inches='tight')  
            plt.close(fig)

        return {"src": image_path}

    @output(id="selected_neighborhood")
    @render.text
    def _():
        return ""

app = App(app_ui, server)