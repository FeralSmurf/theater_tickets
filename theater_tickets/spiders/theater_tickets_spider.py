import scrapy
import json
from datetime import datetime
import shutil
import os

class TheaterTicketsSpider(scrapy.Spider):
    name = "theater_tickets_spider"
    allowed_domains = ["m.iabilet.ro"]
    start_urls = ["https://m.iabilet.ro/bilete-in-bucuresti/"]
    custom_settings = {
        'USER_AGENT': 'bogdanvarzaru@gmail.com',  # Custom user agent
    }

    def __init__(self):
        self.data = []

    def parse(self, response):
        # Extract play titles and links
        plays = response.css('.event-item .text a')
        for play in plays:
            title = play.css('::text').get().strip()
            link = response.urljoin(play.css('::attr(href)').get())
            if title == 'ia bilet':
                continue  # Skip the "ia bilet" link
            self.data.append({'title': title, 'link': link})

        # Follow pagination
        next_page = response.css('.btn-more::attr(href)').get()
        if next_page:
            yield response.follow(next_page, self.parse)
        else:
            # Save extracted data to a JSON file
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            with open('play_titles.json', 'w', encoding='utf-8') as f:
                f.write(f"// Timestamp: {timestamp}\n")  # Add timestamp as a separate line
                json.dump(self.data, f, indent=4, ensure_ascii=False)
                f.write('\n')  # Add newline for readability

            # Move the file to ~/Desktop/scrapy/
            destination_dir = os.path.expanduser('~/Desktop/scrapy/')
            shutil.move('play_titles.json', destination_dir)
            print(f"File moved to {destination_dir}")




