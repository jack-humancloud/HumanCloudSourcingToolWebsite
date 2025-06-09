HUMANCLOUD SOURCING CLASSIFICATION TOOL
======================================

Classify any list of website URLs into your own “codes” with a single click.

WHAT THE APP DOES
-----------------
1. Loads a code list (CSV or XLSX) you provide
2. Reads a prompt template for OpenAI
3. Scrapes each target URL’s text
4. Sends the text to the chosen OpenAI model
5. Returns the top-3 codes for every site in a downloadable table

Everything runs locally once Python is installed.

------------------------------------------------------------
1. PREREQUISITES  (install each just once)
------------------------------------------------------------
• Python 3.11 or newer  
  – Download from https://www.python.org — during install tick **“Add python.exe to PATH”**

• Visual Studio Code  
  – https://code.visualstudio.com

• VS Code Python extension  
  – In VS Code press Ctrl-Shift-X, search “Python”, click Install

• Git  (optional, but makes updates easier)  
  – https://git-scm.com

------------------------------------------------------------
2. GET THE PROJECT CODE
------------------------------------------------------------
Option A  — Download ZIP (simplest)  
  1. On the GitHub repo page click **Code ▸ Download ZIP**  
  2. Un-zip it to a folder such as  C:\HumanCloudTool

Option B  — Clone with Git  
  git clone https://github.com/YOUR-USERNAME/YOUR-REPO.git

------------------------------------------------------------
3. SET UP THE PYTHON ENVIRONMENT
------------------------------------------------------------
Open the project folder in VS Code, then in the built-in terminal run:

    python -m venv .venv          ← create virtual env
    # Windows PowerShell
    .venv\Scripts\Activate.ps1    ← activate
    # macOS / Linux
    source .venv/bin/activate

    pip install -r requirements.txt
    python -m playwright install  ← installs headless browsers

------------------------------------------------------------
4. CONFIGURE YOUR OPENAI KEY
------------------------------------------------------------
1. Copy  env.example  and rename the copy to  .env  
2. Edit .env and paste your real key, e.g.

    OPENAI_API_KEY=sk-********************************

(.env is already in .gitignore so it stays private.)

------------------------------------------------------------
5. RUN THE APP
------------------------------------------------------------
    python app.py

The terminal will say something like:

    Dash is running on http://127.0.0.1:8050/

Copy that address into your browser – the HumanCloud interface appears.

------------------------------------------------------------
6. USING THE INTERFACE
------------------------------------------------------------
1. Upload your class-codes file (CSV/XLSX, one code per line)  
2. Upload your prompt template (.txt)  
3. Choose an OpenAI model  
4. Upload your URL list (CSV/XLSX, single column)  
5. Click **Run Classification** — progress logs appear, results fill the table  
6. Click **Download CSV** to save the output

------------------------------------------------------------
7. PROJECT STRUCTURE
------------------------------------------------------------
app.py              – Dash entry point  
requirements.txt    – Python libraries  
Procfile            – For optional Heroku / Render deploy  
.env.example        – Template for your secrets  
.gitignore  
README.md

------------------------------------------------------------
8. UPDATING LATER  (if you cloned with Git)
------------------------------------------------------------
    git pull
    pip install -r requirements.txt    # grab any new dependencies

------------------------------------------------------------
9. TROUBLESHOOTING
------------------------------------------------------------
• “python not recognized”  
  – Re-run the Python installer and ensure “Add to PATH” is checked

• ModuleNotFoundError after running  
  – Activate the virtual environment, then run `pip install -r requirements.txt` again

• Browser-scraping errors  
  – Re-run `python -m playwright install`; ensure no VPN/firewall blocks outbound traffic

• 404 in browser  
  – Confirm the Dash server started without errors; use the exact address/port shown in the terminal

------------------------------------------------------------
MIT License · © 2025 Jack Richter
