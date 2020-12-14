# Elastic image search 

## Objectives
* Practice ML serving for image search
* Design and implement a horizontally scalable image search micro services 
* Build a general framework that allows changing Tensorflow ML models easily
* Practice monitoring

## Technologies
* Openshift running on Rahti CSC cloud
* Tensorflow: ML model evaluator
* Scikit-learn: Vector clustering, search
* Rabbitmq: Message queue
* MongoDB: Document-origiented database
* Prometheus: Monitoring tool

## Architecture:
![Architecture](./diagram.png "General architecture")

## Demo links: 

* http://serving-mongo.rahtiapp.fi/
* http://serving-resnet-mongo.rahtiapp.fi/
* http://serving-mobilenet-mongo.rahtiapp.fi/
* http://serving-custom-mongo.rahtiapp.fi/

## Project structure
```bash
elastic-img-search/
└─── README.md
└─── extract_worker/    # Download images from Bucket and convert to vectors 
└─── extractors/        # Web server to search 
└─── index/             # Load vector from db and cluster
└─── config/   # source code
    │
    └─── config.json    # Deployment configuration file (ml model, scale) 
    └─── deploy.py      # Parse configuration files and deploy on Openshift 
    └─── templates/     # Kubenetes template files, scripts
    │
    └─── K8s/           # Final configuration files to deploy
```

## Configuration declaration
```json
{
  "models": [
    {
      "name": "resnet"    # Pretrained TF model 
    },
    {
      "name": "mobilenet" 
    },
    {
      "name": "custom",
      "model_url": "https://storage.googleapis.com/images-search/model-finetuned.h5"  # Add custom model to the system
    }
  ],
  "services": [
    {
      "name": "extract_worker",
      "models": [
        {
          "name": "resnet",
          "pods": 4       # num pods 
        },
        {
          "name": "mobilenet",
          "pods": 1 
        }
      ]
    },
    {
      "name": "indexing",
      "models": [
        {
          "name": "resnet",
          "num_indexes": 2, # Create 2 index servers, each load half db
          "pods": 5,
          "index_algorithm": "brute" # Clustering algorithm
        },
        {
          "name": "mobilenet",
          "num_indexes": 1,
          "pods": 1 
        },
        {
          "name": "custom",
          "num_indexes": 1,
          "pods": 1
        }
      ]
    },
    {
      "name": "serving",
      "models": [
        {
          "name": "resnet",
          "pods": 20 
        },
        {
          "name": "mobilenet",
          "pods": 1 
        },
        {
          "name": "custom",
          "pods": 1 
        }
      ] 
    },
    {
      "name": "nginx",
      "pods": 1,
      "serving_weights": [
        {
          "name": "resnet",
          "weight": 1  # weight to load balance between services
        },
        {
          "name": "mobilenet",
          "weight": 1
        },
        {
          "name": "custom",
          "weight": 1
        }
      ]
    },
    {
      "name": "rabbitmq_wrapper",
      "pods": 1
    },
    {
      "name": "rabbitmq",
      "pods": 2 
    },
    {
      "name": "prometheus",
      "pods": 1 
    },
    {
      "name": "mongo",
      "services": [
        {
          "name": "config_db",
          "pods": 3
        },
        {
          "name": "router",
          "pods": 3
        },
        {
          "name": "shard",
          "shards": 2,
          "pods": 3
        }
      ]
    }
  ]
}
```




