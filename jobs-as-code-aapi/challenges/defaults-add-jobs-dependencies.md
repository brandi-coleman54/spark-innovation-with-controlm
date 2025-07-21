About This Lab
===
In this lab, you’ll explore...

## 🚀 What You’ll Learn
✅ Use the **Defaults** section to simplify job definitions

✅ Add additional jobs to your workflow

✅ Add **flow objects** to control job execution order

Step 1: Set `Run As` in the Defaults
===
>💡 **What this is**: Rather than repeating the `Run As` attribute in every job, place it in the `Defaults` section of your JSON.
1. In the [button label="Code Editor"](tab-1) tab, open `~/workflows/first-job-flow.json`.
2. Locate the **Defaults** section and add the Run As attribute.
```json
"Defaults" : {
		"Host": "td-americas-k8s-hg",
		"ControlmServer": "IN01",
		"Application": "[[ Instruqt-Var key="CTM_USER_CODE" hostname="server" ]]_first_job_flow",
		"SubApplication": "[[ Instruqt-Var key="CTM_USER_CODE" hostname="server" ]]_first_job_flow",
		"OrderMethod": "Manual",
		"RunAs": "controlm"
	}
```
3. In the [button label="Terminal"](tab-0) tab, validate your changes to the workflow.
```bash
cd /home/controlm/spark-innovation-with-controlm/jobs-as-code-aapi/workflows
ctm build first-job-flow.json
```
>🧠 **Why this matters**:

Step 2: Add Jobs
===
>💡 **What this is**: Let’s expand your workflow by adding three new jobs to your `first-job-flow.json` file.

1. In the [button label="Code Editor"](tab-1) tab, open `~/workflows/first-job-flow.json`.
2. Locate the **Folder** section, and add 3 Jobs: ShowFiles, PrintCurrentDirectory, and WaitJob.
```json
"[[ Instruqt-Var key="CTM_USER_CODE" hostname="server" ]]_first_job_flow": {
		"Type": "Folder",
		"EchoJob": {
			"Type" : "Job:Command",
			"Command" : "echo hello",
			"RunAs" : "controlm"
		}	,
	"ShowFiles" : {
		"Type": "Job:Command",
		"Command": "ls -la"
	},
	 "PrintCurrentDirectory" : {
		"Type": "Job:Command",
		"Command": "pwd"
	},
	"Wait" : {
		"Type": "Job:Command",
		"Command": "sleep 30"
	}
```
3. In the [button label="Terminal"](tab-0) tab, validate your changes to the workflow.
```bash
cd /home/controlm/spark-innovation-with-controlm/jobs-as-code-aapi/workflows
ctm build first-job-flow.json
```
4. Deploy your changes to the workflow:
```bash
ctm deploy first-job-flow.json
```
>🧠 **Why this matters**:

Step 3:  Add Dependencies
=
>💡 **What this is**:
1. In the [button label="Code Editor"](tab-1) tab, open `~/workflows/first-job-flow.json`.
2. Add a Flow Element to define the sequence of jobs:
```json
"Flow": {
	"Type": "Flow",
	"Sequence": [ "EchoJob", "ShowFiles", "PrintCurrentDirectory", "Wait"]
	}
```
3. In the [button label="Terminal"](tab-0) tab, validate your changes to the workflow.
```bash
cd /home/controlm/spark-innovation-with-controlm/jobs-as-code-aapi/workflows
ctm build first-job-flow.json
```
>🧠 **Why this matters**:

Step 4: Run Your Workflow
===
>💡 **What this is**:
1. In the [button label="Terminal"](tab-0) tab,  run your workflow.
```bash
cd /home/controlm/spark-innovation-with-controlm/jobs-as-code-aapi/workflows
ctm run first-job-flow.json
```
2. Get the status of the run.
```bash
ctm run status <RUN-ID>
```
>[!IMPORTANT]
> Replace `<RUN-ID>` with the `runId` value returned in the previous command.

3. (Optional) Explore other Automation API Services.
```bash
ctm run job:status::get <JOB-ID>
ctm run job:output::get <JOB-ID>
ctm run job:log::get <JOB-ID>
ctm run job:job::rerun <JOB-ID>
```
>[!IMPORTANT]
> Replace `<JOB-ID>` with the `jobId` returned in the previous command.

>🧠 **Why this matters:** Please visit the [Service Reference](https://docs.bmc.com/docs/automation-api/monthly/run-service-1116950330.html#Runservice-run_job_status_getrunjob:status::get) to learn more about the different services.

Step 5: View the Workflow in the Control-M SaaS Monitoring Domain
==
>💡 What this is:
1.  In the [button label="Control-M SaaS"](tab-2) tab,  select the **Monitoring** domain from the top navigation.
2.  Click **Add Viewpoint**
3.  Locate the **Folder Name** field under **Include Attributes** and enter: `[[ Instruqt-Var key="CTM_USER_CODE" hostname="server" ]]*`
4.  Click **Open** .
>🧠 Why this matters:

Summary
==
🎉 You have now:
