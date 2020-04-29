import csv
import pprint as pp
import copy


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
    start_index = i+1
    return url[start_index:target_index]


def parse_data(file_name):

    with open(file_name, "r") as my_file:
        data = list(csv.reader(my_file))
        keys = data[0]
        data_json = []
        for raw_data in data[1:]:
            data_row = {}
            for i in range(len(keys)):
                key = keys[i]
                data_row[key] = raw_data[i]
            data_json.append(data_row)

    return data_json


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


posts_data = parse_data("test.csv")
unique_posts = parse_data("unique_posts.csv")


unique_posts_id = {}

for post in unique_posts:
    unique_posts_id[url_cleaner(post["post_link"])] = post

# pp.pprint(unique_posts_id)
merged_post_data = []

for post in posts_data:

    new_post = copy.deepcopy(post)
    new_post["id"] = unique_posts_id[url_cleaner(post["post_link"])]["id"]
    merged_post_data.append(new_post)


write_to_csv(merged_post_data, "post_data.csv")
