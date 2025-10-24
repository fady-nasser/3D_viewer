import pandas as pd

def load_csv(path):
    return pd.read_csv(path)

def save_csv(data, path):
    """Save data to a CSV file.
    
    Args:
        data: pandas DataFrame to save
        path: string path where to save the CSV file
    """
    data.to_csv(path, index=False)