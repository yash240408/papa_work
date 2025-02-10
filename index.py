import time
import pandas as pd
from io import StringIO
from flask import Flask, render_template, request, Response
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, ElementClickInterceptedException

app = Flask(__name__)

def scrape_exhibitor_data(last_page):
    # Set up Selenium WebDriver (headless mode for Vercel)
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    
    driver = webdriver.Chrome(options=options)
    url = "https://app.virtubox.io/bharat-tex/directory-website"
    driver.get(url)

    print("Opened website successfully.")

    # Wait for the table to load
    try:
        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.XPATH, "/html/body/div[1]/main/div/div[3]/div/section/div/div[3]/div/div[2]/div/table"))
        )
        print("Table loaded successfully.")
    except TimeoutException:
        print("Table did not load in time. Exiting...")
        driver.quit()
        return None

    exhibitors = []
    page = 1  
    headers = []

    while page <= last_page:
        print(f"📄 Scraping Page {page}...")

        try:
            # Locate the table
            table = driver.find_element(By.XPATH, "/html/body/div[1]/main/div/div[3]/div/section/div/div[3]/div/div[2]/div/table")
            rows = table.find_elements(By.TAG_NAME, "tr")

            # Extract column headers if running for the first time
            if page == 1 and rows:
                headers = [th.text.strip() for th in rows[0].find_elements(By.TAG_NAME, "th")]
                print(f"Column Headers: {headers}")

            # Extract data rows
            page_data = []
            for row in rows[1:]:  
                cols = row.find_elements(By.TAG_NAME, "td")
                exhibitor_data = [col.text.strip() for col in cols]
                if exhibitor_data:
                    page_data.append(exhibitor_data)

            print(f"✅ Extracted {len(page_data)} rows from Page {page}")
            exhibitors.extend(page_data)  

            if page >= last_page:
                print(f"✅ Reached last page ({last_page}). Stopping pagination.")
                break

            # Find and click the 'Next' button
            try:
                next_button = driver.find_element(By.XPATH, "/html/body/div[1]/main/div/div[3]/div/section/div/div[3]/div/div[3]/div[2]/div/ul/li[9]")
                button_class = next_button.get_attribute("class")
                if "disabled" in button_class:
                    print("⚠️ Next button is disabled. No more pages to scrape.")
                    break

                driver.execute_script("arguments[0].scrollIntoView();", next_button)
                driver.execute_script("arguments[0].click();", next_button)
                
                time.sleep(3)  
                page += 1  

            except NoSuchElementException:
                print("❌ Next button not found. Ending scraping.")
                break  

            except ElementClickInterceptedException:
                print("⚠️ Click intercepted, retrying...")
                time.sleep(2)
                driver.execute_script("arguments[0].click();", next_button)  

        except Exception as e:
            print(f"❌ Error while scraping: {e}")
            break

    driver.quit()

    # Convert to DataFrame
    if exhibitors:
        df = pd.DataFrame(exhibitors, columns=headers)
        return df
    return None

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        try:
            last_page = int(request.form["last_page"])
            df = scrape_exhibitor_data(last_page)

            if df is not None:
                # Convert to CSV
                csv_buffer = StringIO()
                df.to_csv(csv_buffer, index=False)
                csv_buffer.seek(0)

                # Send as file response
                return Response(
                    csv_buffer.getvalue(),
                    mimetype="text/csv",
                    headers={"Content-Disposition": "attachment;filename=exhibitors.csv"}
                )
            else:
                return "No data scraped. Please check if the website is accessible.", 400
        except ValueError:
            return "Invalid input! Please enter a valid number.", 400

    return render_template("index.html")

if __name__ == "__main__":
    app.run(debug=True)
