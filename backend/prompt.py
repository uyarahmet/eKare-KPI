import numpy as np
import openai
import os

import sqlite3
import csv


from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler
import pandas as pd
import dataScience

# Load the CSV file
data = pd.read_csv('inSightDataCR_May2020_Koc.csv')

# Print the names of the features
#print(data.columns.tolist())

openai.api_key = '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'

def get_completion(prompt, model="gpt-3.5-turbo"):
    messages = [{"role": "user", "content": prompt}]
    response = openai.ChatCompletion.create(
        model=model,
        messages=messages,
        temperature=0, # this is the degree of randomness of the model's output
    )
    return response.choices[0].message["content"]


def correlation_heatmap(csv_file_path):
    # Read the CSV file into a DataFrame
    df = pd.read_csv('inSightDataCR_May2020_Koc.csv')

    # Select required columns
    columns_of_interest = ['Age', 'avg_depth', 'maximum_depth', 'maximum_width', 'maximum_length',
                           'perimeter', 'area', 'volume', 'granulation', 'slough', 'eschar', 'quality_index']
    df_selected = df[columns_of_interest]

    # Remove rows with missing values
    #df_clean = df_selected.dropna()
    df_clean = df_selected[~df_selected.astype(str).eq('NaN').any(1)]

    # Calculate correlations
    correlations = df_clean.corr()
    return correlations


def correlation_heatmap_querybased(query):
    # Create a connection to the SQLite database
    conn = sqlite3.connect('ekare.db')

    # Read data from the table into a DataFrame
    df = pd.read_sql_query(query, conn)

    # Select required columns
    columns_of_interest = ['Age', 'avg_depth', 'maximum_depth', 'maximum_width', 'maximum_length',
                           'perimeter', 'area', 'volume', 'granulation', 'slough', 'eschar', 'quality_index']
    df_selected = df[columns_of_interest]

    df_selected = df_selected.apply(pd.to_numeric, errors='coerce')

    # Remove rows with missing values
    df_clean = df_selected.dropna()
    # Calculate correlations
    correlations = df_clean.corr()

    correlations_str = correlations.to_string()

    return correlations_str


correlation_heatmap_querybased("SELECT * FROM data WHERE gender = 'M' AND Age > 35")

def data_summary(csv_file_path):
    data = pd.read_csv(csv_file_path)
    df_new = data[
        ['Age', 'avg_depth', 'maximum_depth', 'maximum_width', 'maximum_length', 'perimeter', 'area', 'volume',
         'granulation', 'slough', 'eschar', 'quality_index']]

    # Drop rows with 'NaN'
    df_new = df_new.dropna()

    df = pd.read_csv(csv_file_path)

    # Select required columns
    columns_of_interest = ['Age', 'avg_depth', 'maximum_depth', 'maximum_width', 'maximum_length',
                           'perimeter', 'area', 'volume', 'granulation', 'slough', 'eschar', 'quality_index']
    df_selected = df[columns_of_interest]

    # Remove rows with missing values
    #df_clean = df_selected.dropna()
    df_clean = df_selected[~df_selected.astype(str).eq('NaN').any(1)]

    summary = df_clean.describe(include='all').to_dict()

    return {"summary": summary}

def feature_statistics(csv_file_path):
    # Read the CSV file into a DataFrame
    df = pd.read_csv(csv_file_path)

    # Select the feature of interest
    feature_name = 'Age'
    feature_values = df[feature_name]

    # Calculate statistics
    mean_value = feature_values.mean()
    std_deviation = feature_values.std()

    return {"mean": mean_value, "std_deviation": std_deviation}

def principal_component_analysis():
    # Load the data
    data = pd.read_csv("inSightDataCR_May2020_Koc.csv")

    # Select required columns
    df_new = data[
        ['Age', 'avg_depth', 'maximum_depth', 'maximum_width', 'maximum_length', 'perimeter', 'area', 'volume',
         'granulation', 'slough', 'eschar', 'quality_index']]

    # Remove rows with 'NaN'
    df_new = df_new.dropna()

    # Standardize the data
    X = StandardScaler().fit_transform(df_new)

    # Apply PCA
    pca = PCA(n_components=2)
    principalComponents = pca.fit_transform(X)

    # Create a DataFrame with the principal components
    df_pca = pd.DataFrame(data = principalComponents, columns = ['principal component 1', 'principal component 2'])

    return {"principal_components": df_pca.to_dict(orient="records")}

heatmap = '{"correlations":{"Age":{"Age":1.0,"avg_depth":0.15247542489518348,"maximum_depth":0.18897412536269045,"maximum_width":0.07703792953932335,"maximum_length":-0.007804391656444424,"perimeter":0.046950432130723224,"area":0.09687882331862539,"volume":0.13729434078783734,"granulation":0.25555842252674904,"slough":-0.08825449428136478,"eschar":-0.19498357700108085,"quality_index":-0.0347187903907253},"avg_depth":{"Age":0.15247542489518348,"avg_depth":1.0,"maximum_depth":0.9135613860304808,"maximum_width":0.31164567929026726,"maximum_length":0.306880177300067,"perimeter":-0.004794880936093613,"area":0.3396601650080121,"volume":0.7066989839383987,"granulation":0.12374717183618138,"slough":0.01762708244052932,"eschar":-0.14466485848520683,"quality_index":-0.02337129565689621},"maximum_depth":{"Age":0.18897412536269045,"avg_depth":0.9135613860304808,"maximum_depth":1.0,"maximum_width":0.4739204520302308,"maximum_length":0.46017460935772075,"perimeter":-0.006438116859178466,"area":0.5131618383645727,"volume":0.7815330052805223,"granulation":0.06500985614960375,"slough":0.05802103003125802,"eschar":-0.11658624888933986,"quality_index":-0.026407226308099482},"maximum_width":{"Age":0.07703792953932335,"avg_depth":0.31164567929026726,"maximum_depth":0.4739204520302308,"maximum_width":1.0,"maximum_length":0.779511212545529,"perimeter":0.01081031287325048,"area":0.8629168418658288,"volume":0.5182655804726005,"granulation":-0.11881370848846916,"slough":0.16344576429195248,"eschar":-0.011246321507320947,"quality_index":-0.002600927210274688},"maximum_length":{"Age":-0.007804391656444424,"avg_depth":0.306880177300067,"maximum_depth":0.46017460935772075,"maximum_width":0.779511212545529,"maximum_length":1.0,"perimeter":0.003973264268493488,"area":0.8306312758678689,"volume":0.48875627831237267,"granulation":-0.16216191479060685,"slough":0.16190506744785946,"eschar":0.03555780129804428,"quality_index":-0.00346161662316014},"perimeter":{"Age":0.046950432130723224,"avg_depth":-0.004794880936093613,"maximum_depth":-0.006438116859178466,"maximum_width":0.01081031287325048,"maximum_length":0.003973264268493488,"perimeter":1.0,"area":0.003987828932182591,"volume":-0.0023590803067915825,"granulation":-0.014184846270857624,"slough":-0.009491309462247504,"eschar":0.022801570617749074,"quality_index":-0.009825768305170948},"area":{"Age":0.09687882331862539,"avg_depth":0.3396601650080121,"maximum_depth":0.5131618383645727,"maximum_width":0.8629168418658288,"maximum_length":0.8306312758678689,"perimeter":0.003987828932182591,"area":1.0,"volume":0.6999973568593254,"granulation":-0.1250864678466114,"slough":0.15275462622297856,"eschar":0.004247472483540426,"quality_index":-0.014745574072556252},"volume":{"Age":0.13729434078783734,"avg_depth":0.7066989839383987,"maximum_depth":0.7815330052805223,"maximum_width":0.5182655804726005,"maximum_length":0.48875627831237267,"perimeter":-0.0023590803067915825,"area":0.6999973568593254,"volume":1.0,"granulation":-0.005321397356918191,"slough":0.04442567565189829,"eschar":-0.03138750387314925,"quality_index":-0.022278016812635998},"granulation":{"Age":0.25555842252674904,"avg_depth":0.12374717183618138,"maximum_depth":0.06500985614960375,"maximum_width":-0.11881370848846916,"maximum_length":-0.16216191479060685,"perimeter":-0.014184846270857624,"area":-0.1250864678466114,"volume":-0.005321397356918191,"granulation":1.0,"slough":-0.4553733730449911,"eschar":-0.6714003034020896,"quality_index":-0.004944078892192758},"slough":{"Age":-0.08825449428136478,"avg_depth":0.01762708244052932,"maximum_depth":0.05802103003125802,"maximum_width":0.16344576429195248,"maximum_length":0.16190506744785946,"perimeter":-0.009491309462247504,"area":0.15275462622297856,"volume":0.04442567565189829,"granulation":-0.4553733730449911,"slough":1.0,"eschar":-0.3540589690727009,"quality_index":0.00631467003463908},"eschar":{"Age":-0.19498357700108085,"avg_depth":-0.14466485848520683,"maximum_depth":-0.11658624888933986,"maximum_width":-0.011246321507320947,"maximum_length":0.03555780129804428,"perimeter":0.022801570617749074,"area":0.004247472483540426,"volume":-0.03138750387314925,"granulation":-0.6714003034020896,"slough":-0.3540589690727009,"eschar":1.0,"quality_index":-6.248627148126249e-05},"quality_index":{"Age":-0.0347187903907253,"avg_depth":-0.02337129565689621,"maximum_depth":-0.026407226308099482,"maximum_width":-0.002600927210274688,"maximum_length":-0.00346161662316014,"perimeter":-0.009825768305170948,"area":-0.014745574072556252,"volume":-0.022278016812635998,"granulation":-0.004944078892192758,"slough":0.00631467003463908,"eschar":-6.248627148126249e-05,"quality_index":1.0}}}'

array = [1,2,3,4,5,6]
pca  = principal_component_analysis()


csv_file_path = '<inSightDataCR_May2020_Koc.csv>'


query  = "select the female patients that is older than 35 years"

def performQuerySearchByNL(query, csv_file_path):
    prompt = f"""
    From the table which name is: data\
    write the query search that is indicated by\
    triple backticks, in sql languange\
    A few data example is indicated by angel brackets, make the value names and types consistent\
    for example if you look the data, you will see that column 'gender' has values 'M' or 'F', use same\
    for your query\
    I also want you to look at the following column names: {data.columns.tolist()}, make these column names and names at query consistent
    Also, just return resulting query string, not start and end your output with triple backticks\

     <{data[0:10]}>  ```{query}```"""

    return get_completion(prompt)


def analyseHeatmap(query, query_nl):
    prompt = f"""
    Analyse the correlation heatmap that is indicated by triple backticks without mentioning 'area','avg_depth', 'maximum_depth', 'volume' relations \
    make informative comments about it\
    the comments should be based on query search results, query is indicated by angel brackets: <{query_nl}>\
        
    Heatmap: ```{correlation_heatmap_querybased(query)}```
   
    Use the following format:

    Exact Query in natural language: write the exact query in natural langugage which is {query_nl}
    
    Exact Query in sql form:  write the exact query in sql form which is: {query}
    
    Analysis: Your analysis from heatmap.
    
    """

    return get_completion(prompt)

def analyseSummary(csv_file_path):
    prompt = f"""
    Analyse the data summary  that is indicated by triple backticks\
    make informative comments about it\
    Also start to a new line after 10 words\

    Use the following format:
    Analyse: <Your analysis from data>
    Summary: <a brief summary of analysis mostly indicating most informative analysis piece>
    Bussiness Advices: <Give bussiness advices based on your analysis>

     ```{data_summary(csv_file_path)}``` """

    return get_completion(prompt)

def analyseStats(csv_file_path):
    prompt = f"""
    Analyse the means and standard deviations that is indicated by triple backticks\
    make informative comments about it considering column names\
    Also start to a new line after 15 words\

    Use the following format:
    Analyse: <Your analysis from data>
    Summary: <a brief summary of analysis mostly indicating most informative analysis piece>
    Bussiness Advices: <Give bussiness advices based on your analysis>

     ```{feature_statistics(csv_file_path)}``` """

    return get_completion(prompt)


def analyseMultipleLinearRegression(query,query_nl ,features, label):

    prompt = f"""
    I have applied multiple linear regression to my dataset\
    Features are delimited by triple quotes and label is delimited by angle brackets\
    Analyse the multiple linear regression results delimited by triple backticks, analyse indicating feature and label names and importances. \
    Explain the results and make informative comments about results\
    the comments should be based on query search results, query is indicated by angel brackets: <{query_nl}>\
   
    \"\"\"{features}\"\"\"
        <{label}>
     ```{dataScience.analyse_ultra_querybased(query, features, label)}``` 
    Use the following format:
    
    Exact Query in natural language: write the exact query in natural langugage which is {query_nl}  then start a new line\
    
    Exact Query in sql form:  write the exact query in sql form which is: {query}then start a new line\

    Analyse: <Your analysis from data multiple linear regression results  indicated by triple backticks>

      """

    return get_completion(prompt)

label = ['area']
features = ['eschar', 'granulation']

def visualize_pca_results():
    # Call the pca function
    result = principal_component_analysis()

    # Convert the result back to DataFrame
    df_pca = pd.DataFrame(result["principal_components"])
"""
    # Visualize the results
    plt.figure(figsize=(8,6))
    plt.scatter(df_pca['principal component 1'], df_pca['principal component 2'], edgecolor='k')
    plt.xlabel('Principal Component 1')
    plt.ylabel('Principal Component 2')
    plt.title('Principal Component Analysis (2D)')
    plt.grid(True)
    plt.show()
"""
#visualize_pca_results()

label = ['maximum_length']
features = ['avg_depth', 'maximum_width', 'area', 'volume']

#print(analyseMultipleLinearRegression('inSightDataCR_May2020_Koc.csv', features, label))

#print(analyseHeatmap(csv_file_path))

#print(principal_component_analysis())
#print(performQuerySearchByNL('select female patients who are older than 25 years old', csv_file_path))