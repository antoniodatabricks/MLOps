# Databricks notebook source
# MAGIC %md
# MAGIC # Examples on how to authenticate and use model serving endpoint for inference

# COMMAND ----------

from databricks.sdk import WorkspaceClient
from databricks.sdk.service.serving import DataframeSplitInput

# Parameters
endpoint_name = "{ENDPOINT_NAME}"
test_table = "prod.default.mlflow_input_table_test"

# Load test data from Unity Catalog as Pandas dataframes
dataset = spark.read.table(test_table).toPandas()

# Convert it to a DataframeSplitInput
dataframe_split=DataframeSplitInput.from_dict(dataset.to_dict(orient='split'))

# COMMAND ----------

# MAGIC %md
# MAGIC ## Auth Option 1: From within the same workspace as the endpoint
# MAGIC - No credentials required as long as the user has access to the endpoint

# COMMAND ----------

w = WorkspaceClient()

# COMMAND ----------

# MAGIC %md
# MAGIC ## Auth Option 2: From external environments using PAT

# COMMAND ----------

w = WorkspaceClient(host = "{WORKSPACE_URL}", 
                    token = "{PAT}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Auth Option 3: From external environments using SP

# COMMAND ----------

w = WorkspaceClient(host = "{WORKSPACE_URL}", 
                    client_id = "{CLIEND_ID}", 
                    client_secret = "{CLIENT_SECRET}")

# COMMAND ----------

# MAGIC %md
# MAGIC # Inference

# COMMAND ----------

# Score model using the model serving endpoint
response = w.serving_endpoints.query(name = endpoint_name, dataframe_split = dataframe_split)

# Attaching results back to the original dataset
dataset["predictions"] = response.predictions

dataset.display()
