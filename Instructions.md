
# 🧠 HumanCloud Sourcing Classification Tool – User Guide

This tool classifies a list of websites into user-defined categories using OpenAI models. Follow the steps below to interact with the app.

---

## 📋 Step-by-Step Instructions

### ✅ Step 1: Upload Class Code File (`CSV`)
Upload a `.csv` or `.xlsx` file containing the **list of possible classification labels** you want the AI to choose from.

#### **Format**
- **One code per line**
- No headers

#### **Example (`codes.csv`)**
```csv
renters; resid; short; vac
renters; resid; long; single
renters; comm; office
renters; comm; retail
```

---

### 🧠 Step 2: Upload Prompt Template (`.txt`)
Upload a `.txt` file that serves as the **instruction template** for the AI. The template must include the placeholder `{codes}` where the list of codes will be inserted.

#### **Required format**
- Use `{codes}` exactly as written where the list should be placed.
- Include a user-facing instruction requesting classification.

#### **Example (`prompt.txt`)**
```txt
You are a website classifier. Based on the following list of codes:
{codes}

Read the text and return the top 3 classifications that best describe the content of the site.
Only return the top 3 labels, each on a new line.
```

---

### 🧠 Step 3: Select an OpenAI Model
Choose from available OpenAI models (e.g., `gpt-4o`, `gpt-3.5-turbo`). The dropdown includes **estimated cost per 1K tokens**, which helps you budget usage.

---

### 🌐 Step 4: Upload URL List (`CSV`)
Upload a `.csv` or `.xlsx` file with a **single column** containing the list of website URLs to classify.

#### **Format**
- **No header row**
- **One URL per line**

#### **Example (`urls.csv`)**
```csv
https://www.example1.com
https://www.propertymanager.com
https://www.retailleasingco.com
```

---

### 🟦 Step 5: Click “Run Classification”
Once all files are uploaded:
- Click **“Run Classification”**
- The app will fetch website content and use the OpenAI model to classify each page.
- A progress log will show below the button as each site is processed.

---

### 📈 Output Table
After processing, you’ll see a table with:
- `url`
- `top_1_code`
- `top_2_code`
- `top_3_code`

---

### 💾 Download Results
1. Enter your desired filename (no extension needed).
2. Click **“Download CSV”** to save the results.

---

## 🔍 Tips & Troubleshooting

- **Prompt doesn’t work?** Make sure it includes `{codes}`.
- **No results?** Try removing malformed or broken URLs.
- **Timeouts?** Very slow-loading pages may fail silently. They're retried with Playwright but not guaranteed.

---

## 🧪 Full Example

### 1. `codes.csv`
```csv
renters; resid; long; single
renters; comm; office
owners; resid; luxury
```

### 2. `prompt.txt`
```txt
You are a website classifier. Based on the following codes:
{codes}

Analyze the webpage text and identify the top 3 matching categories. Only return those 3 labels, each on a new line.
```

### 3. `urls.csv`
```csv
https://www.propertymanagementny.com
https://www.apartmentfinder.com
https://www.retailofficesolutions.com
```

---

