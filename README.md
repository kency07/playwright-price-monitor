# Playwright Async Price Monitor
A **production-style, async price monitoring system** built with **Playwright + asyncio**, capable of tracking multiple products concurrently, detecting price changes, and sending **batched email alerts** with robust error handling.

This project is designed to demonstrate **real-world scraping reliability**, not just basic scripts.

---
## 📦 Overview

Most beginner price trackers fail when dealing with JavaScript-rendered pages,
network delays, or long-running execution.

This project was built to solve those problems by focusing on:
- asynchronous task isolation
- resilient retry behavior
- persistent state across runs
- safe alert throttling

The goal is not maximum scraping speed, but **stability over time** —
making it suitable for long-running monitoring and freelancing demonstrations.


---
## ✨ Features

- Async multi-product monitoring
- Playwright-based scraping (JavaScript-rendered pages)
- Config-driven products via JSON
- Price normalization (₹, $, €, commas, decimals)
- Price change detection
    - 📉 Price drop

    - 📈 Price increase

    - 🆕 First-time price record

- Batch email notifications (rate-limited)
- Graceful error handling

    - Playwright timeouts
    - Missing selectors
    - Corrupted JSON files

- Persistent price storage
- Structured logging (file + console)
- Safe shutdown & task cancellation

---

## 📁 Project Structure
```
playwright-price-monitor/
│
├── src/
│   ├── browser_manager.py     # Playwright lifecycle manager
│   ├── scraper.py             # Price scraping logic
│   ├── monitor.py             # Price comparison & persistence
│   ├── notifier.py            # Logging & email notifications
│   └── utils.py               # Network checks & price normalization
│
├── data/
│   ├── products.json          # Config-driven product list
│   ├── prices.json            # Stored last known prices
│   ├── last_email_sent.txt    # Email rate-limit tracking
│   └── alerts.log             # Application logs
│
├── logging_config.py          # Central logging setup
├── main.py                    # Async task orchestrator
├── requirements.txt           # Project dependencies 
└── README.md                  # Project documentation

```
---
## ⚙️ How It Works (High Level)

- Loads products from products.json
- Starts a single Playwright browser
- Creates async monitoring tasks (one per product)

- Each task:

    - Fetches the product price
    - Normalizes the value
    - Compares with last stored price
    - Logs changes
    - Queues email alerts (if enabled)

- Email manager sends batched alerts at safe intervals
- Continues monitoring until manually stopped

---
## 🛠 Installation & Setup

### Clone the repository

Clone or download the project, then navigate into the folder
```bash
git clone https://github.com/kency07/playwright-price-monitor.git

cd playwright-price-monitor
```
### Create and activate a virtual environment

```bash 
python -m venv venv
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate
```

### Requirements

- Python 3.10+

- Internet connection

### Install dependencies
```bash
pip install -r requirements.txt
```
**Your requirements.txt should include:**
```
playwright>=1.40.0
python-dotenv>=1.0.0
```
---
## ⚙️ Configuration

### data/products.json
```
{
  "check_interval": 60,
  "products": [
    {
      "id": "product_1",
      "url": "https://www.example.com/dp/PRODUCT_ID_1",
      "platform": "example",
      "price_selector": "#span.a-price"
    },
    {
      "id": "product_2",
      "url": "https://www.example.com/dp/PRODUCT_ID_2",
      "platform": "example",
      "price_selector": "#span.a-price"
    }
  ]
}

```
---

## 📧 Email Alerts (Optional)

Email notifications are disabled by default.

Enable Email Alerts

Create a .env file:
```
EMAIL_ENABLED=true
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your_email@gmail.com
SMTP_PASSWORD=your_app_password
EMAIL_TO=receiver_email@gmail.com
EMAIL_INTERVAL_SECONDS=900
```
Emails are batched and rate-limited to prevent spam.

---
## ▶️ Running the Project

 ⚠️ Ensure Playwright browsers are installed:
 ```bash
 playwright install
 ```

Start monitoring
```bash
python main.py
```
Stop safely with:

Press <kbd>CTRL</kbd> + <kbd>C</kbd>

---
## 🧪 Logging

Console output (real-time)

File logs: data/alerts.log

Example log:
```
[CHECK] current price: 13937.0
📉 PRICE DROPPED from 13999.0 -> 13937.0
Batch email sent successfully
```
---
## 🛡 Error Handling

Handled gracefully without stopping monitoring:

-  Missing or corrupted prices.json
-  Playwright timeouts
-  Selector not found
-  Email credential issues
-  Network connectivity issues

Monitoring continues automatically after failures.

---
## ⚠️ Limitations

- Designed for **personal and educational use**
- Selectors may break if the target website changes its HTML structure
- Continuous monitoring may trigger anti-bot protections on some sites
- Email alerts rely on third-party SMTP services
- Not intended to bypass paywalls or protected endpoints

Users should respect website terms of service when using this tool.

---
## 📌 Use Cases

- Product price tracking

- E-commerce monitoring

- Competitive pricing analysis

- Freelance automation projects

- Async scraping demonstration
---
## 🛠 Tech Stack (Client-Attractive)

| Tool | Purpose |
|-----|--------|
| **Python** | Core application logic |
| **Playwright** | Scraping JavaScript-rendered pages |
| **Async / Await** | Non-blocking, concurrent execution |
| **asyncio** | Parallel product monitoring |
| **JSON / CSV** | Persistent price storage and reporting |
| **Environment Variables** | Secure configuration (email credentials) |

---
## 🧠 Design Philosophy

- Config over hardcoding

- Async-first architecture

- Fail-safe over fail-fast

- Production-style logging

- Minimal but scalable structure

---
## 🔮 Possible Enhancements (Optional)

- Selector fallback list

- Per-product check intervals

- Webhook / Telegram alerts

- Headful debug mode

- Docker support
---
## ⚖️ License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

---
👨‍💻 Author

Built as a freelancing portfolio project to demonstrate:

Web scraping fundamentals

Clean Python architecture

Automation-ready scripting

⭐ If you find this project useful, feel free to star the repository.

---