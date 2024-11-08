from bs4 import BeautifulSoup
from PepinaScraper.request import fetch_html  


class ShoeScraper:
    def __init__(self, url):
       
        self.url = url  
        self.shoes = []
        
    def parse_data(self, html):
        soup = BeautifulSoup(html, 'html.parser')
        
        section_title = soup.find("h1", class_="title")
        if section_title and "Дамски обувки" in section_title.text:
            product_containers = soup.find_all("div", class_="component-product-list-product")
            
            for container in product_containers:
                shoe_data = {}
                
                link_tag = container.find("a", class_="product-link")
                shoe_data["link"] = link_tag['href'] if link_tag else None
                
                img_tag = container.find("div", class_="main-image").find("img")
                shoe_data["image"] = img_tag['src'] if img_tag else None
                
                brand_tag = container.find("div", class_="brand")
                shoe_data["brand"] = brand_tag.text.strip() if brand_tag else None
                
                title_tag = container.find("div", class_="title")
                shoe_data["title"] = title_tag.text.strip() if title_tag else None
                
                price_tag = container.find("div", class_="regular-price")
                shoe_data["price"] = price_tag.text.strip() if price_tag else None
                
                size_tags = container.find("div", class_="available-configurations")
                if size_tags:
                    shoe_data["sizes"] = [size.text.strip() for size in size_tags.find_all("div", class_="value")]
                else:
                    shoe_data["sizes"] = []

                self.shoes.append(shoe_data)
        else:
            print("Секцията 'Дамски обувки' не беше намерена на страницата.")

    def sort_by_brand(self):
        self.shoes.sort(key=lambda x: x['brand'])
    
    def filter_by_size(self, size):
        return [shoe for shoe in self.shoes if size in shoe['sizes']]
    
    def scrape(self):
        html = fetch_html(self.url)  
        if html:
            self.parse_data(html)
        return self.shoes
    

scraper = ShoeScraper("https://example.com/damski-obuvki")  
all_shoes = scraper.scrape()

scraper.sort_by_brand()
print("Обувки, сортирани по брандове:")
for shoe in scraper.shoes:
    print(shoe)

filtered_by_size = scraper.filter_by_size("38")
print("\nОбувки с размер 38:")
for shoe in filtered_by_size:
    print(shoe)