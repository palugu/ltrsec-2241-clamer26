# Scenario 6: Geolocation Service Access Policies for Remote Users (Optional)


Secure Firewall release 7.7 introduced rules to manage VPN access of
remote users based on Geolocation. By setting rules to allow or block
access from specific countries or regions, you can meet compliance
requirements and enhance security. Remote sessions that don't meet
these location-based criteria are blocked before authentication.

## Network Diagram

<figure markdown style="max-width:16.0cm;">
  ![screenshot](assets/screens/6.png){ loading=lazy }
</figure>

## 6.1 Configuring Service Access Rules on Hub (NGFW-HUB)

In this activity you will learn to configure service access rules
which define the controls for remote access sessions.  
  
Since the lab pod and the test workstation are set up in the US
region, this lab section walks you through the steps to restrict
access from the US. You can use the same steps in your production
deployment to block access from regions and countries of your own
choice.

### 6.1.1 Create Service Access Object

1.  Click on the **Objects** menu &mdash; it opens at **Network**
    objects by default.

2.  In the left sidebar, click **Access List &rarr; Service Access**.

3.  Click **Add Service Access Object** at the top right.

    <figure markdown style="max-width:16.0cm;">
      ![screenshot](assets/screens/6.1.1.1.png){ loading=lazy }
    </figure>

4.  The **Add Service Access Object** dialog opens. Enter the
    **Name** as `Corp-RA-Locations`, then click **Add Rule**.

    <figure markdown style="max-width:16.0cm;">
      ![screenshot](assets/screens/6.1.1.2.png){ loading=lazy }
    </figure>

5.  The **Add Service Access Rule** dialog opens. Fill it in as
    follows:

    1.  **Action**: Ensure it is set to **Deny**.
    2.  **Available Countries**: Select **United States** from the list.
    3.  **Selected Geolocation**: Use the ==right-move arrow==
        ![icon](assets/extracted/image217.png){ .inline-icon .off-glb }
        to move **United States** into **Selected Geolocation**.
    4.  Click **Add** to create the rule.

    <figure markdown style="max-width:16.0cm;">
      ![screenshot](assets/screens/6.1.1.3.png){ loading=lazy }
    </figure>

6.  Choose the Default Action: **Allow All Countries**. This action
    applies to connections that do not match any of the configured
    service access rules.

    <figure markdown style="max-width:16.0cm;">
      ![screenshot](assets/screens/6.1.1.4.png){ loading=lazy }
    </figure>

7.  Click **Save** to save the Service Access Rule.

    <figure markdown style="max-width:16.0cm;">
      ![screenshot](assets/screens/6.1.1.5.png){ loading=lazy }
    </figure>

### 6.1.2 Apply the Service Object Configuration in RAVPN

1.  Navigate to Remote Access VPN configuration in **Secure Connections
    \> Remote Access VPN**

2.  A remote access policy named **Remote-Access-via-Hub** is
    pre-configured

3.  Click the **pencil** icon in the middle to edit it

    <figure markdown style="max-width:16.0cm;">
      ![screenshot](assets/screens/6.1.2.1.png){ loading=lazy }
    </figure>

4.  Click on the **Access Interfaces** tab

5.  You may **scroll down** and in the **Service Access Control** section,
    select the service access object that was just created
    **Corp-RA-Locations**

    <figure markdown style="max-width:16.0cm;">
      ![screenshot](assets/screens/6.1.2.2.1.png){ loading=lazy }
    </figure>

    <figure markdown style="max-width:16.0cm;">
      ![screenshot](assets/screens/6.1.2.2.2.png){ loading=lazy }
    </figure>

6.  The service access object now displays the rules summary and default
    action. Ensure this is correct and click **Save** on top right to
    save the configuration.

    !!! note "Save may already be auto-saved"
        You may see **Save** greyed out &mdash; the configuration can
        get auto-saved as soon as the **Service Access** object is
        selected. Click **Save** anyway just to be sure the
        configuration is persisted.

    <figure markdown style="max-width:16.0cm;">
      ![screenshot](assets/screens/6.1.2.3.png){ loading=lazy }
    </figure>

## 6.2 Deploy to Hub Device

In this step, you will review all the configuration changes done on
the Hub and Spoke devices and deploy the configuration to the devices.

1)  Click the Deploy button
    ![icon](assets/extracted/image53.png){ .inline-icon .off-glb }
    on the top right on FMC.

2)  This brings up the list of devices that are Ready for Deployment.
    Select the **Deploy All**
    ![icon](assets/extracted/image54.png){ .inline-icon .off-glb } checkbox and
    click on **ignore warnings (if any)**
    ![icon](assets/extracted/image55.png){ .inline-icon .off-glb } button to trigger the
    deployment.

3)  View the progress of the deployment on the devices and **wait till
    the deployment is marked Completed** on the Deploy dialog

<figure markdown style="max-width:10.0cm;">
  ![screenshot](assets/screens/6.2.png){ loading=lazy }
</figure>

## 6.3 Verify the Remote Access from Secure Client

### 6.3.1 Verify remote access client session

1.  **Connect to Workstation:** Open **Cisco Secure Firewall Quick
    Launch** from Desktop and click **Wkst5** which is present under
    **Remote Access.** This opens a Remote Desktop Connection (RDP)
    window of **Wkst5**.  
      
    Log in using credentials `admin / C1sco12345`.

    <figure markdown style="max-width:16.0cm;">
      ![screenshot](assets/screens/6.3.1.1.png){ loading=lazy }
    </figure>

2.  Click the Windows **Start** button and open the **Cisco Secure
    Client** application by clicking the pinned icon.

    <figure markdown style="max-width:16.0cm;">
      ![screenshot](assets/screens/6.3.1.2.png){ loading=lazy }
    </figure>

3.  Click on **Connect** with **Hub (SSL) IPv4** Profile. Wait for a
    few seconds and choose **Connect Anyway** on the Security Warning
    dialog. The connection attempt should fail.

    <figure markdown style="max-width:16.0cm;">
      ![screenshot](assets/screens/6.3.1.3.png){ loading=lazy }
    </figure>

4.  Verify with Troubleshooting Logs. To validate blocked connections,
    navigate on FMC to **Troubleshooting \> Advanced \>
    Troubleshooting Logs**. Click on **View All**.

    <figure markdown style="max-width:16.0cm;">
      ![screenshot](assets/screens/6.3.1.4.png){ loading=lazy }
    </figure>

Observe the log entry:

**Denied SSL remote access session for reqType SECURE CLIENT faddr
20.1.1.170 by a geo-based rule (geo="United States", id=840)**

!!! note

    Please wait for a few minutes after testing RAVPN in step 3 above
    to ensure the deny events are populated on the FMC.

!!! success "Scenario 6 complete &mdash; Lab complete!"
    Congratulations! You have successfully **completed all the
    scenarios of this Lab.** Thank you for participating &mdash; we
    hope you enjoyed it!

<figure markdown style="max-width:16.0cm;">
  ![screenshot](assets/extracted/image230.png){ loading=lazy }
</figure>

