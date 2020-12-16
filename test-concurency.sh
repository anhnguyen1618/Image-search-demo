#!/bin/bash
for i in {1..10000}
do
  curl --silent --output /dev/null -F "record=@dataset/accordion_image_0016.jpg" http://serving-resnet-mongo.rahtiapp.fi/search &
  if ! (($i % 600)); then
    echo "Waiting at $i"
    wait < <(jobs -p)
  fi
done
