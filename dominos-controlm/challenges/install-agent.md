About This Lab
===

In this lab, you’ll ...

---

## 🚀 What You’ll Learn

✅

✅

✅

Step 1: Install Control-M SaaS Agent
===
>💡 **What this is**:
1.  In the [button label="Terminal"](tab-0) tab, view the available Images to Provision:
```bash
cd /home/controlm
ctm provision images Linux
```
2. Install a local Control-M SaaS Agent:
```bash
ctm provision saas::install Agent_Ubuntu.Linux instruqt [[ Instruqt-Var key="CTM_USER_CODE" hostname="server" ]]_instruqt_server
```
>🧠 **Why this matters**:

Step 2: Update the Host in the Pizza Order Fulfillment Workflow
===
>💡 **What this is**:
1. In the [button label="Code Editor"](tab-1) tab, open `~/worfklows/[[ Instruqt-Var key="CTM_USER_CODE" hostname="server" ]]_order_fulfillment.json`.
2. Replace all placeholder values.
	- **replace-with-instruqt-host** = `[[ Instruqt-Var key="CTM_USER_CODE" hostname="server" ]]_instruqt_server`
3. Deploy your changes to the workflow.
```bash
cd /home/controlm/spark-innovation-with-controlm/dominos-controlm/workflows
ctm deploy [[ Instruqt-Var key="CTM_USER_CODE" hostname="server" ]]_order_fufillment.json
```
>🧠 **Why this matters**:

Step 3: Place Another Order to test the Pizza Order Fulfillment Workflow
==
>💡 **What this is**:
1. In the [button label="Pizza Tracker"](tab-3) tab,   click the **Place Order** to place a another Pizza Order.
2. Confirm the Order was placed successfully.
 3. In the [button label="Control-M SaaS"](tab-2) tab, select the **Monitoring** domain.
 4.  Open the Viewpoint `[[ Instruqt-Var key="CTM_USER_CODE" hostname="server" ]]*`
>🧠 **Why this matters**:

Summary
==

