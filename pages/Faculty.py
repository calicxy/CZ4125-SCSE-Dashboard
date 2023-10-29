import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import altair as alt
# import matplotlib.pyplot as plt

overall_df = pd.read_csv('streamlit_dashboard/data/overall_info_df.csv', index_col=0)
general_df = pd.read_csv('streamlit_dashboard/data/general.csv', index_col=0, dtype={"Citations": 'Int64'})
order_list = ['A*', 'A',  'B', 'C', '--']
general_df["Overall Rank"] = pd.Categorical(general_df["Overall Rank"], categories=order_list, ordered=True)

c0 = st.container()
c0.header("Overview of the SCSE Faculty")

# leaderboards
top_ranks = general_df[general_df['Overall Rank'] == 'A*'][['Name' ,'Overall Rank']].reset_index(drop=True).rename(columns={'Name':'Professor'})
top10_citations = general_df[['Name' ,'Citations']].sort_values('Citations', ascending=False).head(10).reset_index(drop=True).rename(columns={'Name':'Professor'})
# top10_ranks = general_df[['Name' ,'Overall Rank']].sort_values('Overall Rank', ascending=True).head(10)
top10_papernum = overall_df.groupby("Professor").size().sort_values(ascending=False).reset_index(name='Number of Papers').head(10)
c6 = st.container()
c6.header("Leaderboards")
tab60, tab61, tab62 = c6.tabs(["Top Ranked Professors", "Most Citations", "Most papers published"])
tab60.subheader("A* Ranked Professors (By Venue)")
tab60.table(top_ranks)
tab61.subheader("Top 10 Professors with the most citations")
tab61.table(top10_citations)
tab62.subheader("Top 10 Professors with the most number of papers")
tab62.table(top10_papernum)

# graph of top conferences every year / number of paper published
c1 = st.container()
chart_data = overall_df.loc[:,['Year', 'Journal Acronym', 'Rank']].assign(source='total')
# chart_data = pd.melt(chart_data, id_vars=['source'], var_name="item", value_name="quantity")
year_chart = alt.Chart(data=chart_data).mark_bar().encode(
    x=alt.X("Year:O"),
    y=alt.Y("count(Journal Acronym):N", stack=False),
    color=alt.Color('source:N', scale=alt.Scale(domain=['total'])),
)
c1.subheader("Number of Papers published each year")
c1.altair_chart(year_chart, use_container_width=True)

# there are way too many venues
# journal_chart = alt.Chart(data=chart_data).mark_bar().encode(
#     x=alt.X("Journal Acronym:N"),
#     y=alt.Y("count(Year):O", stack=False),
#     color=alt.Color('source:N', scale=alt.Scale(domain=['total'])),
# )
# c1.subheader("Chart of Papers published by venue")
# c1.altair_chart(journal_chart, use_container_width=True)

# maybe can try stacked bar chart of each venue for one rank
rank_chart = alt.Chart(data=chart_data).mark_bar().encode(
    x=alt.X('Rank:N', sort=['A*', 'A',  'B', 'C', 'Australasian B', 'Australasian C', 'National', 'Multiconference', 'Journal Published', 'Unranked']),
    y=alt.Y("count(Journal Acronym)", stack=True),
    color=alt.Color('source:N', scale=alt.Scale(domain=['total'])),
)
c1.subheader("Number of Papers published by venue rank")
c1.altair_chart(rank_chart, use_container_width=True)

# graph of top 10 contributing profs (most number of papers, highest grade, highest number of citations)
c2 = st.container()
# overall wordcloud
c3 = st.container()
c3.header("Wordcloud of keywords in research")
c3.image("streamlit_dashboard/data/overall_wordcloud.png", width=900)

# graph network of coatuhors (label SCSE vs non-SCSE profs)
# with katz centrality, and louvain community detection
# wordcloud for each community?
katz_series = pd.read_csv("streamlit_dashboard/data/katz_series.csv", index_col=0, header=0)
c4 = st.container()
c4.header("Graph analysis of SCSE Professors")
col41, col42 = c4.columns([0.7,0.3])
HtmlFile = open("streamlit_dashboard/data/overall_graph.html", 'r', encoding='utf-8')
source_code = HtmlFile.read() 
with col41:
    components.html(source_code, height=800,width=800)
col42.dataframe(katz_series, height=650)

# c5 = st.container()
# c5.subheader("Wordclouds of each community")




