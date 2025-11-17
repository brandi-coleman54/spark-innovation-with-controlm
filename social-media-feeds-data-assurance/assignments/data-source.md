# Setting up Data Assurance: Adding a Data Source
Connect your `feeds.csv` source – First, you need to give Control-M access to the `feeds.csv` file  by creating a centralized connection profile.

In that profile, you will select the data source type, `File`,  (Data Assurance supports .csv files and Snowflake, PostgreSQL, MSSQL, and Oracle databases) and specify the path to the local directory, `/home/ctmda/social-media-feeds/`, where your `feeds.csv` file is stored.

This must be on the same machine as the Control-M Agent  and Data Assurance plug-in, `dadb`.

Create a Data Assurance Centralized Connection Profile
==
1. In the [button label="Control-M Configration"](tab-0) tab, click **Centralized Connection Profiles**.
![Nov-14-2025_at_18.41.02-image.png](https://play.instruqt.com/assets/tracks/t2hkmzw8ofv4/4be4cd0e74ee6b8e1d1fe342ddcd0462/assets/Nov-14-2025_at_18.41.02-image.png)
2. Select **Add Connection Profile** and the **Data Assurance **Plug-in
![Nov-14-2025_at_17.58.07-image.png](https://play.instruqt.com/assets/tracks/t2hkmzw8ofv4/a3ab79bd20bda8addd13ae2485f8c2bc/assets/Nov-14-2025_at_17.58.07-image.png)
3. In the Add Data Assurance Connection Profile Window, input the following fields:
	-  **Connection Profile Name**: `SOCIAL_MEDIA_FEEDS`
	- **Data source**: `File`
	- **Path**: `/home/ctmda/social-media-feeds/`
	- **File Pattern**: `feeds.csv`
 ![Nov-14-2025_at_17.59.29-image.png](https://play.instruqt.com/assets/tracks/t2hkmzw8ofv4/f5e02a4e932926b05204e1d23b15bd01/assets/Nov-14-2025_at_17.59.29-image.png)
4. Click **Test** to ensure the Connection Profile is configured correctly.
![Nov-14-2025_at_18.01.28-image.png](https://play.instruqt.com/assets/tracks/t2hkmzw8ofv4/2164ae7b123b8875523c07c1185b4276/assets/Nov-14-2025_at_18.01.28-image.png)
5. Select **dadb** from the drop-down list, and click **Test**
![Nov-14-2025_at_18.44.25-image.png](https://play.instruqt.com/assets/tracks/t2hkmzw8ofv4/d638e4b6a97ab3ca8191b3755e7c0c32/assets/Nov-14-2025_at_18.44.25-image.png)
6. With a successful **Test**, Click **Close**
![Nov-14-2025_at_18.47.46-image.png](https://play.instruqt.com/assets/tracks/t2hkmzw8ofv4/f89eb7f1054961ed07e095e551adf553/assets/Nov-14-2025_at_18.47.46-image.png)
7. **Add** the Data Assurance Connection Profile
![Nov-14-2025_at_18.48.24-image.png](https://play.instruqt.com/assets/tracks/t2hkmzw8ofv4/1d583605884e7e3d4c39b1ced9c7ba49/assets/Nov-14-2025_at_18.48.24-image.png)

Summary
==
![social-media-feeds-cp.gif](https://play.instruqt.com/assets/tracks/t2hkmzw8ofv4/ece7dbba5b31bcbc983675051cc0b704/assets/social-media-feeds-cp.gif)
