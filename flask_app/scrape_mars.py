#!/usr/bin/env python
# coding: utf-8

# MARS FACTS

# Import dependencies
import pandas as pd
import requests
from bs4 import BeautifulSoup as bs
from splinter import Browser
import datetime as dt

# # Choose the executable path to driver FOR PCS
# executable_path = {'executable_path': './chromedriver.exe'}
# browser = Browser('chrome', **executable_path, headless=False)


def mars_news(browser):
    url = 'https://mars.nasa.gov/news/'

    # Visit the mars nasa site
    browser.visit(url)

    # Get first list item and wait half a second if not immediately present
    browser.is_element_present_by_css('ul.item_list li.slide', wait_time=0.5)

    html = browser.html
    news_soup = bs(html, 'html.parser')

    #Slide element, everything in the 
    #<ul class = "item_list">
    #  <li class = "slide">
    #  ...
    #</ul>
    try:
        slide_element = news_soup.select_one('ul.item_list li.slide')
        slide_element.find("div", class_="content_title")

        # User the parent element to find the first <a> tag and save it as news_title
        news_title = slide_element.find('div', class_='content_title').get_text()

        # Get the news paragraphs
        news_paragraph = slide_element.find('div', class_='article_teaser_body').get_text()
    except AttributeError:
        return None, None
    return news_title, news_paragraph

'''# In[93]:


# # Visit Nasa news url through splinter module
# url = 'https://mars.nasa.gov/news/'
# browser.visit(url)


# # In[95]:


# # HTML Object
# html = browser.html
    
# # Parse HTML with Beautiful Soup
# news_soup = bs(html, 'html.parser')
    
# Examine the results, then determine element that contains sought info
# print(news_soup.prettify())


# In[96]:


# soup.select(".list_text.a")
# Slide element, everything in the 
#<ul class = "item_list">
#  <li class = "slide">
#  ...
#</ul>
slide_element = news_soup.select_one('ul.item_list li.slide')


# In[97]:


slide_element.find("div", class_="content_title")


# In[98]:


# User the parent element to find the first <a> tag and save it as news_title
news_title = slide_element.find('div', class_='content_title').get_text()
news_title


# In[99]:


# Get the news paragraphs
news_paragraph = slide_element.find('div', class_='article_teaser_body').get_text()
news_paragraph


# # JPL SPACE IMAGES FEATURED IMAGE

# In[50]:
'''

# Visit URL
def featured_image(browser):
    url = 'https://www.jpl.nasa.gov/spaceimages/?search=&category=Mars'
    browser.visit(url)

    # Ask splinter to go to the site, hit a button with a class name
    # Get full_image
    # <button_class="full_image">Full Image</button>
    full_image_button = browser.find_by_id('full_image')
    full_image_button.click()

    # Find the more info button and click on that
    browser.is_element_present_by_text('more info', wait_time=1)
    more_info_element = browser.find_link_by_partial_text('more info')
    more_info_element.click()


    # Parse the results html with soup
    html = browser.html
    image_soup = bs(html, 'html.parser')

    img = image_soup.select_one('figure.lede a img')
    try:
        img_url = img.get('src')
    except AttributeError:
        return None

    # User the base url to create an absolute url
    img_url = f'https://www.jpl.nasa.gov{img_url}'
    return img_url

# # MARS WEATHER


def twitter_weather(browser):
    url = 'https://twitter.com/marswxreport?lang=en'
    browser.visit(url)

    html = browser.html
    weather_soup = bs(html, 'html.parser')

    # Find a tweet with the data-name 'Mars Weather'
    mars_weather_tweet = weather_soup.find('div', attrs={'class': 'tweet', 
                                                        'data-name': 'Mars Weather'})

    # Next search within the tweet for p tags containing the tweet text
    mars_weather = mars_weather_tweet.find('p', 'tweet-text').get_text()
    return mars_weather


def hemisphere(browser):
    url = 'https://astrogeology.usgs.gov/search/results?q=hemisphere+enhanced&k1=target&v1=Mars'
    browser.visit(url)
    hemisphere_image_urls = []

    # First get a list of all the hemispheres
    links = browser.find_by_css('a.product-item h3')

    for item in range(len(links)):
        hemisphere = {}
        
        # We have to find the element on each loop to avoid a stale element exception
        browser.find_by_css('a.product-item h3')[item].click()
        
        # Next we find the Sample Image anchor tag and extract the href
        sample_element = browser.find_link_by_text('Sample').first
        hemisphere['img_url'] = sample_element['href']
        
        # Get Hemisphere title
        hemisphere['title'] = browser.find_by_css('h2.title').text
        
        # Append hemisphere object to list
        hemisphere_image_urls.append(hemisphere)
        
        # Finally we navigate back
        browser.back()
    return hemisphere_image_urls


def scrape_hemisphere(html_text):
    hemisphere_soup = bs(html_text, 'html.paser')

    try:
        title_element = hemisphere_soup.find('h2', class_='title').get_text()
        sample_element = hemisphere_soup.find('a', text='Sample').get('href')
    except AttributeError:
        tile_element = None
        sample_element = None
    hemisphere = {
        'title': title_element,
        'img_url': sample_element
    }
    return hemisphere

# # MARS FACTS

def mars_facts():
    try:
        df = pd.read_html('https://space-facts.com/mars/')[0]
    except BaseException:
        return None
    # df = pd.read_html()
    df.columns=['description', 'value']
    df.set_index('description', inplace=True)

    return df.to_html(classes='table table-striped')


def scrape_all(): # main bot
    executable_path = {'executable_path': '/usr/local/bin/chromedriver'}
    browser = Browser('chrome', **executable_path, headless=False)
    news_title, news_paragraph = mars_news(browser)
    img_url = featured_image(browser)
    mars_weather = twitter_weather(browser)
    hemisphere_image_urls = hemisphere(browser)
    facts = mars_facts()
    timestamp = dt.datetime.now()

    data = {
        'news_title': news_title,
        'news_paragraph': news_paragraph,
        'featured_image': img_url,
        'hemispheres': hemisphere_image_urls,
        'weather': mars_weather,
        'facts': facts,
        'last_modified': timestamp
    }

    browser.quit()
    return data

if __name__ == '__main__':
    print(scrape_all())