import requests
from bs4 import BeautifulSoup

url = 'https://www.franksonnenbergonline.com/blog/are-you-grateful/'
response = requests.get(url)
response.raise_for_status()
soup = BeautifulSoup(response.text, 'lxml')
title_tag = soup.find('main').find('header').find('h1')
title_text = title_tag.text
print(title_text)
image_tag = soup.find('img', class_='attachment-post-image')
print(image_tag['src'])
text_tag = soup.find('div', class_='entry-content').text
print(text_tag)
