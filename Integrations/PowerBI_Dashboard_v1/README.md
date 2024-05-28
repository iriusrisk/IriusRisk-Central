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

## Configuration

When you open the project, the data will be missing. This will require a series of parameters to be updated and a manual refresh performed.
Follow the following steps:
1. Open the PowerBI Project
2. Navigate to Home > Queries > Transform Data - Drop down menu > Edit Parameters
3. Insert a valid value for the following parameters:
   - ProjectId
   - apitoken
   - tenant
4. Click 'OK'
5. Navigate to Home > Queries > Refresh

Parameters
![Parametersd](https://github.com/iriusrisk/IriusRisk-Central/blob/main/Integrations/PowerBI_Dashboard_v1/assets/Parameters.png)

Congratulations, you have successfully configured your PowerBI project.

## Usage
Once configured, you can access the two dashboards - threats & countermeasures.
We have access on the right hand side of our screen to build more visualizations by applying data from the data pane.

## Examples

Countermeasures Dashboard
![Countermeasures Dashboard](https://github.com/iriusrisk/IriusRisk-Central/blob/main/Integrations/PowerBI_Dashboard_v1/assets/CM_Dashboard.png)


Threats Dashboard
![Threats Dashboard](https://github.com/iriusrisk/IriusRisk-Central/blob/main/Integrations/PowerBI_Dashboard_v1/assets/Threat_Dashboard.png)

