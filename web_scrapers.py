from selenium import webdriver
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
import time
import re
import requests
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
# Create a new instance of the Chrome driver
driver = webdriver.Chrome()

# Disable SSL warnings
requests.packages.urllib3.disable_warnings()

# Get the main page
response = requests.get('https://quran411.com/', verify=False)

# Parse the HTML content
soup = BeautifulSoup(response.text, 'html.parser')

# Find the section containing the links
section = soup.find('section', style="padding-top:30px;font-size:17px;line-height: 25px;")

# Extract the URLs and full titles
urls_and_titles = [(a['href'], a.text) for a in section.find_all('a')]

# Open the files in write mode
with open('translations.txt', 'w', encoding='utf-8') as f, open('tasfeer.txt', 'w', encoding='utf-8') as tasfeer_f:
    # Initialize the chapter counter
    chapter_counter = 1

    # Iterate over the URLs and titles
    for url, full_title in urls_and_titles:
        # Navigate to the URL
        driver.get(f'https://quran411.com/{url}')

        # Wait for the page to load completely
        time.sleep(2)

        clickable_element = WebDriverWait(driver, 1.5).until(EC.visibility_of_element_located((By.CSS_SELECTOR, 'div.ac-item:nth-child(3)')))

        # Scroll to the element
        actions = ActionChains(driver)
        actions.move_to_element(clickable_element).perform()

        # Click the element
        clickable_element.click()
        # Wait for the Tafseer div to load
        time.sleep(1)

        # Get the HTML content of the page
        html = driver.page_source

        # Parse the HTML content
        soup = BeautifulSoup(html, 'html.parser')

        # Find the "translation" tab content
        translation_tab = soup.find('div', id='translation')

        # If the "translation" tab is not found, skip this URL
        if translation_tab is None:
            print(f'Translation tab not found for {full_title}')
            continue

        # Find the ordered list within the "translation" tab
        ol = translation_tab.find('ol')

        # If the ordered list is not found, skip this URL
        if ol is None:
            print(f'Ordered list not found for {full_title}')
            continue

        # Extract the English translations
        translations = [li.text for li in ol.find_all('li')]

        # Write the chapter number and full title to the file
        full_title = re.sub(r'\s+', ' ', full_title)  # Replace all whitespace sequences with a single space
        f.write(f'Chapter {chapter_counter}: {full_title.strip()}\n')
        print(f'Chapter {chapter_counter}: {full_title.strip()}')
        # Write the translations to the file with verse numbers
        for verse_counter, translation in enumerate(translations, start=1):
            f.write(f'Verse {verse_counter}: {translation}\n')
        print(f'Translations found for {full_title}')
        # Add a newline after each translation
        f.write('\n')

        # Find the Tafseer content
        tafseer_div = soup.select_one('div.ac-item:nth-child(3) > div:nth-child(2)')
        # If the Tafseer div is not found, skip this URL
        if tafseer_div is None:
            print(f'Tafseer div not found for {full_title}')
            continue
        #print(tafseer_div.prettify())
        # Find the Tafseer content within the div
        tafseer = tafseer_div.text.strip()

        # If the Tafseer content is not found, skip this URL
        if tafseer is None:
            print(f'Tafseer not found for {full_title}')
            continue

        # Write the Tafseer content to the tasfeer.txt file
        tasfeer_f.write(f'Chapter {chapter_counter}: {full_title.strip()}\n')
        tasfeer_f.write(f'{tafseer.strip()}\n\n')
        print(f'Tafseer found for {full_title}')

        # Increment the chapter counter
        chapter_counter += 1

# Don't forget to close the driver when you're done
driver.quit()