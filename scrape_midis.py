# this file contains the code to scrape midi files from two popular websites

from selenium import webdriver
import os
import shutil

# given the name of an artist, get midis related to him/her
def getMIDIs(name):
    # don't recalculate what already exists
    if os.path.exists('/Users/venkatesh/Desktop/112 homework/term project/' + name): 
        return "already done"

    # set up selenium
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')

    # create chrome driver and go to bitmidi.com
    # saving myself some time by just going to the search page rather than
    # having to send keys into the search box
    # putting 'travis scott' into search makes url .../search?q=travis+scott
    # so replace ' ' in name with '+' and add to search
    driver = webdriver.Chrome('chromedriver', options=options)
    driver.get('https://bitmidi.com/search?q=' + name.replace(' ', '+'))

    # i holds xpath article number
    i = '1'
    while True:
        # copied from inspect element
        xpath = '//*[@id="root"]/div/main/div[1]/div[1]/article[' + i + ']/a/div/h2'
        midi_link = driver.find_elements_by_xpath(xpath)

        # if the xpath doesn't exist, break
        if len(midi_link) == 0: break

        # if it's actually a song by that author (ignore case)
        elif name.lower() in midi_link[0].text.lower():
            midi_link[0].click() # click the article link

            driver.refresh() # refresh page

            # copied from inspect element
            download_xpath = '//*[@id="root"]/div/main/div[1]/div[3]/div[1]/p[2]/a'
            download_midi = driver.find_element_by_xpath(download_xpath)
            download_midi.click() # download

            i = str(int(i) + 1) # increment for next article

            # reset
            driver.get('https://bitmidi.com/search?q=' + name.replace(' ', '+'))

        # if it's not then continue to next (just in case)
        else: i = str(int(i) + 1)

    # search on freemidi.com as well
    driver.get('https://freemidi.org/search?q=' + name.replace(' ', '+'))
    xpath_category = '//*[@id="mainContent"]/div[2]/div[1]/div/a'
    best_category = driver.find_elements_by_xpath(xpath_category)
    
    if len(best_category) > 0:
        best_category[0].click()

        current_url = driver.current_url

        i = '1'
        while True:
            driver.get(current_url)
            xpath = '//*[@id="mainContent"]/div[1]/div[2]/div[1]/div/div[' + i + ']/span/a'
            midi_files = driver.find_elements_by_xpath(xpath)

            if len(midi_files) == 0: break

            midi_files[0].click()

            driver.refresh()

            download_midi = driver.find_element_by_id('downloadmidi')
            download_midi.click()

            i = str(int(i) + 1)
    
    # move all downloaded midi files to a folder specified by name of artist
    os.mkdir(name)
    midi_file_path = '/Users/venkatesh/Desktop/112 homework/term project/'
    for f in os.listdir(midi_file_path):
        if f.endswith('.mid'):
            shutil.move(os.path.join(midi_file_path, f), 
                        os.path.join(midi_file_path + name + '/', f))