# ⚓ WMCT — WI Training Dashboard

> **West Med Container Terminal · CATOS Pre-Go-Live · Training Phase**  
> Interactive Streamlit app for managing Work Instructions across 8 binômes.

---

## 🚀 Free Deployment on Streamlit Community Cloud (Best Option for 7 users)

### Step 1 — Create GitHub repository

1. Go to [github.com](https://github.com) and sign up / log in (free)
2. Click **"New repository"**
3. Name it: `wmct-wi-dashboard`
4. Set it to **Public** (required for free tier)
5. Click **Create repository**

### Step 2 — Upload your files

Upload these 2 files to the repository:
- `app.py`
- `requirements.txt`

You can drag-and-drop directly on GitHub, or use the "Add file" button.

### Step 3 — Deploy on Streamlit Community Cloud

1. Go to [share.streamlit.io](https://share.streamlit.io)
2. Sign in with your **GitHub account**
3. Click **"New app"**
4. Select your repository: `wmct-wi-dashboard`
5. Main file path: `app.py`
6. Click **"Deploy!"**

Your app will be live at: `https://your-app-name.streamlit.app`

**✅ 100% FREE — No credit card — Supports 7+ users**

---

## 👤 Default Login Credentials

| Username   | Password     | Role    | Access              |
|------------|-------------|---------|---------------------|
| `manager`  | `manager123` | Manager | Full access         |
| `binome1`  | `pass1`      | Binôme  | Binôme 1 only       |
| `binome2`  | `pass2`      | Binôme  | Binôme 2 only       |
| `binome3`  | `pass3`      | Binôme  | Binôme 3 only       |
| `binome4`  | `pass4`      | Binôme  | Binôme 4 only       |
| `binome5`  | `pass5`      | Binôme  | Binôme 5 only       |
| `binome6`  | `pass6`      | Binôme  | Binôme 6 only       |

> ⚠️ **Change passwords** after first login via Settings → Reset Password

---

## 🗂️ Features

### Manager Features
- 📊 **Dashboard** — KPIs, charts, binôme overview, recent activity
- 📋 **WI Management** — Add, edit, delete, search/filter WIs
- 👥 **Binômes** — Manage teams, update any binôme's progress
- ✅ **Validate WIs** — Official manager validation of completed WIs
- 📈 **Analytics** — Ranking, heatmap, score distribution
- 📥 **Import/Export** — Excel export, Excel import, JSON backup
- ⚙️ **Settings** — User management, password reset

### Binôme Features
- 📊 **Dashboard** — Overall progress view
- 📝 **My Progress** — Update status, score, notes per WI
- 📥 **Export** — Download their own data

---

## 💾 Data Persistence

Data is stored in `wmct_data.json` in the app directory.

**On Streamlit Cloud:** Data resets on app restart. For persistent storage:
- Option A: Use [Streamlit's built-in secrets + external DB](https://docs.streamlit.io/library/advanced-features/secrets-management)
- Option B: Export JSON backup regularly (Import/Export page)
- Option C: Connect to **Google Sheets** as backend (free, persistent)

---

## 🔄 Run Locally

```bash
pip install -r requirements.txt
streamlit run app.py
```

Open: http://localhost:8501

---

## 📋 Excel Import Format

When importing progress from Excel, use these column names exactly:

| WI_Title | Binome_Name | Status | Score | Notes |
|----------|-------------|--------|-------|-------|
| WI: Open Vessel | Binôme 1 | Completed | 5 | Good work |

Download the template from the **Import/Export** page.

---

*WMCT WI Dashboard — Built for CATOS Training Phase*
