# Databricks notebook source
# MAGIC %md
# MAGIC ## Parameters and utils

# COMMAND ----------

# MAGIC %run ./helper

# COMMAND ----------

# Models to validate 

challenger_model_name = dbutils.widgets.get("challenger_model_name")
champion_model_name = dbutils.widgets.get("champion_model_name")

# Validation datasets

validation_data_catalog = dbutils.widgets.get("validation_data_catalog")
validation_data_schema = dbutils.widgets.get("validation_data_schema")

# COMMAND ----------

import mlflow
from mlflow import MlflowClient
import mlflow.sklearn

mlflow.set_registry_uri("databricks-uc")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Tag model to be validated as challenger

# COMMAND ----------

from mlflow import MlflowClient
client = MlflowClient()

challenger_model_version = get_latest_model_version(challenger_model_name)
client.set_registered_model_alias(challenger_model_name, "Challenger", challenger_model_version)

# COMMAND ----------

# MAGIC %md
# MAGIC ## Check if model baseline exists

# COMMAND ----------

# Check if champion model exists

try:
    client.get_model_version_by_alias(champion_model_name, "Champion")
except:
    dbutils.notebook.exit("Success: Champion model does not exist")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Validate model against baseline

# COMMAND ----------

import pandas as pd
import sklearn

# Load data from Unity Catalog as Pandas dataframes
white_wine = spark.read.table(f"{validation_data_catalog}.{validation_data_schema}.white_wine").toPandas()
red_wine = spark.read.table(f"{validation_data_catalog}.{validation_data_schema}.red_wine").toPandas()

# Add Boolean fields for red and white wine
white_wine['is_red'] = 0.0
red_wine['is_red'] = 1.0
data_df = pd.concat([white_wine, red_wine], axis=0)

# Define classification labels based on the wine quality
data_labels = data_df['quality'].astype('int') >= 7
data_df = data_df.drop(['quality'], axis=1)

# Split 80/20 train-test
X_train, X_test, y_train, y_test = sklearn.model_selection.train_test_split(
  data_df,
  data_labels,
  test_size=0.2,
  random_state=1
)

# Build the Evaluation Dataset from the test set
eval_data = X_test
eval_data["label"] = y_test

# COMMAND ----------

# Challenger
challenger_model_uri = f"models:/{challenger_model_name}@Challenger"

# Champion
champion_model_uri = f"models:/{champion_model_name}@Champion"

# COMMAND ----------

# Evaludate Model Challenger
with mlflow.start_run() as run:

    result_challenger = mlflow.evaluate(
        challenger_model_uri,
        eval_data,
        targets="label",
        model_type="classifier",
        evaluators=["default"],
    )

# COMMAND ----------

# Evaludate Model Champion
with mlflow.start_run() as run:

    result_champion = mlflow.evaluate(
        champion_model_uri,
        eval_data,
        targets="label",
        model_type="classifier",
        evaluators=["default"],
    )

# COMMAND ----------

display(result_challenger.metrics)

# COMMAND ----------

display(result_champion.metrics)

# COMMAND ----------

# Comparing metrics of model challenger against model champion

assert float(result_challenger.metrics["score"]) >= float(result_challenger.metrics["score"]) , "Model challenger metrics are doesn't show improvements against model champion."
