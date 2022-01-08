# QR Tracker

## What is this?

Due to the increased useage of QR codes due to the ongoing pandemic, I was curious about how many people were scanning random QR codes.
Further, I saw this as an opportunity to create prank QR codes.

The process flow is described below:

![a flowchart image that describes what happens when the URL encoded on the QR code is opened](flow.png "flowchart")

The QR code contains only a link to a the application.

# Admin interface
Log in after following the instructions in [Deployment](#Deployment)

## Creating a QR campaign

A campaign is just a way to label where a QR code has been distributed.
For example, while conducting an informal experiment, two locations have been identified, such as a bus stop and a bulletin board.
Two separate campaigns would allow identification of which location the user was when scanning the code.


![a screenshot showing the creation of a qr campaign](screenshots/create_qr_camp.png "The create qr page")

Once created, the data collected can be viewed.
![a screenshot showing the data colleced from a qr campaign](screenshots/camp_in_progress.png "Individual campaign page")

All in progress campaigns are shown
![a screenshot showing all qr campaigns](screenshots/list_campaigns.png "All qr campaigns")

Finally, all visitors can be listed. The ability to export these is a planned feature, not yet implemented.


All visitors
![a screenshot showing all visitors](screenshots/all_visitors.png "All visitors")

Anyone who has followed the link on the QR code is shown a message that explains what data is collected.


# Deployment

To deploy, simply clone the repository and create the following files:

* .env
  ```
  FLASK_SECRET_KEY=<some really secure string>
  URL_BASE=localhost:5002
  ```
* app/secrets.py
  ```
  users = {'admin': {'password': '<some really secure password>'}}
  ```
Lastly, run
`docker-compose up --build`

It is suggested that a reverse proxy be used to route a subdomain to the app and handle https certs.

# FAQ's

* Is this malicious?
  * No, but it could be used for phishing if instead of redirecting to rickroll or the stats page, it directed the victim to log in to "facebook"
* Does this collect Personally Identifying Information (PII)?
  * No, the only information collected is the user's IP address and user agent. This information is sent to any website you view.
* How does it work
