import selenium
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import undetected_chromedriver as uc
import time
import random
from selenium.webdriver.common.action_chains import ActionChains
from setup import USER_DATA_DIR, USERNAME, PASSWORD 

def human_typing(element, text):
    for char in text:
        element.send_keys(char)
        time.sleep(random.uniform(0.1, 0.3))

def is_logged_in(driver):
    try:
        driver.get('https://www.linkedin.com/feed/')
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, 'global-nav-typeahead')))
        print("Already logged in.")
        return True
    except:
        print("Not logged in.")
        return False

def log_in(user_data_dir, username_text, password_text):
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument(f"--user-data-dir={user_data_dir}")
    driver = uc.Chrome(options=chrome_options)

    if is_logged_in(driver):
        print("No need to log in again.")
        return driver

    time.sleep(random.uniform(1., 2.))
    driver.get('https://www.linkedin.com/login')

    time.sleep(random.uniform(1., 2.))
    username_field = WebDriverWait(driver, 15).until(EC.visibility_of_element_located((By.ID, 'username')))
    username_field.send_keys(Keys.CONTROL + "a")
    username_field.send_keys(Keys.DELETE)
    human_typing(username_field, username_text)

    time.sleep(random.uniform(1., 2.))
    password_field = WebDriverWait(driver, 15).until(EC.visibility_of_element_located((By.ID, 'password')))
    password_field.send_keys(Keys.CONTROL + "a")
    password_field.send_keys(Keys.DELETE)
    human_typing(password_field, password_text)

    time.sleep(random.uniform(1., 2.))
    password_field.send_keys(Keys.RETURN)

    time.sleep(5)
    print("Login successful, browser will remain open for manual interaction.")
    
    return driver

def search_people(driver, search_keyword, max_pages=5):
    profile_links = set() 

    for page in range(1, max_pages + 1):
        search_url = f"https://www.linkedin.com/search/results/people/?keywords={search_keyword}&network=%5B%22S%22%5D&page={page}"
        driver.get(search_url)
        time.sleep(2)

        last_height = driver.execute_script("return document.body.scrollHeight")

        while True:
            try:
                profiles = driver.find_elements(By.CSS_SELECTOR, "a[href*='/in/']")
                for profile in profiles:
                    profile_url = profile.get_attribute('href')
                    if profile_url:
                        profile_links.add(profile_url)

            except Exception as e:
                print(f"Error while collecting profiles: {e}")

            for _ in range(random.randint(1, 3)): 
                driver.execute_script("window.scrollBy(0, window.innerHeight / 2);")
                time.sleep(random.uniform(1, 3))

            time.sleep(random.uniform(2, 5))

            new_height = driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                break
            last_height = new_height

        print(f"Collected profiles from page {page}")

    print(f"Found {len(profile_links)} unique profiles.")
    return list(profile_links)

def simulate_human_behavior_on_profile(driver):
    """Simulates human-like behavior on a profile page, including scrolling."""
    
    last_height = driver.execute_script("return document.body.scrollHeight")
    for _ in range(random.randint(1, 3)):
        driver.execute_script("window.scrollBy(0, window.innerHeight / 2);")
        time.sleep(random.uniform(1, 3))
        driver.execute_script("window.scrollBy(0, window.innerHeight / 2);")
        time.sleep(random.uniform(1, 3))
    time.sleep(random.uniform(2, 5))


    if random.random() > 0.5:
        try:
            time.sleep(random.uniform(1, 3))
            profile_picture = driver.find_element(By.CSS_SELECTOR, "img.pv-top-card-profile-picture__image--show")
            ActionChains(driver).move_to_element(profile_picture).click().perform()
            time.sleep(random.uniform(4, 10))
            
            close_button = driver.find_element(By.CSS_SELECTOR, 'use[href="#close-medium"]')
            ActionChains(driver).move_to_element(close_button).click().perform()
            time.sleep(random.uniform(1, 3))
        except Exception as e:
            print(f"Could not click profile picture or close it: {e}")
    
    time.sleep(random.uniform(2, 5))

def visit_profiles(driver, profile_links):
    """Visits each profile URL with human-like behavior and random time intervals."""
    for profile_url in profile_links:
        driver.get(profile_url)
        print(f"Visiting profile: {profile_url}")
        simulate_human_behavior_on_profile(driver)
        wait_time = random.uniform(3, 120)
        print(f"Waiting for {wait_time:.2f} seconds before visiting the next profile.")
        time.sleep(wait_time)

driver = log_in(USER_DATA_DIR, USERNAME, PASSWORD)
if driver:
    search_keyword = input("Enter the search keyword: ")
    profile_links = search_people(driver, search_keyword)

    with open("linkedin_profiles.txt", "w") as f:
        for link in profile_links:
            f.write(link + "\n")
    
    print("Profile links saved to linkedin_profiles.txt")

    if profile_links:
        visit_profiles(driver, profile_links)
        print("Finished visiting all profiles.")
