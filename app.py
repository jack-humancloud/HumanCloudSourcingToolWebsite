import pandas as pd
import base64, io, time, requests, trafilatura
from dash import Dash, dcc, html, Input, Output, State, dash_table
import dash_bootstrap_components as dbc
from openai import OpenAI
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright
import os
from dotenv import load_dotenv

# === CONFIG =====================================================================
load_dotenv()
API_KEY = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=API_KEY)
MAX_LENGTH = 3000

app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
app.title = "HumanCloud Sourcing Classification Tool"
server = app.server

# === TOP-LEVEL TABS ==============================================================
app.layout = dbc.Container(
    dbc.Tabs(id="main-tabs", active_tab="tool", children=[

        # ------------------------------------------------------------------ TOOL
        dbc.Tab(label="Classification Tool", tab_id="tool", children=[

            html.H1("HumanCloud Sourcing Classification Tool", className="my-3"),

            # 1) Codes CSV --------------------------------------------------
            dbc.Row([
                dbc.Col([
                    html.H5("1. Upload Class Code File (CSV):"),
                    dcc.Upload(
                        id="upload-code-csv",
                        children=html.Div(["Drag and Drop or ", html.A("Select Code File")]),
                        style={"width": "100%", "height": "60px", "lineHeight": "60px",
                               "borderWidth": "1px", "borderStyle": "dashed",
                               "borderRadius": "5px", "textAlign": "center"},
                        multiple=False,
                    ),
                    html.Div(id="upload-code-feedback",
                             style={"color": "green", "marginTop": "10px"}),
                    dcc.Store(id="stored-code-list")
                ])
            ]),
            html.Hr(),

            # 2) Prompt template -------------------------------------------
            dbc.Row([
                dbc.Col([
                    html.H5("2. Upload Prompt Template (.txt):"),
                    dcc.Upload(
                        id="upload-prompt",
                        children=html.Div(["Drag and Drop or ", html.A("Select Prompt File")]),
                        style={"width": "100%", "height": "60px", "lineHeight": "60px",
                               "borderWidth": "1px", "borderStyle": "dashed",
                               "borderRadius": "5px", "textAlign": "center"},
                        multiple=False,
                    ),
                    html.Div(id="upload-prompt-feedback",
                             style={"color": "green", "marginTop": "10px"}),
                    dcc.Store(id="stored-prompt-text")
                ])
            ]),
            html.Hr(),

            # 3) Model dropdown --------------------------------------------
            dbc.Row([
                dbc.Col([
                    html.H5("3. Select OpenAI Model:"),
                    dcc.Dropdown(
                        id="model-selector",
                        options=[
                            {"label": "gpt-4o ($5.00/$15.00)", "value": "gpt-4o"},
                            {"label": "gpt-4-turbo ($10.00/$30.00)", "value": "gpt-4-turbo"},
                            {"label": "gpt-4 ($30.00/$60.00)", "value": "gpt-4"},
                            {"label": "gpt-3.5-turbo ($0.50/$1.50)", "value": "gpt-3.5-turbo"},
                            {"label": "o3 ($10.00/$40.00)", "value": "o3"},
                            {"label": "o3-mini ($1.10/$4.40)", "value": "o3-mini"},
                        ],
                        value="gpt-4o",
                        clearable=False
                    )
                ])
            ]),
            html.Hr(),

            # 4) URL list ---------------------------------------------------
            dbc.Row([
                dbc.Col([
                    html.H5("4. Upload URL List (CSV, one column of URLs):"),
                    dcc.Upload(
                        id="upload-data",
                        children=html.Div(["Drag and Drop or ", html.A("Select URL File")]),
                        style={"width": "100%", "height": "60px", "lineHeight": "60px",
                               "borderWidth": "1px", "borderStyle": "dashed",
                               "borderRadius": "5px", "textAlign": "center"},
                        multiple=False,
                    ),
                    html.Div(id="upload-feedback",
                             style={"color": "green", "marginTop": "10px"}),
                    html.Div(id="file-upload-status")
                ])
            ]),

            # Run button + progress ----------------------------------------
            dbc.Row([
                dbc.Col([
                    dbc.Button("Run Classification", id="run-button",
                               color="primary", className="mt-2"),
                    dcc.Loading(children=html.Div(id="run-status", className="mt-2"),
                                type="default"),
                    html.Div(id="progress-indicator", className="mt-2",
                             style={"whiteSpace": "pre-wrap"}),
                    dcc.Store(id="stored-csv")
                ])
            ]),
            html.Hr(),

            # Results table -------------------------------------------------
            html.H5("Output Table"),
            dash_table.DataTable(
                id="output-table",
                page_size=10,
                style_table={"overflowX": "auto"},
                style_cell={"textAlign": "left"}
            ),
            html.Br(),
            dcc.Download(id="download-result"),
            html.Div([
                dbc.Input(id="desired-filename",
                          placeholder="classified_websites",
                          value="classified_websites",
                          type="text",
                          style={"maxWidth": "230px",
                                 "display": "inline-block",
                                 "marginRight": "8px"}),
            ], style={"display": "inline-block"}),
            dbc.Button("Download CSV", id="download-btn", color="success"),
        ]),  # end Classification Tool tab

        # -------------------------------------------------------- ENRICH COMPANIES
        dbc.Tab(label="Enrich Companies", tab_id="enrich-main", children=[
            html.Br(),
            html.H3("Enrich Companies"),
            html.P("This page is reserved for future enrichment features "
                   "(e.g., pulling firmographics, ownership data, etc.).")
        ]),

        # --------------------------------------------------------------- INSTRUCTIONS
        dbc.Tab(label="Instructions", tab_id="instructions-main", children=[
            html.Br(),
            html.H3("How to Use This App"),
            html.Ol([
                html.Li("Upload your class codes file (CSV/XLSX)."),
                html.Li("Upload a prompt template (.txt)."),
                html.Li("Choose an OpenAI model."),
                html.Li("Upload a list of URLs to classify."),
                html.Li("Click “Run Classification”. Watch progress below."),
                html.Li("Review results and download the CSV when complete."),
            ]),
            html.P([
                "Full documentation: ",
                html.A("View on Google Drive ↗",
                    href="https://drive.google.com/your_shared_link_here",
                    target="_blank",               # open in new tab
                    style={"textDecoration": "underline"})
            ]),
            html.P("Tip: Edit the prompt template to experiment with different "
                   "instructions for the model.")
        ]),
    ]),
    fluid=True
)

# === CLIENT-SIDE “in-progress” MESSAGE ===========================================
app.clientside_callback(
    """
    function(n_clicks){
        if (n_clicks){ return "🔄 Classification in progress …"; }
        return "";
    }
    """,
    Output("run-status", "children"),
    Input("run-button", "n_clicks")
)

# === CALLBACKS ===================================================================
@app.callback(
    Output("upload-code-feedback", "children"),
    Output("stored-code-list", "data"),
    Input("upload-code-csv", "contents"),
    State("upload-code-csv", "filename"),
    prevent_initial_call=True
)
def load_codes(contents, filename):
    try:
        decoded = base64.b64decode(contents.split(",")[1])
        if filename.endswith(".xlsx"):
            df = pd.read_excel(io.BytesIO(decoded), header=None)
        else:
            df = pd.read_csv(io.StringIO(decoded.decode("utf-8")), header=None)
        codes = df.iloc[:, 0].dropna().astype(str).tolist()
        return f"✅ Loaded '{filename}'", codes
    except Exception as e:
        return f"❌ Error loading file: {e}", None

@app.callback(
    Output("upload-prompt-feedback", "children"),
    Output("stored-prompt-text", "data"),
    Input("upload-prompt", "contents"),
    State("upload-prompt", "filename"),
    prevent_initial_call=True
)
def load_prompt(contents, filename):
    try:
        decoded = base64.b64decode(contents.split(",")[1]).decode("utf-8")
        return f"✅ Loaded prompt '{filename}'", decoded
    except Exception as e:
        return f"❌ Error loading prompt: {e}", None

@app.callback(
    Output("upload-feedback", "children"),
    Input("upload-data", "contents"),
    State("upload-data", "filename"),
    prevent_initial_call=True
)
def update_upload_feedback(contents, filename):
    if contents and filename:
        return f"✅ Loaded '{filename}'"
    return ""

# --------------------------- MAIN CLASSIFIER -------------------------------------
@app.callback(
    Output("file-upload-status", "children"),
    Output("run-status", "children", allow_duplicate=True),
    Output("output-table", "data"),
    Output("output-table", "columns"),
    Output("stored-csv", "data"),
    Output("progress-indicator", "children"),
    Input("run-button", "n_clicks"),
    State("stored-code-list", "data"),
    State("stored-prompt-text", "data"),
    State("model-selector", "value"),
    State("upload-data", "contents"),
    State("upload-data", "filename"),
    prevent_initial_call=True
)
def run_classifier(_, codes, prompt, model,
                   contents, filename):

    if not contents or not codes or not prompt:
        return "❌ Missing file, codes, or prompt.", "", [], [], None, ""

    # read URL list ------------------------------------------------------------
    try:
        decoded = base64.b64decode(contents.split(",")[1])
        if filename.endswith(".xlsx"):
            df = pd.read_excel(io.BytesIO(decoded), header=None, names=["url"])
        else:
            df = pd.read_csv(io.StringIO(decoded.decode("utf-8")), header=None, names=["url"])
    except Exception as e:
        return f"❌ Could not read URL file: {e}", "", [], [], None, ""

    # iterate URLs -------------------------------------------------------------
    top1, top2, top3, progress_log = [], [], [], []
    for url in df["url"]:
        progress_log.append(f"Processing: {url}")
        text = fetch_with_requests(url)
        if not text or len(text.strip()) < 200:
            text = fetch_with_playwright(url)
        if not text:
            top1.append("ERROR: Unable to fetch content"); top2.append(""); top3.append("")
            continue

        try:
            filled_prompt = prompt.replace("{codes}", "\n".join(codes))
            response = client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": filled_prompt},
                    {"role": "user",
                     "content": f"Text:\n{text[:MAX_LENGTH]}\n\nTop 3 classifications:"}
                ]
            )
            out = response.choices[0].message.content.strip().splitlines()
            top1.append(out[0] if len(out) > 0 else "")
            top2.append(out[1] if len(out) > 1 else "")
            top3.append(out[2] if len(out) > 2 else "")
        except Exception as e:
            top1.append(f"ERROR: {e}"); top2.append(""); top3.append("")

    # assemble dataframe -------------------------------------------------------
    df["top_1_code"] = top1
    df["top_2_code"] = top2
    df["top_3_code"] = top3

    columns = [{"name": c, "id": c} for c in df.columns]
    data = df.to_dict("records")
    csv_text = df.to_csv(index=False)

    return (
        f"✅ Uploaded: {filename}",
        f"✅ Processed {len(df)} URLs",
        data,
        columns,
        csv_text,
        "\n".join(progress_log)
    )

# ---------------------------- DOWNLOAD CALLBACK ----------------------------------
@app.callback(
    Output("download-result", "data"),
    Input("download-btn", "n_clicks"),
    State("stored-csv", "data"),
    State("desired-filename", "value"),
    prevent_initial_call=True
)
def trigger_download(_, csv_text, name):
    fname = (name or "classified_websites").strip()
    if not fname.lower().endswith(".csv"):
        fname += ".csv"
    return {"content": csv_text, "filename": fname, "type": "text/csv"}

# === Helper functions ============================================================
def fetch_with_requests(url):
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        r = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(r.text, 'html.parser')
        text = soup.get_text(separator=' ', strip=True)
        return trafilatura.extract(text) or text
    except Exception:
        return ""

def fetch_with_playwright(url):
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch()
            page = browser.new_page()
            page.goto(url, timeout=20000)
            time.sleep(3)
            content = page.content()
            browser.close()
            soup = BeautifulSoup(content, 'html.parser')
            text = soup.get_text(separator=' ', strip=True)
            return trafilatura.extract(text) or text
    except Exception:
        return ""

# === MAIN ========================================================================
if __name__ == "__main__":
    app.run(debug=True)
