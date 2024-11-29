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

agg_merged = merged_gdf.groupby('year', as_index=False)['certified_tot_mean'].mean()
agg_merged['certified_tot_mean_millions'] = agg_merged['certified_tot_mean']

static_chart = alt.Chart(agg_merged).mark_line().encode(
    x=alt.X('year:O', title='Year'),
    y=alt.Y('certified_tot_mean_millions:Q',
            title='Assessed Value (in millions)',
            axis=alt.Axis(format='.1f')),
    tooltip=[alt.Tooltip('year:O', title='Year'),
             alt.Tooltip('certified_tot_mean_millions:Q', format='.2f', title='Certified Total')],
).properties(
    title="Assessed Value Average by Year",
    width=400,
    height=200
)

app_ui = ui.page_sidebar(
    ui.sidebar(
        ui.input_select(
            id='pri_neigh',
            label='Neighborhood:',
            choices=merged_gdf['pri_neigh'].unique().tolist()
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
            sw.output_widget('static_plot')  
        ),
        ui.card(
            ui.card_header("Assessed Value by Neighborhood"),
            sw.output_widget('reactive_plot')  
        ),
        ui.card(
            ui.card_header("Map for Selected Year"),
            ui.output_image('choropleth_map')  
        )
    )
)

def server(input, output, session):

    @output(id="static_plot")
    @sw.render_altair
    def _():
        return static_chart

    @reactive.event(input.pri_neigh)
    def filter_data():
        selected_neighborhood = input.pri_neigh()
        filtered_data = merged_gdf[merged_gdf['pri_neigh'] == selected_neighborhood]
        agg_filtered = filtered_data.groupby('year', as_index=False)['certified_tot_mean'].mean()
        agg_filtered['certified_tot_mean_millions'] = agg_filtered['certified_tot_mean']
        return agg_filtered

    @output(id="reactive_plot")
    @sw.render_altair
    def _():
        filtered_data = filter_data()
        reactive_chart = alt.Chart(filtered_data).mark_line().encode(
            x=alt.X('year:O', title='Year'),
            y=alt.Y('certified_tot_mean_millions:Q', title='Certified Total (in millions)', axis=alt.Axis(format='.1f')),
            tooltip=[alt.Tooltip('year:O', title='Year'),
                     alt.Tooltip('certified_tot_mean_millions:Q', format='.2f', title='Certified Total')],
        ).properties(
            title=f"Assessed Value by Year for {input.pri_neigh()}",
            width=400,
            height=200
        )
        return reactive_chart

    @output(id="choropleth_map")
    @render.image
    def _():
        selected_year = int(input.year_select())
        filtered_data = merged_gdf[merged_gdf['year'] == selected_year]
        
        filtered_data['certified_tot_mean'] = pd.to_numeric(filtered_data['certified_tot_mean'], errors='coerce')

        fig, ax = plt.subplots(figsize=(6, 4))

        filtered_data.plot(column='certified_tot_mean', ax=ax, legend=True,
                           cmap='Blues', edgecolor='lightgray', linewidth=0.5,
                           legend_kwds={'label': "Assessed Value Total by Neighborhood", 'orientation': "horizontal"})
        
        ax.set_title(f"Assessed Value for Year {selected_year}")
        ax.set_xticks([])  
        ax.set_yticks([])  
        
        with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as tmpfile:
            image_path = tmpfile.name
            fig.savefig(image_path)
            plt.close(fig)  
        
        return {"src": image_path}

    @output(id="selected_neighborhood")
    @render.text
    def _():
        return ""

app = App(app_ui, server)