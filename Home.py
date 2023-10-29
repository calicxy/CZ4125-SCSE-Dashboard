import streamlit as st
import streamlit.components.v1 as components
# from streamlit_option_menu import option_menu
# from streamlit_extras.app_logo import add_logo
from streamlit_extras.tags import tagger_component
from st_aggrid import GridOptionsBuilder, AgGrid, JsCode #GridUpdateMode, DataReturnMode
import altair as alt
import pandas as pd
import ast
from functions import *

home_folder = './'

df = pd.read_csv(home_folder+'data/general.csv', index_col=0)
df = df.sort_values("Name")

# App title and logo
st.set_page_config(page_title="Dashboard of SCSE Faculty",layout="wide")
# st.markdown("##")

# Search Bar and version input
#TODO some of the user input text is not being properly shown in the searchbox
selected_prof = st.selectbox('Select a Professor:',
                    tuple(df["Name"]),
                    index=None,
                    placeholder="Choose a professor"
                    )

# Can show all the features of the distribution
if selected_prof == None:
    st.write("No prof")
    # overview of the entire SCSE faculty
else: 
    prof_data = df[df["Name"]==selected_prof]
    prof_data = prof_data.iloc[0]
    # st.sidebar.image(prof_data["Picture"])
    # with st.expander(selected_prof):
    #     # fields include: email, ORCID (?), personal website(?), research interest keywords, total num of citations
    #     st.write('You selected:', selected_prof)
    keywords_list = set(prof_data["Keywords"].split(", "))
    interest_list = set(ast.literal_eval(prof_data["Research Interest"]))
    combined_set = keywords_list.union(interest_list) 
    affiliation_list = ast.literal_eval(prof_data["Affiliation"])
    c0 = st.container()
    c01 = c0.container()
    col011, col012 = c01.columns([0.2, 0.8])
    col011.image(prof_data["Picture"])
    col012.header("Professor {}".format(selected_prof))
    col0121, col0122 = col012.columns(2)
    col0121.metric("Total Citations", int(prof_data["Citations"]))
    col0122.metric("Average Rank of Conferences (CORE2023)", prof_data["Overall Rank"])

    c02 = c0.container()
    c02.write(prof_data["Biography"])
    if len(affiliation_list) > 0:
        c02.write("**Affiliations**")
        for affiliation in affiliation_list:
            c02.markdown("- {}".format(affiliation))
    with c02:
        tagger_component("Research Interests", list(combined_set))
        
    # read the professor's csv or json file
    # table includes: paper name, year, journal / conference
    csv_name = selected_prof.strip().replace(" ", "_")+".csv"
    prof_df = pd.read_csv(home_folder+"data/papers/"+csv_name,  index_col=0)
    # prof_df["Year"] = prof_df["Year"].map(str)
    # st.dataframe(prof_df,use_container_width=True)
    gb = GridOptionsBuilder.from_dataframe(prof_df)
    #customize gridOptions
    gb.configure_default_column(groupable=True, value=True, enableRowGroup=True, aggFunc='count', editable=False)
    comparator_jscode = JsCode("""
    function(valueA, valueB, nodeA, nodeB, isDescending) {
        const order_list = ['A*', 'A',  'B', 'C', 'Australasian B', 'Australasian C', 'National', 'Multiconference', 'Journal Published', 'Unranked'];
        const value = order_list.indexOf(valueA) - order_list.indexOf(valueB);
        return value;
    };
    """)
    gb.configure_column("Rank", sortable=True, comparator=comparator_jscode)
    # gb.configure_selection('multiple', use_checkbox=True,groupSelectsChildren=True, groupSelectsFiltered=True)
    gb.configure_grid_options(domLayout='normal')
    gridOptions = gb.build()
    with st.container():
        st.header("Table of Papers")
        grid_response = AgGrid(
            prof_df, 
            gridOptions=gridOptions,
            height=400, 
            width='100%',
            data_return_mode="FILTERED", 
            update_mode="GRID_CHANGED",
            fit_columns_on_grid_load=True,
            allow_unsafe_jscode=True, #Set it to True to allow jsfunction to be injected
            enable_enterprise_modules=False
        )
    grid_df = grid_response['data']

    # bar chart of conference, year
    #displays the chart
    chart_data = prof_df.loc[:,['Year', 'Journal Acronym', 'Rank']].assign(source='total')
    if not grid_df.empty :
        grid_data = grid_df.loc[:,['Year', 'Journal Acronym', 'Rank']].assign(source='selection')
        chart_data = pd.concat([chart_data, grid_data])

    # st.dataframe(chart_data)
    # chart_data = pd.melt(chart_data, id_vars=['source'], var_name="item", value_name="quantity")
    c1 = st.container()
    year_chart = alt.Chart(data=chart_data).mark_bar().encode(
        x=alt.X("Year:O"),
        y=alt.Y("count(Journal Acronym)", stack=False),
        color=alt.Color('source:N', scale=alt.Scale(domain=['total','selection'])),
    )
    c1.subheader("Number of Papers published each year")
    c1.altair_chart(year_chart, use_container_width=True)

    journal_chart = alt.Chart(data=chart_data).mark_bar().encode(
        x=alt.X("Journal Acronym:N"),
        y=alt.Y("count(Year)", stack=False),
        color=alt.Color('source:N', scale=alt.Scale(domain=['total','selection'])),
    )
    c1.subheader("Number of Papers published by venue")
    c1.altair_chart(journal_chart, use_container_width=True)

    rank_chart = alt.Chart(data=chart_data).mark_bar().encode(
        x=alt.X('Rank:O', sort=['A*', 'A',  'B', 'C', 'Australasian B', 'Australasian C', 'National', 'Multiconference', 'Journal Published', 'Unranked']),
        y=alt.Y("count(Journal Acronym)", stack=False),
        color=alt.Color('source:N', scale=alt.Scale(domain=['total', 'selection'])),
    )
    c1.subheader("Number of Papers published by venue rank")
    c1.altair_chart(rank_chart, use_container_width=True)
    
    # wordcloud of keywords
    c2 = st.container()
    c2.header("Analysis of keyword topics in the research")
    png_name = selected_prof.strip().replace(" ", "_")+".png"
    c2.image(home_folder+"data/wordclouds/"+png_name, width=600)

    # temporal analysis of changing interests
    topwords_table = pd.read_csv(home_folder+"data/keywords/"+csv_name,  index_col=0)
    c2.subheader("Top 3 Most Frequent Keywords each year")
    c2.dataframe(topwords_table)

    # graph network of coauthor index
    c3 = st.container()
    c3.header("Graph Network of Co-authors")
    col31, col32 = c3.columns([0.9, 0.1])
    with col31:
        html_name = selected_prof.strip().replace(" ", "_")+".html"
        HtmlFile = open(home_folder+"data/graphs/"+html_name, 'r', encoding='utf-8')
        source_code = HtmlFile.read() 
        components.html(source_code, height = 900,width=900)
    ## legend for the button
    with col32:
        st.write("Legend:")
        st.markdown("<span style='background-color:rgb(221, 75, 57)'>From SCSE</span>", unsafe_allow_html=True)
        st.markdown("<span style='background-color:rgb(141, 206, 235)'>Not from SCSE</span>", unsafe_allow_html=True)

