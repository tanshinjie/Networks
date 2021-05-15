# Tan Shin Jie 1003715 - Networks Lab 
# Crops Management System

echo "========== Example 1 =========="
# Home route '/' is reachable without any authentication
curl http://localhost:5000
echo -e '\n'

echo "========== Example 2 =========="
# User can login by providing their username and password in the header to /login route
# There are 2 types of user to the APIs: MANAGER and WORKER
echo "========== Example 2.1 =========="
# 'superadmin' and '1234' is the username and password for MANAGER
# The response is a token 'MANAGER_TOKEN' that allows access to all other endpoints
curl -H "Authorization: Basic superadmin:1234" http://localhost:5000/login
curl -H "Authorization: Basic Superadmin:1234" http://localhost:5000/login
echo -e '\n'

echo "========== Example 2.2 =========="
# 'admin' and '1234' is the username and password for WORKER
# The response is a token 'WORKER_TOKEN' that only allows access to GET endpoints
curl -H "Authorization: Basic admin:1234" http://localhost:5000/login
curl -H "Authorization: Basic Admin:1234" http://localhost:5000/login
echo -e '\n'

echo "========== Example 3 =========="
# Send and receive json data
echo "POST request with Content-Type: application/json"
curl -X POST -H "Content-Type: application/json" -H "Authorization: Bearer MANAGER_TOKEN" -d '{"task":"fertilize durian","repeat":"every 24 hours"}' http://localhost:5000/add-schedule
echo -e '\n'

echo "========== Example 4 =========="
# Send and receive text data
echo "POST request with Content-Type: application/text"
curl -X POST -H "Content-Type: application/text" -H "Authorization: Bearer MANAGER_TOKEN" -d 'strawberry' http://localhost:5000/add-crop
echo -e '\n'


echo "========== Example 5 =========="
# MANAGER is allowed to access all endpoints, e.g. GET, POST, UPDATE, DELETE
echo "----- MANAGER POST new schedule ----- "
curl -X POST -H "Content-Type: application/json" -H "Authorization: Bearer MANAGER_TOKEN" -d '{"task":"irrigate banana","repeat":"every 6 hours"}' http://localhost:5000/add-schedule

echo " ----- MANAGER POST new crop ----- "
curl -X POST -H "Content-Type: application/text" -H "Authorization: Bearer MANAGER_TOKEN" -d 'pineapple' http://localhost:5000/add-crop

echo " ----- MANAGER PUT schedule ----- "
curl -X PUT -H "Content-Type: application/json" -H "Authorization: Bearer MANAGER_TOKEN" -d '{"task":"irrigate lime","repeat":"every 15 hours"}'  http://localhost:5000/update-schedule?id=0 

echo " ----- MANAGER DELETE schedule ----- "
curl -X DELETE -H "Content-Type: application/json" -H "Authorization: Bearer MANAGER_TOKEN" http://localhost:5000/remove-schedule?id=0 

echo " ----- MANAGER GET all crops ----- "
curl -X GET -H "Content-Type: application/text" -H "Authorization: Bearer MANAGER_TOKEN" http://localhost:5000/crops

echo " ----- MANAGER GET all schedules ----- "
curl -X GET -H "Content-Type: application/json" -H "Authorization: Bearer MANAGER_TOKEN" http://localhost:5000/schedules

echo " ----- MANAGER GET all crops-health ----- "
curl -X GET -H "Content-Type: application/json" -H "Authorization: Bearer MANAGER_TOKEN" http://localhost:5000/crops-health

echo " ----- MANAGER GET environment-status ----- "
curl -X GET -H "Content-Type: application/json" -H "Authorization: Bearer MANAGER_TOKEN" http://localhost:5000/env-status
echo -e '\n'

echo "========== Example 6 =========="
# WORKER is only allowed to access GET endpoints
echo "----- WORKER POST new schedule ----- "
curl -X POST -H "Content-Type: application/json" -H "Authorization: Bearer WORKER_TOKEN" -d '{"task":"TEST 1","repeat":"every 6 hours"}' http://localhost:5000/add-schedule

echo " ----- WORKER POST new crop ----- "
curl -X POST -H "Content-Type: application/text" -H "Authorization: Bearer WORKER_TOKEN" -d 'pineapple' http://localhost:5000/add-crop

echo " ----- WORKER PUT schedule ----- "
curl -X PUT -H "Content-Type: application/json" -H "Authorization: Bearer WORKER_TOKEN" -d '{"task":"TEST 2","repeat":"every 15 hours"}'  http://localhost:5000/update-schedule?id=0

echo " ----- WORKER DELETE schedule ----- "
curl -X DELETE -H "Content-Type: application/text" -H "Authorization: Bearer WORKER_TOKEN" http://localhost:5000/remove-schedule?id=0

echo " ----- WORKER GET all crops ----- "
curl -X GET -H "Content-Type: application/text" -H "Authorization: Bearer WORKER_TOKEN" http://localhost:5000/crops

echo " ----- WORKER GET all schedules ----- "
curl -X GET -H "Content-Type: application/json" -H "Authorization: Bearer WORKER_TOKEN" http://localhost:5000/schedules

echo " ----- WORKER GET all crops-health ----- "
curl -X GET -H "Content-Type: application/json" -H "Authorization: Bearer WORKER_TOKEN" http://localhost:5000/crops-health

echo " ----- WORKER GET environment status ----- "
curl -X GET -H "Content-Type: application/json" -H "Authorization: Bearer WORKER_TOKEN" http://localhost:5000/env-status
echo -e '\n'


