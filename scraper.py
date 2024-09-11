import json
import time
from selenium import webdriver
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

driver = webdriver.Chrome()
driver.get('https://www.detmir.ru/')
time.sleep(2)


def scroll_element(element):
    """Прокручивает элемент до конца"""
    try:
        while True:
            driver.execute_script("arguments[0].scrollLeft += arguments[1];", element, 800)
            time.sleep(1)
            scroll_left = driver.execute_script("return arguments[0].scrollLeft;", element)
            scroll_width = driver.execute_script("return arguments[0].scrollWidth;", element)

            if scroll_left + element.size['width'] >= scroll_width:
                break
    except Exception as e:
        print(f"Ошибка при прокрутке: {e}")


def parse_block(elements, place):
    data = []
    for position, element in enumerate(elements, start=1):
        try:
            img_element = element.find_element(By.TAG_NAME, 'img')
            image_url = img_element.get_attribute('src')
            alt_text = img_element.get_attribute('alt')
        except Exception as e:
            print(f"Изображение не найдено: {e}")
            image_url = None
            alt_text = None

        try:
            a_element = element.find_element(By.TAG_NAME, 'a')
            content_url = a_element.get_attribute('href')
        except Exception as e:
            print(f"Ссылка не найдена: {e}")
            content_url = None

        data.append({
            "image_url": image_url or '',
            "alt_text": alt_text or '',
            "content_url": content_url or '',
            "place": place,
            "position": position
        })

    return data


def parse_section_by_testid(testid, place, scroll=False):
    """Парсит секции на основе testid"""
    try:
        section = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, f'[data-testid="{testid}"]'))
        )
        driver.execute_script("arguments[0].scrollIntoView(true);", section)
        if scroll:
            scroll_element(section)

        banners = section.find_elements(By.CSS_SELECTOR, '[data-testid="advContainer"]')
        return parse_block(banners, place)
    except Exception as e:
        print(f"Ошибка при парсинге секции {place}: {e}")
        return []


def parse_header():
    try:
        header = driver.find_element(By.CSS_SELECTOR, '[role="banner"]')
        driver.execute_script("arguments[0].scrollIntoView(true);", header)
        adv_container = header.find_element(By.CSS_SELECTOR, '[data-testid="advContainer"]')
        background_image = adv_container.find_element(By.CSS_SELECTOR, 'div[style*="background-image"]').value_of_css_property('background-image')
        content_url = adv_container.find_element(By.CSS_SELECTOR, 'a.gH').get_attribute('href')

        return [{
            "background_image": background_image or '',
            "content_url": content_url or '',
            "place": 5,
            "position": 1
        }]
    except Exception as e:
        print(f"Ошибка при парсинге header: {e}")
        return []


# Парсинг слайдера баннеров (place №1)
data_place1 = parse_section_by_testid('BannersCarousel', place=1, scroll=True)

# Парсинг плитки баннеров (place №2)
data_place2 = parse_section_by_testid('tileUnderMainCarouselBlock', place=2)

# Парсинг предложений от брендов (place №3)
data_place3 = parse_section_by_testid('Banners', place=3, scroll=True)

# Парсинг карусели рекомендаций (place №4)
try:
    product_slider = driver.find_elements(By.CSS_SELECTOR, 'div[data-testid="Products"]._u.baw')[2]
    driver.execute_script("arguments[0].scrollIntoView(true);", product_slider)
    scroll_element(product_slider)
    elements = product_slider.find_elements(By.CSS_SELECTOR, 'div[class^="bax"]')
    data_place4 = parse_block(elements, place=4)
except Exception as e:
    print(f"Ошибка при парсинге карусели: {e}")
    data_place4 = []

# Парсинг header (place №5)
data_place5 = parse_header()

final_data = data_place1 + data_place2 + data_place3 + data_place4 + data_place5

with open('output_data.json', 'w', encoding='utf-8') as f:
    json.dump(final_data, f, ensure_ascii=False, indent=4)

driver.quit()
