# Databricks notebook source
# MAGIC %md
# MAGIC ## Promote model from challenger to champion

# COMMAND ----------

challenger_model_name = "dev.default.wine_model"

# COMMAND ----------

from mlflow import MlflowClient
client = MlflowClient()

model_version = client.get_model_version_by_alias(challenger_model_name, "challenger")
client.set_registered_model_alias(challenger_model_name, "champion", model_version.version)
client.delete_registered_model_alias(challenger_model_name, "challenger")
