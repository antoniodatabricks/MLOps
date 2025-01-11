from flask import Flask, render_template, request, Response
from databricks.connect import DatabricksSession
from databricks.sdk.core import Config
from databricks.sdk import WorkspaceClient
import pandas as pd
import json
import requests
from concurrent.futures import ThreadPoolExecutor, TimeoutError
import time

cluster_id = "0111-231310-n1kybqe3"

app = Flask(__name__)

# Background processing logic
def predict_input(input_table, department):
    """
    Example background process that returns True for success and False for error.
    Modify this logic as needed.
    """
    # Example condition: Both inputs must not be empty and must be alphanumeric
    if input_table and department:

        w = WorkspaceClient()

        catalog_output = "prod" #TODO: Parameterize this
        schema_output = "default" #TODO: Parameterize this
        output_table = f"{catalog_output}.{schema_output}.{department}_output_table"

        w.jobs.run_now_and_wait(job_id="601796253647798",
                                job_parameters={"input_feature_table": input_table, 
                                                "model_name": "prod.default.wine_model",
                                                "output_predictions_table": output_table})

        return output_table

    else:
        raise Exception(f"Invalid input. input_table = {input_table}, department = {department}")

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':

        try:

            # Get data from the form
            input_table = request.form.get('input_table')
            department = request.form.get('department')
            
            # Score model
            config = Config(
                            profile    = "default",
                            cluster_id = cluster_id
                            )
    
            output_table = predict_input(input_table, department)
    
            # Display results
            spark = DatabricksSession.builder.sdkConfig(config).getOrCreate()
            df_pd = spark.table(output_table).limit(20).toPandas()
            table_html = df_pd.to_html(classes="dataframe", index=False)
            return render_template("index.html", label=output_table, table=table_html)
    
        except Exception as e:
            return str(e)

    # Render the form page
    return render_template('index.html', label="", table="")

if __name__ == '__main__':
    app.run(debug=True)    