from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

import json
import time
import traceback
import csv
# import wget

REQUIRED_POSTS = 100
driver = webdriver.Chrome()

with open("config.json") as config_file:
    config_data = json.load(config_file)
    username = config_data["username"]
    password = config_data["password"]


def url_cleaner(url):
    if url == None:
        return None
    target_index = url.find("?")
    return url[:target_index]


def write_to_csv(json_data, file_name):
    with open(file_name, "a") as myFile:
        keys = list(json_data[0].keys())
        # print(keys)
        # myFile.write(",".join(keys)+"\n")
        for row in json_data:
            row_csv = ''
            for key in keys:
                row_csv += '"' + str(row[key]).replace('"', '""') + '",'
            myFile.write(row_csv[:-1]+"\n")


def wait_for_element(selected_type, location, time, driver):
    types = {"name": By.NAME, "id": By.ID,
             "xpath": By.XPATH, "tag": By.TAG_NAME}
    element = WebDriverWait(driver, time).until(
        EC.presence_of_element_located((types[selected_type], location)))
    return element


def get_post_history():
    with open("test.csv", "r") as my_file:
        my_data = list(csv.reader(my_file))
        keys = my_data[0]
        historical_data = {}

        for i in range(1, len(my_data)):
            row_data = my_data[i]
            row_dict = {}
            for j in range(len(keys)):
                key = keys[j]
                row_dict[key] = row_data[j]
            historical_data[url_cleaner(row_dict["post_link"])] = row_dict
        return historical_data


def get_unique_id():
    with open("unique_posts.csv", "r") as my_file:
        my_data = list(csv.reader(my_file))
        return len(my_data)


def no_duplicate(curr_post, historical_data):
    if url_cleaner(curr_post["post_link"]) not in historical_data:
        return True
    else:
        old_post = historical_data[curr_post["post_link"]]
        if old_post["likes"] == curr_post["likes"] and old_post["comments"] == curr_post["comments"]:
            return False
        else:
            return True


def extract_tags(image_tags):
    tags = []

    if image_tags != "":
        parsed_tags = image_tags.split("@")[1:]
        for tag in parsed_tags:
            username = tag.split(" ")[0]
            tags.append(username)

    if len(tags) != 0:
        tags[-1] = tags[-1][:-1]
    return tags


driver.get("https://www.instagram.com/")


username_input = wait_for_element("name", "username", 5, driver)
username_input.send_keys(username)

password_input = driver.find_element_by_name('password')
password_input.send_keys(password)

login_button = driver.find_element_by_xpath(
    '/html/body/div[1]/section/main/article/div[2]/div[1]/div/form/div[4]/button')
login_button.click()


no_notif = wait_for_element(
    "xpath", "/html/body/div[4]/div/div/div[3]/button[2]", 5, driver)

no_notif.click()

driver.execute_script("location.reload()")
time.sleep(5)

# no_notif = wait_for_element(
#     "xpath", "/html/body/div[4]/div/div/div[3]/button[2]", 5, driver)

# no_notif.click()

wait_for_load_buffer = wait_for_element(
    "xpath", "/html/body/div[1]/section/main/section/div[1]/div[1]/div/article[1]", 5, driver)
loaded_posts = wait_for_element(
    "xpath", "/html/body/div[1]/section/main/section/div[1]/div[1]/div", 5, driver).find_elements_by_tag_name("article")

initial_loaded_posts = len(loaded_posts)
# #print(initial_loaded_posts)

'''
username
userpage link
likes
comments
tags
time_since_posted
'''

post_data = {}
post_csv_json = []
post_count = 0

post_id = 1
unique_posts = []
historical_data = get_post_history()
# for i in range(1, initial_loaded_posts+1):
i = 1
while post_count < REQUIRED_POSTS:
    # print()
    curr_post = {"username": None, "likes": None, "comments": None, "tags": None,
                 "time_posted": None, "caption": None, "curr_time": None, "is_video": None, "post_link": None}
    curr_unique_post = {"post_id": None, "username": None, "post_link": None}

    # try:
    post_xpath = "/html/body/div[1]/section/main/section/div[1]/div[1]/div/article["+str(
        i)+"]"

    user_details_xpath = post_xpath+"/div[2]/div[1]/div[1]/div/a"
    post_user_details = wait_for_element(
        "xpath", user_details_xpath, 5, driver)
    post_caption_xpath = post_xpath+"/div[2]/div[1]/div[1]/div/span"
    post_caption_details = wait_for_element(
        "xpath", post_caption_xpath, 5, driver)
    more = post_caption_details.find_elements_by_xpath(".//span")
    likes_div_xpath = post_xpath+"/div[2]/section[2]/div"
    comments_div_xpath = post_xpath+"/div[2]/div[1]/div[2]/div[1]/a"
    posted_time_div = post_xpath+"/div[2]/div[2]/a/time"

    video_src = None
    image_src = None
    is_video = False
    image_tags = []
    try:
        video_src = wait_for_element(
            "xpath", post_xpath+"/div[1]/div", 5, driver).find_element_by_tag_name("video").get_attribute("src")
    except:
        pass

    if (video_src):
        is_video = True

    if not is_video:
        image_node = wait_for_element(
            "xpath", post_xpath+"/div[1]/div", 5, driver).find_element_by_tag_name("img")
        image_src = image_node.get_attribute("src")
        image_tags = image_node.get_attribute("alt")

        image_tags = extract_tags(image_tags)

    if url_cleaner(video_src) in post_data or url_cleaner(image_src) in post_data:

        loaded_posts = wait_for_element(
            "xpath", "/html/body/div[1]/section/main/section/div[1]/div[1]/div", 5, driver).find_elements_by_tag_name("article")

        num_loaded = len(loaded_posts)

        if i < num_loaded:
            i += 1
        elif i > num_loaded:
            i = num_loaded
        else:
            driver.execute_script("window.scrollBy(0, 900);")
            time.sleep(2)

        continue

    likes_span = wait_for_element(
        "xpath", likes_div_xpath, 5, driver).find_elements_by_tag_name("span")[-1]
    try:
        comments_span = wait_for_element(
            "xpath", comments_div_xpath, 2, driver).find_element_by_tag_name("span")
    except:
        comments_span = None
    posted_time = wait_for_element(
        "xpath", posted_time_div, 5, driver).get_attribute("datetime")
    # except Exception as err:
    #     #print(err)
    #     traceback.#print_exc()
    #     driver.execute_script("window.scrollBy(0,50)")
    #     continue
    # posted_time = driver.execute_script("new Date("+posted_time+")")

    # #print(image_tags)
    if len(more) > 1:
        # #print(more[1].find_element_by_tag_name("button"))
        more[1].find_element_by_tag_name("button").click()
        if post_count >= initial_loaded_posts:

            change = 0
            checker_src = ''
            while (url_cleaner(checker_src) != url_cleaner(image_src) and url_cleaner(checker_src) != url_cleaner(video_src)):
                checker_xpath = "/html/body/div[1]/section/main/section/div[1]/div[1]/div/article["+str(
                    i-change)+"]/div[1]/div"
                checker_node = wait_for_element(
                    "xpath", checker_xpath, 5, driver)
                try:
                    checker_src = checker_node.find_element_by_tag_name(
                        "video").get_attribute("src")
                    if checker_src != video_src:
                        change += 1
                except:
                    checker_src = checker_node.find_element_by_tag_name(
                        "img").get_attribute("src")
                    if checker_src != image_src:
                        change += 1
            # print(change)
            # if change:
            post_caption_xpath = "/html/body/div[1]/section/main/section/div[1]/div[1]/div/article["+str(
                i-change)+"]/div[2]/div[1]/div[1]/div/span"
        post_caption_details = wait_for_element(
            "xpath", post_caption_xpath, 5, driver)
        if post_count > initial_loaded_posts:
            i -= 1
    post_caption = post_caption_details.get_attribute("innerText")
    post_user_profile = post_user_details.get_attribute("href")
    post_user_name = post_user_details.get_attribute("innerText")
    likes = likes_span.get_attribute("innerText")
    if comments_span:
        comments = comments_span.get_attribute("innerText")
    else:
        comments = '0'

    datetime_extraction_script = 'return new Date("' + \
        posted_time+'").toString()'
    # #print(datetime_extraction_script)
    posted_time = driver.execute_script(datetime_extraction_script)
    # if is_video:
    #     #print("Video src", video_src)
    # else:
    #     #print("Name: "+post_user_name+" image_Src: "+image_src)

    curr_post["username"] = post_user_name
    curr_post["likes"] = likes
    curr_post["comments"] = comments
    curr_post["tags"] = str(image_tags)
    curr_post["time_posted"] = posted_time
    curr_post["caption"] = post_caption
    curr_post["curr_time"] = driver.execute_script(
        "return new Date().toString()")
    curr_post["is_video"] = is_video
    if is_video:
        curr_post["post_link"] = video_src
        curr_unique_post["post_link"] = video_src
        # wget.download(video_src, "./files/"+str(post_id)+".mp4")
    else:
        curr_post["post_link"] = image_src
        curr_unique_post["post_link"] = image_src
        # wget.download(video_src, "./files/"+str(post_id)+".jpg")

    # curr_unique_post["id"] = post_id
    # post_id += 1
    curr_unique_post["username"] = post_user_name

    # #print("Loaded", num_loaded)

    # if curr_post["post_link"] not in post_data:
    post_data[url_cleaner(curr_post["post_link"])] = True
    # post_csv_json.append(curr_post)
    # unique_posts.append(curr_unique_post)
    if no_duplicate(curr_post, historical_data):
        write_to_csv([curr_post], "test.csv")

    if url_cleaner(curr_post["post_link"]) not in historical_data:
        curr_unique_post["post_id"] = get_unique_id()
        write_to_csv([curr_unique_post], "unique_posts.csv")
    post_count += 1
    # print(post_count)
    # print(curr_post)
    driver.execute_script("window.scrollBy(0, 900);")
    time.sleep(2)

    # #print("post count", post_count)

# write_to_csv(post_csv_json, "test.csv")
# write_to_csv(unique_posts, "unique_posts.csv")

driver.quit()
