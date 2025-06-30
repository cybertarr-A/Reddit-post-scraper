import tkinter as tk
from tkinter import ttk, messagebox
import threading
import praw
import pandas as pd
from datetime import datetime
import time
import prawcore
import requests
import socket
import os
import certifi

# Ensure SSL certificates are available
os.environ['REQUESTS_CA_BUNDLE'] = certifi.where()

# ---------- ✅ Relative Time Function ----------
def get_relative_time(post_timestamp):
    now = datetime.utcnow()
    post_time = datetime.utcfromtimestamp(post_timestamp)
    diff = now - post_time

    years = diff.days // 365
    months = (diff.days % 365) // 30
    weeks = ((diff.days % 365) % 30) // 7
    days = ((diff.days % 365) % 30) % 7
    hours = diff.seconds // 3600
    minutes = (diff.seconds % 3600) // 60

    if years > 0:
        return f"{years} year{'s' if years > 1 else ''} ago"
    elif months > 0:
        return f"{months} month{'s' if months > 1 else ''} ago"
    elif weeks > 0:
        return f"{weeks} week{'s' if weeks > 1 else ''} ago"
    elif days > 0:
        return f"{days} day{'s' if days > 1 else ''} ago"
    elif hours > 0:
        return f"{hours} hour{'s' if hours > 1 else ''} ago"
    elif minutes > 0:
        return f"{minutes} minute{'s' if minutes > 1 else ''} ago"
    else:
        return "Just now"

# ---------- Reddit Initialization ----------
def initialize_reddit(client_id, client_secret, log):
    try:
        log("Initializing Reddit API client...")
        log(f"Client ID: {client_id}")
        log(f"Client Secret: {client_secret}")
        if not client_id or not client_secret:
            log("❌ Client ID or Client Secret is empty")
            return None

        reddit = praw.Reddit(
            client_id=client_id,
            client_secret=client_secret,
            user_agent="RedditScraper/1.0 (by u/MiddleArtichoke7868)",
            username=None,
            password=None
        )
        log("Testing basic network connectivity...")
        socket.create_connection(("www.reddit.com", 443), timeout=5)
        log("✅ Network connectivity to Reddit confirmed")
        log("Testing Reddit API connection...")
        user = reddit.user.me()
        log(f"✅ Successfully connected to Reddit API as {user}")
        return reddit
    except socket.timeout:
        log("❌ Network error: Connection to Reddit timed out")
        return None
    except socket.gaierror:
        log("❌ Network error: Failed to resolve Reddit domain (DNS issue)")
        return None
    except praw.exceptions.RedditAPIException as e:
        log(f"❌ Reddit API authentication error: {e}")
        return None
    except requests.exceptions.SSLError as e:
        log(f"❌ SSL error: {e}")
        return None
    except requests.exceptions.RequestException as e:
        log(f"❌ Network error: {e}")
        return None
    except Exception as e:
        log(f"❌ Error initializing Reddit client: {e}")
        return None

# ---------- Get Posts Function ----------
def get_posts(reddit, subreddit_name, max_posts, sort_type, time_filter, log):
    posts = []
    try:
        log(f"Accessing subreddit: r/{subreddit_name}")
        subreddit = reddit.subreddit(subreddit_name)
        subreddit.id
        log(f"✅ Subreddit r/{subreddit_name} found")

        if sort_type == 'top':
            submissions = subreddit.top(time_filter=time_filter, limit=None)
        elif sort_type == 'new':
            submissions = subreddit.new(limit=None)
        else:
            submissions = subreddit.hot(limit=None)

        count = 0
        for submission in submissions:
            if count >= max_posts:
                break

            posts.append({
                "Title": submission.title,
                "Caption": submission.selftext if submission.selftext else "",
                "Upvotes": submission.score,
                "Comments": submission.num_comments,
                "Author": submission.author.name if submission.author else "N/A",
                "Awards": submission.total_awards_received,
                "Flair": submission.link_flair_text if submission.link_flair_text else "None",
                "URL": submission.url,
                "Post Time": get_relative_time(submission.created_utc)
            })
            count += 1
            if count % 100 == 0:
                log(f"Collected {count} posts...")
                time.sleep(1)

        return posts

    except prawcore.exceptions.NotFound:
        log(f"Subreddit r/{subreddit_name} not found or is private.")
    except Exception as e:
        log(f"Error: {e}")
    return []

# ---------- Save to Excel ----------
def save_to_excel(posts, subreddit_name, sort_type, log):
    df = pd.DataFrame(posts)
    filename = f"{subreddit_name}_reddit_posts_{sort_type}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
    try:
        df.to_excel(filename, index=False)
        log(f"✅ Data saved to {filename}")
    except Exception as e:
        log(f"Error saving to Excel: {e}")

# ---------- Start Scraping Process ----------
def start_scraping(client_id, client_secret, subreddit_name, sort_type, time_filter, max_posts, log):
    reddit = initialize_reddit(client_id, client_secret, log)
    if not reddit:
        return

    log(f"Starting scrape for r/{subreddit_name}")
    posts = get_posts(reddit, subreddit_name, max_posts, sort_type, time_filter, log)
    if posts:
        log(f"✅ Total posts collected: {len(posts)}")
        save_to_excel(posts, subreddit_name, sort_type, log)
    else:
        log("❌ No posts found or an error occurred.")

# ---------- GUI Setup ----------
def run_gui():
    def log_message(msg):
        log_box.insert(tk.END, msg + "\n")
        log_box.see(tk.END)

    def on_submit():
        client_id = client_id_entry.get().strip()
        client_secret = client_secret_entry.get().strip()
        subreddit = subreddit_entry.get().strip()
        sort = sort_var.get()
        time_f = time_filter_var.get()
        try:
            max_p = int(max_posts_entry.get())
            if max_p <= 0:
                raise ValueError
        except:
            messagebox.showerror("Error", "Enter a valid number for max posts.")
            return

        if not client_id or not client_secret:
            messagebox.showerror("Error", "Please enter both Client ID and Client Secret.")
            return

        if not subreddit:
            messagebox.showerror("Error", "Please enter a subreddit name.")
            return

        log_box.delete(1.0, tk.END)
        threading.Thread(
            target=start_scraping,
            args=(client_id, client_secret, subreddit, sort, time_f, max_p, log_message),
            daemon=True
        ).start()

    # Main window
    root = tk.Tk()
    root.title("Reddit Scraper GUI")
    root.geometry("600x600")
    root.resizable(False, False)
    root.configure(bg="#000000")  # Total black background

    # Cyberpunk style
    neon_blue = "#00DFFC"
    neon_pink = "#FF00FF"
    neon_green = "#39FF14"
    black_bg = "#000000"
    hacker_font = ("Courier New", 12)

    # Custom style for ttk widgets
    style = ttk.Style()
    style.configure("Cyber.TCombobox", 
                    fieldbackground=black_bg, 
                    background=black_bg, 
                    foreground=neon_blue, 
                    font=hacker_font,
                    bordercolor=neon_pink,
                    arrowsize=12)
    style.map("Cyber.TCombobox", 
              fieldbackground=[("readonly", black_bg)],
              selectbackground=[("readonly", black_bg)],
              selectforeground=[("readonly", neon_green)],
              background=[("readonly", black_bg)],
              bordercolor=[("focus", neon_green), ("!focus", neon_pink)])

    # Title Label
    tk.Label(root, text="REDDIT SCRAPER", 
             font=("Courier New", 16, "bold"), 
             fg=neon_pink, 
             bg=black_bg).pack(pady=10)

    # API Credentials Section
    tk.Label(root, text="> API CREDENTIALS", 
             font=("Courier New", 12, "bold"), 
             fg=neon_green, 
             bg=black_bg).pack(pady=5)

    tk.Label(root, text="CLIENT ID:", 
             font=hacker_font, 
             fg=neon_blue, 
             bg=black_bg).pack(pady=2)
    client_id_entry = tk.Entry(root, width=40, 
                               font=hacker_font, 
                               fg=neon_green, 
                               bg=black_bg, 
                               insertbackground=neon_pink, 
                               bd=2, 
                               relief="flat",
                               highlightthickness=2,  # Thicker glow
                               highlightcolor=neon_pink,
                               highlightbackground=neon_pink)
    client_id_entry.pack()

    tk.Label(root, text="CLIENT SECRET:", 
             font=hacker_font, 
             fg=neon_blue, 
             bg=black_bg).pack(pady=2)
    client_secret_entry = tk.Entry(root, width=40, 
                                   font=hacker_font, 
                                   fg=neon_green, 
                                   bg=black_bg, 
                                   insertbackground=neon_pink, 
                                   bd=2, 
                                   relief="flat",
                                   highlightthickness=2,  # Thicker glow
                                   highlightcolor=neon_pink,
                                   highlightbackground=neon_pink)
    client_secret_entry.pack()

    # Scraping Parameters Section
    tk.Label(root, text="> SCRAPING PARAMETERS", 
             font=("Courier New", 12, "bold"), 
             fg=neon_green, 
             bg=black_bg).pack(pady=5)

    tk.Label(root, text="SUBREDDIT NAME:", 
             font=hacker_font, 
             fg=neon_blue, 
             bg=black_bg).pack(pady=2)
    subreddit_entry = tk.Entry(root, width=40, 
                               font=hacker_font, 
                               fg=neon_green, 
                               bg=black_bg, 
                               insertbackground=neon_pink, 
                               bd=2, 
                               relief="flat",
                               highlightthickness=2,  # Thicker glow
                               highlightcolor=neon_pink,
                               highlightbackground=neon_pink)
    subreddit_entry.pack()

    tk.Label(root, text="SORT TYPE:", 
             font=hacker_font, 
             fg=neon_blue, 
             bg=black_bg).pack(pady=2)
    sort_var = tk.StringVar(value="hot")
    sort_dropdown = ttk.Combobox(root, textvariable=sort_var, 
                                 values=["hot", "new", "top"], 
                                 state="readonly",
                                 style="Cyber.TCombobox")
    sort_dropdown.pack()

    tk.Label(root, text="TIME FILTER (FOR 'TOP'):", 
             font=hacker_font, 
             fg=neon_blue, 
             bg=black_bg).pack(pady=2)
    time_filter_var = tk.StringVar(value="all")
    time_filter_dropdown = ttk.Combobox(root, textvariable=time_filter_var, 
                                        values=["all", "day", "week", "month", "year"], 
                                        state="readonly",
                                        style="Cyber.TCombobox")
    time_filter_dropdown.pack()

    tk.Label(root, text="MAX POSTS:", 
             font=hacker_font, 
             fg=neon_blue, 
             bg=black_bg).pack(pady=2)
    max_posts_entry = tk.Entry(root, width=10, 
                               font=hacker_font, 
                               fg=neon_green, 
                               bg=black_bg, 
                               insertbackground=neon_pink, 
                               bd=2, 
                               relief="flat",
                               highlightthickness=2,  # Thicker glow
                               highlightcolor=neon_pink,
                               highlightbackground=neon_pink)
    max_posts_entry.insert(0, "500")
    max_posts_entry.pack()

    tk.Button(root, text="START SCRAPING", 
              command=on_submit, 
              font=("Courier New", 12, "bold"), 
              fg=neon_green, 
              bg=black_bg, 
              activebackground=neon_pink, 
              activeforeground=neon_green,
              bd=2, 
              relief="flat",
              highlightthickness=2,  # Thicker glow
              highlightcolor=neon_green,
              highlightbackground=neon_green,
              height=2).pack(pady=10)

    # Log Output
    tk.Label(root, text="> LOGS", 
             font=("Courier New", 12, "bold"), 
             fg=neon_green, 
             bg=black_bg).pack()
    log_box = tk.Text(root, height=15, width=70, 
                      font=("Courier New", 10), 
                      fg=neon_blue, 
                      bg=black_bg, 
                      insertbackground=neon_pink, 
                      bd=2, 
                      relief="flat",
                      highlightthickness=2,  # Thicker glow
                      highlightcolor=neon_pink,
                      highlightbackground=neon_pink)
    log_box.pack(padx=10, pady=5)

    root.mainloop()

# Run GUI
if __name__ == "__main__":
    run_gui()