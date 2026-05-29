# Scenario 1: Simplifying Branch to Hub Communication


Secure Firewall release 7.6 introduced SD-WAN wizard on FMC that
provides admins ability to configure the complete SD-WAN Topology
automating the VPN and Overlay routing configuration using minimal
clicks and automated inputs.

SD-WAN Topology provides –

1.  Simplified wizard to create Route-Based Hub & Spoke Topology

2.  Auto-generation of static virtual tunnel interfaces on spokes

3.  Bulk Spoke Addition

4.  Simplification and automation of overlay routing with BGP

5.  Redistribution of connected routes through BGP

For redistribution of Static and IGP dynamic routes (EIGRP/OSPF),
route-maps are preconfigured in the lab and will be used in device
specific BGP configuration.

## Network Diagram

<figure markdown style="max-width:16.0cm;">
  ![screenshot](assets/screens/s1.png){ loading=lazy }
</figure>

## Task 1: Configuring SD-WAN Topology between Branches (Spokes) and Headquarters (Hub) using DVTI on Hub

In this lab task, you will learn how to create an IPSec VPN Tunnel
between Branch and Hub Secure Firewall using SD-WAN Wizard in FMC
(<https://198.18.133.201/>).  
  
Launch FMC by clicking **FMC Web** icon in Cisco Secure Firewall Quick
Launch window.

Enter the credentials (admin/dCloud123!).

<figure markdown style="max-width:10.0cm;">
  ![screenshot](assets/extracted/image11.png){ loading=lazy }
</figure>

### Step 1: Create SD-WAN Topology

To configure a new SD-WAN Topology, go to **Secure Connections \>
Site-to-Site VPN & SD-WAN**

<figure markdown style="max-width:12.0cm;">
  ![screenshot](assets/screens/s1-t1-s1-1.png){ loading=lazy }
</figure>

Click **+ Add**

<figure markdown style="max-width:16.0cm;">
  ![screenshot](assets/screens/s1-t1-s1-2.png){ loading=lazy }
</figure>

There are prerequisites to SD-WAN Topology. Click/hover on
Prerequisites in Create VPN Topology Dialog to view the information.

<figure markdown style="max-width:16.0cm;">
  ![screenshot](assets/screens/s1-t1-s1-2-1.png){ loading=lazy }
</figure>

Enter the following details in the pop-up:

1.  **Topology Name**: name the VPN topology as **Corp-SD-WAN-1**.

2.  Ensure the following are selected:

    1.  **VPN Type**: SD-WAN Topology
    2.  **VPN Topology**: Hub and Spoke

3.  Click **Create**.

<figure markdown style="max-width:16.0cm;">
  ![screenshot](assets/screens/s1-t1-s1-3.png){ loading=lazy }
</figure>

### Step 2: SD-WAN Topology – Hub Configuration

This opens the SD-WAN Wizard page.  
Click **Add Hub** on the right in **Hubs** section to add the Hub
device.

<figure markdown style="max-width:16.0cm;">
  ![screenshot](assets/screens/s1-t1-s2-1.png){ loading=lazy }
</figure>

Enter the following details in the **Add Hub** dialog:

1.  **Device**: click the dropdown and select the FTD **NGFW-HUB**.

2.  **Dynamic Virtual Tunnel Interface (DVTI)**: click **+** adjacent
    to the drop-down to create a DVTI. The **Add Virtual Tunnel
    Interface** dialog opens. Fill it in:

    1.  **Tunnel Type**: pre-selected to *Dynamic* (greyed out).
    2.  **Name**: pre-filled as `outside_dynamic_vti_1` &mdash; keep
        the default.
    3.  **Enabled**: enabled by default &mdash; leave as-is.
    4.  **Security Zone**: select **Tunnel_Zone** from the drop-down.
    5.  **Template ID**: unique ID for the DVTI, already pre-filled.
    6.  **Tunnel Source**: defaults to **outside**. If not, pick
        **outside** from the drop-down. Set the **Tunnel Source IP
        Address** to `20.1.101.101`.

    <figure markdown style="max-width:6.6cm;">
      ![screenshot](assets/screens/s1-t1-s2-2-1.png){ loading=lazy }
    </figure>

    <figure markdown style="max-width:7.7cm;">
      ![screenshot](assets/screens/s1-t1-s2-2-2.png){ loading=lazy }
    </figure>

    7.  **IPsec Tunnel Mode**: leave as IPv4 (default).
    8.  **IP Address**: DVTI is a template interface and can't have a
        static IP &mdash; it must **Borrow IP (IP unnumbered)** from
        another interface (Cisco recommends a loopback, which never
        goes down). Click **+** next to the **Select Interface**
        drop-down to create one &mdash; the **Add Loopback Interface**
        dialog opens:

        1.  In the **General** tab:

            1.  **Name**: `Hub_Tunnel_IP_1`
            2.  **Loopback ID**: `1`

        2.  In the **IPv4** tab:

            1.  **IP Type**: Use Static IP
            2.  **IP Address**: `169.254.10.1/32`

        3.  Click **OK** to save the loopback.

    9.  Back on the **Add Virtual Tunnel Interface** dialog, confirm
        **Borrow IP (IP unnumbered)** is now set to
        **Loopback1 (Hub_Tunnel_IP_1)**.

3.  Click **OK** on the **Add Virtual Tunnel Interface** dialog to
    save the DVTI. You will see a dialog confirming **Virtual Tunnel
    Interface Added** successfully &mdash; click **OK**.

    <figure markdown style="max-width:9.6cm;">
      ![screenshot](assets/screens/s1-t1-s2-3-1.png){ loading=lazy }
    </figure>

    <figure markdown style="max-width:10.6cm;">
      ![screenshot](assets/screens/s1-t1-s2-3-2.png){ loading=lazy }
    </figure>

    <figure markdown style="max-width:12.0cm;">
      ![screenshot](assets/screens/s1-t1-s2-3-3.png){ loading=lazy }
    </figure>

    <figure markdown style="max-width:9.6cm;">
      ![screenshot](assets/screens/s1-t1-s2-3-4.png){ loading=lazy }
    </figure>

    <figure markdown style="max-width:9.8cm;">
      ![screenshot](assets/screens/s1-t1-s2-3-5.png){ loading=lazy }
    </figure>

4.  Back in the **Add Hub** dialog, confirm the DVTI is automatically
    populated. Otherwise, select **outside_dynamic_vti_1** from the
    **Dynamic Virtual Tunnel Interface (DVTI)** drop-down.

5.  **Hub Gateway IP Address**: shows the Tunnel Source IP &mdash; do
    not change.

6.  **Spoke Tunnel IP Address Pool**: FMC auto-generates the static
    VTI interfaces on the spoke devices. This pool defines the IP
    range FMC draws from when assigning addresses to those sVTI
    interfaces. Click the **+** icon next to the field to create a
    new pool &mdash; the **New IPv4 Pool** dialog opens. Fill it in:

    1.  **Name**: `NGFW_Hub_IPv4_Pool_1`
    2.  **IPv4 Address Range**: `169.254.10.3-169.254.10.100`. FMC
        assigns IPs from this range to the static VTI interfaces on
        the spoke devices.
    3.  **Mask**: `255.255.255.0`
    4.  **Allow Override**: leave disabled (default).
    5.  Click **Save** to create the pool.

    <figure markdown style="max-width:9.6cm;">
      ![screenshot](assets/screens/s1-t1-s2-4-1.png){ loading=lazy }
    </figure>

    <figure markdown style="max-width:12.0cm;">
      ![screenshot](assets/screens/s1-t1-s2-4-2.png){ loading=lazy }
    </figure>

    <figure markdown style="max-width:9.5cm;">
      ![screenshot](assets/screens/s1-t1-s2-4-3.png){ loading=lazy }
    </figure>

    Back on the **Add Hub** dialog, set **Spoke Tunnel IP Address
    Pool** to the pool you just created &mdash; **NGFW_Hub_IPv4_Pool_1**
    (use the drop-down if it isn't auto-populated).

7.  All Hub inputs are now filled in. Click **Add** on the **Add Hub**
    dialog to save it and add the Hub to the SD-WAN topology. The row
    for **NGFW-HUB** appears in the **Hubs** section of the **SD-WAN
    Topology Wizard**. Click **Next** to proceed.

    <figure markdown style="max-width:16.0cm;">
      ![screenshot](assets/screens/s1-t1-s2-5.png){ loading=lazy }
    </figure>

### Step 3: SD-WAN Topology – Bulk Spoke Configuration

**Add Bulk Spoke Dialog** allows admins to add more than one Spoke
Device with simple intuitive workflow.

Click **Add Spokes (Bulk Addition)** button in spokes step.

<figure markdown style="max-width:16.0cm;">
  ![screenshot](assets/screens/s1-t1-s3-1.png){ loading=lazy }
</figure>

Enter the following details in the **Add Bulk Spokes** dialog box:

1)  **Devices**: Select **NGFW-B1** and **NGFW-B2** from the **Available
    Devices**, click on **Add** button to move the devices to
    **Selected Devices**.

2)  **Interface Name Pattern:** Ensure Interface Name Pattern field is
    set to **outside**. Using this name pattern, FMC automatically
    searches the devices for a matching interface, and these
    interfaces are selected as VPN interface for the selected spoke
    devices.

3)  **Next:** Click on **Next** button

4)  **Add:** Once you click on Next button, FMC lists the selected
    devices with Interfaces that matches the given name pattern.
    Review the selection and click on the **Add** button.

5)  **Next:** Once you review the spokes, click on **Next** button to
    move on to the next step

<figure markdown style="max-width:12.0cm;">
  ![screenshot](assets/screens/s1-t1-s3-2-1.png){ loading=lazy }
</figure>

<figure markdown style="max-width:12.0cm;">
  ![screenshot](assets/screens/s1-t1-s3-2-2.png){ loading=lazy }
</figure>

<figure markdown style="max-width:16.0cm;">
  ![screenshot](assets/screens/s1-t1-s3-3.png){ loading=lazy }
</figure>

### Step 4: SD-WAN Topology - Authentication Settings

This lab task uses system-defined defaults for IKE, IPsec etc., to
reduce administrator overhead for configuration though these settings
can be customized. In this step, you will configure pre-shared key
authentication with manual key.

1.  Click **Authentication Type** and select **Pre-shared Manual Key**

2.  Enter **cisco123** in **Key** Text Box

3.  Enter **cisco123** in **Confirm** **Key** Text Box

4.  Click on **Next** button to save the settings

<figure markdown style="max-width:16.0cm;">
  ![screenshot](assets/screens/s1-t1-s4-1.png){ loading=lazy }
</figure>

### Step 5: SD-WAN Topology – Add Tunnel Interfaces to Security Zone Automatically

This section contains the configuration that simplifies the management
of AC policy rules for Tunnel interfaces and BGP for overlay routing.

Upon finishing the SD-WAN Topology Wizard, FMC will automatically
generate Static Virtual Tunnel Interfaces on the spoke devices. Those
auto-generated Tunnel interfaces can be added into a Security Zone
which can be used to define AC rule.

Click on the **Spoke Tunnel Interface Security Zone** drop-down and
select **Tunnel_Zone**.

<figure markdown style="max-width:16.0cm;">
  ![screenshot](assets/screens/s1-t1-s5-1.png){ loading=lazy }
</figure>

### Step 6: SD-WAN Topology – Configure BGP routing

In this step, BGP is configured between Hub and Spoke devices to allow
traffic to be sent through the VPN tunnel. For reference, static
routing is added for underlay (pre-configured in this lab), over which
Spoke to Hub tunnel is established and BGP is configured as overlay.

**SD-WAN Settings** simplifies the configuration of BGP for overlay
network. By providing few simple inputs, BGP configuration can be
deployed to all the Hubs and Spokes.

Enter the following in **SD-WAN Settings**

1)  **Enable BGP on the VPN Overlay Topology**: Enable the checkbox to
    enable BGP.

2)  **Autonomous System Number:** Ensure BGP AS is set to **64512**.

3)  **Community Tag for Local Routes:** Enter **9901** as Community Tag
    which will be used to tag local routes when redistributed.

4)  **Redistribute Connected Interfaces:** Enable the checkbox to
    redistribute the connected inside / LAN interfaces over the
    BGP overlay. Leave the default value **Default Inside** in the
    drop-down.

5)  **Enable Multiple Paths for BGP**: Enable multipath load sharing
    using BGP routes. This checkbox is **enabled** by default. Leave
    the default option.

6)  **Next**: Click on **Next** button to save the changes in SD-WAN
    Settings.

<figure markdown style="max-width:16.0cm;">
  ![screenshot](assets/screens/s1-t1-s6-1.png){ loading=lazy }
</figure>

### Step 7: SD-WAN Topology - Finish

Now, we are done with all the configuration in the SD-WAN Topology.
Click on **Finish** button to save the topology. Click **OK** for the
pop-up dialog “**Click Finish to save your changes.**”

<figure markdown style="max-width:16.0cm;">
  ![screenshot](assets/screens/s1-t1-s7-1.png){ loading=lazy }
</figure>

<figure markdown style="max-width:10.0cm;">
  ![screenshot](assets/screens/s1-t1-s7-2.png){ loading=lazy }
</figure>

1.  Once configured, **Site-to-Site** VPN listing page shows the new
    SD-WAN topology on the same page i.e. on **Secure Connections \>
    Site-to-Site VPN & SD-WAN.**

<figure markdown style="max-width:16.0cm;">
  ![screenshot](assets/screens/s1-t1-s7-3.png){ loading=lazy }
</figure>

2.  Expand the **Corp-SD-WAN-1** node to view all the tunnels in the
    topology. It shows 2 tunnels. Since the configuration has not been
    deployed, it shows **Deployment Pending** and the tunnel shows Amber
    color.

<figure markdown style="max-width:16.0cm;">
  ![screenshot](assets/screens/s1-t1-s7-4.png){ loading=lazy }
</figure>

3.  Verify the Name and IP address of auto generated Static VTI Tunnels
    on Spoke devices using the following steps:

    1.  Click **pencil/edit icon** in Site-to-Site VPN Listing page
        which will open the SD-WAN Topology Wizard

    2.  Click on **edit** link in Spokes step

    3.  Click **View Generated Tunnel Interfaces** button. This opens a
        dialog which shows Spoke devices with generated Static VTIs.

    4.  Click **OK** and then click **Cancel** to revert to Site-to-Site
        VPN Listing page

<figure markdown style="max-width:16.0cm;">
  ![screenshot](assets/screens/s1-t1-s7-5.png){ loading=lazy }
</figure>

<figure markdown style="max-width:16.0cm;">
  ![screenshot](assets/screens/s1-t1-s7-6-1.png){ loading=lazy }
</figure>

<figure markdown style="max-width:16.0cm;">
  ![screenshot](assets/screens/s1-t1-s7-6-2.png){ loading=lazy }
</figure>

<figure markdown style="max-width:16.0cm;">
  ![screenshot](assets/screens/s1-t1-s7-6-3.png){ loading=lazy }
</figure>

## Task 2: Deploy to Hub and Spoke Devices

In this step, you will review all the configuration changes done on
the Hub and Spoke devices and deploy the configuration to the devices.

1)  Click the Deploy button
    ![icon](assets/extracted/image53.png){ .inline-icon .off-glb }
    on the top right on FMC.

2)  This brings up the list of devices that are Ready for Deployment.
    Select the ![icon](assets/extracted/image54.png){ .inline-icon .off-glb }and
    click on **ignore warnings (if any)**
    ![icon](assets/extracted/image55.png){ .inline-icon .off-glb } button to trigger the
    deployment.

3)  View the progress of the deployment on the devices and **wait till
    the deployment is marked Completed** on the Deploy dialog

<figure markdown style="max-width:10.0cm;">
  ![screenshot](assets/extracted/image57.jpeg){ loading=lazy }
</figure>

## Task 3: Configuring BGP Redistribution of EIGRP/OSPF Internal Routes at Hub to SD-WAN

### Step 1: Enable BGP on Hub device

In this step, you will enable BGP on hub device with same autonomous
number as mentioned in SD-WAN Topology.

1.  Edit the device **NGFW-HUB** by navigating to **Devices \> Device
    Management \> Edit NGFW-HUB**

<figure markdown style="max-width:16.0cm;">
  ![screenshot](assets/screens/s1-t3-s1-1.png){ loading=lazy }
</figure>

2.  Click on the **Routing** tab \> scroll down the left menu and click on the
    **BGP** button under **General Settings**, then fill in:

    1.  **Enable BGP**: Check the checkbox to enable BGP.
    2.  **Autonomous System Number**: `64512` (same as specified in the SD-WAN Topology).

<figure markdown style="max-width:16.0cm;">
  ![screenshot](assets/screens/s1-t3-s1-2.png){ loading=lazy }
</figure>

3.  Click on the **BGP IPv4** routing option

    1.  **Enable IPv4**, review the AS Number defaults to **64512**

<figure markdown style="max-width:16.0cm;">
  ![screenshot](assets/screens/s1-t3-s1-3.png){ loading=lazy }
</figure>

### Step 2: Configure redistribution of OSPF routes

In this step, you will enable redistribution of OSPF learnt routes
into BGP. These routes will then be advertised to the SD-WAN peers.

1.  In **BGP IPv4** settings click on **Redistribution** tab and then
    **Add**

<figure markdown style="max-width:16.0cm;">
  ![screenshot](assets/screens/s1-t3-s2-1.png){ loading=lazy }
</figure>

2.  This launches the **Add Redistribution** dialog. Fill it in as
    follows:

    1.  **Source Protocol**: Pick **OSPF** from the drop-down.
    2.  **Process ID**: `1`
    3.  **Route Map**: **Advertise-Hub-Protected-Networks**
    4.  Click **OK** to save the settings.

<figure markdown style="max-width:16.0cm;">
  ![screenshot](assets/screens/s1-t3-s2-2.png){ loading=lazy }
</figure>

### Step 3: Configure redistribution of EIGRP routes

In this step, you will enable redistribution of EIGRP learnt routes
into BGP. These routes will then be advertised to the SD-WAN peers.

1.  In **BGP IPv4** settings click on **Redistribution** tab (you are
    already here with previous step) and then **Add**

2.  This launches the **Add Redistribution** dialog. Fill it in as
    follows:

    1.  **Source Protocol**: Pick **EIGRP** from the drop-down.
    2.  **AS Number**: `1`
    3.  **Route Map**: **Advertise-Hub-Protected-Networks**
    4.  Click **OK** to save the settings.

<figure markdown style="max-width:6.0cm;">
  ![screenshot](assets/screens/s1-t3-s3-1.png){ loading=lazy }
</figure>

3.  Click **Save** on top right to complete the configuration.

<figure markdown style="max-width:16.0cm;">
  ![screenshot](assets/screens/s1-t3-s3-1-1.png){ loading=lazy }
</figure>

## Task 4: Configuring BGP Redistribution of Static Internal Routes at Spoke (NGFW-B1) to SD-WAN

### Step 1: Enable BGP on Spoke device

In this step, you will enable BGP on Spoke device (**NGFW-B1**) with
same autonomous number as mentioned in SD-WAN Topology.

1.  Edit the device **NGFW-B1** by navigating to **Devices \> Device
    Management \> Edit NGFW-B1**

<figure markdown style="max-width:16.0cm;">
  ![screenshot](assets/screens/s1-t4-s1-1.png){ loading=lazy }
</figure>

2.  Click on the **Routing** tab \> click on the **BGP** button under
    **General Settings**, then fill in:

    1.  **Enable BGP**: Check the checkbox to enable BGP.
    2.  **Autonomous System Number**: `64512` (same as specified in the SD-WAN Topology).

<figure markdown style="max-width:16.0cm;">
  ![screenshot](assets/screens/s1-t4-s1-2.png){ loading=lazy }
</figure>

3.  Click on the **BGP IPv4** routing option

    1.  **Enable IPv4**, review the AS Number defaults to **64512**

<figure markdown style="max-width:16.0cm;">
  ![screenshot](assets/screens/s1-t4-s1-3.png){ loading=lazy }
</figure>

### Step 2: Configure redistribution of Static routes

In this step, you will enable redistribution of Static routes into
BGP. These routes will then be advertised to the SD-WAN peers.

1.  In **BGP IPv4** settings click on **Redistribution** tab and then
    **Add**

<figure markdown style="max-width:16.0cm;">
  ![screenshot](assets/screens/s1-t4-s2-1.png){ loading=lazy }
</figure>

2.  This launches the **Add Redistribution** dialog. Fill it in as
    follows:

    1.  **Source Protocol**: Pick **Static** from the drop-down.
    2.  **Route Map**: **Advertise-Branch-Protected-Networks**
    3.  Click **OK** to save the settings.

<figure markdown style="max-width:16.0cm;">
  ![screenshot](assets/screens/s1-t4-s2-2.png){ loading=lazy }
</figure>

3.  Click **Save** on top right to complete the configuration.

<figure markdown style="max-width:16.0cm;">
  ![screenshot](assets/screens/s1-t4-s2-3.png){ loading=lazy }
</figure>

## Task 5: Configuring BGP Redistribution of EIGRP Internal Routes at Spoke (NGFW-B2) to SD-WAN

### Step 1: Enable BGP on Spoke device

In this step, you will enable BGP on Spoke device (**NGFW-B2**) with
same autonomous number as mentioned in SD-WAN Topology.

1.  Edit the device **NGFW-B2** by navigating to **Devices \> Device
    Management \> Edit NGFW-B2**

<figure markdown style="max-width:16.0cm;">
  ![screenshot](assets/screens/s1-t5-s1-1.png){ loading=lazy }
</figure>

2.  Click on the **Routing** tab \> click on the **BGP** button under
    **General Settings**, then fill in:

    1.  **Enable BGP**: Check the checkbox to enable BGP.
    2.  **Autonomous System Number**: `64512` (same as specified in the SD-WAN Topology).

<figure markdown style="max-width:16.0cm;">
  ![screenshot](assets/screens/s1-t5-s1-2.png){ loading=lazy }
</figure>

3.  Click on the **BGP IPv4** routing option

    1.  **Enable IPv4**, review the AS Number defaults to **64512**

<figure markdown style="max-width:16.0cm;">
  ![screenshot](assets/screens/s1-t5-s1-3.png){ loading=lazy }
</figure>

### Step 2: Configure redistribution of EIGRP routes

In this step, you will enable redistribution of EIGRP routes into BGP.
These routes will then be advertised to the SD-WAN peers.

1.  In **BGP IPv4** settings click on **Redistribution** tab and then
    **Add**

<figure markdown style="max-width:16.0cm;">
  ![screenshot](assets/screens/s1-t5-s2-1.png){ loading=lazy }
</figure>

2.  This launches the **Add Redistribution** dialog. Fill it in as
    follows:

    1.  **Source Protocol**: Pick **EIGRP** from the drop-down.
    2.  **AS Number**: `1`
    3.  **Route Map**: **Advertise-Branch-Protected-Networks**
    4.  Click **OK** to save the settings.

<figure markdown style="max-width:16.0cm;">
  ![screenshot](assets/screens/s1-t5-s2-2.png){ loading=lazy }
</figure>

3.  Click **Save** on top right to complete the configuration.

<figure markdown style="max-width:16.0cm;">
  ![screenshot](assets/screens/s1-t5-s2-3.png){ loading=lazy }
</figure>

## Task 6: Deploy to Hub and Spoke Devices

In this step, you will review all the configuration changes done on
the Hub and Spoke devices and deploy the configuration to the devices.

1)  Click the Deploy button
    ![icon](assets/extracted/image53.png){ .inline-icon .off-glb }
    on the top right on FMC.

2)  This brings up the list of devices that are Ready for Deployment.
    Select the ![icon](assets/extracted/image54.png){ .inline-icon .off-glb }and
    click on **ignore warnings (if any)**
    ![icon](assets/extracted/image55.png){ .inline-icon .off-glb } button to trigger the
    deployment.

3)  View the progress of the deployment on the devices and **wait till
    the deployment is marked Completed** on the Deploy dialog

<figure markdown style="max-width:10.0cm;">
  ![screenshot](assets/extracted/image77.jpeg){ loading=lazy }
</figure>

## Task 7: Verify the traffic flow over the VPN tunnel from Spokes to Hub

### Step 1: Verify Site-to-Site VPN Tunnels

In this step, verify the VTI tunnels between the spokes and hub
devices.

Go to **Insights & Reports -\> VPN dashboards -\> SD-WAN Summary** and
Check that the tunnels are up as shown below. You may use **Refresh**
to reload the tunnels status if tunnel has not come up yet. Wait for
few seconds for tunnel status to be updated fully.

<figure markdown style="max-width:16.0cm;">
  ![screenshot](assets/screens/s1-t7-s1-1.png){ loading=lazy }
</figure>

Go to **Insights & Reports -\> VPN dashboards -\> Site-to-Site VPN**
and Check that the tunnels are up as shown below. You can also click
**View All Connections** within **VPN Topology** widget in **SD-WAN
Summary** dashboard to view this page:

<figure markdown style="max-width:16.0cm;">
  ![screenshot](assets/screens/s1-t7-s1-2.png){ loading=lazy }
</figure>

### Step 2: Verify Routes on Hub (NGFW-HUB)

When SD-WAN Topology is deployed to Hubs and Spokes, BGP commands are
auto generated and deployed to the devices. In this step, verify the
BGP and other configured and learnt routes at the Hub.

1.  Go to **Troubleshooting \> Tools \> Threat Defense CLI**.

2.  This launches the **CLI Troubleshoot** dialog. Fill it in as
    follows:

    1.  **Device**: **NGFW-HUB**
    2.  **Command**: `show`
    3.  **Parameter**: Type the argument `route`

3.  Click on **Execute** and review the routes

4.  Verify the connected routes (10.1.1.0/255.255.255.0 and
    10.1.2.0/255.255.255.0) from the Spokes that got re-distributed over
    BGP

<figure markdown style="max-width:16.0cm;">
  ![screenshot](assets/screens/s1-t7-s2-1.png){ loading=lazy }
</figure>

5.  Scroll through routes output and Verify internal routes learnt from
    OSPF (**O**) and EIGRP (**D**)

6.  Verify VPN routes (**V**), the Spokes Tunnel IP addresses

7.  Verify the protected networks at Spokes (192.168.1.0/255.255.255.0
    and 192.168.2.0/255.255.255.0) got distributed over BGP (**B**)

<figure markdown style="max-width:12.0cm;">
  ![screenshot](assets/screens/s1-t7-s2-2.png){ loading=lazy }
</figure>

### Step 3: Verify traffic between protected networks behind spoke (NGFW-B1) and hub (NGFW-HUB)

Network behind spoke (**NGFW-B1**) – 192.168.1.0/24 with a host
**192.168.1.133** (**B1H**)

Network behind hub (**NGFW-HUB**) – 192.168.101.0/24 with a host
**192.168.101.131** (**H1**)

Network behind hub (**NGFW-HUB**) – 192.168.102.0/24 with a host
**192.168.102.132** (**H2**)

1.  **Connect to B1H:** Open **Cisco Secure Firewall Quick Launch** from
    Taskbar and click on **B1H** which is present under **Linux VM
    Access.** This opens **B1H’s** SSH session.

<figure markdown style="max-width:16.0cm;">
  ![screenshot](assets/screens/s1-t7-s3-2.png){ loading=lazy }
</figure>

2.  **Verify Pings from Branch host to hosts behind Hub site.**

    1.  `ping 192.168.101.131 -c 5` which is the Host behind the
        Hub device NGFW-HUB and verify that you are getting the
        response.

    2.  `ping 192.168.102.132 -c 5` which is the Host behind the
        Hub device NGFW-HUB and verify that you are getting the
        response.

<figure markdown style="max-width:16.0cm;">
  ![screenshot](assets/screens/s1-t7-s3-3.png){ loading=lazy }
</figure>

3.  **Verify SSH Connection**

    1.  **SSH** to **192.168.101.131** using password **C1sco12345** and
        verify SSH access works. After successful connection, you may
        **exit**.

<figure markdown style="max-width:16.0cm;">
  ![screenshot](assets/screens/s1-t7-s3-4.png){ loading=lazy }
</figure>

2.  **SSH** to **192.168.102.132** using password **C1sco12345** and
    verify SSH access works. After successful connection, you may
    **exit**.

<figure markdown style="max-width:16.5cm;">
  ![screenshot](assets/extracted/image85.jpeg){ loading=lazy }
</figure>

### Step 4: Verify the traffic flow over the VPN tunnel from Spoke (NGFW-B1) to Spoke (NGFW-B2)

Network behind spoke (**NGFW-B1**) – 192.168.1.0/24 with a host
**192.168.1.133** (**B1H**)

Network behind spoke (**NGFW-B2**) – 192.168.2.0/24 with a host
**192.168.2.134** (**B2H**)

1.  **Connect to/Stay on B1H:** Open **Cisco Secure Firewall Quick
    Launch** and click on **B1H** which is present under **Linux VM
    Access.** This opens **B1H’s** SSH session.

<figure markdown style="max-width:16.0cm;">
  ![screenshot](assets/screens/s1-t7-s3-2.png){ loading=lazy }
</figure>

2.  **Verify Ping**

    1.  `ping 192.168.2.134 -c 5` which is the Host behind the
        spoke device NGFW-B2 and verify that you are getting the
        response.

<figure markdown style="max-width:16.0cm;">
  ![screenshot](assets/screens/s1-t7-s4-1.png){ loading=lazy }
</figure>

3.  **Verify SSH Connection**

    1.  **SSH** to **192.168.2.134** using password **C1sco12345** and
        verify SSH access works.

Note: For any prompt, “Are you sure you want to continue connecting
…?”, type “yes”.

2.  After successful connection, you may **exit**.

<figure markdown style="max-width:16.0cm;">
  ![screenshot](assets/screens/s1-t7-s4-2.png){ loading=lazy }
</figure>

4.  You may close all opened the **PuTTY** sessions

You have successfully configured and verified the SD-WAN topology with
one hub and multiple spokes!!!

