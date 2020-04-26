#!/bin/bash
#
# Run locust load test
#
#####################################################################
ARGS="$@"
HOST="${1}"
SCRIPT_NAME=`basename "$0"`
INITIAL_DELAY=1
TARGET_HOST="$HOST"
CLIENTS=2
RUN_TIME=10s

now=$(date '+%d-%m-%Y_%H:%M:%S');
CSV_BASE_NAME="${now}_"

HATCH_RATE=10


do_check() {

  # check hostname is not empty
  if [ "${TARGET_HOST}x" == "x" ]; then
    echo "TARGET_HOST is not set; use '-h hostname:port'"
    exit 1
  fi

  # check for locust
  if [ ! `command -v locust` ]; then
    echo "Python 'locust' package is not found!"
    exit 1
  fi

  # check locust file is present
  if [ -n "${LOCUST_FILE:+1}" ]; then
  	echo "Locust file: $LOCUST_FILE"
  else
  	LOCUST_FILE="./tests/kubernetes/sock-shop/test/locustfile.py"
  	echo "Default Locust file: $LOCUST_FILE"
  fi
}

do_exec() {
  sleep $INITIAL_DELAY

  # check if host is running
  STATUS=$(curl -s -o /dev/null -w "%{http_code}" ${TARGET_HOST})
  if [ $STATUS -ne 200 ]; then
      echo "${TARGET_HOST} is not accessible"
      exit 1
  fi

  echo "Will run $LOCUST_FILE against $TARGET_HOST. Spawning $CLIENTS clients ($HATCH_RATE client every second) and stop after $RUN_TIME time."
  locust  --csv=${CSV_BASE_NAME} --host=http://$TARGET_HOST -f $LOCUST_FILE --clients=$CLIENTS --hatch-rate=$HATCH_RATE --run-time=$RUN_TIME --no-web --only-summary
  echo "done"
}


do_usage() {
    cat >&2 <<EOF
Usage:
  ${SCRIPT_NAME} [ http://hostname/ ] OPTIONS
Options:
  -d  Delay before starting
  -h  Target host url, e.g. 127.0.0.1:80
  -c  Number of clients (default 2)
  -r  Stop after the specified amount of time (default 10s) (e.g. 300s,20m, 3h, 1h30m, etc.)
  -l  Path to the CSV log files (deafult "${datetime}_")
Description:
  Runs a Locust load simulation against specified host.
EOF
  exit 1
}



while getopts ":d:h:c:r:l:" o; do
  case "${o}" in
    d)
        INITIAL_DELAY=${OPTARG}
        #echo $INITIAL_DELAY
        ;;
    h)
        TARGET_HOST=${OPTARG}
        #echo $TARGET_HOST
        ;;
    c)
        CLIENTS=${OPTARG:-2}
        #echo $CLIENTS
        ;;
    r)
        RUN_TIME=${OPTARG:-10}
        #echo $RUN_TIME
        ;;
    l)
        CSV_BASE_NAME=${OPTARG:-10}
        #echo $CSV_BASE_NAME
        ;;
    *)
        do_usage
        ;;
  esac
done


do_check
do_exec
