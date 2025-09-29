## RootsPlus – Smart Agriculture Platform

---

## Project Overview

**RootsPlus** is a proposed idea for an agricultural company that is interested in technology or wants to move towards digital transformation. The company has many agronomists who follow up on the farming activities of the farms connected to it. For each farm, they create activities, evaluations, and reports. The farm owner can view these updates regularly and stay informed.

---

## Main Roles

RootsPlus supports a multi-tiered user structure, with access and functionality tailored for specific roles:

- **Farmer:** Users can register farms, add and edit crops to their farm, and receive recommendations for their agricultural operations.
- **Agronomist:** Expert users who can supervise multiple linked farms, log field activities, and provide detailed evaluations and seasonal reports.
- **Admin:** Possesses full administrative access, allowing for the management of users, farms, and all system-wide settings.


## Key Features

The system's primary features include:

- Registration of new farms and dynamic user-farm linking.
- Dashboards, interfaces, and functionalities are role-based. Each role sees a personalized experience tailored to their specific responsibilities.
- Comprehensive logging and tracking of diverse agricultural activities.
- Expert evaluation of farms and provision of technical recommendations.
- Generation of seasonal performance reports for individual farms.
- Export capability for all generated reports in **CSV format**.
- Implementation of robust role-based access control and permissions.
- Dynamic alert and notification system for immediate user feedback.

---


## Screenshots

- **Large screen view:**

   ![LS View 1](https://i.ibb.co/8DKG6rmt/Screenshot-29-9-2025-3838-127-0-0-1.jpg)
  
  ![LS View 2](https://i.ibb.co/F1R2KmQ/Screenshot-29-9-2025-3914-127-0-0-1.jpg)

**Mobile view:**

 ![MS View 1](https://i.ibb.co/5WWZpsd2/Screenshot-29-9-2025-31020-127-0-0-1.jpg)


---


## Technologies Used

The following technologies and languages constitute the RootsPlus development stack:

- **Backend:** Django (Python Web Framework)
- **Frontend:** Bootstrap, AJAX, Chart.js
- **Database:** MySQL
- **Languages:** Python, HTML, CSS, JavaScript
- **API Integration:** OpenWeather API for incorporating weather-based insights and generating alerts.
- 
---

## Getting Started

To set up and run the RootsPlus project locally, follow these steps:

```bash
# Clone the repository
git clone https://github.com/MohDDH/rootsPlus.git

# Navigate to the project folder
cd rootsPlus

# Create and activate a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Apply database migrations
python manage.py migrate

# Run the local development server
python manage.py runserver
```

---

## Future Outlook

The development roadmap for RootsPlus includes several key initiatives aimed at expanding platform functionality, reach, and user engagement:

- **Knowledge Sharing:** Launching a technical blog to foster communication between agronomists and farmers, share expert insights, and promote sustainable best practices.
- **Enhanced Reporting:** Enabling interactive image embedding within reports and evaluations to enhance clarity, documentation, and the overall quality of assessments.
- **Advanced Analytics:** Integration of advanced statistics and predictive analytics tools to support smarter, data-driven decision-making and precise farm performance tracking.
- **Localization:** Introducing comprehensive **Arabic language support** across the entire platform to ensure accessibility and inclusivity for Arabic-speaking agricultural communities.

---

## Acknowledgements

Special thanks to **AXSOS Academy** for giving us this valuable opportunity, and heartfelt appreciation to Eng. Mohammad Essa, Eng. Fatima Harahsheh, and Eng. Shahd Fakhouri for their guidance, support, and dedicated efforts.
