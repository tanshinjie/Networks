"""
Tan Shin Jie 1003715 - Networks lab 2
##### Crops Management Platform ####

Descriptions:
The is an attempt to create a backend for an imaginative crops business
There are two types of users to the system 
    1. Manager
    2. Worker

Both manager and worker are required to login with their credentials to use the system
Manager has access to all the services provided by the system, while
Worker only has access to the GET endpoints for crops monitoring purposes and check the tasks assigned by manager
The types of user are determined by the token attached in the request header

Supported services:
    1. Add new crop to                  - POST
    2. Add new schedule                 - POST 
    3. Remove the schedule by ID        - DELETE
    4. Update schedule by ID            - PUT
    5. Check all crops                  - GET
    6. Check all schedules              - GET
    7. Check crops health               - GET
    8. Check the environment conditions - GET

To Run: "python lab2_server.py"
"""

from flask import Flask
from flask import request, jsonify, make_response
import random, json

app = Flask(__name__)

# Authentication Constants
MANAGER = {"username": "superadmin", "password": "1234"}
WORKER = {"username": "admin", "password": "1234"}
MANAGER_TOKEN = "MANAGER_TOKEN"
WORKER_TOKEN = "WORKER_TOKEN"
FUNCTIONAL_SCOPE = {
    WORKER_TOKEN: ["/crops", "/env-status", "/crops-health", "/schedules"],
    MANAGER_TOKEN: [
        "/env-status",
        "/crops-health",
        "/schedules",
        "/crops",
        "/add-crop",
        "/add-schedule",
        "/remove-schedule",
        "/update-schedule",
    ],
}

# Global Variables
counter = 1
schedules = {"0": {"task": "irrigate", "repeat": "everyday 6pm", "id": "0"}}
crops = ["lime", "durain", "banana", "papaya"]
health_level = ["good", "medium", "bad"]


# Middleware to check the functional scope based on token before granting access
@app.before_request
def before_request_func():
    if request.path == "/" or request.path == "/login":
        return
    else:
        hasAuthHeader = request.headers.get("Authorization")
        if hasAuthHeader:
            auth_header = hasAuthHeader.split(" ")
            auth_type = auth_header[0]
            auth_body = auth_header[1]
            if auth_header[0] == "Bearer":
                if request.path not in FUNCTIONAL_SCOPE[auth_body]:
                    return make_response(
                        "You are not authorized to access the resources\n", 401
                    )
        else:
            return make_response(
                "Please provide token to access any resources.\nYou can login to get your token :)\n",
                200,
            )


# Home route that is reachable without authentication
@app.route("/", methods=["GET"])
def home():
    return make_response("Welcome to Crops Management System!\n", 200)


# Return all the crops that are managed by the system in string
@app.route("/crops", methods=["GET"])
def get_crops():
    global crops
    return make_response(json.dumps(crops) + "\n", 200)


# Return the health level (Bad, Medium, Good) of all the crops in JSON
@app.route("/crops-health", methods=["GET"])
def get_crops_health():
    global health_level, crops
    crops_health_data = {}
    for crop in crops:
        crops_health_data[crop] = health_level[random.randint(0, 2)]
    return make_response(jsonify(crops_health_data), 200)


# Return the environment status of the location in JSON
@app.route("/env-status", methods=["GET"])
def get_env_status():
    env_data = {
        "temperature": "33.0 degree celsius",
        "humidity": "60.5%",
        "ligh_intensity": "80.0%",
    }
    return make_response(jsonify(env_data), 200)


# Return all the schedules set by MANAGER
@app.route("/schedules", methods=["GET"])
def get_schedules():
    global schedules
    return make_response(jsonify(schedules), 200)


# Handle adding new crop to the system
# Return a message confirming the newly added crop
@app.route("/add-crop", methods=["POST"])
def add_crop():
    global crops
    new_crop = request.data.decode("utf-8")
    crops.append(new_crop)
    return make_response("New crop '{}' added!\n".format(new_crop), 201)


# Handle adding new schedule to the system
# Return the newly added schedule in JSON
@app.route("/add-schedule", methods=["POST"])
def add_schedule():
    global counter, schedules
    json_data = request.json
    response_data = json_data
    response_data["id"] = str(counter)
    schedules[str(counter)] = response_data
    counter += 1
    return make_response(jsonify(response_data), 201)


# Handle deleting schedule from the system, require id of the schedule
# Return the removed schedule in JSON
@app.route("/remove-schedule", methods=["DELETE"])
def remove_schedule():
    id = request.args.get("id")
    global schedules
    if id in schedules.keys():
        removed_schedule = schedules.pop(id)
        message = {"removed": removed_schedule}
        return make_response(jsonify(message), 200)
    else:
        return make_response("Schedule with id={id} not found\n".format(id=id), 400)


# Handle updating schedule from the system, require id of the schedule
# Return the updated schedule in JSON
@app.route("/update-schedule", methods=["PUT"])
def update_schedule():
    id = request.args.get("id")
    global schedules
    schedule_update = request.json
    if id in schedules.keys():
        schedule_update["id"] = id
        schedules[id] = schedule_update
        message = {"updated": schedules[id]}
        return make_response(jsonify(message), 200)
    else:
        return make_response("Schedule with id={id} not found\n".format(id=id), 400)


# Login route
@app.route("/login")
def login():
    hasAuthHeader = request.headers.get("Authorization")
    if hasAuthHeader:
        auth_header = hasAuthHeader.split(" ")
        credentials = auth_header[1].split(":")
        return do_the_login(credentials[0], credentials[1])
    else:
        return make_response("'username' and 'password' are required login.\n", 200)


# Login function
def do_the_login(username, password):
    if username == MANAGER["username"] and password == MANAGER["password"]:
        return "Welcome Manager! Your token is: " + MANAGER_TOKEN + "\n"
    elif username == WORKER["username"] and password == WORKER["password"]:
        return "Welcome Worker! Your token is: " + WORKER_TOKEN + "\n"
    else:
        return "Invalid username or password :(\n"


if __name__ == "__main__":
    app.run(debug=True, port=5000)  # run app in debug mode on port 5000

