# Performance Monitor (Classifier) Using a Threshold File

This custom monitor provides an example of pulling in the thresholds for analysis from an existing file. This monitor specifically is designed for a classifier where labeled (actual) data is identified and calculates the percentage of positive outcomes in comparison to the total predictions. The monitor also outputs the expected rate which is pulled from the existing thresholds file.

# Required Inputs / Assumptions
**Production (or Sample) Data:**
1. There production (or sample) data contains a column with labels (actuals)
2. The production (or sample) data contains a date column called "POLEFFDATE_M" (this can be changed/configurable). The POLEFFDATE_M is of format 17-May-23

**Business Model Setup:**
3. The business model has been registered in ModelOp Center
4. A schema has been created for the business model with the actuals column identified as "label" in the schema

**KPI Threshold File:**
5. There is a threshold file of type CSV that contains 2 fields: POLEFFDATE_M, Modeled_Policy_Renewal
6. The POLEFFDATE_M is of format 17-May-23

# To Use
**Import this Monitor:**
1. Go to the "Monitors" tab of ModelOp Center
2. Click the "Add Monitor" button in the top right corner
3. Provide the URL to this repo
4. Fill in the other information and click "Import Model"
5. In the resulting page, click "Create Snapshot". Click next several times and click "Create Snapshot"

**Add the Monitor to your Business Model:**
1. Open your model from the "Business Models" inventory page
2. If you haven't taken a snapshot of your model, take a snapshot
3. From the Snapshot of your model, click the "Monitoring" tab
4. Click the "Add Monitor" button
5. Search for the monitor that you added
6. Choose the latest snapshot from the list
7. On the Asset tab:
    a. In the "Input Assets" section, select the Production (Sample) data for your business model
    b. In the "Additional Assets" section, upload the CSV "KPI threshold" file
8. On the "Thresholds" tab, select the "External_KPI.dmn" file that is in this repository
9. Click next, next, and then save.
10. Once saved, click the "Play" button to run the monitor. 
11. You should see the test results once the job complete. 
12. Clicking on resulting "Model Test Results" will take you to the Test Results page, which should have a Notification of whether the test passed or not.
