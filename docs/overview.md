# Overview

**Cisco Secure Firewall SD-WAN — Hands-on Lab (LTRSEC-2241)**

Welcome to the Cisco Secure Firewall SD-WAN hands-on lab. Across the six
scenarios in this guide you will design, deploy and validate an
SD-WAN topology between a Hub and multiple Branches using the SD-WAN
Wizard in the Firewall Management Center (FMC), then extend the design
to handle network growth, dual-ISP branches, overlapping addressing and
Remote Access VPN with geolocation controls.

!!! info "Speakers"

    - **Prema Chand Alugu** — Engineering Technical Leader
    - **Raghu Ram** — Principal Software Engineer
    - **Jesus Medina** — Escalation Engineer

## Learning Objectives

Upon completion of this lab you will be able to:

1. **Bring up a hub-and-spoke SD-WAN deployment** — Configure end-to-end
   secure connectivity between a Branch and Hub Secure Firewall using the
   **SD-WAN Topology** wizard. You will:
    - Simplify **single hub with multiple spokes** configuration using SD-WAN Topology
    - Auto-generate **static Virtual Tunnel Interfaces (VTI)** on spoke devices
    - Add multiple spokes using the **Bulk Spoke** feature
    - **Automate BGP** neighbour configuration and **redistribute IGP / Static routes** via BGP
    - Automatically add the generated VTIs to the Security Zone for Access Control Policy

2. **Expand the Hub network** — Add a new protected network behind the Hub and
   redistribute it through BGP.

3. **Expand branches** — Add new branches to an existing SD-WAN deployment using
   the **Add Spoke** option and redistribute their protected networks through BGP.

4. **Add a secondary ISP link to a branch** — Configure dual-ISP spokes with
   SD-WAN Topology and apply Equal-Cost Multi-Path (**ECMP**) zones for load
   balancing.

5. **Acquire a branch with overlapping addressing (optional)** — Resolve overlapping
   networks using **Pre-encryption NAT** and redistribute the NAT network via BGP.

6. **Control Remote Access VPN by geolocation (optional)** — Configure Service
   Access policies to define allowed regions and verify access is denied for
   restricted geolocations.

## Disclaimer

Although the lab design and configuration examples can be used as a reference,
for design-related questions please contact your Cisco representative or a
Cisco partner.

## Accessing Devices

This section walks you through the devices used in this lab and how to access
them. Please reach out to the lab proctor if you have any issue accessing the
devices.

All NGFW devices run **Cisco Secure Firewall release 10.0**. The lab uses the
following devices:

- **FMC** — Firewall Management Center
- **NGFW-HUB** — Hub device
- **NGFW-B1**, **NGFW-B2**, **NGFW-B3**, **NGFW-B4** — Branch devices
- **B1H**, **B2H** — workstations behind NGFW-B1 / NGFW-B2
- **B3H**, **B4H** — workstations behind NGFW-B3 / NGFW-B4
- **H1**, **H2**, **H3** — workstations behind NGFW-HUB
- **Wkst5** — Secure Client user

<figure markdown style="max-width:16.1cm;">
  ![Lab topology](assets/extracted/image3.png){ loading=lazy }
</figure>

### Lab credentials

| **Device**    | **URL / IP**              | **Username**  | **Password** |
| ------------- | ------------------------- | ------------- | ------------ |
| Jumpbox (RDP) | 198.18.133.50             | Administrator | C1sco12345   |
| FMC (UI)      | <https://198.18.133.201/> | admin         | dCloud123!   |
| B1H           | 198.18.133.133            | root          | C1sco12345   |
| B2H           | 198.18.133.134            | admin         | C1sco12345   |
| B3H           | 198.18.133.155            | admin         | C1sco12345   |
| B4H           | 198.18.133.166            | admin         | C1sco12345   |
| Wkst5 (RDP)   | 198.18.133.170            | admin         | C1sco12345   |

!!! warning "Credential handling"

    These credentials are valid only for this isolated lab environment. Never
    reuse them in a production deployment.

### Jumpbox

The Jumpbox (RDP `198.18.133.50`) can be used to access all the lab devices
from a single user interface. A **Quick Launch** icon is placed on the desktop.

<figure markdown style="max-width:13.3cm;">
  ![Quick Launch icon on the Jumpbox desktop](assets/extracted/image4.jpeg){ loading=lazy }
</figure>

Clicking the **Quick Launch** icon launches the Cisco Secure Firewall Quick
Launch application from which all the devices can be opened and accessed.

<figure markdown style="max-width:16.1cm;">
  ![Cisco Secure Firewall Quick Launch](assets/extracted/image5.png){ loading=lazy }
</figure>

## Pre-configured Objects and Access Control Rules

There are pre-configured Objects and Access Control rules on the FMC and the
Hub device to ensure the connected networks can communicate over the SD-WAN
tunnels.

An object **Branch-Protected-Network** is defined with the override option to
hold the protected networks. Scroll down on the object to see all the values
configured behind each NGFW.

<figure markdown style="max-width:8.9cm;">
  ![Branch-Protected-Network object](assets/screens/pre-configured-branch-protected-network.png){ loading=lazy }
</figure>

This object is in turn used in the pre-configured route map
**Advertise-Branch-Protected-Networks**. The Hub uses an equivalent route map
**Advertise-Hub-Protected-Networks**. Both can be found under **Objects → Route
Map**. The route maps are used when configuring propagation of protected
network routes to SD-WAN peers.

<figure markdown style="max-width:15.7cm;">
  ![Pre-configured route maps](assets/extracted/image7.jpeg){ loading=lazy }
</figure>

The Access Control rules pre-configured at the **Hub** are:

- **Rule 1** — Permit outbound traffic from networks behind Hub to any Spokes through tunnel
- **Rule 2** — Permit inbound traffic from any Spokes to networks behind Hub through tunnel
- **Rule 3** — Permit any traffic between Spokes
- **Rule 4** — Remote access users' traffic accessing networks behind Hub

<figure markdown style="max-width:16.0cm;">
  ![Hub Access Control rules](assets/screens/pre-configured-hub-ac.png){ loading=lazy }
</figure>

The Access Control rules pre-configured at the **Spokes** are:

- **Rule 1** — Permit outbound traffic from networks behind Spokes to any through tunnel
- **Rule 2** — Permit inbound traffic from any to networks behind Spokes through tunnel
- **Rule 3** — Permit any traffic between Spokes

<figure markdown style="max-width:16.0cm;">
  ![Spoke Access Control rules](assets/screens/pre-configured-spokes-ac.png){ loading=lazy }
</figure>

## You're All Set — Let's Begin

The lab environment is ready and the supporting objects are in place. From
here, head into the scenarios &mdash; each one builds on the previous, so
working through them in order will give you the best picture of how the
SD-WAN Wizard fits together end-to-end. Scenarios 5 and 6 are optional
and can be tackled if time permits.

If anything is unclear, a screenshot doesn't match what you see, or a step
behaves differently in your pod, please flag it. Your feedback &mdash; even
the small details &mdash; goes directly back into the next revision of this
guide.

Happy labbing!
