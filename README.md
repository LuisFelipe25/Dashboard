# Quant Signal Performance Suite

Premium Streamlit dashboard for commercial presentation of `Signal 1` and `Signal 2`.

The repository is ready for public deployment and safe to run outside your local network. If local research artifacts are present, the app uses them. If they are missing, the app automatically falls back to a generated demo dataset so deployment still works without machine-specific folders.

The commercial dashboard is normalized to an initial capital of `1,000 USD`.

## Public deploy status

This project is prepared for:

- local execution with `streamlit run app.py`
- Streamlit Community Cloud deployment
- Render deployment

Main entrypoint:

- `app.py`

Deploy files included:

- `requirements.txt`
- `.streamlit/config.toml`
- `runtime.txt`
- `render.yaml`

## Project structure

```text
project_root/
  app.py
  requirements.txt
  runtime.txt
  render.yaml
  README.md
  .gitignore
  .streamlit/
    config.toml
  assets/
    logo.png
    hero_bg.png
    mockup_1.png
    mockup_2.png
  src/
    analytics/
    config/
    data/
    ui/
```

## How the app handles data in the cloud

The app first checks these optional in-repo locations:

- `Fusion_Integration/outputs/latest/...`
- `Estrategia_Trading/data/raw/XAUUSD_H1_*.csv`

If those folders do not exist in the deployed repository, the app does not fail. It switches automatically to demo mode. That makes this repo deployable by any third party without editing paths from your PC.

## Run locally

### 1. Create and activate a virtual environment

Windows PowerShell:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

macOS / Linux:

```bash
python -m venv .venv
source .venv/bin/activate
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Start the app

```bash
streamlit run app.py
```

Expected local URL:

- `http://localhost:8501`

## Push to GitHub

If the project is not yet on GitHub:

```bash
git init
git add .
git commit -m "Prepare dashboard for public deployment"
git branch -M main
git remote add origin <YOUR_GITHUB_REPO_URL>
git push -u origin main
```

If the repository already exists on GitHub:

```bash
git add .
git commit -m "Prepare dashboard for public deployment"
git push
```

## Deploy to Streamlit Community Cloud

### 1. Open Streamlit Community Cloud

Go to:

- [https://share.streamlit.io/](https://share.streamlit.io/)

### 2. Sign in with GitHub

Grant access to the repository you want to deploy.

### 3. Create the app

In the Streamlit dashboard:

1. Click `New app`
2. Select your GitHub repository
3. Select the branch, usually `main`
4. Set the main file path to:

```text
app.py
```

5. Click `Deploy`

### 4. Get the public link

Once the build finishes, Streamlit Community Cloud generates a public URL automatically. That is the public internet link you can share.

### 5. Update the deployment

To publish changes later:

1. Edit the code locally
2. Commit the changes
3. Push to the same GitHub branch used by Streamlit Cloud
4. Streamlit Cloud usually redeploys automatically
5. If it does not, open the app in Streamlit Cloud and click `Reboot` or `Redeploy`

## Alternative deployment on Render

This repository includes a ready Render blueprint:

- `render.yaml`

### Option A: Blueprint deploy

1. Open [https://render.com/](https://render.com/)
2. Sign in
3. Click `New +`
4. Choose `Blueprint`
5. Connect the GitHub repository
6. Render will detect `render.yaml`
7. Confirm deployment

Build command used:

```bash
pip install -r requirements.txt
```

Start command used:

```bash
streamlit run app.py --server.port $PORT --server.address 0.0.0.0
```

### Option B: Manual Render web service

If you do not want Blueprint mode:

1. Create a new `Web Service`
2. Connect the repository
3. Set:

- Environment: `Python`
- Build Command: `pip install -r requirements.txt`
- Start Command: `streamlit run app.py --server.port $PORT --server.address 0.0.0.0`

### Public URL on Render

Render generates a public URL after a successful deploy.

### Updating Render

Push new commits to the connected branch. Render can redeploy automatically or you can trigger a manual deploy in the dashboard.

## Replace demo mode with real data later

If you want the deployed app to use real artifacts instead of demo fallback, add these paths into the repository with the expected formats:

- `Fusion_Integration/outputs/latest/<run_id>/executed_trades.csv`
- `Fusion_Integration/outputs/latest/<run_id>/summary.json`
- `Estrategia_Trading/data/raw/XAUUSD_H1_*.csv`

If those files are not present, the app still works in demo mode.

## Troubleshooting

### The cloud app shows demo data

That is expected when the real artifact folders are not present in the deployed repository.

### Streamlit Cloud build fails

Check:

- `requirements.txt` is committed
- `app.py` is in the repository root
- the selected branch is correct
- the repo is accessible from your Streamlit account

### Render deploy fails

Check:

- `requirements.txt` exists
- `render.yaml` exists if using Blueprint deploy
- the start command includes `--server.port $PORT --server.address 0.0.0.0`

### A third party does not have your PC folders

No problem. The app is intentionally coded to fall back to demo data and avoid path dependency on your local machine.

## Summary

Any third party can now:

1. clone the repository
2. install `requirements.txt`
3. run `streamlit run app.py`
4. deploy to Streamlit Community Cloud or Render
5. obtain a public URL without editing local paths
