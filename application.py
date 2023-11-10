# import libraries
from flask import Flask, render_template
import requests
import pymysql

'''Application'''
# initialize Flask application
application = app = Flask(__name__)

@app.route("/")
def index():
    # source: https://realpython.com/api-integration-in-python/
    # API URL to fetch data
    api_url = "https://ws.cso.ie/public/api.restful/PxStat.Data.Cube_API.ReadDataset/FY002/JSON-stat/2.0/en"
    # fetch data and process into a list
    data = get_data(api_url)
    population_by_year = process_data(data)
        
    # get statistics from data    
    avg_population = get_avg_population(population_by_year)
    most_populated_year, most_population = get_most_population(population_by_year)
    median_population = get_median(population_by_year)
    total_growth, total_growth_percentage = get_total_growth(population_by_year)

    '''DB'''
    # establish connection to the database
    connection = pymysql.connect(host = 'awseb-e-tvrufpsf75-stack-awsebrdsdatabase-wwiq7tqabdft.csqu5agax8wn.eu-west-1.rds.amazonaws.com',
                            port = 3306,
                            user = 'ppetruso',
                            password = '1234512345',
                            database = 'ebdb'
                            )
    
    # create cursor to execute database queries with
    cursor = connection.cursor()

    # create table for population by year
    try: 
        cursor.execute("""DROP TABLE IF EXISTS population_by_year;""")
        cursor.execute("""CREATE TABLE population_by_year (
                                year VARCHAR(4) NOT NULL PRIMARY KEY,
                                total_population INT,
                                male_population INT,
                                female_population INT,
                                most_populous_age_group VARCHAR(20),
                                most_populous_age_group_population INT
                                );""")

        # insert values into the table 
        for yr in population_by_year: 
            cursor.execute("""INSERT INTO population_by_year (year, total_population, male_population, female_population, most_populous_age_group, most_populous_age_group_population)
                            VALUES (%s, %s, %s, %s, %s, %s);""", 
                            (yr['year'], yr['population'], yr['male'], yr['female'], 
                             yr['most_populous_age_group'], yr['most_populous_age_group_population']))
            connection.commit()

    except pymysql.Error as e:
        print("Error: " + str(e))

    # create table for general statistics
    try:
        cursor.execute("""DROP TABLE IF EXISTS general_stats;""")
        cursor.execute("""CREATE TABLE general_stats (
                        id INT AUTO_INCREMENT PRIMARY KEY,
                        avg_population INT,
                        median_population INT,
                        population_growth INT,
                        population_growth_percentage FLOAT,
                        most_populated_year VARCHAR(4),
                        most_population INT
                        );""")
        # insert values into the table
        cursor.execute("""INSERT INTO general_stats (avg_population, median_population, population_growth, population_growth_percentage, most_populated_year, most_population)
                       VALUES (%s, %s, %s, %s, %s, %s);""", 
                       (avg_population, median_population, total_growth, total_growth_percentage, most_populated_year, most_population))
        connection.commit()

    except pymysql.Error as e:
            print("Error: " + str(e))

    # close database connection
    cursor.close()
    connection.close()
    
    # render index.html template with data
    return render_template("index.html", population_by_year=population_by_year, avg_population=avg_population,
                           median_population=median_population, most_populated_year=most_populated_year, 
                           most_population=most_population, total_growth=total_growth, total_growth_percentage=total_growth_percentage)

# function for fetching data from API url
def get_data(url):
    '''
    url -- API URL containing data
    '''
    # get data
    response = requests.get(url)
    # convert JSON response into python dictionary
    return response.json()

# function for processing fetched data
def process_data(data):
    '''
    data -- dictionary containing fetched data from API 
    '''
    # extract years, ages, genders and population from data
    years = data["dimension"]["TLIST(A1)"]["category"]["label"]
    ages = data["dimension"]["C02076V03371"]["category"]["label"]
    genders = data["dimension"]["C02199V02655"]["category"]["label"]
    population = data["value"]

    # list of dictionaries storing processed data
    population_by_year = []
    # iteration indices
    value_index = 0
    year_index = 0

    # process data and organize by year
    for year in years.values():
        # store population of age groups for year
        age_group_population = {}
        for age in ages.values():
            for gender in genders.values():
                # get each age group population
                if age != "All ages" and gender == "Both sexes":
                    age_group_population[age] = int(population[value_index])

                # get total population by year
                if age == "All ages": 
                    # organize data by gender 
                    if gender == "Both sexes":
                        population_by_year.append({
                            "year": year,
                            "population": int(population[value_index])
                        })
                    elif gender == "Male":
                        population_by_year[year_index]["male"] = int(population[value_index])
                    else:
                        population_by_year[year_index]["female"] = int(population[value_index])

                # increment current position in "population"
                value_index += 1

        # get the most populous age group and its population for year    
        most_populous_age_group = max(age_group_population, key=age_group_population.get)
        most_populous_age_group_population = age_group_population[most_populous_age_group]

        # store most populous age group and its population in list
        population_by_year[year_index]["most_populous_age_group"] = most_populous_age_group
        population_by_year[year_index]["most_populous_age_group_population"] = most_populous_age_group_population

        # increment current position in "population_by_year" list
        year_index +=1

    return population_by_year

# function to calculate average population
def get_avg_population(population_data):
    '''
    population_data -- list containing population data by year
    '''
    total_population = 0

    # iterate through the input list to get total population
    for value in population_data:
        total_population += (value["population"])

    # calculate average population
    avg_population = total_population / len(population_data)

    return int(avg_population)

# function to get the most populated year and its population
def get_most_population(population_data):
    '''
    population_data -- list containing population data by year
    '''
    most_populated_year = ""
    most_population = 0

    # iterate through the input list to find most populated year and its population
    for value in population_data:
        if value["population"] > most_population:
            most_population = value["population"]
            most_populated_year = value["year"]

    return (most_populated_year, most_population)

# function to get the median value of population
def get_median(population_data):
    '''
    population_data -- list containing population data by year
    '''
    populations = []

    # iterate through the input list and store each year's population
    for value in population_data:
        populations.append(value["population"])
    
    populations.sort()

    # calculate median value
    n = len(populations)
    if n % 2 == 1:
        median = populations[n // 2]
    else:
        median = (populations[n // 2 - 1] + populations[n // 2]) / 2
    
    return median

# function to get the total growth of the population
def get_total_growth(population_data):
    '''
    population_data -- list containing population data by year
    '''
    first_year_population = population_data[0]["population"]
    last_year_population = population_data[-1]["population"]

    # calculate total growth
    total_growth = last_year_population - first_year_population
    total_growth_percentage = round(((total_growth / first_year_population) * 100), 2)

    return (total_growth, total_growth_percentage)

# start the Flask web application
if __name__ == "__main__":
    app.run()