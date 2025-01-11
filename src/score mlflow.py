# Databricks notebook source
# MAGIC %md
# MAGIC # Parameters

# COMMAND ----------

model_name = dbutils.widgets.get("model_name")
input_feature_table = dbutils.widgets.get("input_feature_table")
output_predictions_table = dbutils.widgets.get("output_predictions_table")

# COMMAND ----------

# MAGIC %md
# MAGIC # Scoring model directly using mlflow

# COMMAND ----------

import mlflow
from mlflow import MlflowClient
import mlflow.sklearn

mlflow.set_registry_uri("databricks-uc")

# Load model from UC
champion_model_uri = f"models:/{model_name}@Champion"
model = mlflow.sklearn.load_model(champion_model_uri)

# Convert features to a pandas DataFrame
features = spark.table(input_feature_table).toPandas()

# Predict
predictions = model.predict(features)

# Attatch predictions to the input features
predictions_df = features.assign(good_quality_predictions=predictions)

# Save results to UC
spark.createDataFrame(predictions_df).write.mode("overwrite").saveAsTable(output_predictions_table)
