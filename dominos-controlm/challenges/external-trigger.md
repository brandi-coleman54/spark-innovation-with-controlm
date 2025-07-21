About This Lab
===

In this lab, you’ll explore **event-driven orchestration** by integrating Control‑M with a simulated Pizza Tracking App. You’ll learn how to configure Control‑M to listen for external events (like a new pizza order) and automatically trigger your workflow—no manual or scheduled execution required.

---

## 🚀 What You’ll Learn

✅ How to create and configure an Event job in Control‑M

✅ How to connect a tracking app trigger (simulated API/webhook) to Control‑M

✅ How to monitor and validate event-driven job execution in the Web UI

Step 1: Review the Pizza Order Application
===
>💡 **What this is**:
1. In the [button label="Code Editor"](tab-1) tab, open `~/scripts/pizza_tracker_app.py`.
2. Take a moment to review the application code.
3. Replace all placeholder values:
	- **replace-with-endpoint** =  `[[ Instruqt-Var key="CTM_AAPI_ENDPOINT" hostname="server" ]]`
	- **replace-with-token** = ` [[ Instruqt-Var key="CTM_AUTH_TOKEN" hostname="server" ]]`
	- **replace-with-ctm-server** = `IN01`
	- **replace-with-ctm-folder** = `[[ Instruqt-Var key="CTM_USER_CODE" hostname="server" ]]_Pizza_Order_Workflow_preprod`
>🧠 **Why this matters**:

Step 2: Run the Pizza Order Application
===
>💡 **What this is**:
1. In the [button label="Terminal"](tab-0) tab, start your Pizza Tracker Application:
```bash
cd /home/controlm/spark-innovation-with-controlm/dominos-controlm/scripts/
python3 pizza_tracker_app.py
```
2. In the [button label="Pizza Tracker"](tab-3) tab, ensure the Pizza Tracker Application is running.
![pizza_tracker_app.png](https://play.instruqt.com/assets/tracks/e0ld5xza7xrm/61cd65397aca680cb5a85b1e68336f1e/assets/pizza_tracker_app.png)
>🧠 **Why this matters**:

Step 3: Place an Order to test the Workflow Trigger in Control-M SaaS
==
>💡 **What this is**:
1. In the [button label="Pizza Tracker"](tab-3) tab, click the **Place Order** button.
2. Confirm the Order was placed successfully.
![pizza_tracker_run.png](https://play.instruqt.com/assets/tracks/e0ld5xza7xrm/aa53d0e9ee8bc63a6b4458f16cf47faa/assets/pizza_tracker_run.png)
>🧠 **Why this matters**:

Step 4: View the Triggered Workflow in the Control-M SaaS Web UI
==
>💡 **What this is**:
1.  In the [button label="Control-M SaaS"](tab-2) tab,  select the **Monitoring** domain from the top navigation.
2.  Click **Add Viewpoint**
3.  Locate the **Folder Name** field under **Include Attributes** and enter: `[[ Instruqt-Var key="CTM_USER_CODE" hostname="server" ]]*`
4.  Click **Open** .
>🧠 **Why this matters**:

Summary
==

