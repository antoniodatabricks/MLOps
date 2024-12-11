# Databricks notebook source
# MAGIC %md
# MAGIC ## Parameters

# COMMAND ----------

# MAGIC %run ./helper

# COMMAND ----------

# Endpoint details
model_name = dbutils.widgets.get("model_name")
model_version = get_latest_model_version(model_name)
endpoint_name = dbutils.widgets.get("endpoint_name")
endpoint_workload_type = "CPU_SMALL" 
endpoint_workload_size = "Small" 
endpoint_scale_to_zero = True

# Traching table details
tracking_table_catalog = dbutils.widgets.get("tracking_table_catalog")
tracking_table_schema = dbutils.widgets.get("tracking_table_schema")
tracking_table_name = dbutils.widgets.get("tracking_table_name")

# Testing
host = dbutils.widgets.get("host")
test_table = dbutils.widgets.get("test_table")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Spin up model serving endpoint

# COMMAND ----------

from databricks.sdk.service.serving import EndpointCoreConfigInput

# COMMAND ----------

endpoint_config_dict = { 
                        "served_entities": [
                                {
                                    "entity_name": model_name,
                                    "entity_version": model_version,
                                    "workload_size": endpoint_workload_size,
                                    "scale_to_zero_enabled": endpoint_scale_to_zero,
                                    "workload_type": endpoint_workload_type
                                }
                        ]
                    }

if tracking_table_catalog and tracking_table_schema and tracking_table_name:
    endpoint_config_dict["auto_capture_config"] = {
        "catalog_name": f"{tracking_table_catalog}",
        "schema_name": f"{tracking_table_schema}",
        "table_name_prefix": f"{tracking_table_name}"
        }
    
endpoint_config = EndpointCoreConfigInput.from_dict(endpoint_config_dict)
print(endpoint_config)

# COMMAND ----------

deploy_model_serving_endpoint(endpoint_name, endpoint_config)

# COMMAND ----------

# MAGIC %md
# MAGIC ## Test endpoint

# COMMAND ----------

import requests
import numpy as np
import pandas as pd
import json


# Load data from Unity Catalog as Pandas dataframes
white_wine = spark.read.table(test_table).toPandas()

# Add Boolean fields for red and white wine
white_wine['is_red'] = 0.0

# Define classification labels based on the wine quality
data_labels = white_wine['quality'].astype('int') >= 7
data_df = white_wine.drop(['quality'], axis=1)

score_model(host, endpoint_name, data_df)
