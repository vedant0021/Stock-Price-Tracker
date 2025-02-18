import yfinance as yf
import sqlite3
import datetime
import tkinter as tk
from tkinter import messagebox

def initialize_database():
    conn = sqlite3.connect("stock_prices.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS stocks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ticker TEXT,
            price REAL,
            timestamp TEXT
        )
    """)
    conn.commit()
    conn.close()

def get_stock_price(ticker):
    try:
        stock = yf.Ticker(ticker)
        data = stock.history(period='1d')
        if data.empty:
            messagebox.showerror("Error", "Invalid ticker symbol or no data available.")
            return None
        price = data['Close'].iloc[-1]
        currency = stock.info.get('currency', 'USD')
        return price, currency
    except Exception as e:
        messagebox.showerror("Error", f"Error fetching stock data: {e}")
        return None, None

def save_to_database(ticker, price):
    conn = sqlite3.connect("stock_prices.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS stocks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ticker TEXT,
            price REAL,
            timestamp TEXT
        )
    """)
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute("INSERT INTO stocks (ticker, price, timestamp) VALUES (?, ?, ?)", (ticker, price, timestamp))
    conn.commit()
    conn.close()

def get_stock():
    ticker = entry_ticker.get().upper()
    if not ticker:
        messagebox.showerror("Error", "Please enter a stock ticker symbol.")
        return
    price, currency = get_stock_price(ticker)
    if price:
        label_result.config(text=f"Current price of {ticker}: {price:.2f} {currency}")
        save_to_database(ticker, price)

def view_stored_prices():
    initialize_database()  # Ensure the table exists
    conn = sqlite3.connect("stock_prices.db")
    cursor = conn.cursor()
    cursor.execute("SELECT ticker, price, timestamp FROM stocks")
    rows = cursor.fetchall()
    conn.close()
    prices_text = "\nStored Stock Prices:\n"
    for row in rows:
        prices_text += f"{row[0]} - {row[1]:.2f} (Recorded on {row[2]})\n"
    messagebox.showinfo("Stored Prices", prices_text)

# GUI Setup
root = tk.Tk()
root.title("Stock Price Retriever")
root.geometry("400x300")

initialize_database()  # Create the database and table if not exists

tk.Label(root, text="Enter Stock Ticker:").pack(pady=5)
entry_ticker = tk.Entry(root)
entry_ticker.pack(pady=5)

tk.Button(root, text="Get Stock Price", command=get_stock).pack(pady=5)
label_result = tk.Label(root, text="")
label_result.pack(pady=5)

tk.Button(root, text="View Stored Prices", command=view_stored_prices).pack(pady=5)

tk.Button(root, text="Exit", command=root.quit).pack(pady=5)

root.mainloop()

