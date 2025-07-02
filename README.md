# 🤖 Smart Telegram Bot

An all-in-one AI-powered Telegram bot that helps you shorten URLs, convert documents, summarize files and beautiful stats.

---

## 🚀 Features

| Feature           | Description                                                                 |
|------------------|-----------------------------------------------------------------------------|
| 🔗 Shorten URL   | Use Bitly API to shorten long URLs instantly                                |
| 📊 Track URL     | Get real-time click stats and view them as a visual chart (Matplotlib)       |
| 📂 File Convert  | Convert files like PDF ↔ Word, Image → PDF using `pdf2docx`, `Pillow`, etc.  |
| 🧠 Summarize Docs| Upload a DOCX, PDF or TXT file and get an AI-generated summary               |


---

## 🧰 Built With

- [`python-telegram-bot`](https://github.com/python-telegram-bot/python-telegram-bot) v13.15
- [`transformers`](https://huggingface.co/transformers/) (BART model) for summarization
- [`matplotlib`](https://matplotlib.org/) for generating click stat charts
- `langdetect`, `googletrans`, `pdf2docx`, `python-docx`, `Pillow`, `PyMuPDF`

---

## 📦 Requirements

Install using:

```bash
pip install -r requirements.txt

 
