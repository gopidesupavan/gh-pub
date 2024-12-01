#!/bin/bash

EXIT=0

type=$1

with_sha="sha$type"
for i in *.$with_sha; do
    echo "Checking $i"
    if ! shasum -a $type `basename $i .$with_sha` | diff - $i; then
        echo "Checksum does not match for $i"
        EXIT=1
    fi
done

if [ $EXIT -eq 1 ]; then
    echo "One or more checksums did not match."
    exit 1
else
    echo "All checksums match."
fi
