# lboc-dashboard

A page to display Lewisham Borough of Culture engagement metrics on the We Are Lewisham site. The application is hosted on Github, and the data is provided via a Google Spreadsheet. 

Updates are scheduled as Github Actions, and the resulting documents are published to the Git branch `gh-pages`.

## Setup

Create a new private Github Actions repository secret called `SHEET_ID` and set it to the ID of the document ID of your Google Sheet.

Enable Github Actions on the project, and make sure the initial run completes without errors.

Enable Github Pages on the project, and point it at the `gh-pages` branch.

Done!
