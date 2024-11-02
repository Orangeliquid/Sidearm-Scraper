from curl_cffi import requests as cureq
from bs4 import BeautifulSoup
from urllib.parse import urlparse


class Sidearm_Scraper:
    def __init__(self, url):
        self.url = url
        self.base_url = self.extract_partial_url()
        self.soup = None
        self.article_content = None
        self.article_title = None
        self.category_titles = None
        self.a_tags_list = []
        self.table_data_list = []
        self.sections = []

    def fetch_page(self):
        response = cureq.get(self.url, impersonate="chrome")
        print(f"RESPONSE: {response}")
        self.soup = BeautifulSoup(response.content, 'html.parser')

    def extract_article_content(self):
        if not self.soup:
            raise Exception("Soup is not initialized. Call fetch_page() first.")
        self.article_content = self.soup.find(class_="sidearm-cume-stats")
        return self.article_content

    # Extract the main h2 article title
    def get_article_title(self):
        if not self.article_content:
            raise Exception("Article content is not available. Call extract_main_content() first.")
        h1_tags = self.article_content.find_all('h1')
        if h1_tags:
            self.article_title = h1_tags[0].get_text(strip=True)
        return self.article_title

    # Extract the category titles
    def get_category_titles(self):
        if not self.article_content:
            raise Exception("Article content is not available. Call extract_main_content() first.")
        article_category_titles = []
        header_div = self.article_content.find('header').find('div')
        if header_div:
            ul = header_div.find('ul')
            if ul:
                for li in ul.find_all('li'):
                    a_tag = li.find('a')
                    if a_tag:
                        article_category_titles.append(a_tag.get_text(strip=True))
        self.category_titles = article_category_titles
        return article_category_titles

    # Extract all a tags from sections
    def get_a_tags(self):
        if not self.article_content:
            raise Exception("Article content is not available. Call extract_main_content() first.")
        sections = self.article_content.find_all('section')
        self.sections = sections

        team_h4 = self.article_content.find('h4')
        if team_h4:
            self.a_tags_list.append(team_h4.get_text(strip=True))
            print("team_h4 found.")

        for section in self.sections:
            sidearm_tabs_div = section.find('div', class_='sidearm-tabs')
            if sidearm_tabs_div:
                ul = sidearm_tabs_div.find('ul')
                if ul:
                    for li in ul.find_all('li'):
                        a_tag = li.find('a')
                        if a_tag:
                            self.a_tags_list.append(a_tag.get_text(strip=True))
        return self.a_tags_list

    # Extract tables and their data
    def get_table_titles_and_data(self):
        if not self.article_content:
            raise Exception("Article content is not available. Call extract_main_content() first.")

        all_tables_data = []  # To store all extracted tables and their data

        # Loop through each section to process table titles and data
        # sections = self.article_content.find_all('section', recursive=False)
        # print(self.sections)

        target_div = self.article_content.find_all('div')[2]
        target_sections = target_div.find_all('section', recursive=False)
        # for section in target_sections:
        #     print("____________________________")
        #     print(section)
        for section in target_sections:

            section_data = {}  # To store the data for this section

            # Step 1: Try to grab the h3 tag for table title
            h3_tag = section.find('h3')
            if h3_tag:
                table_title = h3_tag.get_text(strip=True)
                section_data['title'] = table_title
                print(f"H3 TAG FOUND: {h3_tag}")
            else:
                section_data['title'] = "No title found"

            # Step 2: Find the table tag with class="sidearm-table"
            table = section.find('table', class_='sidearm-table')
            if table:
                print(f"Table: {table}")

    # attempts to extract game url from Game-By-Game - Team data
    def extract_game_urls(self):
        if not self.article_content:
            raise Exception("Article content is not available. Call extract_article_content() first.")

        sections = self.article_content.find_all('section')

        # Check if there are enough sections
        if len(sections) < 7:
            print("Not enough sections found.")
            return []

        team_game_by_game = sections[6]
        tbodies = team_game_by_game.find_all('tbody')

        # List to hold the game URLs
        game_urls = []

        # Iterate through each tbody
        for tbody in tbodies:
            # Find all rows within the current tbody
            rows = tbody.find_all('tr')
            for row in rows:
                # Find the <td> element that contains the <a> tag
                link_td = row.find('td', class_='text-no-wrap')
                if link_td:
                    link = link_td.find('a')
                    if link and link.get('href'):
                        full_url = link['href']
                        if full_url not in game_urls:
                            game_urls.append(f"{self.base_url}{full_url}")
                            # print(f"Found game URL: {full_url}")  # Debugging output

        print("All Game URLs found:", game_urls)
        return game_urls

    def extract_partial_url(self):
        parsed_url = urlparse(self.url)
        base_url = f"{parsed_url.scheme}://{parsed_url.netloc}"
        return base_url


# transitioning over to using pandas to scrape the tables
if __name__ == '__main__':
    odu_url = "https://ohiodominicanpanthers.com/sports/mens-basketball/stats/"
    odu_url_partial = "https://ohiodominicanpanthers.com"
    hillsdale_url = "https://hillsdalechargers.com/sports/mens-basketball/stats/"
    hillsdale_url_partial = "https://hillsdalechargers.com"

    season = "2023-24"
    team_name = "Ohio Dominican University"
    url = odu_url
    scraper = Sidearm_Scraper(url=url)
    scraper.fetch_page()
    scraper.extract_article_content()
    scraper.extract_partial_url()
    game_url_list = scraper.extract_game_urls()
    for url in game_url_list:
        print(url)
