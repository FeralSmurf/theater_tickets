import scrapy
import json

class TheaterTicketsSpiderSpider(scrapy.Spider):
    name = "theater_tickets_spider"
    allowed_domains = ["m.iabilet.ro"]
    start_urls = ["https://m.iabilet.ro/bilete-teatru/"]
    user_agent = "bogdanvarzaru@gmail.com" # not a malicious user agent, just someone who likes theater

    def parse(self, response):
        play_titles = response.css('.event-item .text a::text').getall()
        data = [{'title': title.strip()} for title in play_titles if title.strip().lower() != 'ia bilet']
        for i in range(1, len(data), 2):
            data[i]['location'] = data[i]['title']
            del data[i]['title']

        json_string = json.dumps(data, indent=4, ensure_ascii=False) # make it look normal
        with open('play_titles.json', 'a', encoding='utf-8') as f:
            f.write(json_string + '\n')

        next_page = response.css('.btn-more::attr(href)').get()
        if next_page:
            yield response.follow(next_page, self.parse)

