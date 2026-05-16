# 🥋 MMA Fighting Platform

![Django](https://img.shields.io/badge/Django-5.0-green) ![Python](https://img.shields.io/badge/Python-3.11-blue) ![Bootstrap](https://img.shields.io/badge/Bootstrap-5-purple) ![Leaflet](https://img.shields.io/badge/Leaflet-OpenStreetMap-brightgreen)

## 📌 Overview

**MMA Fighting Platform** is an all‑in‑one web application for MMA enthusiasts. It centralises news, event calendars, an AI training assistant, a stopwatch, a fighter search engine, and gym geolocation – all in one responsive platform.

Built with **Django**, **Bootstrap**, **Leaflet**, and multiple external APIs (GNews, Groq, OpenStreetMap), it offers a seamless experience for amateurs, coaches, and administrators.

---

## ✨ Features

| Module | Description |
|--------|-------------|
| 📰 **MMA News** | Fetch latest MMA articles via GNews API. Admin can hide/show articles. |
| 🤖 **AI Assistant** | Chat with a Llama‑powered assistant (Groq API) for training, nutrition, and fight preparation. |
| 🗓️ **Events Calendar** | View upcoming events, countdown to the next big fight (e.g. UFC 309). |
| ⏱️ **Training Stopwatch** | Simple start/stop/reset timer – perfect for round tracking. |
| 🗺️ **Nearby Gyms** | Geolocation (Leaflet + Overpass API) – find MMA/fitness gyms within a 10 km radius. |
| 🔍 **Fighter Search** | Search fighters by name, view their record, weight class, style, and fight history. |
| 👤 **User Roles** | Amateur, Coach, Admin – permissions managed via Django admin panel. |
| 🛠️ **Admin Dashboard** | Manage users (suspend, change role), articles, API call logs, and recent actions. |

---

## 🧰 Tech Stack

- **Backend**: Django 5.x (Python)
- **Frontend**: HTML5, Bootstrap 5, CSS, JavaScript
- **Database**: SQLite (dev) – ready for PostgreSQL
- **APIs**:
  - [GNews](https://gnews.io/) – news articles
  - [Groq](https://console.groq.com/) – Llama LLM for AI assistant
  - [Overpass API](https://overpass-api.de/) + [OpenStreetMap](https://www.openstreetmap.org/) – gym location data
- **Mapping**: Leaflet.js
- **Version Control**: Git / GitHub

---

## 🚀 Getting Started

### Prerequisites

- Python 3.11+
- pip
- virtualenv (recommended)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/mma-fighting-platform.git
   cd mma-fighting-platform
