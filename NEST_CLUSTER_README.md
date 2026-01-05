# NEST Cluster Website Prototype

## What I Built
A responsive single-page website for NEST Cluster, IIT Guwahati featuring a header with navigation menu, an About section describing the cluster's mission, an Activities section displaying three event cards (each with title, date, and description), and a footer with contact information. The design is fully responsive, working seamlessly on both desktop and mobile devices.

## Tools Used
- **HTML5** for structure and semantic markup
- **CSS3** with Flexbox and Grid for responsive layout
- **JavaScript** (minimal) for mobile menu toggle and smooth scrolling

## Data Management Approach
The data management sheet (`nest_cluster_data.csv`) contains event information with columns: Event Name, Date, Category, and Status. To ensure data remains updated and consistent on the website, I would implement an automated sync mechanism: regularly export the Google Sheet as CSV and use a simple script or CMS to import it into the website's data source. Alternatively, use Google Sheets API to fetch data dynamically, ensuring real-time updates without manual file replacements. This approach maintains a single source of truth (the spreadsheet) while keeping the website current.

## Improvement I Would Add
If given more time, I would integrate a dynamic content management system that pulls event data directly from the Google Sheet using the Google Sheets API, automatically updating the Activities section without manual intervention and allowing non-technical team members to manage content easily.


