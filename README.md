
# FactoryControlApp:

This module controls the Alarm Light and Reset button.
The Output of VA (Video Analytics) i.e. the classified results data (MetaData, Frame) is published on a topic (which is mentioned in the docker compose.yml file in VA section) & the Factory control app subscribes to this topic (again sub topic mentioned in compose file of factory control app section). This meta data is parsed by the FCA & is used to determine if the frame is Defective or a proper one & glow the Red or green light in the IO module (Adam controller) respectively.

FactoryControlApp uses Message Bus Library to subscribe the output of VA (Video analytics) on the topic where VA publishes the classified data on the same topic.
The config about Adamcontroller (IO module) like port, IP address, register bits is stored in ETCD (A distributed key-value store).

# Running FactoryControlApp

**Pre-requisites**
1. Configure io_module using a tool **AdamApax.Net Utility V2.05.11 B19.msi**. This can be downloaded from [here]
   (https://support.advantech.com/support/DownloadSRDetail_New.aspx?SR_ID=1-2AKUDB&Doc_Source=Download) by selecting **Primary** Download Site with the **AdamApax.Net Utility V2.05.11 B19.msi**.

    **Note**: System from which io_module is configures and io_module both should be in same subnet.
    During the next step, if password prompt is asked then the password is "00000000"

2. Install and open the downloaded app and follow the below instructions:<br>
    a. On the left-hand side pannel, right click on `Ethernet` and select `Search Device`<br>
    b. io_module will be detected (ADAM-6050) under Ethernet, click on it and go to `Network` tab and set the `<ip_address>` to the io_module.<br>

Changes needs to be done in ETCD for FactoryControlApp/config as follows:
```
{
    "io_module_ip": "<IP of IO module>",
    "io_module_port": 502,
    "red_bit_register": 20,
    "green_bit_register": 19
}
```
Just verify if "PubTopics" of VA in compose file is same as the "SubTopics" of FCA in compose file. Also the stream config file (<Topic>_cfg) of both VA & FCA should be same. Post this goto the host system then do a "sudo make build run" from [repo]/docker_setup directory which will build & run all the modules including VA, FCA & start the pipeline.
RED and GREEN lights should start glowing.

**NOTE**: For the circuit connections of the lab setup, refer 4.5 (4.5.2 IO module) in the document **FactoryControlApp/HW_Configuration.pdf**
