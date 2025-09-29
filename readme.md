## RootsPlus – Smart Agriculture Platform

---

## Project Overview

**RootsPlus** is a proposed concept for an agricultural technology company dedicated to transforming farm management. The platform is designed to bridge the gap between farmers and agronomists by providing **smart tools, actionable insights,** and a supportive ecosystem to promote agricultural success. Its core mission is to make farming smarter, more sustainable, and more profitable by connecting expert agricultural knowledge with real-world farming needs.

---

## Main Roles

RootsPlus supports a multi-tiered user structure, with access and functionality tailored for specific roles:

- **Farmer:** Users can register farms, manage crop cycles, and receive targeted recommendations for their agricultural operations.
- **Agronomist:** Expert users who can supervise multiple linked farms, log field activities, and provide detailed evaluations and seasonal guidance.
- **Admin:** Possesses full administrative access, allowing for the management of users, farms, and all system-wide settings.

---

## Screenshots

- **Large screen view:**

  ![LS View 1](https://i.ibb.co/8DKG6rmt/Screenshot-29-9-2025-3838-127-0-0-1.jpg)

  ![LS View 2](https://i.ibb.co/F1R2KmQ/Screenshot-29-9-2025-3914-127-0-0-1.jpg)

- **Mobile view:** ![MS View 1](https://i.ibb.co/5WWZpsd2/Screenshot-29-9-2025-31020-127-0-0-1.jpg)

  ![MS View 2](https://i.ibb.co/wFHqcRFC/Screenshot-29-9-2025-3957-127-0-0-1.jpg)

---

## Core Modules

The platform is built around several interconnected modules designed to cover the full spectrum of farm management:

- **Farm Management:** Functionality for adding, modifying, and associating farms with specific users.
- **Crop Tracking:** Allows for the recording of detailed crop information, including planting dates, cultivated areas, and expected yields.
- **Activity Logging:** A mechanism to track and log various agricultural activities, such as irrigation scheduling, fertilization applications, pest control measures, and harvesting operations.
- **Evaluations and Reports:** Enables expert agronomists to submit formal farm evaluations and issue seasonal recommendations.
- **Dashboard:** Provides a summarized view of key performance indicators, data visualizations (charts), and statistics tailored to the respective user role.
- **Authentication:** Manages role-based login, security, and user session management.

---

## Technical Stack

The following technologies and languages constitute the RootsPlus development stack:

- **Backend:** Django (Python Web Framework)
- **Frontend:** Bootstrap, AJAX, Chart.js
- **Database:** MySQL
- **Languages:** Python, HTML, CSS, JavaScript
- **API Integration:** OpenWeather API for incorporating weather-based insights and generating alerts.

---

## Key Features

The system's primary features include:

- Registration of new farms and dynamic user-farm linking.
- Comprehensive logging and tracking of diverse agricultural activities.
- Expert evaluation of farms and provision of technical recommendations.
- Generation of seasonal performance reports for individual farms.
- Export capability for all generated reports in **CSV format**.
- Implementation of robust role-based access control and permissions.
- Dynamic alert and notification system for immediate user feedback.

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
