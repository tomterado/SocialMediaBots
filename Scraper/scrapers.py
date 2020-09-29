import requests
from requests_html import HTMLSession
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from itertools import chain
from functools import reduce
import pandas as pd
import numpy as np
import time
import re
import random

def login(**kwargs):

    # Input arguments - instagram username + password
    username = kwargs.get('username')
    password = kwargs.get('password')

    #Set Chrome Options to look like a real person
    user_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.50 Safari/537.36'
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument(f'user-agent={user_agent}')
    chrome_options.add_argument('--disable-extensions')
    chrome_options.add_argument('--profile-directory=Default')
    chrome_options.add_argument("--incognito")
    chrome_options.add_argument("--disable-plugins-discovery")
    #chrome_options.add_argument("--start-maximized")
    driver = webdriver.Chrome(options=chrome_options,executable_path='../chromedriver')
    #driver = webdriver.Chrome(options=chrome_options)
    driver.delete_all_cookies()
    #driver.set_window_size(800, 800)
    #driver.set_window_position(0, 0)

    #Use Chrome Driver & login in to instagram
    wait = WebDriverWait(driver, 120)

    driver.get('https://www.instagram.com/')

    user_input = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "label input")))

    #Get details if supplied otherwise use mine
    if('username' in kwargs and username is not None):
        user_input[0].send_keys(username)
    else:
        user_input[0].send_keys('nishant.patra1@gmail.com')

    if('password' in kwargs and password is not None):
        user_input[1].send_keys(password)
    else:
        user_input[1].send_keys('levron')

    #Login with supplied details
    login_button = driver.find_element_by_css_selector(".DhRcB")
    login_button.click()
    time.sleep(3)

    #Check and remove popup if there
    popup = check_popup(driver=driver)
    if(popup):
        print("Popup Removed")

    time.sleep(3)

    #Check and remove notifications popup
    notification = check_notification(driver=driver)
    if(notification):
        print("Notification Removed")

    return(driver)

def check_blocked(**kwargs):
    #Input argument - driver
    driver = kwargs.get('driver')

    wait = WebDriverWait(driver, 3)
    #Check if blocked
    try:
        blocked_notification = wait.until(EC.presence_of_element_located((By.CLASS_NAME, "_08v79")))
        blocked_text = blocked_notification.find_element_by_tag_name("h3").text
        blocked = True
    except Exception as e:
        blocked = False
        blocked_text = 'Not Blocked :)'

    return(blocked,blocked_text)


def check_notification(**kwargs):
    # Input argument - driver
    driver = kwargs.get('driver')

    wait = WebDriverWait(driver, 3)

    # Check if popup, click ok to continue if so
    try:
        browser_notification = wait.until(EC.presence_of_element_located((By.CLASS_NAME, "button")))
        notification_button_off = browser_notification[len(browser_notification) - 1]
        notification_button_off.click()
        notification = True

    except Exception as e:
        notification = False

    return(notification)

def check_popup(**kwargs):
    # Input argument - driver
    driver = kwargs.get('driver')

    wait = WebDriverWait(driver, 3)

    # Check if popup, click ok to continue if so
    try:
        browser_notification = wait.until(EC.presence_of_element_located((By.CLASS_NAME, "cmbtv")))
        browser_notification_button = browser_notification.find_element_by_class_name("sqdOP")
        popup = True

        if (browser_notification_button.text == 'Not Now'):
            browser_notification_button.click()
    except Exception as e:
        popup = False

    return (popup)


def get_private_public_user_nologin(**kwargs):
    # Input arguments - instagram username + driver
    username = kwargs.get('username')
    driver = kwargs.get('driver')

    USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko)\
     Chrome/59.0.3071.115 Safari/537.36'

    # storing the cookies generated by the browser
    request_cookies_browser = driver.get_cookies()
    s = requests.Session()
    s.headers = {'user-agent': USER_AGENT}

    # passing the cookies generated from the browser to the session
    c = [s.cookies.set(rc['name'], rc['value']) for rc in request_cookies_browser]

    # Go to post
    base_url = 'https://www.instagram.com/'
    full_url = base_url + username
    s.headers.update({'Referer': full_url})
    r = s.get(full_url)
    time.sleep(1)

    # Get user status
    page_text = r.text
    is_private = page_text[page_text.find('is_verified')-7:page_text.find('is_verified')-2]
    time.sleep(10 + random.random() * 3)

    if is_private == ':true':
        profile_status = 'Private'
    elif is_private == 'false':
        profile_status = 'Public'
    else:
        profile_status = 'Error'

    return (profile_status)


def get_private_public_user(**kwargs):
    # Input arguments - instagram username + driver
    driver = kwargs.get('driver')
    username = kwargs.get('username')

    wait = WebDriverWait(driver, 3)

    # Go to post
    base_url = 'https://www.instagram.com/'
    full_url = base_url + username
    driver.get(full_url)
    time.sleep(1)

    try:
        # Find follow button element for public profile
        follow_button = wait.until(EC.element_to_be_clickable((By.CLASS_NAME, "_5f5mN")))
        time.sleep(10+random.random()*2)
        profile_status = 'Public'

    except Exception as e:
        # Find follow button element for private profile
        try:
            follow_button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, ".y3zKF")))
            time.sleep(10+random.random()*2)
            profile_status = 'Private'
        except Exception as f:
            time.sleep(10+random.random()*2)
            profile_status = 'Error'

    return (profile_status)

def get_page_followers(**kwargs):
    # Input arguments - instagram username + driver
    page_link = kwargs.get('page_link')
    driver = kwargs.get('driver')

    # Set wait time for expected conditions and implicit wait
    wait = WebDriverWait(driver, 10)
    driver.implicitly_wait(2)
    start_time = time.time()

    # Go to webpage
    base_url = 'https://www.instagram.com/'
    full_url = base_url + page_link
    driver.get(full_url)

    # Create sets to store usernames
    following_user_old_set = set()
    following_user_new_set = set()

    # Open followers popup
    buttons_list = wait.until(EC.presence_of_all_elements_located((By.CLASS_NAME, '-nal3 ')))
    followers_popup = buttons_list[1]
    num_followers = int(reduce(lambda x, y: x + y, re.findall(r'\d+', followers_popup.text)))
    followers_popup.click()

    while (len(following_user_new_set) <= num_followers):

        # Get initial elements
        elements_old = wait.until(EC.presence_of_all_elements_located((By.CLASS_NAME, 'FPmhX')))
        following_user_old_list = [e.text for e in elements_old]
        following_user_old_set.update(following_user_old_list)
        following_user_new_set.update(following_user_old_list)

        # Scroll down to load new followers
        followers_frame = wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'isgrP')))
        driver.execute_script('arguments[0].scrollTop = arguments[0].scrollTop + arguments[0].offsetHeight;',
                              followers_frame)
        time.sleep(2)
        # Get new elements and update new set only!
        elements_new = wait.until(EC.presence_of_all_elements_located((By.CLASS_NAME, 'FPmhX')))
        following_user_new_list = [e.text for e in elements_new]
        following_user_new_set.update(following_user_new_list)

        #print(len(following_user_new_set))

        # Break loop if no more scrolls available
        if (len(following_user_new_set) >= num_followers):
            print("End break")
            break

        # Break loop if timeout
        if (time.time() - start_time > 600):
            print("Time break")
            break

        while (len(following_user_new_set) > len(following_user_old_set)):

            following_user_old_set.update(following_user_new_set)

            # Scroll down to load new followers
            driver.execute_script("return arguments[0].scrollIntoView();", elements_new[-1])
            time.sleep(3)

            # Get new elements
            elements_new = wait.until(EC.presence_of_all_elements_located((By.CLASS_NAME, 'FPmhX')))
            following_user_new_list = [e.text for e in elements_new]
            following_user_new_set.update(following_user_new_list)

            start_time = time.time()

            #print(len(following_user_new_set))

            # Break loop if no more scrolls available
            if (len(following_user_new_set) >= num_followers):
                print("End break")
                break

    return (following_user_new_set)

def get_page_followers_publicprivate(**kwargs):
    # Input arguments - instagram username + 2 drivers
    page_link = kwargs.get('page_link')
    driver = kwargs.get('driver')
    driver2 = kwargs.get('driver2')

    # Set wait time for expected conditions and implicit wait
    wait = WebDriverWait(driver, 10)
    driver.implicitly_wait(2)
    start_time = time.time()

    # Go to webpage
    base_url = 'https://www.instagram.com/'
    full_url = base_url + page_link
    driver.get(full_url)

    # Create sets to store usernames
    following_user_old_set = set()
    following_user_new_set = set()
    full_user_out_df = pd.DataFrame(columns=['username','status'])

    # Open followers popup
    try:
        buttons_list = wait.until(EC.presence_of_all_elements_located((By.CLASS_NAME, '-nal3 ')))
        followers_popup = buttons_list[1]
        num_followers = int(reduce(lambda x, y: x + y, re.findall(r'\d+', followers_popup.text)))
        followers_popup.click()
    except Exception as e:
        print("Blocked")
        return()

    while (len(following_user_new_set) <= num_followers):

        # Get initial elements
        elements_old = wait.until(EC.presence_of_all_elements_located((By.CLASS_NAME, 'FPmhX')))
        following_user_old_list = [e.text for e in elements_old]
        following_user_old_set.update(following_user_old_list)
        following_user_new_set.update(following_user_old_list)

        # Scroll down to load new followers
        followers_frame = wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'isgrP')))
        driver.execute_script('arguments[0].scrollTop = arguments[0].scrollTop + arguments[0].offsetHeight;',
                              followers_frame)
        time.sleep(2)

        # Get new elements and update new set only!
        elements_new = wait.until(EC.presence_of_all_elements_located((By.CLASS_NAME, 'FPmhX')))
        following_user_new_list = [e.text for e in elements_new]
        following_user_new_set.update(following_user_new_list)
        new_user_list = following_user_new_set - following_user_old_set

        for u in  new_user_list:
            #Get public/private profile of user
            user_status = get_private_public_user_nologin(driver=driver2, username=u)
            #Use selenium is error using requests
            if (user_status == 'Error'):
                user_status = get_private_public_user(driver=driver2, username=u)
                # Wait 10 secs and try again if error
                if (user_status == 'Error'):
                    user_status = get_private_public_user(driver=driver2, username=u)

            user_dict = {'username':['https://www.instagram.com/' + u],'status':[user_status]}
            user_out_df = pd.DataFrame(user_dict)
            full_user_out_df = full_user_out_df.append(user_out_df)
            print((full_user_out_df.shape[0],user_status))
        # Break loop if no more scrolls available
        if (len(following_user_new_set) >= num_followers):
            print("End break")
            break

        # Break loop if timeout
        if (time.time() - start_time > 300):
            print("Time break")
            break

        while (len(following_user_new_set) > len(following_user_old_set)):

            following_user_old_set.update(following_user_new_set)

            # Scroll down to load new followers
            driver.execute_script("return arguments[0].scrollIntoView();", elements_new[-1])
            time.sleep(3)

            # Get new elements
            elements_new = wait.until(EC.presence_of_all_elements_located((By.CLASS_NAME, 'FPmhX')))
            following_user_new_list = [e.text for e in elements_new]
            following_user_new_set.update(following_user_new_list)
            new_user_list = following_user_new_set - following_user_old_set

            # Get public/private profile status of users
            for u in new_user_list:
                user_status = get_private_public_user_nologin(driver=driver2,username=u)
                # Use selenium is error using requests
                if (user_status == 'Error'):
                    user_status = get_private_public_user(driver=driver2, username=u)
                    # Wait 10 secs and try again if error
                    if (user_status == 'Error'):
                        user_status = get_private_public_user(driver=driver2, username=u)

                user_dict = {'username': ['https://www.instagram.com/' + u], 'status': [user_status]}
                user_out_df = pd.DataFrame(user_dict)
                full_user_out_df = full_user_out_df.append(user_out_df)
                print((full_user_out_df.shape[0],user_status))
            start_time = time.time()

            #print(len(following_user_new_set))

            # Break loop if no more scrolls available
            if (len(following_user_new_set) >= num_followers):
                print("End break")
                break

    return (full_user_out_df)