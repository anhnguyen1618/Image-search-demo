ALGO=brute-force
INDEX=1
SERVING=1
# export MLFLOW_EXPERIMENT_ID=$(mlflow experiments create -n $ALGO-$INDEX-index-$SERVING-serving | rev | cut -d " " -f1 | rev) && 
python3 run_experiment.py -a $ALGO -i $INDEX -se $SERVING