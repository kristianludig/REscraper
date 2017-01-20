import scrapy
from REscraper.items import Unit
from scrapy.linkextractors import LinkExtractor

class REscraper(scrapy.Spider):
    name = "units"

    def start_requests(self):
        urls = [
            'http://www.metcap.com/searchresults/apartment-for-rent-in-Toronto?province=ON&PriceSortOrder=asc&propertyType=Apartment%20/%20Condo%20/%20Strata',
            'http://briarlane.ca/'
        ]

        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        #Metcap Scraper
        if 'metcap' in response.url:
            for unit in response.xpath('//p[@class="building"]'):
                next_page = unit.xpath('.//a/@href').extract_first()
                yield scrapy.Request(next_page, callback=self.parse_metcap)
        #Briar Lane Scraper
        if 'briarlane' in response.url:
            for unit in response.xpath('//div[@id="tab1"]/div[@class="span6"]/div/div[@class="span6"]'):
                if unit.xpath('.//a[@class="btn btn-info"]/@href').extract_first() is not None:
                    next_page = unit.xpath('.//a[@class="btn btn-info"]/@href').extract_first()
                    yield {'link': response.urljoin(next_page)}

        '''page = response.url.split("/")[-2]
        filename = 'units-metcap.html'
        with open(filename, 'wb') as f:
            f.write(response.body)
        self.log("saved file %s" % filename)'''

    def parse_metcap(self, response):
        address = response.xpath('//p[@class="address"]/text()').extract_first().strip()
        bedrooms = response.xpath('//td[@class="col-beds"]/text()').re_first(r'(Studio|\d)')
        yield {
            'address': response.xpath('//p[@class="address"]/text()').extract_first().strip(),
            #can get all units with this regex, but all groups under the one bedrooms attribute - need to figure out how to separate, maybe Items?
            'bedrooms': response.xpath('//td[@class="col-beds"]/text()').re_first(r'(Studio|\d)')
        }