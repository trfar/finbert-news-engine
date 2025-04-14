import pandas as pd
import argparse as ap
import os

class DataProcessor:
    """Class to Process Data and Save to Master CSV"""
    def __init__(self, scraped_dict, master_CSV_path="master.csv"):
        """
        Initializes the DataProcessor
        """
        self.scraped_dict = scraped_dict
        self.data_CSV = master_CSV_path
        self.df = pd.DataFrame(scraped_dict)

    def process_data(self):
        """
        Splits Body into Sentences and Saves to CSV
        """
        expanded_rows = []

        # Iterate through each row of the scraped DataFrame
        for _, row in self.df.iterrows():
            # Split the body text into sentences using '.' as delimiter
            # and strip whitespace, ignoring empty strings
            sentences = [s.strip() for s in row['body'].split('.') if s.strip()]

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

        # Append to the CSV if it exists; otherwise create a new file
        if os.path.exists(self.data_CSV):
            expanded_df.to_csv(self.data_CSV, mode='a', header=False, index=False)
        else:
            expanded_df.to_csv(self.data_CSV, mode='w', header=True, index=False)