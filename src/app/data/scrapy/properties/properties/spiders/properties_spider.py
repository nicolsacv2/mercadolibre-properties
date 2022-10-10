import scrapy
from datetime import date
import unidecode

# Next page button = '//li[@class="andes-pagination__button andes-pagination__button--next shops__pagination-button"]/a/@href'

class PropertiesSpider(scrapy.Spider):
    name = 'properties'
    start_urls = [
        'https://listado.mercadolibre.com.co/inmuebles/venta/venta_NoIndex_True#applied_filter_id%3DOPERATION%26applied_filter_name%3DOperaci%C3%B3n%26applied_filter_order%3D5%26applied_value_id%3D242075%26applied_value_name%3DVenta%26applied_value_order%3D3%26applied_value_results%3D73047%26is_custom%3Dfalse'
    ]
    custom_settings = {
        'FEED_URI': 'properties.json',
        'FEED_FORMAT': 'json'
    }

    def __init__(self):
        self.today = date.today().strftime("%Y-%m-%d")

    def parse_property(self, response, **kwargs):
        if kwargs:
            hrefs = kwargs['hrefs']
            property_dict = kwargs['property_dict']
            next_page_button_link = kwargs['next_page_button_link']

            price = response.xpath('//*[@id="price"]//meta[@itemprop="price"]/@content').get()
            location = unidecode.unidecode(response.xpath('//*[@id="location"]//div/p[@class="ui-pdp-color--BLACK ui-pdp-size--SMALL ui-pdp-family--REGULAR ui-pdp-media__title"]/text()').get())
            keys = response.xpath('//table[@class="andes-table"]/tbody/tr/th/text()').getall()
            values = response.xpath('//table[@class="andes-table"]/tbody/tr/td/span/text()').getall()

            property_dict.update({
                'price': price,
                'location': location
                }
            )
            property_dict.update({unidecode.unidecode(k):unidecode.unidecode(v) for k,v in zip(keys, values)})
            yield property_dict

            if hrefs:
                href = hrefs.pop(0)
                sit_site_id = href.split('/')[3].split('-')[0]
                property_id = href.split('/')[3].split('-')[1]
                property_dict = {
                'date': self.today,
                'platform': 'Mercadolibre',
                'sit_site_id': sit_site_id,
                'property_id': property_id
                }
                yield response.follow(href, self.parse_property, cb_kwargs = {
                    'hrefs': hrefs, 'property_dict': property_dict, 'next_page_button_link': next_page_button_link
                    }
                )
            else:
                yield response.follow(next_page_button_link, callback = self.parse)

    def parse(self, response):
        hrefs = response.xpath('//ol//li/div/div/a/@href').getall()
        next_page_button_link = response.xpath('//li[@class="andes-pagination__button andes-pagination__button--next shops__pagination-button"]/a/@href').get()
        if hrefs:
            href = hrefs.pop(0)
            sit_site_id = href.split('/')[3].split('-')[0]
            property_id = href.split('/')[3].split('-')[1]
            property_dict = {
                'date': self.today,
                'platform': 'Mercadolibre',
                'sit_site_id': sit_site_id,
                'property_id': property_id
            }
            yield response.follow(href, callback = self.parse_property, cb_kwargs = {
                'hrefs': hrefs, 'property_dict': property_dict, 'next_page_button_link': next_page_button_link
                }
            )