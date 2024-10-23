import pandas as pd
import json
from Sidearm_Scraper import Sidearm_Scraper


class Sidearm_Data:
    def __init__(self, team: str, url: str, year: str):
        # Scrape title, categories, a_tags
        self.team_name = team
        self.url = url + year
        self.season = year
        self.scraper = Sidearm_Scraper(self.url)
        self.tables_data = {}
        self.title_count = {}  # Dictionary to keep track of title counts
        self.article_title = None
        self.categories = None
        self.a_tags = None
        self.data_scrape()
        self.organize_tables_by_category()
        self.new_file_name = None
        self.finalize_json()

    def data_scrape(self):
        self.scraper.fetch_page()
        self.scraper.extract_article_content()

        self.article_title = self.scraper.get_article_title()
        self.article_title = f"{self.team_name} {self.article_title}"
        print(f"Article Title: {self.article_title}")

        # Define categories based on your provided ranges
        self.categories = self.scraper.get_category_titles()
        print(f"Categories: {self.categories}")

        self.a_tags = self.scraper.get_a_tags()
        print(f"A Tags: {self.a_tags}")

        # Scrape all tables
        tables_created = pd.read_html(self.url)
        print(f"Total tables scraped: {len(tables_created)}")

        for i, table in enumerate(tables_created):
            # Get the table title, ensuring it is unique
            table_title = self.a_tags[i] if i < len(self.a_tags) else f"Table_{i + 1}"

            # Check for duplicates and modify the title if necessary
            if table_title in self.title_count:
                self.title_count[table_title] += 1
                table_title = f"{table_title}_{self.title_count[table_title]}"
            else:
                self.title_count[table_title] = 1

            # Clean each table if necessary
            if i in [1, 2]:  # Example for specific tables
                table = table.drop(columns=table.columns[-1:], errors='coerce')  # Drop the last column

            # Flatten column names if they are tuples
            if isinstance(table.columns, pd.MultiIndex):
                table.columns = [' '.join(map(str, col)).strip() for col in table.columns.values]

            # Add the cleaned table to the dictionary
            self.tables_data[table_title] = table.to_dict(orient='records')

    # Function to organize tables under their respective categories
    def organize_tables_by_category(self) -> dict:
        organized_data = {}

        # Define the starting and ending indices for each category
        category_ranges = {
            self.categories[0]: (0, 1),  # TEAM
            self.categories[1]: (1, 5),  # INDIVIDUAL
            self.categories[2]: (5, 8),  # GAME-BY-GAME
            self.categories[3]: (8, 10),  # GAME HIGHS
            self.categories[4]: (10, 22)  # CATEGORY LEADERS
        }

        # Loop through each category and its range
        for category, (start, end) in category_ranges.items():
            organized_data[category] = {}

            # Add tables to their respective category
            for table_index in range(start, end):
                table_title = list(self.tables_data.keys())[table_index]
                organized_data[category][table_title] = self.tables_data[table_title]

        return organized_data

    def finalize_json(self):
        # Organize tables into a nested structure
        final_data = self.organize_tables_by_category()

        # Create a new dictionary with article title as the top-level key
        output_data = {self.article_title: final_data}

        # add underscores to self.team_name that is more than one word to keep formatting of json filename
        try:
            self.team_name = self.team_name.replace(" ", "_")
        except ValueError:
            raise ValueError

        self.new_file_name = f"{self.team_name}_Tables_Data_{self.season}.json"
        # Convert to JSON and save to file
        with open(self.new_file_name, 'w') as f:
            json.dump(output_data, f, indent=4)

        print("Data successfully saved to JSON.")
