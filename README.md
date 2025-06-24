# ✈️ Air Traffic Automation for Turkish Airspace

A real-time flight tracking and analytics system for Turkish airspace using OpenSky Network data, PostgreSQL, and Power BI.

---

## 🚀 Features
- Live flight data collection from **OpenSky API**
- Data processing and transformation with **Python**
- Scheduled automation via **GitHub Actions**
- **PostgreSQL** storage for analytics
- **Power BI** dashboard integration

---

## 📂 Project Structure
- `script.py`: Main Python script for data extraction and transformation
- `.github/workflows`: GitHub Actions configuration for automation
- `README.md`: Project overview

---

## 🛠️ Tech Stack
- **Python** (pandas, requests, psycopg2)
- **GitHub Actions** (cron scheduling)
- **PostgreSQL (Neon.tech)**
- **Power BI** (real-time dashboard)

---

## 📈 Sample Dashboard (Power BI)
![Dashboard Screenshot](https://github.com/ikara35/air_trafic_automation/blob/main/dashboard_screenshot.png)

---

## 📅 Scheduled Automation (GitHub Actions)
This project includes a fully automated data pipeline using GitHub Actions. The workflow runs the script.py file every 15 minutes, fetches live flight data from OpenSky Network, processes it, and updates the PostgreSQL database hosted on Neon.tech.

**🔄 Workflow Configuration
Location: .github/workflows/script.yml**

yaml
on:
  schedule:
    - cron: '*/15 * * * *'  ** # Runs every 15 minutes*
  workflow_dispatch:        ** # Also allows manual trigger*

**🔧 What It Does**
Triggers every 15 minutes using GitHub's cron scheduler.

Sets up a Python 3.10 environment.

Installs required dependencies: **pandas, requests, sqlalchemy, psycopg2-binary.**

Runs the script.py to:

Authenticate with OpenSky API.

Fetch live aircraft data over Turkish airspace.

Detect approaching aircraft near Istanbul, Izmir, and Antalya.

Write data into Neon.tech PostgreSQL.

**✅ The automation makes the system fully serverless and maintenance-free.**

---

## ⚙️ Setup Instructions
1. Clone the repo
2. Configure `.env` with API keys and DB credentials
3. Run `script.py` or trigger workflow

---

## 👤 Author
📎 [LinkedIn: Ibrahim KARAMAN](https://www.linkedin.com/in/ibrahim-karaman-data-analyst/)

📧 ibrahimkaraman711@gmail.com


