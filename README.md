# **Instagram Likes Predictor**
*By Khan Naseer Ahmed, Koppar Devansh Sunil & Garodia Shivanshi*

*The github repository and the scraped data for this project can be found [here](https://github.com/naseer2426/Data-Analysis-Project)*

---

## **Introduction**

This is a data science project that is prepared in fulfilment of the module requirements (CE9010 - Introduction to Data Science). This notebook will discuss the following:



*   The Data - Problem, Acquisition and Exploration
*   Pre-Processing and Data Analysis

## **Objective & The Data Problem**

Have you ever wanted to know how many likes your instagram post will get, before even posting it? Is it possible to predict the number of likes on Instagam? This question was the motivation behind our data analysis project.

In this notebook, we create a regression model that predicts instagram likes from scratch.

## **Data Acquisition**
### - Khan Naseer Ahmed (U1722257F)

The data was collected using a Selenium web scrapper that scrapped instagram.com. All the code used for scrapping is  [here](https://github.com/naseer2426/Data-Analysis-Project).  This web scrapper collected data on top 20 posts on my instagram feed. This data included, likes, comments, people tagged, caption, sentiment analysis of the caption, number of followers/following of the user.

Sentiment analysis was done using the paralleldots API.

The web scrapper was run as a sub-process in a javascript code that was also running a discord bot. This javascript code ran the web scrapper subprocess as a cron job every 6 minutes for around 3 days. 

```javascript
var scrape = () => {
    const channel = client.channels.cache.get("701711183824289806");
    console.log("started scrapping");
    channel.send("Scrapping session finsished");
    var stdout = child.execSync("python3 scrapper.py").toString();
    channel.send(stdout);
};

var job = new CronJob("0 0,6,12,18,24,30,36,42,48,54 * * * *", function () {
    scrape();
});
job.start();
```

The discord bot was set up so that to track the process of the scrapper. It could tell how many posts had been scrapped. It would also send error messages if the web scrapper failed for any reason.


##### **Problems faced while scrapping**

Since instagram is an infinte scroll type of website, the web page doesn't load in all the posts at once. Depending on the size of the post, it loads in 5-8 posts. Once you start scrolling, it unloads the old posts and loads the new posts. 

This was the most difficult problem to solve. There was a need to uniquely identify a post, since its position on the HTML kept changing depeinding on how many posts before it have been unloaded, and how many posts after it have been loaded. 

Initially the post was uniquely identified with the src tag of the image/video in the post. This logic eventually failed becuase instagram sources the images from different databases depending traffic. This meant the src link of the same post changed depending on traffic.

The src url had to be parsed to find the unique identifier of an image irrespective of the database its being sourced from.

```python
def url_cleaner(url):
    if url == None:
        return None
    target_index = url.find("?")
    start_index = target_index
    if start_index == -1:
        return None
    for i in range(start_index, -1, -1):
        if url[i] == "/":
            break
    start_index = i
    return url[start_index+1:target_index]
```

After finding the unique identifier for a post, the logic of scrapping the data and scrolling distance had to be developed.


Posts that haven't changed any data (liks,comments etc) had to be excluded from the csv file to avoid duplicates. The logic that handled all this is given below.

```python
while post_count < REQUIRED_POSTS:
        
        curr_post = {"username": None, "likes": None, "comments": None, "tags": None,
                     "time_posted": None, "caption": None, "curr_time": None, "is_video": None, "post_link": None}
        curr_unique_post = {"post_id": None,
                            "username": None, "post_link": None}

        
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
        
        if len(more) > 1:
            
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
        
        posted_time = driver.execute_script(datetime_extraction_script)
       

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
            
        else:
            curr_post["post_link"] = image_src
            curr_unique_post["post_link"] = image_src
            

        
        curr_unique_post["username"] = post_user_name
        post_data[url_cleaner(curr_post["post_link"])] = True
        
        if no_duplicate(curr_post, historical_data):
            write_to_csv([curr_post], "test.csv")

        
        if url_cleaner(curr_post["post_link"]) not in historical_data:
            curr_unique_post["post_id"] = get_unique_id()
            write_to_csv([curr_unique_post], "unique_posts.csv")
        post_count += 1
        
        driver.execute_script("window.scrollBy(0, 900);")
        time.sleep(2)
```

