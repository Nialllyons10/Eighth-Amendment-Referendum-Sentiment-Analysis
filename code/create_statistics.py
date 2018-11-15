#Output is added to csv files as requested by UI as highchart.js reads data from csv

def total_overall_sentiment(t, p, n): #Calculates percentage of negative and positive tweets

    total_neg = round(((n/t)*100), 2)
    total_pos = round(((p/t)*100), 2)
    return total_neg, total_pos

def location_stats(countries, counties, user_info, total): #finds locations and sorts them into the appropriate dictionary

    for line in user_info:
        line = line.strip("\n")
        line = line.split(" ")

        user_locat = line[-2]

        if user_locat == "null": #user hasn't specified where they are from
            countries["null"] += 1
        elif user_locat == "ireland": #user has Ireland as their location but has not specified a county
            countries["ireland"] += 1
            counties["unknown"] += 1
        elif user_locat in counties: #User is from a county in Ireland
            counties[user_locat] += 1
            countries["ireland"] += 1
        else:
            countries["other"] += 1 #User is from somewhere else in the World


    country_stats(countries, total, "/var/www/html/country_stats.csv")
    county_stats(counties, countries, "/var/www/html/county_stats.csv")


def country_stats(countries, total, file): #calculates country stats in percentages

    open(file, "w").close() #deletes previous data as is being recalculated frequently
    country_file = open(file, "w")
    country_file.write("Country,Precentage\n")

    for country in countries:
        stat = calculate_location_stats(countries, country, total)
        country_file.write(country + "," + str(stat) + "\n")


def county_stats(counties, countries, file): #calculates county stats in ireland in percentages

    open(file, "w").close() #deletes previous data as is being recalculated frequently
    county_file = open(file, "w")
    county_file.write("County,Precentage\n")

    total_counties = countries["ireland"]

    for county in counties:
        stat = calculate_location_stats(counties, county, total_counties)
        county_file.write(county + "," + str(stat) + "\n")

def calculate_location_stats(dict, locat, tot): #calculates stats for each location
    stat = round(((dict[locat]/tot)*100), 2)
    return stat

def main():
    counties = {"unknown": 0,
                 "antrim": 0,
                 "armagh": 0,
                 "carlow": 0,
                 "cavan": 0,
                 "clare": 0,
                 "cork": 0,
                 "derry": 0,
                 "donegal": 0,
                 "down": 0,
                 "dublin": 0,
                 "fermanagh": 0,
                 "galway": 0,
                 "kerry": 0,
                 "kildare": 0,
                 "kilkenny": 0,
                 "laois": 0,
                 "leitrim": 0,
                 "limerick": 0,
                 "longford": 0,
                 "louth": 0,
                 "mayo": 0,
                 "meath": 0,
                 "monaghan": 0,
                 "offaly": 0,
                 "roscommon": 0,
                 "sligo": 0,
                 "tipperary": 0,
                 "tyrone": 0,
                 "waterford": 0,
                 "westmeath": 0,
                 "wexford": 0,
                 "wicklow": 0}

    countries = {"ireland": 0,
                 "other": 0,
                 "null": 0}

    negative = 0
    positive = 0
    total = 0
    data = open("data/all_tweets.json", "r").readlines()

    open("/var/www/html/overall_sa_stats.csv", "w").close() #deletes previous data as is being recalculated frequently
    neg_pos_file = open("/var/www/html/overall_sa_stats.csv", "w")


    for line in data: #finds Sentiment Analysis score and checks if it is negative or positive
        total += 1
        line = line.strip("\n")
        line = line.split(" ")

        sent_score = float(line[-1])

        if sent_score > 0 and sent_score <= 0.5: #checks if sentiment score is negative
            negative += 1
        if sent_score > 0.5 and sent_score <= 1.0: #checks if sentiment score is positive
            positive += 1

    t_n, t_p = total_overall_sentiment(total, positive, negative)
    neg_pos_file.write("Categories,Negative,Positive\n")
    neg_pos_file.write("Sentiment Score," + str(t_n) + "," + str(t_p)) #writes stats to csv file for UI to read

    location_stats(countries, counties, data, total) #categorises locations and produces stats to csv file

    open("/var/www/html/total_num_tweets.csv", "w").close()
    new_f = open("/var/www/html/total_num_tweets.csv", "w")
    new_f.write("Categories,Tweets\nAmount," + str(total)) #writes total amount of tweets to csv file for UI to read


if __name__ == "__main__":
    main()