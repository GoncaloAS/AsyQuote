import aiohttp
import asyncio
import pandas as pd
from bs4 import BeautifulSoup
import requests
import aiofiles

first_url = 'https://casapeixoto.pt/2-produtos'
data = []
product_titles = []
product_hrefs = []
product_prices = []
unique_urls = set()
unique_data = []
numberpage = 1
global teller
teller = True
global i
i = 0


async def fetch(session, url, headers):
    retry_limit = 10
    retry_count = 0
    while retry_count < retry_limit:
        try:
            async with session.get(url, headers=headers) as response:
                return await response.text()
        except aiohttp.client_exceptions.ServerDisconnectedError:
            retry_count += 1
            print(f"Retrying request ({retry_count}/{retry_limit}) due to ServerDisconnectedError")
            await asyncio.sleep(2 ** retry_count)  # You can adjust the sleep duration if needed

    raise RuntimeError(f"Exceeded retry limit ({retry_limit}) for {url}")


def save_to_excel(product_titles, product_hrefs, product_prices, category_name):
    data = {'Title': product_titles, 'Href': product_hrefs, 'Price': product_prices}
    df = pd.DataFrame(data)
    filename = f'{category_name}_products.xlsx'
    df.to_excel(filename, sheet_name='products', index=False)
    print(f"Saved data for category {category_name} to {filename}")


def scrape_product(page_content, product_titles, product_hrefs, product_prices):
    global teller
    soup = BeautifulSoup(page_content, 'html.parser')
    product_info = soup.find_all(class_='product-meta')

    for product_title in product_info:
        title_product = product_title.select('a')
        for title_element in title_product:
            title_text = title_element.get_text()
            title_link = title_element['href']
            product_titles.append(title_text)
            product_hrefs.append(title_link)
    price = ""
    price_info = soup.find_all(class_='price')
    for price_element in price_info:
        price = price_element.get_text()
        product_prices.append(price)
        print(price)

    if (price == "" or price == " "):
        teller = False
        print("ola")


async def scrape_category_async(category_url, headers, product_titles, product_hrefs,
                                product_prices, numberpage):
    global i, teller
    retry_limit = 10
    retry_count = 0
    async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=300)) as session:
        while (teller and retry_count < retry_limit):

            print(f"--------------------------------{i}")
            tasks = []
            for page in range(numberpage, numberpage + 10):
                url = f"{category_url}?page={page}"
                tasks.append(fetch(session, url, headers))

            try:
                responses = await asyncio.gather(*tasks)
            except RuntimeError as e:
                print(e)
                retry_count += 1
                continue

            for page_content in responses:
                scrape_product(page_content, product_titles, product_hrefs, product_prices)

            numberpage += 10
            i += 1


def main():
    global teller
    headers = {
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,'
                  'application/signed-exchange;v=b3;q=0.7',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/119.0.0.0 Safari/537.36',
        'Accept-Encoding': 'zip, deflate, br',
        'referer': 'https://casapeixoto.pt/',
        'Accept-Language': 'pt-PT,pt;q=0.9,en-US;q=0.8,en;q=0.7,fr;q=0.6',
        'Cookie': 'PrestaShop-79b824b0fa117ffd9481e07926c1c67f=def502008cc0f05260acbb16709ec21544b3560c1371e'
                  'e2a8044f709672a9021d1bf668ad45d70065946cdebff909996dfdca93ae0fd3200b8c485c906e5ef83e608ad6ff5828f38b'
                  'f56675c6335a2bc46e7afdfc5a81f557dbbdee52bcc466e05054f714533400e26479c1d821fc4314e340fbfd7b50646f38d'
                  '2086de3ecfe93b4f1fba533b6a1a87046cc9e7c3e8b8400dfe9f91de4a19643908a474b96bd3e54ded2; PHPSESSID=a708r5eja'
                  '6i32aat3b6k5p9chn; cp-popup-last-displayed=1700757457; cp-popup-2=1700757457; cp-popup-9=1700757457; '
                  'AT_MOVIC'
                  '_PANEL_CONFIG_grid_list=grid; '
                  'PrestaShop-7a2f84d12b6be0b64676bafbcb0e4075=def502001fdbb657a7a83434c1b3ac566d84606'
                  'c834a2b2f466c9e19b9ecd67640304907147b867283b18bdbca6a31a81246d3ef062ced5b17654aadb6a320112b936be519eb8'
                  'e3213d40eae701060c708c26d0a76523afda2177514bcbcd8a1ce6681efed2e69f67c4640e26d28710916bfc188ac1f477cccd'
                  '981ae5f4919f70b55e3007be16abae0d72917cf7559bf62d0c96ca520154c7f0cce55ffa2269fdd7de108a62c02a6ba2866e804'
                  '9d05af340a10d55ea49213a429bee74ba1e14bb9c422623d03c9f8840885f08186baad09aeb9c391da6252ad2a30b9fb13dccc6'
                  '11b1c64f57583957a54548e9a09e12479ce043c15d585bc0df4815f067e2f13bd27e81899001877d0a6c46922eff63235a89d5d'
                  '63e96edb39f3b527e2a4bc1765fc9fa190d40342701d1e9f9c04b763055c6d160494c4df452b109e8b65a60dfad37e0fed2f7a'
                  '78d6e064399a413093ec3971c0325f72a8a9fd35b532d6fa15f994f9f9ff1270f51bb365345483345a8bcd8e6eff3af973433db'
                  '4e3bf0868f8a34ae81d0fb2577229951747f1af255e685bab877c684694dc',
    }
    response = requests.get(first_url, headers=headers)

    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        product_containers = soup.find_all('ul', {'class': 'category-sub-menu'})
        start_processing = False

        for product_container in product_containers:
            links_main = product_container.find_all('li', {'data-depth': '0'})

            for li in links_main:
                first_a_tag = li.find('a')

                if first_a_tag:
                    category_url = first_a_tag.get('href')

                    if start_processing or category_url.startswith('https://casapeixoto.pt/712-lar-e-iluminacao'):
                        start_processing = True
                        print(f"Processing category URL: {category_url}")
                        data.append({'Category': category_url})
                    if start_processing:
                        pass

    for entry in data:
        category_url = entry['Category']
        if category_url not in unique_urls:
            unique_urls.add(category_url)
            unique_data.append(entry)
    df = pd.DataFrame(unique_data)
    df.to_excel('products_links.xlsx', sheet_name='products_links', index=False)

    # Tudo Certo para cima para ir buscar os links

    category_url = 'https://casapeixoto.pt/865-ferragens'
    print(category_url)
    numberpage = 1
    i = 0

    loop = asyncio.get_event_loop()
    loop.run_until_complete(
        scrape_category_async(category_url, headers, product_titles, product_hrefs, product_prices, numberpage))

    save_to_excel(product_titles, product_hrefs, product_prices, category_url.split('/')[-1])
    # Reset
    product_titles.clear()
    product_hrefs.clear()
    product_prices.clear()
    teller = True


if __name__ == "__main__":
    main()
