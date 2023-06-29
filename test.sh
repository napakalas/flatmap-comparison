#!/bin/sh

# if [ -f "flatmaps/staging/a" ]; then
#     rm flatmaps/staging/a
# fi

# if [ -f "flatmaps/staging/a" ]; then
#     echo "$FILE exists."
# else 
#     echo "$FILE does not exist."
# fi

# if [[ $3 = "asd" || $2 = "2" ]]; then
#     echo "correct"
# else
#     echo "incorrect $2 $3"
# fi

SOURCE=sources/$1

PRODUCTION=flatmaps/production
MAP_PRODUCTION=$PRODUCTION/$1-flatmap
LOG_PRODUCTION=$PRODUCTION/$1.log

STAGING=flatmaps/staging
MAP_STAGING=$STAGING/$1-flatmap
LOG_STAGING=$STAGING/$1.log

OUTPUT=results/$1.$2

IS_REFRESH=${3:-no}

if [[ $1 = "functional-connectivity" ]]; then
    echo "tidak ada $IS_REFRESH"
else
    echo "ada $IS_REFRESH"
fi