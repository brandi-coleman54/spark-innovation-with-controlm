About This Lab
===
In this lab, you’ll explore...

---

## 🚀 What You'll Learn
✅ Customize and run a JSON-based Control-M job flow

✅ Use the CLI to build and monitor your execution

✅ Interact with Control-M Automation API services

✅ Visualize your workflow in the Control-M SaaS web interface

Step 1: Update Your First Job Flow
===
>💡 **What this is**:
1. In the [button label="Code Editor"](tab-1) tab,  open `~/workflows/first-job-flow.json`.
2. Take a moment to review the job flow:
3. Replace all placeholder values:
	- **replace-with-usercode** = `[[ Instruqt-Var key="CTM_USER_CODE" hostname="server" ]]`
4. In the [button label="Terminal"](tab-0) tab, validate your changes to the workflow.
```bash
cd /home/controlm/spark-innovation-with-controlm/jobs-as-code-aapi/workflows
ctm build first-job-flow.json
```
5. Deploy your changes to the workflow:
```bash
ctm deploy first-job-flow.json
```
>🧠 Why this matters:

Step 2: View the Workflow in the Control-M SaaS Planning Domain
===
>💡 **What this is**:
1.  In the [button label="Control-M SaaS"](tab-2) tab, select the **Planning** domain from the top navigation.
2.  Open the **Folders and Jobs** tab.
3.  In the **Filter Folders and Jobs** panel, locate the **Folder Name** field and enter: `[[ Instruqt-Var key="CTM_USER_CODE" hostname="server" ]]`
4.  Click **Apply** to filter the list.
5.  Find your Folder named: `[[ Instruqt-Var key="CTM_USER_CODE" hostname="server" ]]_first_job_flow`
6. Click the **Open Workspace** button.
7. Validate that the updates have been made to your workflow.

>🧠 **Why this matters:**

Summary
===
🎉 You have now:
- Customized and built your first Control-M JSON job flow
- Executed and monitored it using the CLI
- Queried job status, logs, and reruns with Automation API
- Logged into Control-M SaaS and viewed your workflow in the UI

