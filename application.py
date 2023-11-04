from flask import Flask, render_template
import requests

application = app = Flask(__name__)

@app.route("/")
def index():
    # source: https://realpython.com/api-integration-in-python/
    api_url = "https://ws.cso.ie/public/api.restful/PxStat.Data.Cube_API.ReadDataset/FY002/JSON-stat/2.0/en"
    response = requests.get(api_url)
    data = response.json()

    years = data["dimension"]["TLIST(A1)"]["category"]["label"]
    ages = data["dimension"]["C02076V03371"]["category"]["label"]
    genders = data["dimension"]["C02199V02655"]["category"]["label"]
    population = data["value"]

    all_stats = []
    population_by_year = []

    value_index = 0
    year_index = 0
    for year in years.values():
        for age in ages.values():
            for gender in genders.values():
                all_stats.append({
                    "year": year,
                    "age": age,
                    "gender": gender,
                    "population": int(population[value_index])
                })
                if age == "All ages": 
                    if gender == "Both sexes":
                        population_by_year.append({
                            "year": year,
                            "population": int(population[value_index])
                        })
                    elif gender == "Male":
                        population_by_year[year_index]["male"] = int(population[value_index])
                    else:
                        population_by_year[year_index]["female"] = int(population[value_index])
                value_index += 1
        year_index +=1
        
        
    avg_population = get_avg_population(population_by_year)
    
    return render_template("index.html", population_by_year=population_by_year)

def get_avg_population(population_list):
    total_population = 0
    for value in population_list:
        total_population += (value["population"])
    avg_population = total_population / len(population_list)
    return int(avg_population)



if __name__ == "__main__":
    app.run()