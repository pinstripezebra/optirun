## Running Condition Forecasting with Optirun
Optirun uses open source weather forecast and user preferences to identify the optimal time to go for a run. A LLM is then incorporated to provide additional context to the running forecast in plain english.

### Components

* Weather Forecast from OpenMeteo: https://github.com/m0rp43us/openmeteopy
* User preferences stored in PostgreSQL Database
* Front end Dash appplication Deployed on Render: https://render.com/
* Weather interpreter using Anthropics Claude


### Login and Registration

Login using Flask and our PostgreSQL database to authenticate user, load preferences, and generate forecasts for their location and preferences.

![alt text](image.png)

Registration allowing each user to specify their unique preferences for running conditions.

![alt text](image-1.png)