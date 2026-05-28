# Task 1: Configuring SD-WAN Topology between Branches (Spokes) and Headquarters (Hub) using DVTI on Hub

## Step 1: Create SD-WAN Topology
To configure a new SD-WAN Topology, go to **Secure Connections > Site-to-Site VPN & SD-WAN**. Click **+ Add**.

1.  **Topology Name**: Name the VPN topology as `Corp-SD-WAN-1`.
2.  **VPN Type**: Select `SD-WAN Topology`.
3.  **VPN Topology**: Select `Hub and Spoke`.
4.  Click **Create**.

## Step 2: SD-WAN Topology – Hub Configuration
1.  Click **Add Hub** in the Hubs section.
2.  **Device**: Select `FTD NGFW-HUB`.
3.  **Dynamic Virtual Tunnel Interface (DVTI)**: Click the **+** icon to create a new interface.
    *   **Name**: `outside_dynamic_vti_1`
    *   **Security Zone**: `Tunnel_Zone`
    *   **Tunnel Source**: `outside` (IP: `20.1.101.101`)
    *   **IP Address**: Click **+** to create a Loopback interface. Name it `Hub_Tunnel_IP_1`, ID `1`, IP `169.254.10.1/32`.
    *   Set **Borrow IP** to `Loopback1`.
4.  **Spoke Tunnel IP Address Pool**: Click **+** to add a new pool.
    *   **Name**: `NGFW_Hub_IPv4_Pool_1`
    *   **IPv4 Address Range**: `169.254.10.3-169.254.10.100`
    *   **Mask**: `255.255.255.0`
5.  Click **Add** to save the Hub. Click **Next**.

## Step 3: SD-WAN Topology – Bulk Spoke Configuration
1.  Click **Add Spokes (Bulk Addition)**.
2.  **Devices**: Select `NGFW-B1` and `NGFW-B2`.
3.  **Interface Name Pattern**: Ensure it is set to `outside`.
4.  Review and click **Add**, then **Next**.

## Step 4: SD-WAN Topology - Authentication Settings
1.  **Authentication Type**: Select `Pre-shared Manual Key`.
2.  **Key**: `cisco123`.
3.  Click **Next**.

## Step 5: SD-WAN Topology – Add Tunnel Interfaces to Security Zone Automatically
1.  Select `Tunnel_Zone` in the **Spoke Tunnel Interface Security Zone** drop-down.

## Step 6: SD-WAN Topology – Configure BGP routing
1.  **Enable BGP on the VPN Overlay Topology**: Checked.
2.  **Autonomous System Number**: `64512`.
3.  **Community Tag**: `9901`.
4.  **Redistribute Connected Interfaces**: Enabled (`Default Inside`).
5.  **Enable Multiple Paths for BGP**: Enabled.
6.  Click **Next**.

## Step 7: SD-WAN Topology - Finish
1.  Click **Finish** to save the topology.
