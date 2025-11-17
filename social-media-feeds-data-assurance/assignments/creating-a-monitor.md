# Setting up Data Assurance: Creating a Monitor

Explore the Data Assurance Domains
==
1. In the [button label="Control-M Data Assurance"](tab-0) tab, review the different domains.
	- **Dashboard**: Provides a unified real-time view of all validation outcomes, showing where data passed, failed, or needs attention.
	![Nov-15-2025_at_10.16.03-image.png](https://play.instruqt.com/assets/tracks/t2hkmzw8ofv4/0768649ecc5f422303aea3f14367a857/assets/Nov-15-2025_at_10.16.03-image.png)
	- **Catalog**: Defines your data sources, schemas, and validation rules so Control-M knows what “good data” looks like.
	![Nov-15-2025_at_10.16.16-image.png](https://play.instruqt.com/assets/tracks/t2hkmzw8ofv4/744e6e41a3e4f67994b2524115445a2b/assets/Nov-15-2025_at_10.16.16-image.png)
	- **Monitors**: Apply those rules to real datasets, automatically checking quality and triggering actions based on results.
	![Nov-15-2025_at_10.16.27-image.png](https://play.instruqt.com/assets/tracks/t2hkmzw8ofv4/f32b23530fb220733771643cb8b9bb75/assets/Nov-15-2025_at_10.16.27-image.png)

Configure the Schema
==
In the previous Challenge, Control-M was given access to the `feeds.csv` file through the `SOCIAL_MEDIA_FEEDS` Centralized Connection Profile.

1. Select the **Catalog** tab, and then click **Refresh**.
![Nov-14-2025_at_13.13.45-image.png](https://play.instruqt.com/assets/tracks/t2hkmzw8ofv4/92fa0f465753ee633da60e5d541c8e69/assets/Nov-14-2025_at_13.13.45-image.png)
2.  After the Refresh is complete, your data source,  **SOCIAL_MEDIA_FEEDS**,  will appear in the Data Assurance Catalog (with warning, due to missing schema).
3.  Select the **SOCIAL_MEDIA_FEEDS** data source, and then Select **Configure Schema**
![Nov-14-2025_at_19.45.03-image.png](https://play.instruqt.com/assets/tracks/t2hkmzw8ofv4/7963738227e674fcadaddf2cd4b446a1/assets/Nov-14-2025_at_19.45.03-image.png)
4.  Input the Schema Name: `SOCIAL_MEDIA_FEEDS_SCHEMA`
5. Create a CSV file locally,  with the below contents:

```
Field name, DATA TYPE
PostID, CHAR
Platform, CHAR
Author, CHAR
Date, CHAR
Content, CHAR
Hashtags, CHAR
Likes, INT
Comments, INT
Shares, INT
```
6. Select **Schema**, and **Attach** the CSV file created in the previous step. This file will tell Control-M the schema (structure) of your data source.
![Nov-14-2025_at_13.21.13-image.png](https://play.instruqt.com/assets/tracks/t2hkmzw8ofv4/1fc004d329f5f69e1e1289dd3894bfba/assets/Nov-14-2025_at_13.21.13-image.png)
7. With the Schema file attached, select **Next**
![Nov-15-2025_at_10.33.50-image.png](https://play.instruqt.com/assets/tracks/t2hkmzw8ofv4/05c82020a14082524e315e2c73b2da43/assets/Nov-15-2025_at_10.33.50-image.png)
8. Review the Schema (structure), and click **Save**
![Nov-15-2025_at_10.38.44-image.png](https://play.instruqt.com/assets/tracks/t2hkmzw8ofv4/63843fdb32125695a68a8eab141e4611/assets/Nov-15-2025_at_10.38.44-image.png)

You've defined the data to validte, the next step is to set up your data validation checks by defining monitors and metrics.

Configure the Monitor and Metrics
==
A monitor is a collection of up to 50 metrics. A metric is a single check against a dataset (e.g., a database table or .csv file).

1. Select the **Monitors** tab, and then **New Monitor**.
![Nov-14-2025_at_13.24.17-image.png](https://play.instruqt.com/assets/tracks/t2hkmzw8ofv4/aaf3e547f2120f41dfe18dff22b18f60/assets/Nov-14-2025_at_13.24.17-image.png)
2. Expand the **SOCIAL_MEDIA_FEEDS** data source,  select the **SOCIAL_MEDIA_FEEDS_SCHEMA**, and click **Select dataset**
![Nov-15-2025_at_10.53.55-image.png](https://play.instruqt.com/assets/tracks/t2hkmzw8ofv4/84f094533f51631864fa612527aabfef/assets/Nov-15-2025_at_10.53.55-image.png)
3. Enter the monitor name: `SOCIAL_MEDIA_FEEDS_MONITOR`, and select **New Metric**.
![Nov-15-2025_at_10.57.27-image.png](https://play.instruqt.com/assets/tracks/t2hkmzw8ofv4/95201f6b2ab48716f554fdf1376446d5/assets/Nov-15-2025_at_10.57.27-image.png)
4. Complete the Metric **Scope** with the folliwng selections, and select **Add metric**.
	- **Field**: `Likes (numerical)`
	- **Metric**: `Distinct values count`
	- **Operator**: `Greater than or equal to`
	- **Threshold**: `50`
>[!NOTE]


![Nov-15-2025_at_10.59.54-image.png](https://play.instruqt.com/assets/tracks/t2hkmzw8ofv4/073bb05240bf70ca0e491cedd361844a/assets/Nov-15-2025_at_10.59.54-image.png)

5. Add a second Metric by selecting **New Metric**.
6. Complete the Metric **Scope** with the folliwng selections, and select **Add metric**.
	- **Field**: `Shares (numerical)`
	- **Metric**: `Distinct values count`
	- **Operator**: `Greater than or equal to`
	- **Threshold**: `10`
>[!NOTE]


![Nov-15-2025_at_11.02.47-image.png](https://play.instruqt.com/assets/tracks/t2hkmzw8ofv4/cca334965f70dc1e177e759c1e21dadf/assets/Nov-15-2025_at_11.02.47-image.png)
7. With the **Shares** and **Likes** Metrics added,  click **Save Monitor**
![Nov-15-2025_at_11.04.32-image.png](https://play.instruqt.com/assets/tracks/t2hkmzw8ofv4/86607c7e908bceb7e9a093239b394d06/assets/Nov-15-2025_at_11.04.32-image.png)

Summary
==
