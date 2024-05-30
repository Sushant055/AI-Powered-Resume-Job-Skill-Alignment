import streamlit as st
import pdfplumber
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.chrome.options import Options
import time
import re
import google.generativeai as genai
from io import StringIO
from contextlib import redirect_stdout
from streamlit_option_menu import option_menu
from webdriver_manager.chrome import ChromeDriverManager

def module0():
    st.title("Project Overview")
    st.markdown(
        """
        This project aims to help the user to know what skills are in industry demand in their interested field,
        and assist them in identifying the skills their resume may lack.
        """
    )
    st.markdown("## Instructions:")
    st.markdown(
        """
        <ol>
            <li>Choose "LinkedIn Job Scraper" from the sidebar menu to search for job details in your interested domain.</li>
            <li>After finding relevant job listings, download the CSV file.</li>
            <li>Proceed to "Skill Extraction" and upload your resume to extract your skills.</li>
            <li>Upload the CSV file from step 2 to identify top industry demand skills.</li>
        </ol>
        """,
        unsafe_allow_html=True
    )
    st.markdown("## Architecture Diagram:")
    diagram_image = "./archi_diag.jpg"  # Replace with the actual path to your image
    st.image(diagram_image, use_column_width=True)

# Function for module 1: Resume Parser
def extract_skills(text):
    skills = set()

    # Keywords representing common tech skills
    tech_skills_keywords = {
        # Programming Languages
        "javascript", "java", "python", "c++", "c#", "php", "ruby", "swift", "typescript", "rust",
        # Web Development
        "html", "css", "sass", "bootstrap", "jquery", "ajax", "xml", "json", "graphql",
        # Frontend Frameworks/Libraries
        "react", "angular", "vue", "ember", "backbone", "d3", "three.js", "p5.js",
        # Backend Frameworks/Libraries
        "node.js", "express.js", "koa", "django", "flask", "laravel", "spring", "ruby on rails", "sinatra",
        # Databases
        "sql", "mysql", "postgresql", "sqlite", "mongodb", "redis", "firebase",
        # Machine Learning/Data Science
        "tensorflow", "keras", "pytorch", "scikit-learn", "pandas", "numpy", "matplotlib", "seaborn", "jupyter", "spark",
        "machine learning", "data science",
        # DevOps/Cloud Computing
        "docker", "kubernetes", "aws", "azure", "google cloud", "heroku", "digitalocean", "openstack",
        # Version Control
        "git", "svn", "mercurial",
        # Agile/Project Management
        "agile", "scrum", "kanban", "waterfall", "lean", "pmp", "prince2",
        # Testing
        "unittest", "junit", "pytest", "mocha", "jasmine", "selenium", "cucumber", "jmeter",
        # Other Technologies
        "blockchain", "iot", "nlp", "robotics", "cybersecurity", "networking", "ansible", "terraform",
        # Soft Skills
        "communication", "teamwork", "problem solving", "leadership", "creativity", "adaptability", "time management"
    }

    # Tokenize the text by spaces
    for skill in tech_skills_keywords:
        if skill.lower() in text.lower():
            skills.add(skill)
            
    return list(skills)

def module1():
    st.markdown(
        """
        <style>
        .title {
            font-size: 36px;
            color: #2a9df4; /* Blue color */
            text-align: center;
            margin-bottom: 30px;
        }
        .info-msg {
            font-size: 18px;
            color: #555555; /* Dark gray color */
            text-align: center;
            margin-bottom: 30px;
        }
        .upload-btn {
            color: white;
            background-color: #2a9df4; /* Blue color */
            border: none;
            border-radius: 5px;
            padding: 10px 20px;
            font-size: 18px;
            cursor: pointer;
        }
        .upload-btn:hover {
            background-color: #1b7db8; /* Darker blue color on hover */
        }
        </style>
        """,
        unsafe_allow_html=True
    )
    st.markdown("<h1 style='text-align: center; color:#2a9df4;'>Resume Skill Extractor</h1>", unsafe_allow_html=True)
    st.markdown("<h3 style='text-align: center; color:black;'>Upload your resume in PDF format to extract skills.</h3>", unsafe_allow_html=True)
    uploaded_file = st.file_uploader("Upload PDF", type=['pdf'], key="file_uploader")
    if uploaded_file is not None:
        with pdfplumber.open(uploaded_file) as pdf:
            resume_text = ""
            for page in pdf.pages:
                resume_text += page.extract_text()
        st.write("**Resume Content:**")
        st.write(resume_text)
        skills_extracted = extract_skills(resume_text)
        if skills_extracted:
            st.write("**Extracted Skills from Resume:**")
            for skill in skills_extracted:
                st.write(skill)
        else:
            st.write("**No skills extracted.**")

# Function for module 2: LinkedIn Job Scraper
class Linkedin_Project():
    def __init__(self):
        self.path = "chromedriver-path"  # Place the path of your ChromeDriver here
        self.job_title = []
        self.company_name = []
        self.job_location = []
        self.job_id = []
        self.job_description = []

    # def initialize_driver(self, webpage):
    #     self.driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
    #     self.driver.get(webpage)
    #     self.driver.maximize_window()

    def initialize_driver(self, webpage):
        try:
            # Check if environment variable is set
            if os.environ.get("webdriver.chrome.driver"):
                chromedriver_path = os.environ.get("webdriver.chrome.driver")
            else:
                chromedriver_path = ChromeDriverManager().install()
            self.driver = webdriver.Chrome(service=Service(chromedriver_path))
            self.driver.get(webpage)
            self.driver.maximize_window()
        except Exception as e:
            print(f"Error initializing driver: {e}")

    def login(self, username, password):
        self.username = username
        self.password = password
        WebDriverWait(self.driver, 5).until(EC.presence_of_element_located((By.XPATH, "//input[contains(@autocomplete,'username')]")))
        username_input = self.driver.find_element_by_xpath("//input[contains(@autocomplete,'username')]")
        username_input.send_keys(self.username)
        WebDriverWait(self.driver, 5).until(EC.presence_of_element_located((By.XPATH, "//input[contains(@autocomplete,'current-password')]")))
        password_input = self.driver.find_element_by_xpath("//input[contains(@autocomplete,'current-password')]")
        password_input.send_keys(self.password)
        WebDriverWait(self.driver, 5).until(EC.presence_of_element_located((By.XPATH, "//button[contains(@data-id,'submit-btn')]")))
        sign_up_button = self.driver.find_element_by_xpath("//button[contains(@data-id,'submit-btn')]")
        sign_up_button.click()
        time.sleep(15)
        WebDriverWait(self.driver, 20).until(EC.url_contains("https://www.linkedin.com/feed"))

    def user_interest_jobs(self, job_title):
        WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.XPATH, "//*[@id='global-nav']/div/nav/ul/li[3]/a")))
        jobs_button = self.driver.find_element_by_xpath("//*[@id='global-nav']/div/nav/ul/li[3]/a")
        jobs_button.click()
        time.sleep(3)
        self.user_job_title = job_title
        WebDriverWait(self.driver, 5).until(EC.presence_of_element_located((By.XPATH, "//input[contains(@id,'jobs-search-box-keyword')]")))
        job_title_bar = self.driver.find_element_by_xpath('//input[contains(@id,"jobs-search-box-keyword")]')
        job_title_bar.send_keys(self.user_job_title)
        job_title_bar.send_keys(Keys.ENTER)
        WebDriverWait(self.driver, 10).until(EC.visibility_of_all_elements_located((By.XPATH, "//ul[@class='scaffold-layout__list-container']/li[contains(@id,'ember')]")))

    def load_more_jobs(self):
        last_page = self.driver.execute_script('return document.body.scrollHeight')
        while True:
            self.driver.execute_script('window.scrollTo(0,document.body.scrollHeight);')
            time.sleep(5)
            new_page = self.driver.execute_script('return document.body.scrollHeight')
            if new_page == last_page:
                break
            else:
                last_page = new_page

    def pagination_pages(self):
        total_results = WebDriverWait(self.driver, 5).until(EC.presence_of_element_located((By.XPATH, "//div[@class='jobs-search-results-list__subtitle']/span")))
        total_results_int = int(re.sub(r"[^\d.]", "", total_results.text.split(' ')[0]))
        if total_results_int > 24:
            time.sleep(2)
            current_page = self.driver.current_url
            try:
                for page_number in range(0, 25, 25): 
                    self.driver.get(current_page + '&start=' + str(page_number))
                    self.job_available_scraping()
                    time.sleep(2)
                self.driver.quit()
            except:
                print("Scraped pages less than 5 ")
                self.driver.quit()
        else:
            self.job_available_scraping()
            self.driver.quit()

    def job_available_scraping(self):
        self.load_more_jobs()

        while True:  # Loop to handle stale element exceptions
            try:
                jobs_available = WebDriverWait(self.driver, 40).until(
                    EC.presence_of_all_elements_located((By.XPATH, "//ul[@class='scaffold-layout__list-container']/li"))
                )
                break  # Exit the loop if elements are found
            except:
                print("Stale Element Exception occurred. Re-trying...")
                time.sleep(2)  # Short delay before retrying

        print(f"Total number of job elements found: {len(jobs_available)}")

        for i in range(len(jobs_available)):
            self.driver.execute_script('arguments[0].scrollIntoView();', jobs_available[i])
            try:
                # Re-find elements within the loop
                job_title_element = WebDriverWait(self.driver, 20).until(
                    EC.presence_of_element_located((By.XPATH, f"//ul[@class='scaffold-layout__list-container']/li[{i+1}]//div[contains(@class,'lockup__title ember-view')]"))
                )
                job_title = job_title_element.text

                company_element = WebDriverWait(self.driver, 20).until(
                    EC.presence_of_element_located((By.XPATH, f"//ul[@class='scaffold-layout__list-container']/li[{i+1}]//div[contains(@class,'lockup__subtitle ember-view')]"))
                )
                company_name = company_element.text

                job_location_element = WebDriverWait(self.driver, 20).until(
                    EC.presence_of_element_located((By.XPATH, f"//ul[@class='scaffold-layout__list-container']/li[{i+1}]//div[contains(@class,'lockup__caption ember-view')]"))
                )
                job_location = job_location_element.text

                job_id = WebDriverWait(self.driver, 20).until(
                    EC.presence_of_element_located((By.XPATH, f"//ul[@class='scaffold-layout__list-container']/li[{i+1}]/div/div[1]"))
                )
                job_id_number = job_id.get_attribute('data-job-id')

                time.sleep(3) 
                job_title_element.click() 
                time.sleep(5)  # Increased wait time for job details

                WebDriverWait(self.driver, 20).until( 
                    EC.presence_of_element_located((By.XPATH, "//article[contains(@class,'jobs-description__container')]"))
                )

                try:
                    # More robust way to get job description
                    job_details_elements = WebDriverWait(self.driver, 20).until(
                        EC.presence_of_all_elements_located((By.XPATH, "//article[contains(@class,'jobs-description__container')]//p | //article[contains(@class,'jobs-description__container')]//li")) 
                    )
                    job_description = " ".join([elem.text for elem in job_details_elements])

                    time.sleep(3) 

                except:
                    print("Couldn't fetch job details")
                    job_description = ""  # Assign an empty string if details can't be fetched

                self.job_title.append(job_title)
                self.job_description.append(" ".join(job_description.split()))
                self.company_name.append(company_name)
                self.job_location.append(job_location)
                self.job_id.append(job_id_number)
            except:
                print("Couldn't fetch")

def module2():
    st.markdown("<h1 style='text-align: center; color: #2a9df4;'>LinkedIn Job Scraper</h1>", unsafe_allow_html=True)
    st.markdown("<h3 style='text-align: center; color:black;'>Enter your LinkedIn credentials and job details below:</br></br></h3>", unsafe_allow_html=True)
    username = st.text_input("Enter your LinkedIn Username")
    password = st.text_input("Enter your LinkedIn Password", type="password")
    job_title = st.text_input("Interested Domain/Job Title/Company")
    submit_button = st.button("Submit")
    if submit_button:
        st.markdown("<h3 style='text-align: center; color: green;'>Scraping LinkedIn for jobs...</h3>", unsafe_allow_html=True)
        driver = Linkedin_Project()
        driver.initialize_driver('https://www.linkedin.com/')
        driver.login(username, password)
        driver.user_interest_jobs(job_title)
        driver.pagination_pages()
        df = pd.DataFrame({'JOB_ID': driver.job_id, 'JOB_TITLE': driver.job_title, 'COMPANY_NAME': driver.company_name, 'JOB_LOCATION': driver.job_location, 'JOB_DESCRIPTION': driver.job_description})
        df.to_csv('linkedin_jobs.csv', index=False)
        st.markdown("<h3 style='text-align: center; color: green;'>Scraping complete! Check the CSV file for the results.</h3>", unsafe_allow_html=True)
        st.write(df)

# Function for module 3: Skills extraction using Google Gemini Pro
def module3():
    st.markdown(
        """
        <style>
        .title {
            font-size: 36px;
            color: #2a9df4; /* Blue color */
            text-align: center;
        }
        .info-msg {
            font-size: 18px;
            color: #555555; /* Dark gray color */
            text-align: center;
            margin-bottom: 30px;
        }
        .upload-btn {
            color: white;
            background-color: #2a9df4; /* Blue color */
            border: none;
            border-radius: 5px;
            padding: 10px 20px;
            font-size: 18px;
            cursor: pointer;
        }
        .upload-btn:hover {
            background-color: #1b7db8; /* Darker blue color on hover */
        }
        </style>
        """,
        unsafe_allow_html=True
    )
    api_key = "AIzaS**************************"  # Replace with your actual Google Gemini API key
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel("gemini-pro")

    def create_context_from_dataframe(df, question):
        # Customize this to extract the most relevant information
        skills_column = df['JOB_DESCRIPTION']
        top_skills = skills_column.value_counts().nlargest(10).to_string()
        context = f"The top 10 technical skills mentioned in the dataset are:\n{top_skills}"
        return context

    def get_gemini(context, question):
        prompt = f"{context}\n\n{question}"
        response = model.generate_content(prompt)
        return f"{response.text}"

    st.markdown("<h1 style='text-align: center; color: #2a9df4;'>Skills Extraction Using Google Gemini Pro</h1>", unsafe_allow_html=True)
    st.markdown("<h3 style='text-align: center; color:black;'>To extract industry demands skills, please upload the CSV file (linkedin_jobs.csv) containing scraped job data.</br></br></h3>", unsafe_allow_html=True)
    uploaded_file = st.file_uploader("Upload CSV/Excel file", type="csv")
    if uploaded_file is not None:
        df = pd.read_csv(uploaded_file)
        st.write(df)
        question = "tell me the top 10 technical skills mentioned in the csv"
        if st.button("Get the Industry Demand Skills"):
            if question:
                context = create_context_from_dataframe(df, question)
                response = get_gemini(context, question)
                st.write(f"Answer:\n {response}")
            else:
                st.warning("Please enter a question")

# Create sidebar menu
with st.sidebar:
    selected_page = option_menu(
        menu_title="Main Menu",
        options=["Home", "LinkedIn Job Scraper", "Skills Extraction"],
        icons=["house", "linkedin", "card-checklist"],
        menu_icon="cast",
        default_index=0,
    )

# Display selected page based on user's choice
if selected_page == "Home":
    module0()
elif selected_page == "LinkedIn Job Scraper":
    module2()
elif selected_page == "Skills Extraction":
    module1()
    module3()
