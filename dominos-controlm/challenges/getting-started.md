About This Lab
===
In this hands-on lab, you’ll work with a **Pizza Order Fufillment**  workflow using Control‑M. You’ll learn how Control‑M automates multi-step processes across systems, ensures standards are enforced, and lets you monitor everything from a single pane of glass.

---

## 🚀 What You'll Learn

✅ How to configure and use the Control‑M CLI to interact with your Control-M SaaS environment

✅ How to log in and navigate the Control‑M SaaS Web UI

✅ How to explore and understand a Jobs-as-Code workflow

✅ How to apply naming standards and personalize a workflow using a Deploy Descriptor

Step 1: Set Up the Control-M CLI Environment
===
>💡 **What this is**: Control‑M CLI commands run against an environment, which is just a combination of a Control‑M API endpoint and your authentication token.
1. In the [button label="Terminal"](tab-0) tab, add the **preprod** environment (this points the CLI to your Control‑M SaaS PreProd instance):
```run
ctm env add preprod [[ Instruqt-Var key="CTM_AAPI_ENDPOINT" hostname="server" ]] [[ Instruqt-Var key="CTM_AUTH_TOKEN" hostname="server" ]]
```
> 🧠**Why this matters**: The Control-M CLI is your gateway to automating workflows programmatically. Defining your environment lets you securely connect and interact with the Control-M API. For more information, refer to the documentation:  [Environment Service](https://documents.bmc.com/supportu/controlm-saas/en-US/Documentation/API_Services_EnvironmentService.htm#environmentadd)

Step 2: Login to Control-M SaaS for the First Time
===
>💡 **What this is**:
1. Locate the email titled "Welcome to Helix Control-M!". Sent to: `[[ Instruqt-Var key="CTM_USER" hostname="server" ]]`.
2. Retrieve your login credentials:
	- From the email, copy your <b>User name</b>  and  <b>Password</b> and store them for the next step.
3.  In Instruqt, click on the [button label="Control-M SaaS"](tab-2) tab to open the Control-M SaaS Web UI.
4. Paste your <b>User name</b>  and  <b>Password</b> from the email and Login.
> 🧠**Why this matters**:

Step 3: Explore the Pizza Order Fulfillment Workflow
===
>💡 **What this is**: This step introduces you to the Control‑M workflow definition for the Domino’s Pizza use case. The workflow is written as JSON, where each job represents part of the pizza order process.
1. In the [button label="Code Editor"](tab-1) tab,  open `~/workflows/order_fufillment.json`.
2. Take a moment to review the job flow:
	- Each job represents a stage of the pizza order lifecycle (Order → Inventory → Payment → Kitchen → Delivery → Reporting).
	- These jobs currently lack dependencies, but we’ll correct that later by adding a Flow element.
> 🧠**Why this matters**: Understanding how jobs and flows are structured in Control‑M Jobs-as-Code helps you visualize the full process and shows how orchestration ensures data and events move seamlessly from one system to another (from order placement all the way to reporting).

Step 4: Prepare the Pizza Order Fulfillment Workflow for Updates
===
>💡 **What this is**: Before updating, you’ll personalize the workflow and apply company standards to avoid conflicts and ensure compliance.
1. In the [button label="Code Editor"](tab-1) tab, open `~/workflows/deploy-descriptor.json`.
2. Replace all placeholder values:
	- **replace-with-usercode** = `[[ Instruqt-Var key="CTM_USER_CODE" hostname="server" ]]`
	- **replace-with-email** = `[[ Instruqt-Var key="CTM_USER" hostname="server" ]]`
3.  In the [button label="Terminal"](tab-0) tab, transform the workflow using the Deploy Descriptor:
```bash
cd /home/controlm/spark-innovation-with-controlm/dominos-controlm/workflows
ctm deploy transform order_fulfillment.json deploy_descriptor.json > [[ Instruqt-Var key="CTM_USER_CODE" hostname="server" ]]_order_fulfillment.json
```
4. Ensure the transformation is correct, and deploy  your workflow using the Deploy Descriptor:
```bash
ctm deploy [[ Instruqt-Var key="CTM_USER_CODE" hostname="server" ]]_order_fulfillment.json
```
> 🧠 **Why this matters**: Organizations usually enforce naming conventions, folder structures, and ownership rules for all Control‑M jobs, called Site Standards. If you deploy without aligning to these standards, you risk overwriting other jobs or causing conflicts.  For more information, refer to the documentation:  [Deploy Descriptor](https://documents.bmc.com/supportu/controlm-saas/en-US/Documentation/API_DeployDescriptor.htm)

Step 5: View the Workflow in the Control-M SaaS Planning Domain
==
>💡 **What this is**:
1.  In the [button label="Control-M SaaS"](tab-2) tab, select the **Planning** domain from the top navigation.
2.  Open the **Folders and Jobs** tab.
3.  In the **Filter Folders and Jobs** panel, locate the **Folder Name** field and enter: `[[ Instruqt-Var key="CTM_USER_CODE" hostname="server" ]]`
4.  Click **Apply** to filter the list.
5.  Find your workflow named: `[[ Instruqt-Var key="CTM_USER_CODE" hostname="server" ]]_Dominos_Pizza_Workflow_preprod`
6. Click **Open Workspace** .
> 🧠 **Why this matters**:

Summary
===
🎉 You have:
 - Configured the Control‑M CLI and connected to a SaaS environment
 - Logged in and navigated the Control‑M Web UI
 - Explored a Jobs-as-Code workflow for a Pizza Order Fufillment Data Pipeline
 - Applied naming standards and personalized the workflow
 - Deployed and viewed the workflow in Control‑M SaaS

