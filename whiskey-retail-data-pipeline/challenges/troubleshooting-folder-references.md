About This Lab
===
In this hands-on lab, ...

---

## 🚀 What You'll Learn

✅

Step 1: Prepare the Payments Workflow for Updates
===
>💡 **What this is**:
1.  In the [button label="Terminal"](tab-0) tab, transform the workflow using the Deploy Descriptor:
```bash
cd /home/controlm/spark-innovation-with-controlm/whiskey-retail-data-pipeline/workflows/
ctm deploy transform payments.json deploy_descriptor.json > [[Instruqt-Var key="CTM_USER_CODE" hostname="server" ]]_payments.json
```
2.  Validate your changes.
```bash
ctm build [[Instruqt-Var key="CTM_USER_CODE" hostname="server" ]]_payments.json
```
> 🧠 **Why this matters**:

Step 2: Correct and Deploy the Payments Workflow
==
>💡 **What this is**: The Payments Workflow triggers a DAG (workflow) in Apache Airflow — a powerful integration that demonstrates how Control-M orchestrates across platforms, handles secure file transfers between cloud and local systems — a critical function in real-world ETL pipelines, and writes the data into a MySQL database — completing the ETL cycle.
1.  In the [button label="Code Editor"](tab-1) tab, open `~/workflows/[[Instruqt-Var key="CTM_USER_CODE" hostname="server" ]]_payments.json`.
2.  Update the **Defaults** section.
```json
"Defaults": {
"Host": "td-americas-k8s-hg",
"ControlmServer": "IN01",
"RunAs": "controlm",
"Application": "[[ Instruqt-Var key="CTM_USER_CODE" hostname="server" ]]-whiskey-pipeline",
"SubApplication": "[[ Instruqt-Var key="CTM_USER_CODE" hostname="server" ]]-process-whiskey-data"
}
```
3. Update the **get_payment_data** job definition.
```json
"get_payment_data": {
            "Type" : "Job:Airflow",
						"ConnectionProfile" : "TD_GCP_AIRFLOW",
						"DagId": "product_function"
        }
```
4. Update the **transfer_payment_data** job defintion.
```json
"transfer_payment_data": {
            "Type": "Job:FileTransfer",
						"ConnectionProfileSrc" : "TD_VSE_S3_IAM",
						"ConnectionProfileDest" : "TD_VSE_LOCAL_FS",
            "FileTransfers": [
                {
                    "Src": "/data_engineering/payments.csv",
                    "Dest": "/home/controlm/payments.csv",
                    "TransferOption": "SrcToDest",
                    "TransferType": "Binary"
                }
            ],
            "S3BucketName": "ctm-techday-resources"
						}
```
5. Update the **insert_payment_data** job defintion.
```json
"insert_payment_data": {
           "Type" : "Job:Database:EmbeddedQuery",
					 "ConnectionProfile" : "TD_VSE_MYSQL",
					 "OutputSQLOutput" : "Y"
					 "Query" : "use %%usercode_whiskey_retail_shop;\\n\\nLOAD DATA LOCAL INFILE '/home/controlm/payments.csv'\\nINTO TABLE payments\\nFIELDS TERMINATED BY ',' \\n(@col1,@col2,@col3,@col4,@col5,@col6,@col7) set payment_id=@col2, date=@col3, customer_id=@col4, employee_id=@col5, product_id=@col6, price=@col7;\\n\\nDELETE FROM payments\\nWHERE payment_id = 0;"
        }
```
6. Update the **data_pipeline_payments_flow** Flow element.
```json
  "data_pipeline_payments_flow": {
            "Type": "Flow",
            "Sequence": ["get_payment_data", "transfer_payment_data", "insert_payment_data"]
        }
```
7.   In the [button label="Terminal"](tab-0) tab, validate your changes and deploy the Payments Workflow.
```bash
cd /home/controlm/spark-innovation-with-controlm/whiskey-retail-data-pipeline/workflows/
ctm build [[Instruqt-Var key="CTM_USER_CODE" hostname="server" ]]_payments.json
ctm deploy [[Instruqt-Var key="CTM_USER_CODE" hostname="server" ]]_payments.json
```
> 🧠 **Why this matters**: The payments workflow is a reusable subcomponent. Adding the right attributes ensures it’s complete, valid, and can be referenced by other workflows — a common pattern in scalable orchestration.Folder references only work if the folder already exists in the environment. You’re ensuring dependencies are deployed in the correct order. Refer to the documentation for more information on Reference Sub-Folders.

Step 3: Run the Whiskey Retail Data Pipeline
==
>💡 **What this is**:
1.  In the [button label="Terminal"](tab-0) tab, run the Whiskey Retail Data Pipeline
```bash
cd /home/controlm/spark-innovation-with-controlm/whiskey-retail-data-pipeline/workflows/
ctm run [[Instruqt-Var key="CTM_USER_CODE" hostname="server" ]]_data-pipeline.json
```
Step 5: View the Workflow in the Control-M SaaS Monitoring Domain
==
>💡 **What this is**:
1.  In the [button label="Control-M SaaS"](tab-2) tab,  select the **Monitoring** domain from the top navigation.
2.  Click **Add Viewpoint**
3.  Locate the **Folder Name** field under **Include Attributes** and enter: `[[ Instruqt-Var key="CTM_USER_CODE" hostname="server" ]]*`
4.  Click **Open** .
> 🧠 **Why this matters**:

Summary
==
