#!/bin/bash

PARAM_Q_MIN=100
PARAM_Q_MAX=260
PARAM_Q_STEP=84

PARAM_D_MIN=256
PARAM_D_MAX=8192
PARAM_D_STEP=2024

PARAM_M_MIN=400
PARAM_M_MAX=10000
PARAM_M_STEP=4000

function testNumerical {
  if [ $1 -eq $1 2> /dev/null ]; then
    return
  fi
  echo "$1 is not numerical!"
  exit 1
}

while getopts "q:d:m:" opt; do
  testNumerical $OPTARG
  case $opt in
    q)
      PARAM_Q_STEP=$OPTARG
      ;;
    d)
      PARAM_D_STEP=$OPTARG
      ;;
    m)
      PARAM_M_STEP=$OPTARG
      ;;
  esac
done

PARAMFILE=$( mktemp )

PARAM_Q=$PARAM_Q_MIN
PARAM_D=$PARAM_D_MIN
PARAM_M=$PARAM_M_MIN

STR_PARAM_Q=""

while [ $PARAM_Q_MAX -ge $PARAM_Q ]; do
  # Ugly hack in order not to have to use bc
  if [ $[ $PARAM_Q / 10 ] -eq 0  ]; then
    STR_PARAM_Q="0.00${PARAM_Q}"
  elif [ $[ $PARAM_Q / 100 ] -eq 0 ]; then
    STR_PARAM_Q="0.0${PARAM_Q}"
  else
    STR_PARAM_Q="0.${PARAM_Q}"
  fi
  while [ $PARAM_D_MAX -ge $PARAM_D ]; do
    while [ $PARAM_M_MAX -ge $PARAM_M ]; do
      echo "-q ${STR_PARAM_Q} -d ${PARAM_D} -m ${PARAM_M}" >> $PARAMFILE
      PARAM_M=$[ $PARAM_M+$PARAM_M_STEP ]
    done
    PARAM_M=$PARAM_M_MIN
    PARAM_D=$[ $PARAM_D+$PARAM_D_STEP ]
  done
  PARAM_D=$PARAM_D_MIN
  PARAM_Q=$[ $PARAM_Q+$PARAM_Q_STEP ]
done

echo ${PARAMFILE}
