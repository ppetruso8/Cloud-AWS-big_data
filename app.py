from flask import Flask, render_template, request, redirect, url_for, session, get_flashed_messages
import json

app = Flask(__name__)

@app.route("/")
def index():
    stats_file = open('data.json')
    data = json.load(stats_file)

    years = data["dimension"]["TLIST(A1)"]["category"]["label"]
    ages = data["dimension"]["C02076V03371"]["category"]["label"]
    genders = data["dimension"]["C02199V02655"]["category"]["label"]
    population = data["value"]

    stats = []

    i = 0
    for year in years.values():
        for age in ages.values():
            for gender in genders.values():
                stats.append({
                    "year": year,
                    "age": age,
                    "gender": gender,
                    "population": population[i]
                })
                i += 1
    
    return render_template("index.html", stats=stats)

if __name__ == "__main__":
    app.run()