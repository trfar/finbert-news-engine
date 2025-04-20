import pandas as pd
import os

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
                    'url': row['url'],
                    'source': row['source']
                }
                expanded_rows.append(new_row)

        # Convert the list of new rows into a DataFrame
        expanded_df = pd.DataFrame(expanded_rows)

        # Recreate the File
        expanded_df.to_csv(self.model_CSV, mode='w', header=True, index=False)