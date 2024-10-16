#importing libraries
import pandas as pd
import streamlit as st 
import plotly.express as px 
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import altair as alt

#________________________________________________________
#SETTING PAGE CONFIGURATIONS
st.set_page_config(
    page_title="Global military spending dashboard: 2014-2023",
    page_icon=":chart_with_upwards_trend:",
    layout="wide",
    initial_sidebar_state="expanded")

st.title('Global military spending dashboard: 2014-2023 ')
st.markdown('<style>div.block-container{padding-top:5rem;}<style>', unsafe_allow_html=True)
alt.themes.enable("dark")

with st.expander('About', expanded=False):
        st.write('''
            - Welcome to the Global Military Data web app dashboard, where the analysis of the data is of 140 countries spanning the years 2014 to 2023. The dynamic visualizations include a choropleth map, bar charts, a bar and line combo chart, a sunburst chart, a treemap, and a summary table. Dive in and gain insights into countries’ military capabilities worldwide!
            - Data was sourced from: [Stockholm International Peace Research Institute (SIPRI) database](https://www.sipri.org/databases/milex).
            - Vist my website for great data science projects - Happy Analyzing Data Warriors: [Data Warrior Analytics](https://nigelgondo.github.io/NigelGondoDataAnalyst.github.io/).
            ''')
        
        st.image("https://nigelgondo.github.io/NigelGondoDataAnalyst.github.io/images/dwa%20logo.png")

#___________________________________________________________
#LOADING DATAFRAME
df = pd.read_csv('Military data.csv')

#adjusting format of certain columns
df['Military expenditure (Current USD - millions)'] =\
df['Military expenditure (Current USD - $ millions)'].map('${:,.2f}'.format)

df['Real percent change in military spending']=\
(df['Percentage change in military expenditure']/100).apply('{:.2%}'.format)

df['Military expenditure as a porportion of GDP']=\
df['Military expenditure as a share of GDP'].apply('{:.2%}'.format)

df['Military expendenture as a proportion of government spending']=\
df['Military expendenture as a share of government spending'].apply('{:.2%}'.format)

df['Armed forces personnel']=\
df['Total of armed forces personnel'].map('{:,.0f}'.format)

df['Armed forces personnel as a proportion of total labour force']=\
df['Armed forces personnel (% of total labour force)'].apply('{:.2%}'.format)

#_________________________________________________________________
#CREATING SIDE BAR
#setting up side bar with filters of year, country and colour palette
with st.sidebar:
    st.header('FILTERS')

    #year filter
    year_list = list(df['Year'].unique())
    year_selected = st.selectbox('Choose year', year_list)
    df_year_selected = df[df['Year'] == year_selected]

    #country filter
    country_list = sorted(list(df['Country'].unique()))
    country_selected = st.selectbox('Choose country', country_list)
    df_country_selected = df[df['Country'] == country_selected]
    
    #color palette filter
    color_palette_list = ['cividis', 'inferno', 'magma', 'plasma', 'rainbow', 'turbo', 'viridis']
    selected_palette = st.selectbox('Choose color palette', color_palette_list)

#____________________________________________________________________
#CREATING FUNCTIONS FOR SO AS TO HAVE CLEANER CODE WHEN CREATING DASHBOARD
#function for choropleth map
def choropleth_map():
    choropleth_map = px.choropleth(df, 
                                   locations='GMI_CNTRY', 
                                   locationmode='ISO-3',
                                   color='Military expenditure (Current USD - $ millions)',
                                   hover_name='Country', 
                                   hover_data=['Military expenditure (Current USD - $ millions)',
                                               'Real percent change in military spending',
                                               'Military expenditure as a porportion of GDP',
                                               'Military expendenture as a proportion of government spending',
                                               'Armed forces personnel as a proportion of total labour force',
                                               'Armed forces personnel'],
                                   color_continuous_scale=selected_palette)
        
    choropleth_map.update_layout(template='plotly_dark', 
                                 dragmode=False,
                                 plot_bgcolor='rgba(0, 0, 0, 0)',
                                 paper_bgcolor='rgba(0, 0, 0, 0)',
                                 margin=dict(l=0, r=0, t=0, b=0))

    choropleth_map.update_coloraxes(showscale=False)
    
    return choropleth_map

#function for barcharts
def barcharts():
    barplot = make_subplots(rows=1, cols=3,shared_yaxes=True, horizontal_spacing=0.15)

    barplot.add_trace(go.Bar(x=df_country_selected['Percentage change in military expenditure'],
                             y=df_country_selected['Year'],
                             text=df_country_selected['Percentage change in military expenditure'], 
                             texttemplate='%%{text:.3s}', 
                             textposition='auto',
                             orientation='h',
                             name='% change in military spending'), 
                      row=1, col=1)

    barplot.add_trace(go.Bar(x=df_country_selected['Military expenditure as a share of GDP'], 
                             y=df_country_selected['Year'], 
                             text=df_country_selected['Military expenditure as a share of GDP'], 
                             texttemplate='%%{text:.3s}', 
                             textposition='auto',
                             orientation='h',
                             name='Military spending as a proportion of GDP'),
                      row=1, col=2)

    barplot.add_trace(go.Bar(x=df_country_selected['Military expendenture as a share of government spending'],
                             y=df_country_selected['Year'], 
                             text=df_country_selected['Military expendenture as a share of government spending'], 
                             texttemplate='%%{text:.3s}', 
                             textposition='auto',
                             orientation='h', 
                             name='Military spending as a proportion of government spending'),
                      row=1, col=3)

    barplot.update_layout(margin_pad=20,template='plotly_dark',
                          yaxis=dict(tickmode='linear',
                                     tick0=0,
                                     dtick=0),
                          legend=dict(orientation = "h",
                                      yanchor="bottom",
                                      y=-.50,
                                      xanchor="right",
                                      x=1))    
     
    barplot.update_xaxes(showgrid=False)
    
    barplot.update_yaxes(secondary_y=False, 
                         showgrid=False,
                         autorange="reversed") 
    
    return barplot

#function for sunburst plot
#creating dataframe that filters for the year 2023 and aggregate data by continent
df_sunburst=\
df[df['Year']==year_selected]\
.groupby(['Continent', 'Sub-Continent'])\
.agg({'Military expenditure (Current USD - $ millions)':'sum'})\
.sort_values(by='Military expenditure (Current USD - $ millions)',
             ascending=False)\
.reset_index()

#creating a new column that calculates percentage of total
df_sunburst['Percentage of total']= \
df_sunburst['Military expenditure (Current USD - $ millions)']\
.apply(lambda x: (x / df_sunburst['Military expenditure (Current USD - $ millions)']\
                  .sum()) * 100).round(2)

df_sunburst['% of total'] =\
    df_sunburst['Percentage of total'].apply('{:.2%}'.format)

def sunburst_plot():
    sunburst = px.sunburst(df_sunburst, 
                           path=['Continent', 'Sub-Continent'], 
                           values='Percentage of total', 
                           color='Percentage of total',
                           color_continuous_scale=selected_palette)
    
    sunburst.update_coloraxes(showscale=False)
    
    sunburst.update_layout(height=400)
    
    sunburst.data[0].textinfo='label+text+value'
    
    
    return sunburst

#function for combo chart - bar and line chart
def combo_chart():
    combo_fig = make_subplots(specs=[[{'secondary_y':True}]])

    combo_fig.add_trace(go.Scatter(x=df_country_selected['Year'], 
                                   y=df_country_selected['Percentage change in military expenditure'], 
                                   name='Real percent change in military spending',
                                   mode='lines+markers+text',
                                   text=df_country_selected['Percentage change in military expenditure']/100,
                                   texttemplate='%{text:,.2%}'),
                        secondary_y=True)

    combo_fig.add_trace(go.Bar(x=df_country_selected['Year'], 
                               y=df_country_selected['Military expenditure (Current USD - $ millions)'], 
                               name='Military spending (Current USD)', 
                               text=df_country_selected['Military expenditure (Current USD - $ millions)'],
                               texttemplate='%{text:$,.2f}',
                               textposition='outside'),
                        secondary_y=False)

    combo_fig.update_layout(template='plotly_dark', 
                            xaxis=dict(tickmode='linear',
                                       tick0=0,
                                       dtick=0),
                            legend=dict(orientation = "h",
                                        yanchor="bottom",
                                        y=-.50,
                                        xanchor="right",
                                        x=1))    

    combo_fig.update_xaxes(title_text='Year', 
                           showgrid=False)

    combo_fig.update_yaxes(title_text='Military spending (Current USD)',
                           secondary_y=False, 
                           showgrid=False)

    combo_fig.update_yaxes(title_text='Real percentage change in military spending', 
                           secondary_y=True, 
                           showgrid=False)
    
    return combo_fig

#function for treemap
def tree_map():
    df_tree_map = df_year_selected.sort_values(by='Total of armed forces personnel',
                                               ascending=False).iloc[:10]
    
    treemap = px.treemap(df_tree_map, 
                         path=['Continent','Country'], 
                         hover_data=['Armed forces personnel as a proportion of total labour force'],
                         values='Total of armed forces personnel', 
                         color='Total of armed forces personnel',
                         color_continuous_scale=selected_palette)
    
    treemap.data[0].textinfo='label+text+value'
    
    treemap.update_layout(showlegend=False)
    
    treemap.update_coloraxes(showscale=False)
    
    return treemap

#_______________________________________________________________________
#CREATING DASHBOARD ELEMENTS
#inserting choropleth map
st.markdown('##### Choropleth map: Global military spending ' + '' + str(year_selected), 
            unsafe_allow_html=True)
st.plotly_chart(choropleth_map(), use_container_width=True)

#creating columns
col = st.columns((2.5,1),gap='large')

#first column elements
with col[0]:
    #plotting bar chart subplots
     st.markdown('##### '+ ' ' +str(country_selected) +': Trends of military data between 2014 and 2023')
     st.plotly_chart(barcharts())
     
     #plotting combo chart - bar and line 
     st.markdown('##### ' + ' ' +str(country_selected) + ': Trends in military spending and real* percentage change in spending (2014-2023)')
     st.plotly_chart(combo_chart())

#second column elements
with col[1]:
    #plotting sunburst chart
    st.markdown('##### Percentage share of global military spend by continent and sub-continent' + ' ' + str(year_selected))
    st.plotly_chart(sunburst_plot(), use_container_width=True)
    
    #plotting treemap
    st.markdown('##### Top 10 countries with the most armed forces personnel' + ' ' + str(year_selected))
    st.plotly_chart(tree_map(), use_container_width=True)
    
#__________________________________________________   
#CREATING A SUMMARY DATAFRAME FOR MILITARY DATA
df_summary_table = df_country_selected[['Year',
                                        'Country',
                                        'Military expenditure (Current USD - $ millions)',
                                        'Percentage change in military expenditure',
                                        'Military expenditure per capita',
                                        'Military expenditure as a share of GDP',
                                        'Military expendenture as a share of government spending',
                                        'Total of armed forces personnel',
                                        'Armed forces personnel (% of total labour force)']]

st.markdown('##### Summary table for military data')
st.dataframe(df_summary_table, 
             column_config={'Year':st.column_config.NumberColumn('Year',
                                                                   format="%.0f"),
                            'Military expenditure (Current USD - $ millions)':st.column_config.ProgressColumn('Military spending (Current USD - millions)', 
                                                                                                              format="$%.2f",
                                                                                                              min_value=0, 
                                                                                                              max_value=max(df_summary_table['Military expenditure (Current USD - $ millions)'])), 
                            'Percentage change in military expenditure':st.column_config.ProgressColumn('% change in military spend', 
                                                                                                              format="%%%.2f",
                                                                                                              min_value=0, 
                                                                                                              max_value=max(df_summary_table['Percentage change in military expenditure'])), 
                            'Military expenditure per capita':st.column_config.ProgressColumn('Military spending per capita', 
                                                                                                              format="%.2f",
                                                                                                              min_value=0, 
                                                                                                              max_value=max(df_summary_table['Military expenditure per capita'])), 
                            'Military expenditure as a share of GDP':st.column_config.ProgressColumn('Military spending as a share of GDP', 
                                                                                                              format="%%%.2f",
                                                                                                              min_value=0, 
                                                                                                              max_value=max(df_summary_table['Military expendenture as a share of government spending'])) , 
                            'Military expendenture as a share of government spending':st.column_config.ProgressColumn('Military spending as a share of government spending', 
                                                                                                              format="%%%.2f",
                                                                                                              min_value=0, 
                                                                                                              max_value=max(df_summary_table['Military expendenture as a share of government spending'])), 
                            'Total of armed forces personnel':st.column_config.ProgressColumn('Total of armed forces personnel', 
                                                                                                              format="%.0f",
                                                                                                              min_value=0, 
                                                                                                              max_value=max(df_summary_table['Total of armed forces personnel'])), 
                            'Armed forces personnel (% of total labour force)':st.column_config.ProgressColumn('Armed forces personnel (% of total labour force)', 
                                                                                                              format="%%%.2f",
                                                                                                              min_value=0,
                                                                                                              max_value=max(df_summary_table['Total of armed forces personnel']))},
             hide_index=True)
