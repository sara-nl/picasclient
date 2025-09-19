#!/bin/bash

# show the commands being executed
#set -x

BASE_URL="http://couchdb:5984"
AUTH="-u ${COUCHDB_USER:-admin}:${COUCHDB_PASSWORD:-mypassword}"

# DEBUG
# infinite loop with 1 second sleep and print the time
#while true; do
#  echo "Current time: $(date)"
#  sleep 1
#done

# Wait for CouchDB to be ready
until curl -s $AUTH $BASE_URL > /dev/null; do
  echo 'Waiting for CouchDB...'
  sleep 1
done

# DEBUG/DEV
# sleep infinity

# Check if Monitor view exists
echo 'Checking if Monitor view exists...'
cmd_out=$(curl -s $AUTH $BASE_URL/mytestdb/_design/Monitor)
echo "Check result: $cmd_out"

echo "$cmd_out" | jq .error | grep -q 'not_found'
exist_code=$?
echo "Exit code: $exist_code"

if [ $exist_code -eq 0 ]; then
  echo 'The monitor view does not exist, setting up CouchDB...'

  # create the database
  echo 'Checking if mytestdb exists...'
  cmd_out=$(curl -s $AUTH $BASE_URL/mytestdb)
  echo "Check result: $cmd_out"
  echo "$cmd_out" | jq .error | grep -q 'not_found'
  exist_code=$?
  echo "Exit code: $exist_code"
  if [ $exist_code -eq 0 ]; then
    echo 'Database mytestdb does not exist, creating it...'

    # create database
    cmd_out=$(curl -s -X PUT $AUTH $BASE_URL/mytestdb)
    echo "Create database result: $cmd_out"

    # ensure that the mytestdb database was created
    echo "Checking if mytestdb was created..."
    cmd_out=$(curl -s $AUTH $BASE_URL/mytestdb)
    echo "Check result: $cmd_out"
    echo "$cmd_out" | jq .db_name | grep -q 'mytestdb'
    exist_code=$?
    echo "Exit code: $?"
    if [ $exist_code -eq 0 ]; then
      echo 'Database mytestdb created successfully.'
    else
      echo 'Failed to create database mytestdb.'
      exit 1
    fi
  else
    echo 'Database mytestdb already exists.'
  fi

  # create the _users database
  cmd_out=$(curl -s -X PUT $AUTH $BASE_URL/_users)
  echo "Check result: $cmd_out"
  echo "$cmd_out" | jq .error | grep -q 'not_found'
  exist_code=$?
  echo "Exit code: $exist_code"
  if [ $exist_code -eq 0 ]; then
    echo 'Creating _users database...'
    cmd_out=$(curl -s -X PUT $AUTH $BASE_URL/_users)
    echo "Create _users database result: $cmd_out"
    echo "$cmd_out" | jq .ok | grep -q 'true'
    exist_code=$?
    echo "Exit code: $exist_code"
    if [ $exist_code -eq 0 ]; then
      echo '_users database created successfully.'
    else
      echo 'Failed to create _users database.'
      exit 1
    fi
  else
    echo '_users database already exists.'
  fi

  # create the user
  echo 'Checking if user myuser1 exists...'
  cmd_out=$(curl -s $AUTH $BASE_URL/_users/org.couchdb.user:myuser1)
  echo "Check result: $cmd_out"
  echo "$cmd_out" | jq .error | grep -q 'not_found'
  exist_code=$?
  echo "Exit code: $exist_code"
  if [ $exist_code -eq 0 ]; then
    echo 'User myuser1 does not exist, creating it...'
    cmd_out=$(curl -s -X PUT $AUTH $BASE_URL/_users/org.couchdb.user:myuser1 \
      -H 'Content-Type: application/json' \
      -d '{"name": "myuser1", "password": "myuser1password", "roles": [], "type": "user"}')
    echo "Create user result: $cmd_out"
    echo "$cmd_out" | jq .ok | grep -q 'true'
    exist_code=$?
    echo "Exit code: $exist_code"
    if [ $exist_code -eq 0 ]; then
      echo 'User myuser1 created successfully.'
    else
      echo 'Failed to create user myuser1.'
      exit 1
    fi
  else
    echo 'User myuser1 already exists.'
  fi

  # set up security
  echo 'Setting up security for mytestdb...'
  curl -s -X PUT $AUTH $BASE_URL/mytestdb/_security \
    -H 'Content-Type: application/json' \
    -d '{
      "admins": {
        "names": [],
        "roles": []
      },
      "members": {
        "names": ["myuser1"],
        "roles": []
      }
    }'
  echo 'Security setup completed.'

  # promote the user to admin for the database
  echo 'Promoting user myuser1 to admin for mytestdb...'
  curl -s -X PUT $AUTH $BASE_URL/mytestdb/_security \
    -H 'Content-Type: application/json' \
    -d '{
      "admins": {
        "names": ["myuser1"],
        "roles": []
      },
      "members": {
        "names": [],
        "roles": []
      }
    }'
  echo 'User myuser1 promoted to admin for mytestdb.'

  # create the Monitor design document
  echo 'Creating Monitor design document...'
  curl -s -X PUT $AUTH $BASE_URL/mytestdb/_design/Monitor \
    -H 'Content-Type: application/json' \
    --data '{
      "language": "javascript",
      "views": {
        "todo": {
          "map": "function (doc) { if (doc.type === \"token\" && doc.lock == 0 && doc.done == 0) { emit(doc._id, doc._id); } }"
        }
      }
    }'
  echo 'Monitor design document creation completed at: '$(date)

  # display the url to check the Monitor view
  echo 'Monitor view URL: http://127.0.0.1:5984/_utils/#database/mytestdb/_all_docs'
else
  echo 'Setup already completed, the monitor view exists.'
  echo 'Monitor view URL: http://127.0.0.1:5984/_utils/#database/mytestdb/_all_docs'
fi
