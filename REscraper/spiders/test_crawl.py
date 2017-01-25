import scrapy
from REscraper.items import Unit
from scrapy.loader import ItemLoader

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

#scrapes available units from Metcap Toronto and outputs address, bedrooms, and rent for each unit
#at each address
    def parse_metcap(self, response):
        units = []
        address = response.xpath('//p[@class="address"]/text()').extract_first().strip()
        bedrooms = response.xpath('//td[@class="col-beds"]/text()').re(r'(Studio|\d)')
        rents = response.xpath('//td[@class="col-rent-from"]/text()').re(r'(\$\d+,*\d*)')

        if not bedrooms:
            load = ItemLoader(item=Unit())
            load.replace_value("address", address)
            units.append(load.load_item())
        else:
            for unit in bedrooms[:]:
                load = ItemLoader(item=Unit())
                load.replace_value("address", address)
                load.replace_value("bedrooms", bedrooms.pop())
                if rents:
                    load.replace_value("rent", rents.pop())
                units.append(load.load_item())

        return units

    def parse_briarlane(self, response):
        units = []
        address = response.xpath('//h2/text()').extract_first().strip()
        #note: try sorting by tr instead of td - too many different types of unit names
        bedrooms = response.xpath('//table[@class="table table-striped"]/tbody/td/text()').re(r'(Bachelor|Studio|One|Two|Three|Four)')
        rents = response.xpath()

