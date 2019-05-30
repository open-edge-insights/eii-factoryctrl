# FactoryControlApp:

This module controls the Alarm Light and Reset button. IO_Module(Adam controller) publishes the data to mqtt with topic "Advantech/<ADAM_MODULE_ID>/data" and telegraf which is subscribed to same topic receives the data from io_module(Adam controller) and writes module_io measurement in influxdb.

FactoryControlApp uses StreamSubLib to subscribe to influxdb on the required **output_stream** which should be given in FactoryControlApp/config.json.

**output_stream** data is used to control alarm light.

# Running FactoryControlApp

**Pre-requisites**
1. Configure io_module using a tool **AdamApax.Net Utility V2.05.11 B19.msi**. This can be downloaded from [here]
   (https://support.advantech.com/support/DownloadSRDetail_New.aspx?SR_ID=1-2AKUDB&Doc_Source=Download) by selecting **Primary** Download Site with the **AdamApax.Net Utility V2.05.11 B19.msi**.

    **Note**: System from which io_module is configures and io_module both should be in same subnet.
    During the next step, if password prompt is asked then the password is "00000000"

2. Install and open the downloaded app and follow the below instructions:<br>
    a. On the left-hand side pannel, right click on `Ethernet` and select `Search Device`<br>
    b. io_module will be detected (ADAM-6050) under Ethernet, click on it and go to `Network` tab and set the `<ip_address>` to the io_module.<br>

Changes needs to be done in FactoryControlApp/config.json. They are as follows:

1. FactoryControlApp/config.json
    * "output_stream" : "stream1_results" or "cam_serial1_results" or "cam_serial1_results" and so on.
    * "io_module_ip" : "<ip_address given in the pre-requisite step#2.b>"

**NOTE**: For the circuit connections of the lab setup, refer 4.5 (4.5.2 IO module) in the document **FactoryControlApp/HW_Configuration.pdf**
