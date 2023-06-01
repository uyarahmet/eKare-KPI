import pandas as pd
import statsmodels.api as sm
import numpy as np





def analyse_avg_depth(csv_file_path):
    # Read the CSV file into a DataFrame
    df = pd.read_csv(csv_file_path)

    # Select your columns
    df_selected = df[['avg_depth', 'maximum_depth', 'volume']]

    # Drop missing values
    df_clean = df_selected.dropna()

    # Define the dependent variable (y) and the independent variables (X)
    y = df_clean['avg_depth']
    X = df_clean[['maximum_depth', 'volume']]

    # Add a constant to the independent variables (a requirement for statsmodels)
    X = sm.add_constant(X)

    # Fit the model
    model = sm.OLS(y, X)
    results = model.fit()

    # Print out the results
    return results.summary()

def analyse_maximum_width(csv_file_path):
    # Read the CSV file into a DataFrame
    df = pd.read_csv(csv_file_path)

    # Select your columns
    df_selected = df[['maximum_width', 'area', 'maximum_depth']]

    # Drop missing values
    df_clean = df_selected.dropna()

    # Define the dependent variable (y) and the independent variables (X)
    y = df_clean['maximum_width']
    X = df_clean[['area', 'maximum_depth']]

    # Add a constant to the independent variables (a requirement for statsmodels)
    X = sm.add_constant(X)

    # Fit the model
    model = sm.OLS(y, X)
    results = model.fit()

    # Print out the results
    return results.summary()

def analyse_maximum_length(csv_file_path):
    # Read the CSV file into a DataFrame
    df = pd.read_csv(csv_file_path)

    # Select your columns
    df_selected = df[['maximum_length', 'avg_depth', 'maximum_width', 'area', 'volume']]

    # Drop missing values
    df_clean = df_selected.dropna()

    # Define the dependent variable (y) and the independent variables (X)
    y = df_clean['maximum_length']
    X = df_clean[['avg_depth', 'maximum_width', 'area', 'volume']]

    # Add a constant to the independent variables (a requirement for statsmodels)
    X = sm.add_constant(X)

    # Fit the model
    model = sm.OLS(y, X)
    results = model.fit()

    # Print out the results
    return results.summary()


def analyse_ultra(csv_file_path, features, label):
    # Read the CSV file into a DataFrame
    df = pd.read_csv(csv_file_path)

    # Select your columns
    df_selected = df[features + label]

    # Drop missing values
    df_clean = df_selected.dropna()

    # Define the dependent variable (y) and the independent variables (X)
    y = df_clean[label]
    X = df_clean[features]

    # Add a constant to the independent variables (a requirement for statsmodels)
    X = sm.add_constant(X)

    # Fit the model
    model = sm.OLS(y, X)
    results = model.fit()

    # Print out the results
    return results.summary()


label = ['maximum_length']
features = ['avg_depth', 'maximum_width', 'area', 'volume']

print(analyse_ultra('inSightDataCR_May2020_Koc.csv', features, label))