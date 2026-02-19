<p align="center">
  <h1 align="center">🌍 Events Planner</h1>
  <p align="center">
    A Tourism Management System for discovering, booking, and reviewing events.
    <br />
    Built as a university project for <strong>Software Engineering 1 & 2</strong>.
  </p>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.x-blue?logo=python&logoColor=white" />
  <img src="https://img.shields.io/badge/Flask-Web_Framework-black?logo=flask" />
  <img src="https://img.shields.io/badge/SQLite-Database-07405E?logo=sqlite&logoColor=white" />
  <img src="https://img.shields.io/badge/CI-GitHub_Actions-2088FF?logo=githubactions&logoColor=white" />
</p>

---

## ✨ Features

| Feature | Description |
|---|---|
| 🔐 **Authentication** | User registration & login with IP-based brute-force protection |
| 📅 **Event Browsing** | Browse, search, and filter events by category |
| 🎟️ **Event Booking** | Book events and manage your reservations |
| ⭐ **Reviews & Ratings** | Leave reviews and star ratings on events |
| 🏢 **Organizer Portal** | Create, edit, and delete events with image uploads |
| 🛡️ **Admin Dashboard** | Full admin control over users and events |

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| **Front-End** | HTML & CSS (Jinja2 templates) |
| **Back-End** | Flask (Python) |
| **Database** | SQLite via SQLAlchemy ORM |
| **Deployment** | Gunicorn |
| **CI/CD** | GitHub Actions (pytest + flake8) |

---

## 🚀 Getting Started

### Prerequisites

- Python 3.x
- pip

### Installation

```bash
# Clone the repository
git clone https://github.com/your-username/SWE-Project.git
cd SWE-Project

# Install dependencies
pip install -r requirements.txt
```

### Running Locally

```bash
python auth/auth.py
```

The app will be available at `http://localhost:5000`.

---

## 🧪 Testing

The project includes both functional and non-functional tests, automated via GitHub Actions on every push and PR to `main`.

```bash
# Run functional tests
pytest --html=report.html --self-contained-html

# Run static analysis (linting)
flake8 .
```

---

## 📁 Project Structure

```
SWE-Project/
├── auth/
│   ├── auth.py            # Main Flask application (routes, models, logic)
│   ├── templates/          # Jinja2 HTML templates
│   │   ├── login.html
│   │   ├── register.html
│   │   ├── welcome.html        # User homepage / event discovery
│   │   ├── events.html         # User's booked events
│   │   ├── reviews.html        # Event reviews page
│   │   ├── org_portal.html     # Organizer event management
│   │   ├── admin_dashboard.html
│   │   └── admin_show_events.html
│   └── uploads/            # User-uploaded event images
├── tests/
│   └── test_auth.py        # Pytest test suite
├── .github/workflows/
│   └── tests.yml           # CI pipeline config
├── requirements.txt
├── Procfile                 # Gunicorn deployment config
└── README.md
```

---

## 👥 Contributors

| Name | GitHub |
|---|---|
| Abdulelah Khalaf Alanazi | <a href="https://github.com/AkhmDev"><img src="https://github.com/AkhmDev.png?size=30" width="30px;" alt=""/> @AkhmDev</a> |
| Mohammed Salah Alshebil | <a href="https://github.com/shbl1"><img src="https://github.com/shbl1.png?size=30" width="30px;" alt=""/> @shbl1</a> |
| Abdulaziz Abdulrahman Aldaws | <a href="https://github.com/abosaudalmansour"><img src="https://github.com/abosaudalmansour.png?size=30" width="30px;" alt=""/> @abosaudalmansour</a> |
| Abdulkreem Abdullah Almqbel | <a href="https://github.com/Almqbel"><img src="https://github.com/Almqbel.png?size=30" width="30px;" alt=""/> @Almqbel</a> |
| Khalid Hesham Aljubaily | <a href="https://github.com/KJ66KK"><img src="https://github.com/KJ66KK.png?size=30" width="30px;" alt=""/> @KJ66KK</a> |
| Abdullah Ali Almanee | <a href="https://github.com/AbdullahAM1"><img src="https://github.com/AbdullahAM1.png?size=30" width="30px;" alt=""/> @AbdullahAM1</a> |
