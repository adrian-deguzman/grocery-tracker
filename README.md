# 🛒 Grocery Tracker

A lightweight, mobile-first web application designed for planning grocery trips and tracking real-time shopping expenses while in-store. Built with **FastAPI** and a sleek, dark-themed **Tailwind CSS** Single Page Application (SPA).

---

## 📋 Table of Contents

- [Project Overview](#-project-overview)
- [Key Features](#-key-features)
- [Tech Stack](#-tech-stack)
- [Project Structure](#-project-structure)
- [Prerequisites](#-prerequisites)
- [Getting Started (Local Setup)](#-getting-started-local-setup)
- [Exposing via Tunnel (Mobile In-Store Testing)](#-exposing-via-tunnel-mobile-in-store-testing)
- [API Reference](#-api-reference)
- [Roadmap & Future Enhancements](#-roadmap--future-enhancements)

---

## 🌟 Project Overview

Grocery shopping often involves juggling pre-planned lists with spontaneous additions while trying to stay within a budget. **Grocery Tracker** bridges this gap:

1. **Pre-Store Planning:** Rapidly type item names into the **To Buy** list before heading out without worrying about prices upfront.
2. **In-Store Shopping:** Move items into the **Cart** as you pick them up, enter the shelf price and quantity, and watch your total calculate live in Philippine Pesos (₱).
3. **Budget Control:** Toggle items on or off to inspect the updated grand total before heading to the checkout counter.

---

## ✨ Key Features

- **Dual-Stage Workflow ("To Buy" vs. "In Cart"):**
  - **Planned List:** Quick-add items on the fly by hitting <kbd>Enter</kbd>.
  - **Transition Modal:** Effortlessly move items to the cart while entering unit price, quantity, and attaching photos.
  - **Direct Add:** Quickly log unplanned or impulse items directly to the cart.
- **Dynamic Running Total:** Instant calculation of `₱ Price × Qty` with item selection checkboxes to include/exclude items dynamically.
- **Smart Duplicate Merging:** Adding the same item with identical price and status merges quantities automatically rather than creating duplicate entries.
- **Photo Attachments & Lightbox:** Upload item photos (converted to Base64) to confirm labels or brands, with a fullscreen modal and download capability.
- **Mobile-First Dark Mode UI:** Clean, thumb-friendly iOS-inspired interface styled with Tailwind CSS, touch transitions, and real-time loading feedback.
- **Interactive API Documentation:** Auto-generated Swagger/OpenAPI documentation provided out-of-the-box by FastAPI.

---

## 🛠️ Tech Stack

- **Backend:** [Python 3.10+](https://www.python.org/), [FastAPI](https://fastapi.tiangolo.com/), [Uvicorn](https://www.uvicorn.org/), [Pydantic v2](https://docs.pydantic.dev/)
- **Frontend:** Vanilla HTML5, JavaScript (ES6+), [Tailwind CSS (CDN)](https://tailwindcss.com/)
- **Data Persistence:** In-memory store (dictionary-backed)
- **Tunneling:** [Cloudflare Tunnels (`cloudflared`)](https://developers.cloudflare.com/cloudflare-one/connections/connect-networks/) or [ngrok](https://ngrok.com/)

---

## 📁 Project Structure

```text
grocery-tracker/
├── api/
│   └── routes.py          # FastAPI REST endpoints (/api/cart)
├── core/
│   └── database.py        # In-memory storage & business logic (deduplication/merging)
├── models/
│   └── schemas.py         # Pydantic data schemas (Item, StatusEnum, etc.)
├── static/
│   ├── css/
│   │   └── style.css      # Custom styling & font declarations
│   ├── js/
│   │   └── app.js         # Frontend application logic & API integrations
│   └── index.html         # Main single-page application interface
├── main.py                # FastAPI entry point & static file routing
├── requirements.txt       # Project dependencies
└── README.md              # Project documentation
```

---

## ⚙️ Prerequisites

Ensure you have the following installed on your machine:
- **Python 3.10+** ([Download Python](https://www.python.org/downloads/))
- **Git** ([Download Git](https://git-scm.com/))
- *(Optional for tunneling)*: **cloudflared** ([Cloudflare Tunnel CLI](https://developers.cloudflare.com/cloudflare-one/connections/connect-networks/downloads/)) or **ngrok** ([ngrok CLI](https://ngrok.com/download))

---

## 🚀 Getting Started (Local Setup)

### 1. Clone the Repository

```bash
git clone https://github.com/<your-username>/grocery-tracker.git
cd grocery-tracker
```

### 2. Set Up a Virtual Environment

**Windows (PowerShell):**
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

**macOS / Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Run the Development Server

Start the application with Uvicorn:

```bash
uvicorn main:app --reload
```

The server will start at:
- **Web App:** [http://localhost:8000](http://localhost:8000)
- **Interactive API Docs (Swagger):** [http://localhost:8000/docs](http://localhost:8000/docs)
- **Alternative Docs (ReDoc):** [http://localhost:8000/redoc](http://localhost:8000/redoc)

---

## 🌐 Exposing via Tunnel (Mobile In-Store Testing)

To test the application on your mobile device while at the grocery store without deploying to a cloud host, you can expose your local server securely over an HTTPS tunnel.

### Option A: Cloudflare Tunnel (Recommended - No account required)

1. Make sure your local server is running on port 8000 (`uvicorn main:app --reload`).
2. In a separate terminal, run:
   ```bash
   cloudflared tunnel --url http://localhost:8000
   ```
3. Copy the generated `https://<random-subdomain>.trycloudflare.com` URL and open it on your mobile browser.

### Option B: ngrok

1. In a separate terminal, run:
   ```bash
   ngrok http 8000
   ```
2. Open the generated public HTTPS URL on your mobile device.

---

## 📡 API Reference

Base URL prefix: `/api/cart`

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/cart` | Retrieve all items across both `planned` and `in_cart` lists |
| `POST` | `/api/cart` | Add a new item (or merge quantity if item already exists) |
| `PUT` | `/api/cart/{item_id}` | Replace/update all fields of an existing item |
| `PATCH` | `/api/cart/{item_id}/status` | Update item status (`planned` or `in_cart`) |
| `DELETE` | `/api/cart/{item_id}` | Remove an item from the cart |

---

## 🔮 Roadmap & Future Enhancements

- [ ] **Persistent Database:** Transition from in-memory storage to SQLite, PostgreSQL, or Firebase Firestore.
- [ ] **Trip History & Budgets:** Save completed trips and compare spending over time.
- [ ] **Barcode / OCR Scanner:** Scan price tags or grocery receipts using device cameras.
- [ ] **Offline PWA Support:** Service worker support for offline usage in grocery stores with poor cellular reception.