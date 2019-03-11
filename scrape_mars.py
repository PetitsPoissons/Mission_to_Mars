from splinter import Browser
from bs4 import BeautifulSoup
import time
import pandas as pd

def init_browser():
    # @NOTE: Replace the path with your actual path to the chromedriver
    executable_path = {"executable_path": "/usr/local/bin/chromedriver"}
    return Browser("chrome", **executable_path, headless=False)

def scrape():
    browser = init_browser()
    info_scraped = {}

    # Scrape NASA Mars News
    nasa_url = 'https://mars.nasa.gov/news'
    browser.visit(nasa_url)
    time.sleep(1)
    nasa_html = browser.html
    nasa_soup = BeautifulSoup(nasa_html, 'lxml')
    nasa_results = nasa_soup.find_all('li', class_='slide')
    news_title = nasa_results[0].find('div', class_='content_title').get_text()
    info_scraped["news_title"] = news_title
    news_p = nasa_results[0].find('div', class_='article_teaser_body').get_text()
    info_scraped["news_p"] = news_p

    # Scrape JPL Mars Space Images - Featured Image
    jpl_url = 'https://www.jpl.nasa.gov/spaceimages/?search=&category=Mars'
    browser.visit(jpl_url)
    browser.is_element_present_by_id("full_image", 1)
    jpl_html = browser.html
    jpl_soup = BeautifulSoup(jpl_html, 'lxml')
    img_src = jpl_soup.find(id='full_image')['data-fancybox-href']
    img_name = img_src.split('/')[-1].split('_')[0]
    featured_image_url = 'https://www.jpl.nasa.gov/spaceimages/images/largesize/' + img_name + '_hires.jpg'
    info_scraped["featured_image_url"] = featured_image_url

    # Scrape Mars Weather
    tweet_url = 'https://twitter.com/marswxreport?lang=en'
    browser.visit(tweet_url)
    tweet_html = browser.html
    tweet_soup = BeautifulSoup(tweet_html, 'lxml')
    tweets_MarsWxReport = tweet_soup.find_all('div', attrs={'data-screen-name': 'MarsWxReport'})
    for tweet in tweets_MarsWxReport:
        try:
            # Keep first weather report
            report = tweet.find('p', class_='TweetTextSize TweetTextSize--normal js-tweet-text tweet-text')
            # Remove pic text if present
            if (report.find('a')):
                txt = report.get_text()
                pic = report.find('a').get_text()               
                mars_weather = txt.split(pic)[0]
            else:
                continue
            break
        except AttributeError:
            pass          
    info_scraped["mars_weather"] = mars_weather

    # Scrape Mars Facts
    facts_url = 'https://space-facts.com/mars/'
    # Scrape all tabular data from Mars facts page
    tables = pd.read_html(facts_url)
    # There's only one table in the Mars facts page
    df = tables[0]
    df.columns = ['description', 'value']
    df.set_index('description', inplace=True)
    # Convert dataframe to a HTML table string
    html_table = df.to_html()
    # Strip unwanted newlines
    html_table.replace('\n', '')
    info_scraped["html_table"] = html_table

    # Scrape Mars Hemispheres
    url = 'https://astrogeology.usgs.gov/search/results?q=hemisphere+enhanced&k1=target&v1=Mars'
    xpath = "//div[@class='item']//a[@class='itemLink product-item']/img"
    # Loop through each of the four hemispheres thumbnails and click to grab info
    hemisphere_image_urls = []
    for i in range(4):
        browser.visit(url)
        images = browser.find_by_xpath(xpath)
        images[i].click()
        # Create html object
        html = browser.html
        # Create BeautifulSoup object; parse with 'lxml'
        soup = BeautifulSoup(html, 'lxml')
        img_src = soup.find('img', class_='wide-image')['src']
        img_url = 'https://astrogeology.usgs.gov' + img_src
        title = soup.find('h2', class_='title').get_text()
        # Append to list
        hemisphere_image_urls.append({'title': title, 'img_url': img_url})
        info_scraped["hemisphere_image_urls"] = hemisphere_image_urls

    # Close the browser after scraping
    browser.quit()
    # Return results
    return info_scraped