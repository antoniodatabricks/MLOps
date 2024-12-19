from flask import Flask, render_template, request, Response
from databricks.connect import DatabricksSession
from databricks.sdk.core import Config
from databricks.sdk import WorkspaceClient
import pandas as pd
import json
import requests
from concurrent.futures import ThreadPoolExecutor, TimeoutError
import time

token = "dapied063fdd5fd50fb165df2277e7a9a00d-3"
endpoint_url = "https://adb-10697646213410.10.azuredatabricks.net/serving-endpoints/demo_model_serving_endpoint/invocations"
cluster_id = "1218-232809-cpuroe4o"

app = Flask(__name__)

def create_tf_serving_json(data):
    return {'inputs': {name: data[name].tolist() for name in data.keys()} if isinstance(data, dict) else data.tolist()}

# Background processing logic
def predict_input(spark, input_table, department):
    """
    Example background process that returns True for success and False for error.
    Modify this logic as needed.
    """
    # Example condition: Both inputs must not be empty and must be alphanumeric
    if input_table and department:

        ### Retrieve test data
        dataset = spark.read.table(input_table).toPandas()

        headers = {'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'}
        ds_dict = {'dataframe_split': dataset.to_dict(orient='split')} if isinstance(dataset, pd.DataFrame) else create_tf_serving_json(dataset)
        data_json = json.dumps(ds_dict, allow_nan=True)
        response = requests.request(method='POST', headers=headers, url=endpoint_url, data=data_json)

        if response.status_code != 200:
            raise Exception(f"Request failed with status {response.status_code}, {response.text}")
        
        response_json = response.json()
        string_list = ["yes" if b else "no" for b in response_json["predictions"]]
        dataset["good_quality_predictions"] = string_list
        
        catalog_output = "prod" #TODO: Parameterize this
        schema_output = "default" #TODO: Parameterize this
        output_table = f"{catalog_output}.{schema_output}.{department}_output_table"
        spark.createDataFrame(dataset).write.mode("overwrite").saveAsTable(output_table)

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
    
            spark = DatabricksSession.builder.sdkConfig(config).getOrCreate()
            output_table = predict_input(spark, input_table, department)
    
            # Display results
            df_pd = spark.table(output_table).limit(20).toPandas()
            table_html = df_pd.to_html(classes="dataframe", index=False)
            return render_template("index.html", label=output_table, table=table_html)
    
        except Exception as e:
            return str(e)

    # Render the form page
    return render_template('index.html', label="", table="")

if __name__ == '__main__':
    app.run(debug=True)    