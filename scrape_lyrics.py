# this file contains the code to scrape all artist lyrics from a website and
# splits the received data up into training data and vaildation data

from selenium import webdriver
import os
import shutil

# given name of artist, get lyrics of all songs he/she has written
# with that, create training & validation files
def get_all_lyrics(name):
    # don't redo if already exists
    if not os.path.exists('/Users/venkatesh/Desktop/112 homework/term project/training/' + name + '/' + name + '.txt'): 
        # set up selenium
        options = webdriver.ChromeOptions()
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')

        # get song lyrics from azlyrics.com
        # ex/ for eminem, the link is azlyrics.com/e/eminem.html
        driver = webdriver.Chrome('chromedriver', options=options)
        driver.get('https://azlyrics.com/' + name.lower()[0] + '/' + name.replace(' ', '') + '.html')
        # print(driver.current_url)

        index = '2'
        prev_not_working = -1 # holds previous not working div find

        while True:
            # copied from inspect element
            song_xpath = '//*[@id="listAlbum"]/div[' + index + ']/a'
            #print("xpath: " + song_xpath)
            curr_song = driver.find_elements_by_xpath(song_xpath)
            
            # not working
            if len(curr_song) == 0: 
                if int(prev_not_working) == int(index) - 1: 
                    break
                
                # update
                prev_not_working = index
                index = str(int(index) + 1)
                continue
            
            # works! so click on the link
            # takes you to a new tab, so switch
            curr_song[0].click()
            driver.switch_to.window(driver.window_handles[1])
            #print(driver.current_url)

            driver.refresh()

            # xpath's not being found from selenium, so just extract from the
            # page source; these two give a song
            source = driver.page_source.split('<div>')

            # if you can't split then just stop (ie, access element 1)
            if len(source) == 1 or len(source[1].split('</div>')) == 1: break

            song = source[1].split('</div>')[0]
            
            # first line is empty and second line is a html comment -- remove
            song = '\n'.join(line for line in song.splitlines()[2:])

            # get rid of any br or i tags
            song = song.replace('<br>', '')
            
            fixed_lines = []
            for line in song.splitlines():
                start_index = line.find('<i>')
                if start_index == -1: fixed_lines.append(line)
                else:
                    end_index = line.find('</i>')
                    line = line.replace(line[start_index:end_index + 4], '')
                    fixed_lines.append(line)
            song = '\n'.join(line for line in fixed_lines)
            
            #print(song)
            #print()
            
            # make path and store raw file
            if not os.path.exists('/Users/venkatesh/Desktop/112 homework/term project/training/' + name):
                os.mkdir('/Users/venkatesh/Desktop/112 homework/term project/training/' + name)
    
            f = open('/Users/venkatesh/Desktop/112 homework/term project/training/' + name + '/' + name + '.txt', 'a')
            f.write(song)
            f.write('\n')
            f.close()

            driver.close()
            driver.switch_to.window(driver.window_handles[0])

            index = str(int(index) + 1)
    
    # split data into lines and then create training text & validation text
    split_data = open('/Users/venkatesh/Desktop/112 homework/term project/training/' + name + '/' + name + '.txt', 'r').read().splitlines()
    training = open('/Users/venkatesh/Desktop/112 homework/term project/training/' + name + '/' + name + '_train.txt', 'w')
    validation = open('/Users/venkatesh/Desktop/112 homework/term project/training/' + name + '/' + name + '_val.txt', 'w')
    
    # 80% for training and 20% for validation
    for i in range(len(split_data)):
        if i <= len(split_data) * 0.80:
            training.write(split_data[i])
            training.write('\n')
        else:
            validation.write(split_data[i])
            validation.write('\n')
    
    training.close()
    validation.close()
