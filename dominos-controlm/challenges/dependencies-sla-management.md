About This Lab
===

In this lab, you’ll learn how to extend and validate a Control‑M workflow for Pizza Order Fulfillment. You’ll add a Flow element to ensure jobs run in sequence, and an SLA job to monitor performance and alert the operations team if delivery exceeds 45 minutes.

---

## 🚀 What You'll Learn

✅ How to add a Flow element to orchestrate job execution

✅ How to add and configure an SLA job to track workflow deadlines

✅ How to use ctm build to validate your workflow JSON before deployment


Step 1: Add an SLA Job to the Workflow
==
>💡 **What this is**: This step shows you how to create a Service Level Agreement (SLA) job that monitors your pizza workflow and triggers an alert if it doesn’t complete within the expected time of 45 minutes.
1. In the [button label="Code Editor"](tab-1), open `~/workflows/[[ Instruqt-Var key="CTM_USER_CODE" hostname="server" ]]_order_fulfillment.json`.
2. Within the  **Folder** section, add this SLA job definition:
```json
 "SLA" : {
	 "Type" : "Job:SLAManagement",
	 "ServiceName" : "Dominos Pizza Order",
	 "JobRunsDeviationsTolerance" : "3",
	 "CompleteIn" : {
		 "Time" : "0:45"
		 },
		 "ServiceActions" : {
			 "If:SLA:ServiceIsLate_0" : {
			 "Type" : "If:SLA:ServiceIsLate",
			 "Action:SLA:Notify_0" : {
			 "Type" : "Action:SLA:Notify",
			 "Severity" : "Regular",
			 "Message" : "Service %%SERVICE_NAME is projected to be late. The service deadline is %%SERVICE_DUE_TIME but it is estimated to complete at %%SERVICE_EXPECTED_END_TIME. The following job(s) are problematic: %%PROBLEMATIC_JOBS"
			 }
		}
	}}
```
3. In the [button label="Terminal"](tab-0), validate your changes to the workflow:
```bash
cd /home/controlm/spark-innovation-with-controlm/dominos-controlm/workflows
ctm build [[ Instruqt-Var key="CTM_USER_CODE" hostname="server" ]]_order_fulfillment.json
```
>🧠 **Why this matters**:

Step 2:  Add a Flow Element Pizza Order Fulfillment
==

>💡 **What this is**:
1. In the [button label="Code Editor"](tab-1), open `~/workflows/order_fufillment.json`.
2. Add a Flow Element to define the sequence of jobs:
```json
"Flow": {
	"Type": "Flow",
	"Sequence": [ "Place_Order", "Inventory_And_Store_Check", "Process_Payment", "Kitchen_Prep", "Delivery_Or_Pickup", "Generate_Reporting", "SLA"]
	}
```
3. In the [button label="Terminal"](tab-0), validate your changes to the workflow:
```bash
cd /home/controlm/spark-innovation-with-controlm/dominos-controlm/workflows
ctm build [[ Instruqt-Var key="CTM_USER_CODE" hostname="server" ]]_order_fulfillment.json
```
4. Deploy your changes to the workflow:
```run
ctm deploy [[ Instruqt-Var key="CTM_USER_CODE" hostname="server" ]]_order_fulfillment.json
```

>🧠 **Why this matters**: Adding flow elements like this lets you extend the business logic quickly—Control‑M automatically manages the dependencies so everything runs in sequence. Before deploying, running ctm build to validate your JSON ensures there are no syntax errors, missing dependencies, or naming conflicts, so your workflow will deploy and execute correctly.

Step 3: View the Workflow in the Control-M SaaS Planning Domain
==
>💡 **What this is**:
1.  In the [button label="Control-M SaaS"](tab-2),  select the **Planning** domain from the top navigation.
2.  Open the **Folders and Jobs** tab.
3.  In the **Filter Folders and Jobs** panel, locate the **Folder Name** field and enter: `[[ Instruqt-Var key="CTM_USER_CODE" hostname="server" ]]`
4.  Click **Apply** to filter the list.
5.  Find your **Folder** named: `[[ Instruqt-Var key="CTM_USER_CODE" hostname="server" ]]_Dominos_Pizza_Workflow_preprod`
6. Click the **Open Workspace** button.
7. Validate that the updates have been made to your workflow.
>🧠 **Why this matters**:

Summary
==
🎉 You have now:
