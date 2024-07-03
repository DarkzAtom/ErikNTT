import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.options import Options
from selenium.webdriver import ActionChains
from selenium.common.exceptions import StaleElementReferenceException
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.support import expected_conditions as EC
from anticaptchaofficial.imagecaptcha import *
import sys


# THE SECTION WITH THE QUERY PARAMS IS HERE
# **********************************************************

TT_LINK = "https://www.tiktok.com/@crawly_possessed/video/7385326325285817633"
# don't forget to keep the right format of the link, with https:// at the beginning

TT_USERNAME = "@greg_757"
# PROVIDE USERNAME WITH @! Here I left the @ on purpose as a reminder, that you should look for account's @ (usernameid), which is above their account's name that can be whatever they want, so you should be careful. It looks bolder and bigger in font as well. on the site exactly the @'s are shown. I guess you understand all of that, but just in case I left this short instruction if the script is passed for usage to someone else

ROUNDS = 3
# This param is for how much time you want to boost likes for a comment
# The average for one boosting is 70-90, you might know better so in case i'm wrong correct me

SHOW_BROWSER_INSTANCE_OR_NOT = True
# THIS PARAM ENABLES ("True") OR DISABLES ("False") THE ACTIVE BROWSER WINDOW. If you dont need to see the script doing all the job, than simply replace True with False and vice versa


# ****************************************************
# THE END OF THE QUERY PARAMS SECTION


class SlowDownException(Exception):
    pass


def set_selenium_driver(show_browser_instance):
    options = Options()
    options.add_experimental_option("detach", True)
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("window_size=1280,800")
    options.add_argument("--disable-popup-blocking")
    options.add_argument("--disable-save-password-bubble")
    options.add_argument("--lang=en")
    options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36 Edg/91.0.864.59')
    if not show_browser_instance:
        options.add_argument('--headless')

    driver = webdriver.Chrome(options=options)
    return driver


def solve_captcha(driver):
    captcha_element = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, 'img.img-thumbnail.card-img-top.border-0'))
    )
    captcha_pic = captcha_element.screenshot_as_png

    with open('captcha_picture.png', 'wb') as file:
        file.write(captcha_pic)
    print('The picture is ready')

    solver = imagecaptcha()
    solver.set_verbose(1)
    solver.set_key("014a048cb9d6b3ba949dd6c76e2ce51b")
    solver.set_soft_id(0)

    captcha_text = solver.solve_and_return_solution("captcha_picture.png")
    if captcha_text != 0:
        print("captcha text " + captcha_text)
    else:
        print("task finished with error " + solver.error_code)
        raise Exception("Captcha solving failed")

    return captcha_text


def countdown_and_proceed(driver, btn_sbt, i):
    driver.implicitly_wait(5)
    if i >= 1:
        try:
            success_sent_likes = WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.XPATH, '//span[contains(text(), "Comment hearts successfully sent.")]')))
            print('Likes have been successfuly sent')
            time.sleep(2)
        except:
            print("Seems like we haven't achieved success in sending likes, or the script just can't detect the line approving that we sent them.\n Anyway, the script keeps going")
            pass
    try:
        countdown_before_proceeding = WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.CSS_SELECTOR, 'span.br.c-hearts-countdown'))).text

        seconds_cd = None
        minutes_cd = None

        splited_cd = countdown_before_proceeding.strip().split(' ')

        for index, cd_item in enumerate(splited_cd):
            if "second" in cd_item:
                seconds_cd = splited_cd[index - 1]
            if "minute" in cd_item:
                minutes_cd = splited_cd[index - 1]

        print(countdown_before_proceeding)

        print(f'Minutes: {minutes_cd}')
        print(f'Seconds: {seconds_cd}')

        time_cd_sec = int(minutes_cd) * 60 + int(seconds_cd) + 1.5
        time.sleep(time_cd_sec)

        btn_sbt.click()
    except:
        print('There was not a timer')
        pass

    btn_to_proceed = WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.XPATH, '//*[@id="c2VuZC9mb2xsb3dlcnNfdGlrdG9r"]/div[1]/div/form/button')))
    btn_to_proceed.click()


def locate_comment_and_like(driver, TT_USERNAME):
    local_i = 1
    while True:
        driver.implicitly_wait(5)
        list_page_elements = driver.find_elements(By.XPATH, '//div[@id="c2VuZC9mb2xsb3dlcnNfdGlrdG9r"]/div[1]//form')

        try:
            locate_username_element = WebDriverWait(driver, 5).until(EC.visibility_of_element_located((By.XPATH, f'//*[contains(text(), "{TT_USERNAME}")]')))
        except:
            print("Can't find the username on this page")
            locate_username_element = None
            pass

        if locate_username_element:
            try:
                driver.execute_script("arguments[0].scrollIntoView(true);", locate_username_element)
                time.sleep(1.5)
                like_element = locate_username_element.find_element(By.XPATH, './../../button')
                like_element.click()
                local_i = 1
                break
            except Exception as e:
                print("Like element, for some reason, isn't clickable")
                print(f"Exception: {e}")
        else:
            if local_i < len(list_page_elements):
                list_page_elements = driver.find_elements(By.XPATH,'//div[@id="c2VuZC9mb2xsb3dlcnNfdGlrdG9r"]/div[1]//form')
                list_page_elements[local_i].click()
                local_i += 1
                time.sleep(0.8)
                driver.implicitly_wait(3)
            else:
                print('All pages have been scanned for username but none is found. Ending the work of script...')
                driver.quit()
                sys.exit()


def main():
    driver = None
    try:
        while True:
            try:
                if driver:
                    driver.quit()
                driver = set_selenium_driver(SHOW_BROWSER_INSTANCE_OR_NOT)
                driver.get('https://zefoy.com')
                # driver.maximize_window()
                time.sleep(4.5)
                driver.implicitly_wait(5)

                try:
                    consroot = driver.find_element(By.CSS_SELECTOR, 'div.fc-consent-root')
                    manoptbtn = consroot.find_element(By.XPATH, './/*[contains(text(), "Manage options")]')
                    manoptbtn.click()
                    time.sleep(1.5)
                    consentbtn = consroot.find_element(By.XPATH, './/*[contains(text(), "Confirm choices")]')
                    consentbtn.click()
                except Exception as e:
                    print('Exception occured while consenting:', e)
                    pass

                time.sleep(3)

                captcha_text = solve_captcha(driver)

                text_box = driver.find_element(By.XPATH, './/input[@placeholder="Enter the word"]')
                text_box.click()
                text_box.send_keys(captcha_text)

                time.sleep(1.2)

                proceed_btn = driver.find_element(By.XPATH, './/button[@type="submit"]')
                proceed_btn.click()

                time.sleep(3)

                try:
                    exception_string = driver.find_element(By.XPATH,'//*[contains(text(), "Captcha code is incorrect.")]')
                    if exception_string:
                        print("The captcha result is wrong by the service's side. Restarting the script...")
                        continue
                except:
                    print("Captcha solved successfully")
                    break

            except Exception as e:
                print('Exception during CAPTCHA solving:', e)
                time.sleep(5)

        commentshearts_proceedbtn = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, '//*[contains(text(), "Comments Hearts")]/following-sibling::button')))
        commentshearts_proceedbtn.click()
        print("Proceeded to Comments Hearts")

        time.sleep(1.6)
        driver.implicitly_wait(5)

        form_element = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, '/html/body/div[9]/div/form/div')))
        time.sleep(1.5)

        input_box_url = form_element.find_element(By.XPATH, './input')
        input_box_url.click()
        time.sleep(0.67)
        input_box_url.send_keys(TT_LINK)
        time.sleep(0.84)
        btn_sbt = form_element.find_element(By.XPATH, './div/button')
        btn_sbt.click()

        time.sleep(0.8)

        try:
            slowdown = driver.find_element(By.XPATH, '//*[contains(text(), "Slow down")]')
            print('Give the scraper a rest, as the site gives you warnings to slow down.')
            raise SlowDownException
        except SlowDownException:
            driver.quit()
        except NoSuchElementException:
            print("'Slow down' site's warning isn't detected, proceeding..")
            pass
        except Exception as e:
            print(f'an unexpected exception occured in slowdown detection section: {e}')
            pass

        i = 0

        while i < ROUNDS:
            countdown_and_proceed(driver, btn_sbt, i)
            time.sleep(1.78)
            locate_comment_and_like(driver, TT_USERNAME)
            time.sleep(1.83)
            i += 1

        print('The end of the script')
        time.sleep(5)
        driver.quit()
        sys.exit()

    except Exception as e:
        print(f'Exception in main loop: {e}')
    finally:
        if driver:
            driver.quit()


if __name__ == '__main__':
    main()






