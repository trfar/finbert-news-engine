import pandas as pd
import os
from datetime import datetime, timedelta

class DataProcessor:
    """Class to Process Data and Save to Master CSV"""
    def __init__(self, scraped_dict, archive_path="archive.csv", model_path="master.csv", master_path="master.csv"):
        """
        Initializes the DataProcessor
        """
        self.scraped_dict = scraped_dict
        self.data_CSV = master_path
        self.model_CSV = model_path
        self.archive_CSV = archive_path
        self.df = pd.DataFrame(scraped_dict)

    def check_for_old_duplicates(self):
        """
        Checks for Old Duplicates in the Archive CSV
        """
        if os.path.exists(self.archive_CSV):
            archive_df = pd.read_csv(self.archive_CSV)
            self.df = self.df[~self.df['url'].isin(archive_df['url'])]

    def append_to_archive_data(self):
        """
        Appends Data to Archive CSV
        """
        if os.path.exists(self.archive_CSV):
            self.df.to_csv(self.archive_CSV, mode='a', header=False, index=False)
        else:
            self.df.to_csv(self.archive_CSV, mode='w', header=True, index=False)

    def process_and_append_model_data(self):
        """
        Splits Body into Sentences and Saves to CSV
        """
        expanded_rows = []
        print("Current columns:", self.df.columns.tolist())

        # Iterate through each row of the scraped DataFrame
        for _, row in self.df.iterrows():
            # Split the body text into sentences using '.' as delimiter
            # and strip whitespace, ignoring empty strings
            sentences = [s.strip() for s in row['body'].split('. ') if s.strip()]

            # For each sentence, create a new row with original metadata
            for sentence in sentences:
                new_row = {
                    'title': row['title'],
                    'symbol': row['symbol'],
                    'body': sentence,
                    'datetime': row['datetime'],
                    'todaysDate': row['todaysDate'],
                    'url': row['url'],
                    'source': row['source'],
                    'sentiment': None
                }
                expanded_rows.append(new_row)

        # Convert the list of new rows into a DataFrame
        expanded_df = pd.DataFrame(expanded_rows)

        # Recreate the File
        expanded_df.to_csv(self.model_CSV, mode='w', header=True, index=False)

    def clean_csv_by_date(self, csv_path, date_column='datetime', days=3):
        """
        Cleans the given CSV by removing rows older than `days` based on `date_column`.
        Overwrites the CSV with only recent rows.

        Parameters:
            csv_path (str): Path to the CSV to clean.
            days (int): Number of days to retain.
        """
        ## Make sure the CSV Exists and it can be Read
        if not os.path.exists(csv_path):
            print(f"[INFO] File not found: {csv_path}")
            return
        try:
            df = pd.read_csv(csv_path)
        except Exception as e:
            print(f"[ERROR] Failed to read {csv_path}: {e}")
            return
        
        ## Check if the Date Column Exists
        if "todaysDate" not in df.columns:
            print(f"[WARNING] Column '{date_column}' not found in {csv_path}")
            return

        ## Correcting Date Column and Filtering
        # Convert to datetime safely
        df[date_column] = pd.to_datetime(df[date_column], errors='coerce')
        # Drop NaT rows and apply cutoff
        cutoff = datetime.now() - timedelta(days=days)
        df = df[df[date_column] >= cutoff]

        ## Exporting the CSV
        try:
            df.to_csv(csv_path, index=False)
            print(f"[SUCCESS] Cleaned {csv_path}. Remaining rows: {len(df)}")
        except Exception as e:
            print(f"[ERROR] Failed to write cleaned data to {csv_path}: {e}")