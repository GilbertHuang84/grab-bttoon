import os
import re
import json
import time

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoAlertPresentException

from config import cartoon_dir, image_json, cartoon_json, chrome_driver_path


option = webdriver.ChromeOptions()
option.add_argument('--user-agent=iphone')
option.add_argument('--no-proxy-server')
option.add_argument('--headless')
driver = webdriver.Chrome(chrome_driver_path, options=option)


def get_cartoon_json_path(cartoon_name):
    return os.path.join(cartoon_dir, cartoon_name, cartoon_json)


def go_next_chapter():
    for next_chapter in driver.find_elements_by_xpath('//div[@id="commicBox"]/div[4]/a[@class="afterChapter"]'):
        next_chapter.send_keys(Keys.ENTER)
        break


def run_cartoon_page(page_url):
    if driver.current_url != page_url:
        driver.get(page_url)

    next_page_exists = True
    while next_page_exists:
        # Check dir for download
        print('Checking page: {}'.format(driver.current_url))
        title = driver.title.split(' - ', 1)[0]
        if '第' not in title:
            go_next_chapter()
            continue

        cartoon_name, chapter_name = title.split('第', 1)
        chapter_name = chapter_name.strip().replace('?', '')
        chapter_dir = os.path.join(cartoon_dir, cartoon_name, chapter_name)
        if not os.path.exists(chapter_dir):
            os.makedirs(chapter_dir)

        # Get init image links
        image_dict = {}
        image_json_path = os.path.join(chapter_dir, image_json)
        if os.path.exists(image_json_path):
            with open(image_json_path) as f:
                image_dict = json.load(f)

        # Downloading
        for img in driver.find_elements_by_xpath('//div[@id="commicBox"]//img'):
            src_path = img.get_attribute('data-original')

            last_index = sorted(image_dict.values(), reverse=True)
            if src_path in image_dict:
                current_index = image_dict[src_path]
            elif last_index:
                current_index = last_index[0] + 1
            else:
                current_index = 0

            image_dict[src_path] = current_index

        # Save latest cartoon page
        cartoon_json_path = get_cartoon_json_path(cartoon_name=cartoon_name)
        with open(cartoon_json_path, 'w+') as f:
            f.write(driver.current_url)

        # Save image link
        with open(image_json_path, 'w+') as f:
            json.dump(image_dict, f, indent=4)

        # Go to next page
        next_page_exists = False
        for next_page in driver.find_elements_by_xpath('//div[@id="commicBox"]/div[3]/a[@class="ChapterLestMune"]'):
            next_page_exists = True
            next_page.send_keys(Keys.ENTER)
            break

        # Go to next chapter
        if not next_page_exists:
            go_next_chapter()
            next_page_exists = True

        # Switch to the first page
        time.sleep(3)
        for window in driver.window_handles[1:]:
            driver.switch_to.window(window)
            driver.close()
        driver.switch_to.window(driver.window_handles[0])

        # Remove alert
        try:
            driver.switch_to.alert.accept()
            next_page_exists = False
        except NoAlertPresentException:
            pass


def run_latest_cartoon_page(page_url):
    print('run_latest_cartoon_page for {}'.format(page_url))
    driver.get(page_url)

    title = driver.title.split(' - ', 1)[0]
    cartoon_name, chapter_name = title.split('第', 1)
    chapter_name = chapter_name.strip()
    chapter_dir = os.path.join(cartoon_dir, cartoon_name, chapter_name)
    if not os.path.exists(chapter_dir):
        os.makedirs(chapter_dir)

    cartoon_json_path = get_cartoon_json_path(cartoon_name=cartoon_name)
    if os.path.exists(cartoon_json_path):
        with open(cartoon_json_path) as f:
            run_cartoon_page(f.read())
    else:
        run_cartoon_page(page_url=page_url)


def get_cartoon_page(comic_name):
    driver.get("https://www.bttoon.com/comic/{}".format(comic_name))
    chapter_list_div = driver.find_element_by_xpath('//div[@id="list"]')
    page_url = chapter_list_div.find_element_by_xpath('.//a').get_attribute('href')
    return page_url


def get_cartoon_list(page_url='https://www.bttoon.com/nansheng'):
    driver.get(page_url)
    ranking_list = driver.find_element_by_xpath('//div[@id="listRanking"]')
    top_3 = ranking_list.find_elements_by_xpath('.//div[@class="img-div relative"]')
    others = ranking_list.find_elements_by_xpath('.//div[@class="img-div relative ver-t"]')
    comic_names = []
    for comic_item in top_3 + others:
        click_value = comic_item.get_attribute('onclick')
        m = re.match(r'clkComic\((\d+)\)', click_value)
        if m:
            comic_names.append(m.groups()[0])

    for comic_name in comic_names:
        comic_url = get_cartoon_page(comic_name=comic_name)
        yield comic_url


if __name__ == '__main__':
    for cartoon_url in get_cartoon_list():
        run_latest_cartoon_page(cartoon_url)
    driver.quit()

