About This Lab
===

In this hands-on lab,  you'll install the **Control-M Automation API CLI** using Python and configuring it for use with a pre-defined Control-M SaaS environment.

## 🚀 What You'll Learn

✅Download and install the CLI

✅ Set up your CLI environment for authenticated access

✅  Verify the setup by executing your first API call

 Step 1: Perform a Python Package Installation of Control-M CLI
===
>💡 **What this is**: The Control-M CLI has been downloaded for you.

>🧠 **Why this matters**: For more information, refer to the documentation:  [Performing a Python Package Installation of Control-M Automation API CLI](https://documents.bmc.com/supportu/controlm-saas/en-US/Documentation/API_H_SettingUp.htm#PerformingaPythonPackageInstallationofControlMAutomationAPICLI)

Step 2: Create a Token for API Authentication
===
>💡 **What this is**:  An API Token has been created for you.

>🧠 **Why this matters**: For more information, refer to the documentation:  [Creating a Token for API Authentication](https://documents.bmc.com/supportu/controlm-saas/en-US/Documentation/API_H_SettingUp.htm#CreatingaTokenforAPIAuthentication)

 Step 3: Set Up the Control-M CLI Environment
===
>💡 **What this is**: Control‑M CLI commands run against an environment, which is just a combination of a Control‑M API endpoint and your authentication token.
1. In the [button label="Terminal"](tab-0) tab,  add the **preprod** environment (this points the CLI to your Control‑M SaaS PreProd instance):
```bash
ctm env add preprod [[ Instruqt-Var key="CTM_AAPI_ENDPOINT" hostname="server" ]] [[ Instruqt-Var key="CTM_AUTH_TOKEN" hostname="server" ]]
```
> 🧠**Why this matters**: The Control-M CLI is your gateway to automating workflows programmatically. Defining your environment lets you securely connect and interact with the Control-M API. For more information, refer to the documentation:  [Environment Service](https://documents.bmc.com/supportu/controlm-saas/en-US/Documentation/API_Services_EnvironmentService.htm#environmentadd)

Step 4: Login to Control-M SaaS for the First Time
===
>💡 **What this is**:
1. Locate the email titled "Welcome to Helix Control-M!". Sent to: `[[ Instruqt-Var key="CTM_USER" hostname="server" ]]`.
2. Retrieve your login credentials:
	- From the email, copy your <b>User name</b>  and  <b>Password</b> and store them for the next step.
3.  In Instruqt, click on the [button label="Control-M SaaS"](tab-2) tab to open the Control-M SaaS Web UI.
4. Paste your <b>User name</b>  and  <b>Password</b> from the email and Login.
> 🧠**Why this matters**:

Summary
===
🎉 You have:
- Installed the Control-M Automation CLI
- Authenticated with a pre-configured SaaS environment
- Run your first API command


