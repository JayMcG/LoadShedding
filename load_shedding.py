from bs4 import BeautifulSoup
import requests
import json

# APIs
base_api = "https://loadshedding.eskom.co.za/LoadShedding/"
status_api = base_api + "GetStatus/"
province_api = base_api + "GetMunicipalities/?Id="
suburb_api = base_api + "GetSurburbData/?pageSize={size}&pageNum={pg_no}&id={id}"
schedule_api = base_api + "GetScheduleM/"

# Load shedding stages
stages = {
    1: "No load shedding", 
    2: "Stage 1", 
    3: "Stage 2", 
    4: "Stage 3", 
    5: "Stage 4",
    6: "Stage 5",
    7: "Stage 6",
    8: "Stage 7",
    9: "Stage 8"
    }

# Predefined provinces
provinces = {
    1: "Eastern Cape",
    2: "Free State",
    3: "Gauteng",
    4: "KwaZulu-Natal",
    5: "Limpopo",
    6: "Mpumalanga",
    7: "North West",
    8: "Northern Cape",
    9: "Western Cape",
    }

# Final results from the search
results = {}


# Get the status of load shedding and return "stage"
def get_status(status_api):
    print("Let's check the current load shedding status")
    print("Searching now...")

    response = requests.get(status_api)
    if response.status_code == 200:
        response_result = response.text
        search_result = json.JSONDecoder().decode(response_result)
        stage = search_result
        print("The current status is: \"{}\"".format(stages[search_result]))
        return stage
    else:
        print("Error, status code: ", response.status_code)


# Check the municipality
def get_municipality():
    print()
    print("Let's check which Province you fall under, please select from one of the following:")
    
    # Identify the user's province
    for province in provinces.items():
        print("{number}: {name}".format(number= province[0], name= province[1]))
    province_id = input("Enter the corresponding number for your selection (e.g: 1): ")

    print()
    print("Thank you, searching for {province}...".format(province=provinces[int(province_id)]))
    print()

    # Identify the user's suburb
    response = requests.get(province_api + str(province_id))
    response_result = response.text
    search_result = json.JSONDecoder().decode(response_result)
    
    print("Here are the Municipalities I found under {province}:".format(province=provinces[int(province_id)]))
    
    cities = []
    for result in search_result:
        print("{number}: {name}".format(number= search_result.index(result), name= result["Text"]))
        cities.append(result["Value"])
    answer = input("Enter the corresponding number for your selection (e.g: 1): ")
    
    print()
    print("Thank you, searching for {}".format(search_result[int(answer)]["Text"]))
    
    city_id = cities[int(answer)]
    
    return province_id, city_id
  

# Find the suburb
def get_suburb(city_id):
    size = 10000 # Not sure of size limit but value executes
    pg_no = 1
    cities = []
    
    response = requests.get(suburb_api.format(size=str(size), pg_no=str(pg_no), id=str(city_id)))
    response_result = response.text
    search_result = json.JSONDecoder().decode(response_result)
    print()
    answer = input("Kindly provide the first 3 letters of your Suburb: ")
    print("Here are the results I found: ")
    
    for result in search_result["Results"]:
        if result["Tot"] >= 0 and answer.lower().strip() in result["text"].lower():
            cities.append([result["id"], result["text"], result["Tot"]])
    
    for city in enumerate(cities):
        print("{index}: {city}".format(index=city[0], city=city[1][1]))

    get_city = input("Kindly confirm your suburb from the results above: ")
    suburb_id = cities[int(get_city)]
    
    return suburb_id


# Get the schedule
def get_schedule(suburb_id, stage, province_id, municipality_total):
    print()
    print("Let's get that schedule using the following url:")
    print(schedule_api + str(suburb_id) + "/" + str(stage) + "/" + str(province_id) + "/" + str(municipality_total))
    print()
    print("Ok, this is what I found:")
    print()

    url = schedule_api + str(suburb_id) + "/" + str(stage) + "/" + str(province_id) + "/" + str(municipality_total)
    html_text = requests.get(url).text
    soup = BeautifulSoup(html_text, 'html.parser')

    for item in soup.findAll("div", class_= "scheduleDay"):
        days = item.text.strip()
        times = []
        for time in item("a"):
            times.append(time.text.strip())
        results[days[:7]] = times


# Start search
def start_search():
    answer = input("Hello, do you want to check for load shedding?: (Yes to continue) ")
    if answer.lower().strip() == "yes":
        status = get_status(status_api)
        return status
    else:
        print("Sorry, no valid input")
        start_search()


# Execute program
def execute():
    stage = start_search()
    if stage == 1:
        print()
        answer = input("Do you still want to check the schedule? (Yes to continue): ")
        if answer.lower().strip() == "yes":
            municipality = get_municipality()
            suburb_id = get_suburb(municipality[1])
            get_schedule(suburb_id[0], stage, municipality[0], suburb_id[2])
        else:
            print("Goodbye")
    else:
        municipality = get_municipality()
        get_schedule(suburb_id[0], stage, municipality[0], suburb_id[2])


execute()
for result in results.items():
    if result[1] == []:
        print("{result}: None".format(result=result[0]))
    else:
        print("{result}: {times}".format(result=result[0], times=result[1]))
