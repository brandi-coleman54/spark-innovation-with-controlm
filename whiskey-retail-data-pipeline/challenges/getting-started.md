About This Lab
===
In this hands-on lab, ...

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

Step 3: Explore the Whiskey Retail Data Pipeline and the Payments Worfklow
===
>💡 **What this is**:
1. In the [button label="Code Editor"](tab-1) tab,  open `~/workflows/data-pipeline.json`.
2. Take a moment to review the job flow:
3. Open `~/workflows/payments.json`.
4. Take a moment to review the job flow:
> 🧠**Why this matters**:

Step 4: Prepare the Data Pipeline for Updates
===
>💡 **What this is**: Before updating, you’ll personalize the workflow and apply company standards to avoid conflicts and ensure compliance.
1. In the [button label="Code Editor"](tab-1) tab, open `~/workflows/deploy-descriptor.json`.
2. Replace all placeholder values:
	- **replace-with-usercode** = `[[ Instruqt-Var key="CTM_USER_CODE" hostname="server" ]]`
	- **replace-with-email** = `[[ Instruqt-Var key="CTM_USER" hostname="server" ]]`
3.  In the [button label="Terminal"](tab-0) tab, transform the workflow using the Deploy Descriptor:
```bash
cd /home/controlm/spark-innovation-with-controlm/whiskey-retail-data-pipeline/workflows/
ctm deploy transform data-pipeline.json deploy_descriptor.json > [[ Instruqt-Var key="CTM_USER_CODE" hostname="server" ]]_data-pipeline.json
```
4. Ensure the transformation is correct.
> 🧠 **Why this matters**: Organizations usually enforce naming conventions, folder structures, and ownership rules for all Control‑M jobs, called Site Standards. If you deploy without aligning to these standards, you risk overwriting other jobs or causing conflicts.  For more information, refer to the documentation:  [Deploy Descriptor](https://documents.bmc.com/supportu/controlm-saas/en-US/Documentation/API_DeployDescriptor.htm)

Summary
===
🎉 You have:
 - Configured the Control‑M CLI and connected to a SaaS environment
 - Logged in and navigated the Control‑M Web UI
 - Explored a Jobs-as-Code workflow for a Pizza Order Fufillment Data Pipeline
 - Applied naming standards and personalized the workflow
 - Deployed and viewed the workflow in Control‑M SaaS

