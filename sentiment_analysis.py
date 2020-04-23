import paralleldots
import csv
import json

with open("config.json", "r") as my_file:
    config_data = json.load(config_file)
    api_key = config_data["paralleldots_key"]

paralleldots.set_api_key(api_key)

lang_code = "en"


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


my_data = parse_data("post_data.csv")
unique_data = {}
for data in my_data:
    unique_data[data["post_id"]] = data


captions = []
ids = []
for key in unique_data:
    ids.append(key)
    captions.append(unique_data[key]["caption"])

print(len(captions))
print(len(ids))
# response = paralleldots.batch_sentiment(captions, lang_code)
# sentiments = response["sentiment"]

with open("clean_response.txt", "r") as my_file:
    sentiments = json.load(my_file)


# with open("response.txt", "w") as my_file:
#     my_file.write(str(response))
sentiment_analysis_data = []
print(len(sentiments))
for i in range(len(sentiments)):
    caption_data = {"post_id": None,
                    "caption": None, "sentiment_analysis": None}
    caption_data["post_id"] = ids[i]
    caption_data["caption"] = captions[i]
    caption_data["sentiment_analysis"] = sentiments[i]
    write_to_csv([caption_data], "caption_sentiment_analysis.csv")
    sentiment_analysis_data.append(caption_data)
print(sentiment_analysis_data)

# write_to_csv(sentiment_analysis_data, "caption_sentiment_analysis.csv")

# test_text = ["Hello my name is Naseer", "I am super depressed today"]
# response = paralleldots.batch_sentiment(test_text, lang_code)


# with open("response.txt", "r") as my_file:
#     # response = my_file.read()
#     my_dict = json.load(my_file)

# cleaned_data = []

# sentiments = my_dict["sentiment"]

# for stuff in sentiments:
#     if "code" not in stuff:
#         cleaned_data.append(stuff)

# with open("clean_response.txt", "w") as my_file:
#     my_file.write(str(cleaned_data))
