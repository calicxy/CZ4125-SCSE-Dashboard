import pandas as pd
import numpy as np
import spacy

def score_to_rank(mean_score):
    if mean_score >= 4.5:
        return(4)
    elif mean_score > 3.5:
        return(3)
    elif mean_score > 2.5:
        return(2)
    elif mean_score > 1.5:
        return(1)
    else:
        return(0)


def count_words(df):
    word_count = {}

    for i in range(len(df)):
        title = df.iloc[i]["Title"]
        # print(title)

        nlp = spacy.load('en_core_web_sm')
        doc = nlp(title)
        for noun_chunk in doc.noun_chunks:
            keyword = noun_chunk.text.lower()
            if keyword in word_count.keys():
                word_count[keyword] += 1
            else:
                word_count[keyword] = 1    
    return pd.Series(word_count)

def generate_topwords_table(df):
    table={}

    wc = count_words(df)
    wc = wc[wc>1]
    top3 = wc.sort_values(ascending=False)[:3].index.tolist()
    top3 = top3+[np.nan]*(3-len(top3))
    table["Overall"] = top3

    for year in list(df["Year"].unique()):
        sub_df = df[df["Year"]==year]
        wc = count_words(sub_df)
        wc = wc[wc>1]
        top3 = wc.sort_values(ascending=False)[:3].index.tolist()
        if len(top3) < 3:
            top3 = top3+[np.nan]*(3-len(top3))
        table[year] = top3
    
    return pd.DataFrame(table)