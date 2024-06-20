# IriusRisk PowerBI Dashboard

This project provides an API-driven approach using PowerBI.
This can be considered version 1, which requires some manual action to select the project.

## Overview

The user has access to a series of dashboards outlining countermeasure and threat data for a project.
Additionally, this project provides the source data to build custom dashboards and visualizations as you require (threat & countermeasure data).

## Table of Contents

- [Prerequisites](#prerequisites)
- [Configuration](#configuration)
- [Usage](#usage)
- [Examples](#examples)

## Prerequisites

- Enable the API in IriusRisk settings.
- Obtain a valid IriusRisk API token.
- Ensure the API token is associated with an account with the necessary permissions.
- Installed the appropriate pre-requisites to run python in your PowerBI environment. Please see here: https://learn.microsoft.com/en-us/power-bi/connect-data/desktop-python-scripts


## Configuration

When you open the project, the data will be missing. This will require a series of parameters to be updated and a manual refresh performed.
Follow the following steps:
1. Open the PowerBI Project
2. Navigate to Home > Queries > Transform Data - Drop down menu > Edit Parameters
3. Insert a valid value for the following parameters:
   - apitoken
   - tenant
4. Click 'OK'
5. Navigate to Home > Queries > Refresh
6. You may be asked to explicitly give permission to run the associated python script which PowerBI utilises. This is expected. If you agree to using these dashboards, then feel free to grant permission.

Parameters

![Parameters](https://github.com/iriusrisk/IriusRisk-Central/blob/main/Integrations/PowerBI_Dashboard_v1/assets/Parameters.png)

Congratulations, you have successfully configured your PowerBI project.

## Usage
Once configured, you can access the two dashboards - threats & countermeasures.
We have access on the right hand side of our screen to build more visualizations by applying data from the data pane.
We dynamically pull in all custom fields. This allows great reporting functionality. Please be aware if we wish to update any filters, that the bookmarks must be updated to reflect this (View > Bookmarks. View > Selection)

## Examples

Countermeasures Dashboard
![Countermeasures Dashboard](https://github.com/iriusrisk/IriusRisk-Central/blob/main/Integrations/PowerBI_Dashboard_v1/assets/Countermeasure_Dashboard.png)

Countermeasures Report Dashboard
![Countermeasures Dashboard](https://github.com/iriusrisk/IriusRisk-Central/blob/main/Integrations/PowerBI_Dashboard_v1/assets/Countermeasures_report.png)

Threats Dashboard
![Threats Dashboard](https://github.com/iriusrisk/IriusRisk-Central/blob/main/Integrations/PowerBI_Dashboard_v1/assets/Threat_Dashboard.png)

Threats Dashboard
![Threats Dashboard](https://github.com/iriusrisk/IriusRisk-Central/blob/main/Integrations/PowerBI_Dashboard_v1/assets/Threats_report.png)

We can make use of filters for our dashboards by ctrl clicking the button atop the filters pane. These update the visualizations in real time.
![Filters](https://github.com/iriusrisk/IriusRisk-Central/blob/main/Integrations/PowerBI_Dashboard_v1/assets/Slicer.png)


