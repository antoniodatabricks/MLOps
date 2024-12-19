# MLOps

MLOps pipeline from DEV to PROD


1. Create a repo in GitHub copying the code base from https://github.com/antoniodatabricks/MLOps
2. Create a development branch in addition to the existing Main branch
3. Clone the development branch using Databricks Repos
4. Run https://github.com/antoniodatabricks/MLOps/blob/main/demo_prep/demo_setup.py
5. Update the environment-related information in the bundle file by adding the Databricks Workspace URL:
https://github.com/antoniodatabricks/MLOps/blob/main/databricks.yml#L72
https://github.com/antoniodatabricks/MLOps/blob/main/databricks.yml#L79
6. Update all “notebook_path” in the bundle file to reflect the new notebook paths. For example https://github.com/antoniodatabricks/MLOps/blob/main/databricks.yml#L11
7. Create a new GitAction Secret named “DATABRICKS_PROD_WS_TOKEN” containing a valid Databricks Personal Access Token
8. Commit the change to the development branch
9. Create a Pull Request from the development branch to the main branch (this should trigger a code validation action)
10. Merge the Pull Request (this should trigger the deployment in the Databricks Workspace)
11. GitHub Actions also triggers the execution of the jobs training_validation_promotion and create_serving_endpoint. Wait for it to finish
12. As a result of the job executions in the previous step, we should have a new model version named prod.default.wine_model tagged as champion and a model serving endpoint named “demo_model_serving_endpoint”
13. Create a cluster DBR 15.4LTS. You’ll provide its ID in the next step
14. Update the Databricks App source code with your local environment information (PAT, Model Serving URL and Cluster ID):

	https://github.com/antoniodatabricks/MLOps/blob/main/databricks_app/app.py#L11
	https://github.com/antoniodatabricks/MLOps/blob/main/databricks_app/app.py#L12
	https://github.com/antoniodatabricks/MLOps/blob/main/databricks_app/app.py#L13

15. Create a Custom Databricks App pointing to your local git folder https://github.com/antoniodatabricks/MLOps/tree/main/databricks_app and provide its service principal admin privileges in the Workspace
16. Provide the Databricks App service principal all privileges to the catalog prod
17. Test the app by passing Input Table = prod.default.mlflow_input_table_test and Department = test
