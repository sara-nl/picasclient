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

#sleep infinity


# Check if Monitor view exists
echo 'Checking if Monitor view exists...'
cmd_out=$(curl -s $AUTH $BASE_URL/mytestdb/_design/Monitor)
echo "Check result: $cmd_out"

echo "$cmd_out" | jq .error | grep -q 'not_found'
exist_code=$?
echo "Exit code: $exist_code"

if [ $exist_code -eq 0 ]; then
  echo 'The monitor view does not exist, setting up CouchDB...'

  # check if the mytestdb database already exists
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

  ## check if the database mytestdb already exists
  #if curl -s $AUTH $BASE_URL/mytestdb | grep -q '"error": "not_found"'; then
  #  # create database
  #  curl -s -X PUT $AUTH $BASE_URL/mytestdb

  #  # ensure that the mytestdb database was created
  #  if curl -s $AUTH $BASE_URL/mytestdb | grep -q '"ok": true'; then
  #    echo 'Database mytestdb created successfully.'
  #  fi
  #else
  #  echo 'Database mytestdb already exists.'
  #fi



  ## Create _users database
  #curl -s -X PUT $AUTH $BASE_URL/_users

  ## Create user
  #curl -s -X PUT $AUTH $BASE_URL/_users/org.couchdb.user:myuser1 \
  #  -H 'Content-Type: application/json' \
  #  -d '{"name": "myuser1", "password": "myuser1password", "roles": [], "type": "user"}'

  ## Set up security
  #curl -s -X PUT $AUTH $BASE_URL/mytestdb/_security \
  #  -H 'Content-Type: application/json' \
  #  -d '{"admins": {"names": [], "roles": []}, "members": {"names": ["myuser1"], "roles": []}}'

  ## Create Monitor design document
  #curl -s -X PUT $AUTH $BASE_URL/mytestdb/_design/Monitor \
  #  -H 'Content-Type: application/json' \
  #  -d '{"language": "javascript", "views": {"todo": {"map": "function (doc) { if (doc.type === \\"token\\" && doc.lock == 0 && doc.done == 0) { emit(doc._id, doc._id); } }"}}}'
else
  echo 'Setup already completed, the monitor view exists.'
fi
