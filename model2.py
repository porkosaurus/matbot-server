import pandas as pd
import requests
from bs4 import BeautifulSoup
import os
from openai import OpenAI
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
import time as time_module
import spacy
from flask import Flask, request, jsonify
from flask_cors import CORS
import mysql.connector
from mysql.connector import Error
import re
import google.generativeai as genai
import google.generativeai.generative_models as genai_models
from google.ai.generativelanguage import Content, Part

# Configure the API with your API key
genai.configure(api_key="")

#Initialize Database
db_connection = mysql.connector.connect(
    host="34.94.235.177", 
    user="root",  
    password="connorjuman", 
    database="course_info" 
)
cursor = db_connection.cursor()

# Initialize the Flask application
app = Flask(__name__)
CORS(app)


# Load the medium model
# nlp = spacy.load("en_core_web_lg")

# Initialize the OpenAI client
api_key = ''
client = OpenAI(api_key=api_key)
# openai.api_key = ''

departments = [
    "Accounting",
    "Africana Studies",
    "American Indian Studies",
    "Anthropology",
    "Art and Design",
    "Asian American Studies",
    "Biology",
    "Business Administration, Graduate Level",
    "Business Honors",
    "David Nazarian College of Business and Economics",
    "Business Law",
    "Real Estate",
    "Central American and Transborder Studies",
    "Chemistry and Biochemistry",
    "Chicana and Chicano Studies",
    "Child and Adolescent Development",
    "Cinema and Television Arts",
    "Civic and Community Engagement",
    "Applied Mechanics",
    "Civil Engineering",
    "Civil Engineering and Construction Management",
    "Communication Disorders and Sciences",
    "Communication Studies",
    "Computer Science",
    "Criminology and Justice Studies",
    "Deaf Studies",
    "Economics",
    "Educational Leadership and Policy Studies",
    "Educational Psychology and Counseling",
    "Electrical and Computer Engineering",
    "Elementary Education",
    "English",
    "Environmental and Occupational Health",
    "Family and Consumer Sciences",
    "Finance, Financial Planning, and Insurance",
    "Gender and Women's Studies",
    "Geography and Environmental Studies",
    "Geological Sciences",
    "Health Sciences",
    "History",
    "Humanities, Graduate Level",
    "Interdisciplinary Studies",
    "Interdisciplinary Studies and Liberal Studies",
    "Sustainability",
    "Jewish Studies",
    "Journalism",
    "Mass Communication",
    "Athletic Training",
    "Athletics",
    "Kinesiology",
    "Linguistics/Teaching English as a Second Language",
    "Entrepreneurship",
    "Management",
    "Marketing",
    "Mathematics",
    "Aerospace Engineering",
    "Mechanical Engineering",
    "Arabic",
    "Armenian",
    "Chinese",
    "Classics",
    "Foreign Literature in Translation",
    "French",
    "Hebrew",
    "Italian",
    "Japanese",
    "Korean",
    "Persian",
    "Russian",
    "Spanish",
    "Music",
    "Nursing",
    "Philosophy",
    "Physical Therapy",
    "Astronomy",
    "Physics and Astronomy",
    "Political Science",
    "Psychology",
    "Public Administration",
    "Queer Studies",
    "Recreation and Tourism Management",
    "Religious Studies",
    "Secondary Education",
    "Social Work",
    "Sociology",
    "Special Education",
    "Sustainability, Graduate Level",
    "Business Analytics",
    "Information Systems",
    "Systems and Operations Management",
    "Theatre",
    "Urban Studies and Planning"
]

department_shorthand = {
    "Accounting": ["ACCT"],
    "Africana Studies": ["AFRS"],
    "American Indian Studies": ["AIS"],
    "Anthropology": ["ANTH"],
    "Art and Design": ["ART"],
    "Asian American Studies": ["AAS"],
    "Assistive Technology Engineering": ["ATE"],
    "Biology": ["BIOL"],
    "Business Administration, Graduate Level": ["GBUS"],
    "David Nazarian College of Business and Economics": ["BUS"],
    "Business Law": ["BLAW"],
    "Real Estate": ["RE"],
    "Central American and Transborder Studies": ["CAS"],
    "Chemistry and Biochemistry": ["CHEM"],
    "Chicana and Chicano Studies": ["CHS"],
    "Child and Adolescent Development": ["CADV"],
    "Cinema and Television Arts": ["CTVA"],
    "Civic and Community Engagement": ["CCE"],
    "Applied Mechanics": ["AM"],
    "Civil Engineering": ["CE"],
    "Civil Engineering and Construction Management": ["CM"],
    "Communication Disorders and Sciences": ["CD"],
    "Communication Studies": ["COMS"],
    "Computer Science": ["CIT", "CS"],
    "Criminology and Justice Studies": ["CJS"],
    "Deaf Studies": ["DEAF"],
    "Diverse Community Development Leadership": ["DCDL"],
    "Economics": ["ECON"],
    "Educational Leadership and Policy Studies": ["ELPS"],
    "Educational Psychology and Counseling": ["EPC"],
    "Electrical and Computer Engineering": ["ECE"],
    "Elementary Education": ["EED"],
    "English": ["ENGL"],
    "Environmental and Occupational Health": ["EOH"],
    "Family and Consumer Sciences": ["FCS"],
    "Finance, Financial Planning, and Insurance": ["FIN"],
    "Gender and Women's Studies": ["GWS"],
    "Geography and Environmental Studies": ["GEOG"],
    "Geological Sciences": ["GEOL"],
    "Health Sciences": ["HSCI"],
    "History": ["HIST"],
    "Humanities, Graduate Level": ["HUM"],
    "Interdisciplinary Studies": ["IDS", "LRS"],
    "Sustainability": ["SUST"],
    "Jewish Studies": ["JS"],
    "Journalism": ["JOUR"],
    "Kinesiology": ["KIN", "AT"],
    "Linguistics/Teaching English as a Second Language": ["LING"],
    "Entrepreneurship": ["ENTR"],
    "Knowledge Management": ["KM"],
    "Management": ["MGT"],
    "Manufacturing Systems Engineering and Management": ["MSE"],
    "Marketing": ["MKT"],
    "Mathematics": ["MATH"],
    "Aerospace Engineering": ["AE"],
    "Mechanical Engineering": ["ME"],
    "Arabic": ["ARAB"],
    "Armenian": ["ARMN"],
    "Chinese": ["CHIN"],
    "Classics": ["CLAS"],
    "Foreign Literature in Translation": ["FLIT"],
    "French": ["FREN"],
    "Hebrew": ["HEB"],
    "Italian": ["ITAL"],
    "Japanese": ["JAPN"],
    "Korean": ["KOR"],
    "Persian": ["PERS"],
    "Russian": ["RUSS"],
    "Spanish": ["SPAN"],
    "Music": ["MUS"],
    "Nursing": ["NURS"],
    "Philosophy": ["PHIL"],
    "Physical Therapy": ["PT"],
    "Astronomy": ["ASTR"],
    "Physics and Astronomy": ["PHYS"],
    "Political Science": ["POLS"],
    "Psychology": ["PSY"],
    "Public Administration": ["MPA"],
    "Queer Studies": ["QS"],
    "Recreation and Tourism Management": ["RTM"],
    "Religious Studies": ["RS"],
    "Secondary Education": ["SED"],
    "Social Work": ["SWRK"],
    "Sociology": ["SOC"],
    "Special Education": ["SPED"],
    "Sustainability, Graduate Level": ["SUST"],
    "Business Analytics": ["BANA"],
    "Information Systems": ["IS"],
    "Systems and Operations Management": ["SOM"],
    "Theatre": ["TH"],
    "Urban Studies and Planning": ["URBS"],
}

# Define keywords for each department

department_keywords = {
    "Accounting": ["financial", "audit", "accounting", "taxation", "ledger", "bookkeeping", "cpa", "accountant", "revenue", "expenses"],
    "Africana Studies": ["african", "diaspora", "afrocentric", "pan-african", "colonialism", "slavery", "black studies", "african culture", "african history", "african diaspora"],
    "American Indian Studies": ["native", "indigenous", "tribal", "american indian", "reservation", "native culture", "native history", "tribal law", "indigenous rights", "native languages"],
    "Anthropology": ["culture", "ethnography", "human evolution", "social anthropology", "archaeology", "linguistic anthropology", "physical anthropology", "cultural diversity", "fieldwork", "anthropological theory"],
    "Art and Design": ["creative", "visual arts", "design", "fine arts", "painting", "sculpture", "graphic design", "illustration", "photography", "art history"],
    "Asian American Studies": ["asian american", "pacific islander", "immigration", "ethnic studies", "asian diaspora", "asian culture", "asian history", "racial identity", "asian politics", "asian literature"],
    "Biology": ["genetics", "ecology", "microbiology", "evolution", "cell biology", "botany", "zoology", "biotechnology", "conservation biology", "marine biology"],
    "Business Administration, Graduate Level": ["mba", "management", "entrepreneurship", "business strategy", "organizational behavior", "operations management", "business ethics", "international business", "human resources", "marketing strategy"],
    "Business Honors": ["honors", "leadership", "business ethics", "corporate governance", "strategic management", "financial management", "honors thesis", "business research", "innovation", "business analysis"],
    "David Nazarian College of Business and Economics": ["economics", "finance", "marketing", "supply chain", "business analytics", "accounting", "international trade", "economic theory", "microeconomics", "macroeconomics"],
    "Business Law": ["corporate law", "legal", "contracts", "regulations", "business litigation", "intellectual property", "employment law", "commercial law", "corporate governance", "legal ethics"],
    "Real Estate": ["property", "housing", "real estate", "mortgage", "property management", "real estate development", "real estate finance", "land use", "real estate law", "urban planning"],
    "Central American and Transborder Studies": ["central america", "border", "transnational", "migration", "latin america", "immigration policy", "border security", "human rights", "cultural studies", "transborder communities"],
    "Chemistry and Biochemistry": ["organic chemistry", "biochemistry", "molecular", "inorganic chemistry", "analytical chemistry", "physical chemistry", "chemical biology", "medicinal chemistry", "environmental chemistry", "chemical synthesis"],
    "Chicana and Chicano Studies": ["chicano", "latinx", "mexican american", "social justice", "chicana feminism", "cultural identity", "chicano history", "latino politics", "chicano literature", "chicano art"],
    "Child and Adolescent Development": ["childhood", "adolescence", "developmental psychology", "youth", "early childhood education", "adolescent psychology", "child development", "parenting", "child psychology", "adolescent development"],
    "Cinema and Television Arts": ["film", "media", "cinematography", "screenwriting", "broadcasting", "film production", "television production", "media studies", "film theory", "video production"],
    "Civic and Community Engagement": ["community", "civic", "volunteer", "social change", "community service", "public service", "civic education", "community development", "social activism", "community organizing"],
    "Applied Mechanics": ["mechanics", "dynamics", "materials", "structural analysis", "fluid mechanics", "solid mechanics", "mechanical properties", "stress analysis", "vibration", "thermodynamics"],
    "Civil Engineering": ["infrastructure", "construction", "civil engineering", "transportation", "structural engineering", "water resources", "geotechnical engineering", "environmental engineering", "urban planning", "construction management"],
    "Civil Engineering and Construction Management": ["construction management", "project management", "civil engineering", "construction technology", "sustainable construction", "cost estimation", "construction safety", "contract management", "construction planning", "building codes"],
    "Communication Disorders and Sciences": ["speech pathology", "audiology", "language development", "hearing disorders", "speech therapy", "communication disorders", "voice disorders", "language disorders", "speech science", "audiological assessment"],
    "Communication Studies": ["interpersonal communication", "media studies", "public speaking", "rhetoric", "communication theory", "organizational communication", "nonverbal communication", "persuasion", "mass communication", "communication research"],
    "Computer Science": ["programming", "algorithms", "software engineering", "computer networks", "data structures", "artificial intelligence", "database systems", "computer architecture", "operating systems", "cybersecurity"],
    "Criminology and Justice Studies": ["criminal justice", "law enforcement", "criminology", "forensic science", "corrections", "juvenile justice", "crime prevention", "criminal law", "victimology", "criminal behavior"],
    "Deaf Studies": ["sign language", "deaf culture", "interpreting", "linguistics of sign language", "deaf education", "audiology", "communication access", "deaf history", "deaf community", "American Sign Language"],
    "Economics": ["microeconomics", "macroeconomics", "economic theory", "international economics", "labor economics", "public economics", "development economics", "econometrics", "industrial organization", "environmental economics"],
    "Educational Leadership and Policy Studies": ["educational leadership", "education policy", "school administration", "educational reform", "instructional leadership", "education law", "school finance", "educational equity", "school improvement", "educational governance"],
    "Educational Psychology and Counseling": ["learning theory", "educational psychology", "counseling psychology", "child development", "mental health", "school counseling", "psychological assessment", "cognitive development", "behavioral interventions", "counseling techniques"],
    "Electrical and Computer Engineering": ["circuit design", "signal processing", "electrical engineering", "computer engineering", "control systems", "communications engineering", "power systems", "microelectronics", "digital systems", "embedded systems"],
    "Elementary Education": ["early childhood education", "elementary teaching", "curriculum development", "literacy", "classroom management", "educational technology", "math education", "science education", "social studies education", "special education"],
    "English": ["literature", "creative writing", "English language", "literary theory", "poetry", "fiction", "non-fiction", "drama", "composition", "English studies"],
    "Environmental and Occupational Health": ["environmental health", "occupational health", "public health", "industrial hygiene", "environmental toxicology", "risk assessment", "air quality", "water quality", "hazardous waste management", "environmental policy"],
    "Family and Consumer Sciences": ["nutrition", "child development", "family studies", "consumer behavior", "interior design", "textiles", "fashion", "food science", "family resource management", "human development"],
    "Finance, Financial Planning, and Insurance": ["finance", "financial planning", "insurance", "investment", "risk management", "corporate finance", "personal finance", "financial markets", "financial analysis", "retirement planning"],
    "Gender and Women's Studies": ["feminism", "gender studies", "women's studies", "queer studies", "gender identity", "sexuality", "feminist theory", "gender roles", "women's rights", "gender politics"],
    "Geography and Environmental Studies": ["geography", "environmental studies", "GIS", "human geography", "physical geography", "urban planning", "climate change", "sustainability", "cartography", "environmental science"],
    "Geological Sciences": ["geology", "earth sciences", "mineralogy", "paleontology", "geochemistry", "geophysics", "sedimentology", "petrology", "stratigraphy", "environmental geology"],
    "Health Sciences": ["public health", "healthcare administration", "epidemiology", "health education", "community health", "health policy", "biostatistics", "environmental health", "health promotion", "global health"],
    "History": ["historical research", "world history", "American history", "European history", "ancient history", "military history", "cultural history", "social history", "historiography", "political history"],
    "Humanities, Graduate Level": ["philosophy", "literature", "art history", "classics", "cultural studies", "ethics", "religious studies", "language studies", "comparative literature", "humanities research"],
    "Interdisciplinary Studies": ["interdisciplinary research", "critical thinking", "problem solving", "collaboration", "creativity", "innovation", "integrative learning", "cross-disciplinary", "diversity", "interdisciplinary projects"],
    "Interdisciplinary Studies and Liberal Studies": ["liberal arts", "interdisciplinary learning", "general education", "holistic education", "liberal studies", "critical inquiry", "ethical reasoning", "social responsibility", "civic engagement", "liberal arts research"],
    "Sustainability": ["sustainable development", "environmental sustainability", "climate change", "renewable energy", "sustainable agriculture", "conservation", "sustainable business", "sustainability science", "sustainable design", "sustainable urban planning"],
    "Jewish Studies": ["Jewish history", "Hebrew", "Judaism", "Jewish culture", "Israel studies", "Holocaust studies", "Jewish literature", "Jewish philosophy", "Jewish religious texts", "Jewish diaspora"],
    "Journalism": ["news writing", "media ethics", "investigative journalism", "broadcast journalism", "digital journalism", "photojournalism", "journalistic research", "multimedia storytelling", "media law", "sports journalism"],
    "Mass Communication": ["mass media", "communication theory", "media studies", "media production", "advertising", "public relations", "social media", "media effects", "media literacy", "media industry"],
    "Athletic Training": ["sports medicine", "injury prevention", "rehabilitation", "exercise physiology", "kinesiology", "orthopedic assessment", "emergency care", "athletic performance", "strength conditioning", "sports nutrition"],
    "Athletics": ["sports management", "coaching", "physical education", "sports psychology", "athletic administration", "sports marketing", "recreational sports", "sports law", "sports ethics", "athletic training"],
    "Kinesiology": ["human movement", "exercise science", "biomechanics", "motor behavior", "physical activity", "sport science", "health and fitness", "exercise physiology", "sports medicine", "physical education"],
    "Linguistics/Teaching English as a Second Language": ["linguistics", "language acquisition", "phonetics", "syntax", "semantics", "pragmatics", "TESOL", "language teaching", "applied linguistics", "sociolinguistics"],
    "Entrepreneurship": ["startups", "venture creation", "business innovation", "entrepreneurial finance", "small business management", "new venture development", "entrepreneurial marketing", "social entrepreneurship", "business planning", "entrepreneurial mindset"],
    "Management": ["organizational behavior", "leadership", "strategic management", "human resources", "operations management", "project management", "change management", "business ethics", "management theory", "team building"],
    "Marketing": ["marketing strategy", "consumer behavior", "brand management", "digital marketing", "market research", "advertising", "sales management", "product development", "marketing communications", "international marketing"],
    "Mathematics": ["algebra", "calculus", "geometry", "statistics", "mathematical analysis", "number theory", "differential equations", "linear algebra", "mathematical modeling", "discrete mathematics"],
    "Aerospace Engineering": ["aeronautics", "astronautics", "flight mechanics", "propulsion", "aerodynamics", "aircraft design", "spacecraft design", "avionics", "materials science", "flight dynamics"],
    "Mechanical Engineering": ["thermodynamics", "fluid mechanics", "mechanics of materials", "dynamics", "machine design", "manufacturing processes", "heat transfer", "vibration analysis", "control systems", "robotics"],
    "Arabic": ["Arabic language", "Arabic literature", "Arabic culture", "Middle Eastern studies", "Arabic linguistics", "Islamic studies", "Arabic calligraphy", "Arabic grammar", "Arabic dialects", "translation studies"],
    "Armenian": ["Armenian language", "Armenian history", "Armenian literature", "Armenian culture", "Armenian Genocide", "Armenian diaspora", "Armenian studies", "Armenian art", "Armenian music", "Armenian linguistics"],
    "Chinese": ["mandarin", "chinese culture", "chinese history", "chinese literature", "chinese language", "chinese philosophy", "chinese calligraphy", "chinese cuisine", "chinese politics", "chinese society"],
   "Armenian": ["armenian culture", "armenian language", "armenian history", "armenian literature", "armenian diaspora", "armenian genocide", "armenian art", "armenian studies", "armenian music", "armenian politics"],
    "Chinese": ["mandarin", "chinese culture", "chinese history", "chinese literature", "chinese language", "chinese philosophy", "chinese calligraphy", "chinese cuisine", "chinese politics", "chinese society"],
    "Classics": ["ancient greece", "ancient rome", "latin", "classical literature", "classical mythology", "ancient history", "classical archaeology", "greek language", "roman history", "classical studies"],
    "Foreign Literature in Translation": ["world literature", "translated literature", "literary translation", "global literature", "multicultural literature", "translated works", "international literature", "cross-cultural literature", "literary works", "translated texts"],
    "French": ["french language", "french literature", "french culture", "french history", "french cinema", "french cuisine", "french art", "french philosophy", "french society", "francophone studies"],
    "Hebrew": ["hebrew language", "hebrew literature", "jewish studies", "israeli history", "hebrew bible", "jewish culture", "modern hebrew", "biblical hebrew", "israeli culture", "hebrew linguistics"],
    "Italian": ["italian language", "italian literature", "italian culture", "italian history", "italian cinema", "italian cuisine", "italian art", "italian fashion", "italian society", "renaissance studies"],
    "Japanese": ["japanese language", "japanese literature", "japanese culture", "japanese history", "japanese cinema", "japanese cuisine", "japanese art", "japanese society", "japanese linguistics", "japanese philosophy"],
    "Korean": ["korean language", "korean literature", "korean culture", "korean history", "korean cinema", "korean cuisine", "korean art", "korean society", "korean studies", "korean politics"],
    "Persian": ["persian language", "persian literature", "persian culture", "iranian history", "persian poetry", "iranian studies", "persian art", "persian cuisine", "persian society", "persian philosophy"],
    "Russian": ["russian language", "russian literature", "russian culture", "russian history", "russian cinema", "russian art", "soviet studies", "russian society", "russian politics", "russian philosophy"],
    "Spanish": ["spanish language", "spanish literature", "latin american studies", "spanish culture", "hispanic studies", "spanish history", "spanish cinema", "spanish art", "spanish linguistics", "spanish society"],
    "Music": ["music theory", "music history", "music performance", "music composition", "music education", "music technology", "musicology", "music therapy", "jazz studies", "classical music"],
    "Nursing": ["nursing practice", "nursing theory", "patient care", "healthcare systems", "nursing research", "clinical nursing", "nursing ethics", "community health nursing", "nursing education", "nursing leadership"],
    "Philosophy": ["ethical theory", "metaphysics", "epistemology", "philosophical logic", "political philosophy", "philosophy of mind", "philosophy of science", "ancient philosophy", "moral philosophy", "continental philosophy"],
    "Physical Therapy": ["rehabilitation", "kinesiology", "musculoskeletal", "neurological therapy", "physical therapy techniques", "orthopedic therapy", "sports physical therapy", "pediatric physical therapy", "geriatric physical therapy", "manual therapy"],
    "Astronomy": ["stellar astronomy", "galactic astronomy", "cosmology", "planetary science", "observational astronomy", "astrophysics", "solar system", "space exploration", "celestial mechanics", "astrobiology"],
    "Physics and Astronomy": ["classical mechanics", "quantum mechanics", "thermodynamics", "electromagnetism", "optics", "atomic physics", "nuclear physics", "particle physics", "astrophysics", "cosmology"],
    "Political Science": ["political theory", "comparative politics", "international relations", "public policy", "political economy", "political philosophy", "political behavior", "political institutions", "political methodology", "political sociology"],
    "Psychology": ["clinical psychology", "cognitive psychology", "developmental psychology", "social psychology", "industrial psychology", "forensic psychology", "health psychology", "neuropsychology", "psychological research", "psychological assessment"],
    "Public Administration": ["public policy", "public management", "public finance", "public sector", "public service", "public leadership", "public ethics", "public governance", "public law", "public economics"],
    "Public Health": ["epidemiology", "biostatistics", "environmental health", "global health", "health policy", "health promotion", "community health", "public health research", "public health practice", "public health education"],
    "Religious Studies": ["religious history", "religious philosophy", "religious ethics", "religious texts", "religious traditions", "religious cultures", "religious practices", "religious beliefs", "religious identity", "religious pluralism"],
    "Social Work": ["social welfare", "social justice", "community organizing", "social policy", "social services", "social work practice", "social work research", "social work ethics", "social work theory", "social work education"],
        "Sociology": ["social theory", "cultural sociology", "urban sociology", "social research", "sociological methods", "race and ethnicity", "social stratification", "gender sociology", "sociology of family", "sociology of education"],
    "Special Education": ["inclusive education", "learning disabilities", "behavioral disorders", "educational interventions", "autism spectrum", "special education law", "assistive technology", "early intervention", "special needs", "individualized education"],
    "Sustainability, Graduate Level": ["sustainable development", "environmental sustainability", "sustainable business", "climate change", "renewable energy", "sustainable agriculture", "green technology", "sustainability management", "conservation", "sustainable design"],
    "Business Analytics": ["data analysis", "business intelligence", "analytics tools", "predictive modeling", "statistical analysis", "big data", "data visualization", "decision making", "data-driven strategy", "market analysis"],
    "Information Systems": ["information technology", "database management", "systems analysis", "network security", "software development", "data communication", "information security", "enterprise systems", "IT project management", "cybersecurity"],
    "Systems and Operations Management": ["operations research", "supply chain management", "quality management", "production planning", "logistics", "inventory management", "process improvement", "project management", "operations strategy", "business process"],
    "Theatre": ["dramatic arts", "theatrical performance", "stage design", "acting techniques", "theater history", "directing", "playwriting", "costume design", "lighting design", "theater production"],
    "Urban Studies and Planning": ["urban planning", "city development", "urban policy", "community planning", "land use", "transportation planning", "urban design", "housing policy", "environmental planning", "urban sociology"]
}


general_education = """
GE A1 - Oral Communication: AAS 151, AFRS 151, CAS 151, CHS 151, COMS 151, QS 151
GE A2 - Written Communication: AAS 113B, AAS 114B, AAS 115, AFRS 113B, AFRS 114B, AFRS 115, CAS 113B, CAS 114B, CAS 115, CHS 113B, CHS 114B, CHS 115, ENGL 113B, ENGL 114B, ENGL 115, LING 113B, QS 113B, QS 114B, QS 115
GE A3 - Critical Thinking: AAS 201, AFRS 204, AIS 210, CHS 202, COMS 225, ENGL 215, GEH 111HON, HIST 202, JS 220, PHIL 100, PHIL 200, PHIL 230, QS 201, RS 204
GE B1 - Physical Science: ASTR 152, ASTR 154, CHEM 100, CHEM 101, CHEM 102, CHEM 103, CHEM 104, CHEM 110, GEOG 101, GEOG 101A, GEOG 103, GEOG 103A, GEOG 112, GEOL 101, GEOL 107, GEOL 110, GEOL 113, GEOL 117, GEOL 122, GEOL 125, PHYS 100A, PHYS 100B, PHYS 220A, PHYS 220B, SCI 111, SUST 111
GE B2 - Life Science: ANTH 151, BIOL 100, BIOL 101, BIOL 106, BIOL 107, BIOL 218, BIOL 292, GEOL 110, GEOL 113, GEOL 125   
GE B3 - Science Laboratory Activity: ASTR 154L, BIOL 100L, BIOL 101L, BIOL 106L, BIOL 107L, BIOL 218L, BIOL 292L, CHEM 100L, CHEM 101L, CHEM 102L, CHEM 103L, CHEM 104L, CHEM 110L, GEOG 101AL, GEOG 103AL, GEOG 112L, GEOL 102, GEOL 107L, GEOL 112, GEOL 117L, GEOL 123, PHYS 100AL, PHYS 100BL, PHYS 220AL, PHYS 220BL, SCI 111L, SUST 111L
GE B4 - Mathematics and Quantitative Reasoning: COMP 102/L, MATH 102, MATH 103, MATH 105, MATH 106, MATH 131, MATH 140, MATH 140BUS, MATH 140SCI, MATH 141/L, MATH 150A, MATH 255A, PHIL 135
GE B5 - Scientific Inquiry and Quantitative Reasoning: ANTH 341, ASTR 352, BIOL 306, BIOL 323, BIOL 324, BIOL 325, BIOL 327, BIOL 341, BIOL 362, BIOL 366, BIOL 375, CM 336/L, EOH 353, FCS 315, FCS 323, FCS 324, GEH 333HON, GEOG 311, GEOG 316, GEOG 365, GEOG 366, GEOL 300, GEOL 324, GEOL 327, GEOL 344, HSCI 336, HSCI 337, HSCI 345, KIN 309, LING 303, LING 310, MATH 331, MSE 303, PHIL 325, PHYS 305, PHYS 331, QS 369, RS 366
GE C1 - Arts: AFRS 246, AFRS 280, AFRS 351, ANTH 232, ART 100/L, ART 110, ART 114, ART 124A, ART 140, ART 141, ART 305, CHS 111, CHS 310, COMS 104, COMS 305, CTVA 210, CTVA 215, CTVA 309, CTVA 323, ENGL 208, FCS 111, FLIT 151, FLIT 250, HUM 101, HUM 105, HUM 106, JS 300, KIN 139A, KIN 144A, KIN 236/L, KIN 380/L, LING 240, MUS 105, MUS 106HH, MUS 107, MUS 108, MUS 306, PHIL 314, TH 110, TH 111, TH 310
GE C2 - Humanities: AAS 220, AAS 321, AFRS 245, AFRS 343, AFRS 344, AFRS 346, AFRS 352, AIS 301, AIS 318, ANTH 222, ANTH 326, CAS 201, CHS 201, CHS 350, CHS 351, CHS 380, CHS 381, CHS 382, CLAS 315, CTVA 215, DH 320, ENGL 254, ENGL 255, ENGL 258, ENGL 259, ENGL 275, ENGL 300, ENGL 316, ENGL 318, ENGL 322, ENGL 333, ENGL 364, FLIT 151, FLIT 331, FLIT 381, GWS 100, GWS 230, GWS 351, HIST 150, HIST 151, HIST 303, HIST 304, HUM 101, HUM 105, HUM 106, JS 100, JS 255, JS 300, JS 333, LING 200, PHIL 150, PHIL 165, PHIL 170, PHIL 201, PHIL 202, PHIL 240, PHIL 250, PHIL 260, PHIL 265, PHIL 280, PHIL 310, PHIL 314, PHIL 325, PHIL 330, PHIL 337, PHIL 349, PHIL 353, PHIL 354, QS 101, QS 303, RS 100, RS 101, RS 304, RS 307, RS 310, RS 356, RS 361, RS 362, RS 370, SUST 240, TH 333
GE C3: AFRS 271, AFRS 272, AIS 250, CHS 245, ECON 175, HIST 270, HIST 271, HIST 370, HIST 371, PHIL 317, RS 256
GE D1 - Social Sciences: AAS 210, AAS 350, AFRS 201, AFRS 220, AFRS 221, AFRS 304, AFRS 361, AIS 222, ANTH 150, ANTH 151, ANTH 152, ANTH 153, ANTH 212, ANTH 250, ANTH 262, ANTH 302, ANTH 305, ANTH 319, ANTH 341, CADV 150, CAS 309, CAS 310, CAS 368, CAS 369, CHS 261, CHS 331, CHS 345, CHS 346, CHS 347, CHS 361, CHS 362, CHS 366, COMS 312, COMS 323, ECON 101, ECON 160, ECON 161, ECON 310, ECON 311, ECON 360, FCS 253, FCS 256, FCS 318, FCS 340, FCS 357, FLIT 325, GEH 333HON, GEOG 107, GEOG 150, GEOG 170, GEOG 301, GEOG 321, GEOG 330, GEOG 351, GEOG 370, GWS 110, GWS 220, GWS 222, GWS 300, GWS 320, GWS 340, GWS 351, GWS 370, HIST 110, HIST 111, HIST 305, HIST 341, HIST 342, HIST 350, HIST 380, HIST 389, HSCI 132, HSCI 345, HSCI 369, JOUR 365, JS 318, LING 230, LING 309, MKT 350, PHIL 305, PHIL 391, POLS 156, POLS 225, POLS 310, POLS 350, POLS 380, PSY 150, PSY 312, PSY 352, PSY 365, RS 240, SOC 150, SOC 200, SOC 305, SOC 324, SUST 300, URBS 150, URBS 310, URBS 380
GE D3/D4: AAS 347, AFRS 161, CHS 260, CHS 445, POLS 155, POLS 355, RS 255
GE D4 - California State and Local Government: POLS 403, POLS 490CA
GE E - Lifelong Learning: AAS 230, AAS 390/F, AFRS 337, AIS 301, ART 151, ART 201, BIOL 327, BIOL 375, BLAW 280, BLAW 368, BUS 104, CADV 310, CAS 270/F, CCE 200, CD 133, CD 361, CHS 270SOC/F, CHS 347, CHS 360, CHS 390, CJS 340, CM 336/L, COMP 100, COMP 300, COMS 150, COMS 251, COMS 323, COMS 360, CTVA 100, CTVA 323, ENGL 253, ENGL 306, ENGL 313, ENGL 315, ENT 101, EOH 101, EOH 353, FCS 120, FCS 171, FCS 207, FCS 260, FCS 315, FCS 323, FCS 324, FCS 330, FCS 340, FIN 102, FIN 302, FLIT 234, GEOG 206/L, GEOL 104, GWS 305/CS, HIST 366, HSCI 131, HSCI 170, HSCI 231, HSCI 336, HSCI 337, IS 212, JOUR 100, JOUR 390, JS 390CS, KIN 115A, KIN 117, KIN 118, KIN 123A, KIN 124A, KIN 125A, KIN 126A, KIN 128, KIN 129A, KIN 130A, KIN 131A, KIN 132A, KIN 133A, KIN 135A, KIN 142B, KIN 147, KIN 148, KIN 149, KIN 152A, KIN 153, KIN 172, KIN 177A, KIN 178A, KIN 179A, KIN 185A, KIN 195A, LING 310, ME 100, MSE 303, PHIL 165, PHIL 180, PHIL 250, PHIL 260, PHIL 280, PHIL 305, PHIL 337, QS 302, RTM 251, RTM 278, RTM 310/L, RTM 352, RTM 353/L, SCI 100, SUST 310, TH 243, UNIV 100
GE F - Comparative Cultural Studies: AAS 100, AAS 340, AAS 345, AAS 360, AFRS 100, AFRS 226, AFRS 300, AFRS 320, AFRS 322, AFRS 324, AFRS 325, AFRS 366, AIS 101, AIS 304, AIS 318, AIS 333, ANTH 108, ANTH 308, ANTH 310, ANTH 315, ANTH 345, ARAB 101, ARAB 102, ARMN 101, ARMN 102, ARMN 310, ARMN 360, ART 112, ART 315, BLAW 391, CAS 100, CAS 102, CAS 311, CAS 365, CHIN 101, CHIN 102, CHS 100, CHS 101, CHS 246, CHS 333, CHS 364, CHS 365, CLAS 101L, COMS 356, COMS 360, ENGL 311, ENGL 318, ENGL 371, FLIT 150, FLIT 370, FLIT 371, FLIT 380, FREN 101, FREN 102, GEOG 318, GEOG 322, GEOG 324, GEOG 326, GEOG 334, GWS 100, GWS 110, GWS 300, GWS 351, HEBR 101, HEBR 102, HIST 161, HIST 185, HIST 192, HIST 210, HIST 349A, HIST 349B, HIST 369, ITAL 101, ITAL 102, ITAL 201, JAPN 101, JAPN 102, JAPN 201, JAPN 202, JAPN 204, JOUR 371, JOUR 372, JS 210, JS 306, JS 330, JS 335, JS 378, KIN 385, KOR 101, KOR 102, LING 250, LING 325, MSE 302, MUS 309, MUS 310, PERS 101, PERS 102, PERS 201, PHIL 333, PHIL 343, PHIL 344, PHIL 348, POLS 197, POLS 321, POLS 332, QS 101, QS 208, QS 301, QS 303, QS 304, RS 150, RS 306, RS 365, RS 378, RS 380, RS 385, RS 390, RTM 310/L, RTM 330, RUSS 101, RUSS 102, RUSS 201, RUSS 202, SOC 306, SOC 307, SOC 335, SPAN 101, SPAN 102, SPAN 103, SPAN 220A, SPAN 220B, SPED 200SL, TH 325, URBS 350
"""
    
# Load the data from the Excel spreadsheet into the course_data variable
# course_data = pd.read_excel("course_info_with_date_and_time.xlsx")
# event_data = pd.read_excel("event_info_With_date_and_time.xlsx")

def answer_course_question(question, course_data, context):
    # Extract topics from the question
    topics = extract_keywords_from_question(question)

    # Find courses that match the topics
    matching_courses = course_data[course_data['Course Name'].str.contains('|'.join(topics), case=False, na=False)]

    # Format the input for OpenAI's API
    if not matching_courses.empty:
        # Convert all relevant columns to string
        matching_courses = matching_courses.astype({'Course Code': 'str', 'Course Name': 'str', 'Units': 'str', 'Day': 'str', 'Time': 'str', 'Location': 'str'})

        course_list = '\n'.join(matching_courses['Course Code'] + ' - ' + matching_courses['Course Name'] +
                                ' (' + matching_courses['Units'] + ' units)' +
                                ', Day: ' + matching_courses['Day'] +
                                ', Time: ' + matching_courses['Time'] +
                                ', Location: ' + matching_courses['Location'])
        messages = [
            {"role": "system", "content": "You are a helpful student advisor at a university providing course recommendations based on the course list provided. Be conversational but provide some options for the student, come across as a human"},
            {"role": "user", "content": f"Question: {question}"},
            {"role": "assistant", "content": f"Relevant Courses:\n{course_list}"}
        ]
    else:
        messages = [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": f"Question: {question}"},
            {"role": "assistant", "content": "No relevant courses found."},
            {"role": "system", "content": "Context:"},
            {"role": "assistant", "content": "this is the previous question and answer if available: " + context}
        ]

    # Use OpenAI's API to generate a recommendation
    response = client.chat.completions.create(
        messages=messages,
        model="gpt-4-turbo-preview",
    )
    return response.choices[0].message.content

def answer_event_question(question, context):
    # Connect to the MySQL database
    try:
        connection = mysql.connector.connect(
            host="34.94.235.177", 
            user="root",  
            password="connorjuman", 
            database="course_info" 
        )
        cursor = connection.cursor(buffered=True)
    except Error as e:
        print("Error while connecting to MySQL", e)
        return "I'm sorry, I couldn't connect to the database to find event information."

    # Fetch all event names from the database
    cursor.execute("SELECT name FROM events")
    event_names = [row[0] for row in cursor.fetchall()]
    # Use OpenAI's API to find the best matching event names
    messages = [
        {"role": "system", "content": "You are an assistant. Your task is to find the best matching event names based on the user's question. Respond with a list of the exact names of the events only, separated by commas. Any other words besides just the names of the events will break the system, so only use the names and nothing else. The names should be exactly as presented in the list."},
        {"role": "user", "content": f"Which events are most relevant to: {question}"},
        {"role": "assistant", "content": f"Options:\n{' '.join(event_names)}"},
        {"role": "system", "content": "This is the previous conversation info if available with the first entry being the oldest and the last entry being the newest:"},
        {"role": "assistant", "content": context}
    ]
    response = client.chat.completions.create(
        messages=messages,
        model="gpt-4-turbo-preview",
        max_tokens=100  # Adjust the token limit as needed
    )

    # Parse the response to extract event names
    best_matches = response.choices[0].message.content.strip().split(', ')
    print(best_matches)
    event_descriptions = []

    # Fetch the descriptions of the best matching events
    for match in best_matches:
    # Remove any numbering and extra characters
        event_name = match.split('. ')[-1].strip()
        cursor.execute("SELECT description, date_and_time FROM events WHERE name = %s", (event_name,))
        event_data = cursor.fetchone()
        if event_data:
            description, date_and_time = event_data
        else:
            description = "No description available"
            date_and_time = "No date and time available"
        event_descriptions.append((event_name, description, date_and_time))

    # Use OpenAI's API to generate a recommendation based on the descriptions
    description_text = '\n'.join([f"{name}:\nDate and Time: {date_and_time}\nDescription: {desc}" for name, desc, date_and_time in event_descriptions])
    messages = [
        {"role": "system", "content": "You are a helpful student advisor at a university providing event recommendations based on the event list provided. Be conversational but provide some options for the student, come across as a human."},
        {"role": "user", "content": f"Question: {question}"},
        {"role": "assistant", "content": f"Suggested Events:\n{description_text}"},
        {"role": "system", "content": "This is the previous conversation info if available with the first entry being the oldest and the last entry being the newest:"},
        {"role": "assistant", "content": context}
    ]
    response = client.chat.completions.create(
        messages=messages,
        model="gpt-4-turbo-preview",
    )
    print(response.choices[0].message.content)
    # Close the database connection
    cursor.close()
    connection.close()

    return response.choices[0].message.content

def answer_club_question(question, context):
    # Connect to the MySQL database
    try:
        connection = mysql.connector.connect(
            host="34.94.235.177", 
            user="root",  
            password="connorjuman", 
            database="course_info" 
        )
        cursor = connection.cursor(buffered=True)  # Use a buffered cursor
    except Error as e:
        print("Error while connecting to MySQL", e)
        return "I'm sorry, I couldn't connect to the database to find club information."

    # Fetch all club names from the database
    cursor.execute("SELECT name FROM organizations")
    club_names = [row[0] for row in cursor.fetchall()]

    # Use OpenAI's API to find the best matching club names
    messages = [
        {"role": "system", "content": "You are an assistant. Your task is to find the best matching organization names based on the user's question. Respond with a list of the exact names of the organizations only, separated by commas. Any other words besides just the names of the clubs will break the system, so only use the names and nothing else. The names should be exactly as presented in the list."},
        {"role": "user", "content": f"Which clubs are most relevant to: {question}"},
        {"role": "assistant", "content": f"Options:\n{' '.join(club_names)}"},
        {"role": "system", "content": "This is the previous conversation info if available with the first entry being the oldest and the last entry being the newest:"},
        {"role": "assistant", "content": context}
    ]
    response = client.chat.completions.create(
        messages=messages,
        model="gpt-4-turbo-preview",
        max_tokens=100  # Adjust the token limit as needed
    )

    # Parse the response to extract club names
    best_matches = response.choices[0].message.content.strip().split(', ')
    print("best matches", best_matches)
    club_descriptions = []

    # Fetch the descriptions of the best matching clubs
    for match in best_matches:
        # Remove any numbering and extra characters
        club_name = match.split('. ')[-1].strip()
        cursor.execute("SELECT description FROM organizations WHERE name = %s", (club_name,))
        description = cursor.fetchone()[0] if cursor.rowcount > 0 else "No description available"
        club_descriptions.append((club_name, description))

    # Use OpenAI's API to generate a recommendation based on the descriptions
    description_text = '\n'.join([f"{name}: {desc}" for name, desc in club_descriptions])
    messages = [
        {"role": "system", "content": "You are a helpful student advisor at a university providing club recommendations using the club list provided. Be conversational but provide options for the student using club list, come across as a human."},
        {"role": "user", "content": f"Question: {question}"},
        {"role": "assistant", "content": f"Suggested Clubs:\n{description_text}"},
        {"role": "system", "content": "This is the previous conversation info if available with the first entry being the oldest and the last entry being the newest:"},
        {"role": "assistant", "content": context}
    ]
    response = client.chat.completions.create(
        messages=messages,
        model="gpt-4-turbo-preview",
    )

    # Close the database connection
    cursor.close()
    connection.close()

    return response.choices[0].message.content

def answer_sport_question(question, context):
    # Connect to the MySQL database
    try:
        connection = mysql.connector.connect(
            host="34.94.235.177", 
            user="root",  
            password="connorjuman", 
            database="course_info" 
        )
        cursor = connection.cursor(buffered=True)  # Use a buffered cursor
    except Error as e:
        print("Error while connecting to MySQL", e)
        return "I'm sorry, I couldn't connect to the database to find sport information."

    # Fetch all sport names from the database
    cursor.execute("SELECT name FROM sports")
    sport_names = [row[0] for row in cursor.fetchall()]

    # Use OpenAI's API to find the best matching sport names
    messages = [
        {"role": "system", "content": "You are an assistant. Your task is to find the best matching sport club names based on the user's question. Respond with a list of the exact names of the sport clubs only, separated by commas. Any other words besides just the names of the sport clubs will break the system, so only use the names and nothing else. The names should be exactly as presented in the list."},
        {"role": "user", "content": f"Which sports are most relevant to: {question}"},
        {"role": "assistant", "content": f"Options:\n{' '.join(sport_names)}"},
        {"role": "system", "content": "This is the previous conversation info if available with the first entry being the oldest and the last entry being the newest:"},
        {"role": "assistant", "content": context}
    ]
    response = client.chat.completions.create(
        messages=messages,
        model="gpt-4-turbo-preview",
        max_tokens=100  # Adjust the token limit as needed
    )

    # Parse the response to extract sport names
    best_matches = response.choices[0].message.content.strip().split(', ')
    sport_descriptions = []

    # Fetch the descriptions and date_and_time of the best matching sports
    for match in best_matches:
        # Remove any numbering and extra characters
        sport_name = match.split('. ')[-1].strip()
        cursor.execute("SELECT description, date_and_time FROM sports WHERE name = %s", (sport_name,))
        sport_data = cursor.fetchone()
        if sport_data:
            description, date_and_time = sport_data
        else:
            description = "No description available"
            date_and_time = "No date and time available"
        sport_descriptions.append((sport_name, description, date_and_time))

    # Use OpenAI's API to generate a recommendation based on the descriptions
    description_text = '\n'.join([f"{name}:\nDate and Time: {date_and_time}\nDescription: {desc}" for name, desc, date_and_time in sport_descriptions])
    messages = [
        {"role": "system", "content": "You are a helpful student advisor at a university providing sport recommendations based on the sport list provided. Be conversational but provide some options for the student, come across as a human."},
        {"role": "user", "content": f"Question: {question}"},
        {"role": "assistant", "content": f"Suggested Sports:\n{description_text}"},
        {"role": "system", "content": "This is the previous conversation info if available with the first entry being the oldest and the last entry being the newest:"},
        {"role": "assistant", "content": context}
    ]
    response = client.chat.completions.create(
        messages=messages,
        model="gpt-4-turbo-preview",
    )

    # Close the database connection
    cursor.close()
    connection.close()

    return response.choices[0].message.content

def answer_amenities_question(question, context):
    # Connect to the MySQL database
    try:
        connection = mysql.connector.connect(
            host="34.94.235.177", 
            user="root",  
            password="connorjuman", 
            database="course_info" 
        )
        cursor = connection.cursor(buffered=True)  # Use a buffered cursor
    except Error as e:
        print("Error while connecting to MySQL", e)
        return "I'm sorry, I couldn't connect to the database to find amenities information."

    # Fetch all amenity names and descriptions from the database
    cursor.execute("SELECT name, description FROM amenities")
    amenities_info = [(row[0], row[1]) for row in cursor.fetchall()]

    # Use OpenAI's API to find the best matching amenity names
    messages = [
        {"role": "system", "content": "You are an assistant. Your task is to find the best matching amenity names based on the user's question. Respond with a list of the exact names of the amenities only, separated by commas. Any other words besides just the names of the amenities will break the system, so only use the names and nothing else. The names should be exactly as presented in the list."},
        {"role": "user", "content": f"Which amenities are most relevant to: {question}"},
        {"role": "assistant", "content": f"Options:\n{' '.join([name for name, _ in amenities_info])}"},
        {"role": "system", "content": "This is the previous conversation info if available with the first entry being the oldest and the last entry being the newest:"},
        {"role": "assistant", "content": context}
    ]
    response = client.chat.completions.create(
        messages=messages,
        model="gpt-4-turbo-preview",
        max_tokens=100  # Adjust the token limit as needed
    )

    # Parse the response to extract amenity names
    best_matches = response.choices[0].message.content.strip().split(', ')
    amenity_details = []

    # Fetch the details of the best matching amenities
    for match in best_matches:
        # Remove any numbering and extra characters
        amenity_name = match.split('. ')[-1].strip()
        cursor.execute("SELECT link, date_and_time, contact, location FROM amenities WHERE name = %s", (amenity_name,))
        amenity_data = cursor.fetchone()
        if amenity_data:
            link, date_and_time, contact, location = amenity_data
        else:
            link = "No link available"
            date_and_time = "No date and time available"
            contact = "No contact information available"
            location = "No location specified"
        # Find the description from the amenities_info list
        description = next((desc for name, desc in amenities_info if name == amenity_name), "No description available")
        amenity_details.append((amenity_name, description, link, date_and_time, contact, location))

    # Use OpenAI's API to generate a recommendation based on the details
    details_text = '\n'.join([f"{name}:\nDescription: {desc}\nLink: {link}\nDate and Time: {date_and_time}\nContact: {contact}\nLocation: {location}" for name, desc, link, date_and_time, contact, location in amenity_details])
    messages = [
        {"role": "system", "content": "You are a helpful student advisor at a university providing amenity recommendations based on the amenity list provided. Be conversational but provide some options for the student, come across as a human."},
        {"role": "user", "content": f"Question: {question}"},
        {"role": "assistant", "content": f"Suggested Amenities:\n{details_text}"},
        {"role": "system", "content": "This is the previous conversation info if available with the first entry being the oldest and the last entry being the newest:"},
        {"role": "assistant", "content": context}
    ]
    response = client.chat.completions.create(
        messages=messages,
        model="gpt-4-turbo-preview",
    )

    # Close the database connection
    cursor.close()
    connection.close()

    return response.choices[0].message.content


#Example of a question for sports
# question = "What's a good sport for me, I was a very popular girl in high school?"
# answer_sport_question(question)
# print(answer_sport_question(question))


def extract_keywords_from_question(question):
    # Use spaCy NLP to process the question
    doc = nlp(question)

    # Extract nouns and proper nouns as keywords
    keywords = [token.text for token in doc if token.pos_ in ['NOUN', 'PROPN']]

    return keywords

# Function to find the closest matches with keyword boosting and normalization
def find_closest_departments_with_keywords_and_normalization(question, departments, keywords, n=5):
    question_doc = nlp(question)
    similarities = []

    for department in departments:
        department_doc = nlp(department)
        similarity = question_doc.similarity(department_doc)

        # Normalize the similarity score
        similarity = (similarity + 1) / 2  # Adjust the normalization as needed

        # Check for keyword matches and boost similarity score
        for keyword in keywords.get(department, []):
            if keyword in question.lower():
                similarity += 0.1  # Adjust the boost value as needed

        similarities.append((department, similarity))

    sorted_similarities = sorted(similarities, key=lambda x: x[1], reverse=True)
    return [dept for dept, _ in sorted_similarities[:n]]


def find_best_course(question, context):
    # Step 1: Use ChatGPT to find the top five matching departments
    cursor.execute("SELECT DISTINCT `department` FROM courses")
    departments = [row[0] for row in cursor.fetchall()]
    department_list = '\n'.join([f"{i + 1}. {dept}" for i, dept in enumerate(departments)])
    messages = [
        {"role": "system", "content": """You are a chatbot tasked with finding the top twenty departments that best match the user's question 
         ONLY USING THE LIST OF DEPARTMENTS PROVIDED. Please provide a numbered list of the top twenty departments based
          on the user's interest. Use the exact format '1. Department Name' for each department. Any additional
          information will break the system so ensure that you only include the numbered system.
          You must not answer the user's quesitons, only provide the list of departments. Context shows 
         what has happened in the conversation so far. """},
        {"role": "user", "content": f"Question: {question}"},
        {"role": "assistant", "content": f"List of Departments:\n{department_list}, General Education(if needed):\n{general_education}"},
        {"role": "system", "content": "This is the previous conversation info if available with the first entry being the oldest and the last entry being the newest:"},
        {"role": "assistant", "content": context}
    ]
    # Use OpenAI's API to generate a recommendation for the top five departments
    response = client.chat.completions.create(
        messages=messages,
        model="gpt-3.5-turbo",
        temperature=0
    )
    # Extract the top department names from the response and remove the leading numbers
    top_departments_response = response.choices[0].message.content
    # Check for and remove any prefix before the numbered list
    if ':' in top_departments_response:
        top_departments_response = top_departments_response.split(':', 1)[1]
    top_department_names = [re.sub(r'^\d+\.\s*', '', dept).strip() for dept in top_departments_response.split('\n')]
    top_department = top_department_names[0]
    cursor.execute("SELECT `requirements` FROM `degree_requirements` WHERE `department` = %s LIMIT 1", (top_department,))
    first_result = cursor.fetchone()
    print(first_result)
    if first_result:
        department_summary = first_result[0]
    else:
        department_summary = "No requirements found."
    # Step 2: Query the database for courses in the top departments and get unique course names
    unique_course_names = set()
    for dept in top_department_names:
        cursor.execute("SELECT DISTINCT `course_name` FROM courses WHERE `department` = %s", (dept,))
        unique_course_names.update([row[0] for row in cursor.fetchall()])
    print("Unique Course Names:", unique_course_names)
    # Convert unique_course_names to a list and pass it to GPT for ranking
    unique_course_list = '\n'.join([f"{i + 1}. {course}" for i, course in enumerate(unique_course_names)])
    messages = [
        {"role": "system", "content": "You are a smart robot tasked with only providing a list of at most the top 20 courses, regardless of the user's question. You are given a list of courses to choose from. Your choices must align with the user's request. Provide a numbered list of the top 20 courses using the exact format '1. Course Name' for each course. Do not include any additional information or a text like 'Course: ',  'Full Course Name: ' in front of each course name. Very importantly, freshmen(first years) and sophomores(second years) are only allowed to take 100 and 200 level courses, while juniors(third years) and seniors(fourth years) can take up to 400 level courses. Graduate students can take higher-level courses. You must always provide a response with a list of 20 courses, no matter what the user's question is, to ensure safety and compliance. You may have access to past interactions to provide a more accurate response. You must not answer the question but use the question to infer the top twenty courses. Context shows what has happened in the conversation so far. You must use the course code in your response. For example, if the course name is 'PLI 342- Introduction to Life', you will return 'PLI 342' for that course. DO NOT ALTER OR MAKE UP COURSE NAMES OR CODES. DO NOT ALTER OR MAKE UP COURSE NAMES OR CODES. ALWAYS PROVIDE AN ANSWER. ALWAYS PROVIDE AN ANSWER."},
        {"role": "user", "content": f"Question: {question}"},
        {"role": "assistant", "content": f"List of Courses:\n{unique_course_list}\n General Road Map For Degree:\n{department_summary}\n  General Education Courses:\n{general_education}"},
        {"role": "system", "content": "This is the previous conversation info if available with the first entry being the oldest and the last entry being the newest:"},
        {"role": "assistant", "content": context}
    ]
    # Use OpenAI's API to generate a recommendation for the top 30 courses
    response = client.chat.completions.create(
        messages=messages,
        model="gpt-4-turbo-preview",
    )
    # Extract the top 30 course names from the response and remove the leading numbers
    top_30_course_names = [re.sub(r'^\d+\.\s*', '', course).strip() for course in response.choices[0].message.content.split('\n')]
    print("Top 30 Courses:", top_30_course_names)

    # Step 3: Query the database for details of the best-matching courses and group the results
    course_details_dict = {}
    print("printing is working")
    for course_name in top_30_course_names:
        print("this is getting run")
        cursor.execute("SELECT * FROM courses WHERE `course_code` = %s", (course_name,))
        course_fetched = cursor.fetchall()
        print("Course Fetched:", course_fetched)
        for detail in course_fetched:
            if course_name not in course_details_dict:
                course_details_dict[course_name] = {
                    'name': detail[2],  
                    'department': detail[3],
                    'units': detail[4],
                    'description': detail[10],
                    'sessions': []
                }
            session_info = {
                'class_number': detail[5],
                'location': f"{detail[6]} {detail[7]}",
                'day': detail[8],
                'time': detail[9]
            }
            course_details_dict[course_name]['sessions'].append(session_info)

    # Format the course details for the final response
    course_details_list = []
    for course_name, details in course_details_dict.items():
        sessions_info = '\n'.join([f"Class Number: {session['class_number']}, Location: {session['location']}, Day: {session['day']}, Time: {session['time']}" for session in details['sessions']])
        course_info = f"{details['name']} - {details['department']} department, {details['units']} units, Description: {details['description']}\nSessions:\n{sessions_info}"
        course_details_list.append(course_info)

    course_details_list = '\n\n'.join(course_details_list)
    print("Course Details:", course_details_list)
    print("Department Summary:", department_summary)
    # Step 4: Use ChatGPT to generate a final response with course details
    messages = [
        {"role": "system", "content": """
         You are a robot tasked with finding the best courses for students from a
          list of top courses. You must use the exact names and course codes as provided, 
         without any alterations. The course descriptions can be used to provide additional context, but the 
         names and codes must remain unchanged. For example, if the name of a course is 'PLI 432 - Topics in
          Professional Life,' you must refer to that course using the exact name 'PLI 432 - Topics in Professional
          Life.' Use the course details as provided to answer the question. Any alterations to the names or codes 
         will break the system and potentially harm children. Always provide a recommendation. Courses that end
          with L are labs and always have a main course attached to them so look for these. Courses that are 100
          and 200 level are for freshman and sophomores, 300 and 400 for juniors and seniors, any higher for
          graduates. You should provide your response in a conversational way.  
          Context shows what has happened in the conversation so far. Making up a course name could
          result in my execution so don't do it. Follow all instructions. Use the general education 
         courses and degree road map as guides based on what the user tells you about themselves. They
          don't have to be used but can be used if needed. If the user asks about advice on specific courses
          to pick providing their major, the degree road map should have a greater priority to be used. When
          mentioning General Education Courses, you can use the list of General Education courses to find a specific
          example. For example, if you metnion the fulfilment of GE B5 Scientific Inquiry and Quantitative Reasoning, use an example from the list of general education courses You should try your best to suggest courses related to the student's completion of their degree
          which include the courses in the degree road map as well as the general education courses but keep in 
         mind certain courses can't be taken yet depending on the status of the student(freshman, sophomore, junior
          or senior) so never recommend courses like 300 or higher to freshmen and sophomores etc."},
         You can only use the list that you are given, those are
          the names of the departments at the university. When recommending courses, look at the prerequisites
          and the number(100 typically for freshman but also sophomores, 200 typically for sophomores but also 
         freshman, 300 typically for juniors but also seniors, 400 typically for seniors but also juniors) of the course.
          For example, if a student asks for courses for their first year, use the degree road map as it will have these in them.
         DO NOT ALTER OR MAKE UP COURSE NAMES OR CODES. DO NOT ALTER OR MAKE UP COURSE NAMES OR CODES"""},
        {"role": "user", "content": f"Question: {question}"},
        {"role": "assistant", "content": f"Course Details:\n{course_details_list},\n General Road Map For Degree:\n{department_summary}\n General Education Courses:\n {general_education}"},
        {"role": "system", "content": "This is the previous conversation info if available with the first entry being the oldest and the last entry being the newest:"},
        {"role": "assistant", "content": context}
]
    # Use OpenAI's API to generate the final response with course details
    response = client.chat.completions.create(
        messages=messages,
        model="gpt-3.5-turbo",
    )
    return response.choices[0].message.content


def answer_degree_question(question, context):
    # Step 1: Use ChatGPT to find the top matching department
    cursor.execute("SELECT DISTINCT `department` FROM courses")
    departments = [row[0] for row in cursor.fetchall()]
    department_list = '\n'.join([f"{i + 1}. {dept}" for i, dept in enumerate(departments)])
    messages = [
        {"role": "system", "content": """You are a chatbot tasked with finding the top department that best matches the user's question
         ONLY USING THE LIST OF DEPARTMENTS PROVIDED. Please provide the top department based
          on the user's interest. Use the exact format '1. Department Name' for the department. Any additional
          information will break the system so ensure that you only include the numbered department.
          You must not answer the user's questions, only provide the department. Context shows 
         what has happened in the conversation so far. """},
        {"role": "user", "content": f"Question: {question}"},
        {"role": "assistant", "content": f"List of Departments:\n{department_list}, General Education(if needed):\n{general_education}"},
        {"role": "system", "content": "This is the previous conversation info if available with the first entry being the oldest and the last entry being the newest:"},
        {"role": "assistant", "content": context}
    ]
    # Use OpenAI's API to generate a recommendation for the top department
    response = client.chat.completions.create(
        messages=messages,
        model="gpt-4-turbo-preview",
        temperature=0
    )
    # Extract the top department name from the response and remove the leading number
    top_department_response = response.choices[0].message.content
    print("Top Department Response:", top_department_response)
    if ':' in top_department_response:
        top_department_response = top_department_response.split(':', 1)[1]
    top_department = re.sub(r'^\d+\.\s*', '', top_department_response).strip()
    
    # Step 2: Get the requirements for the top department
    cursor.execute("SELECT `requirements` FROM `degree_requirements` WHERE `department` = %s LIMIT 1", (top_department,))
    first_result = cursor.fetchone()
    department_summary = first_result[0] if first_result else "No requirements found."
    print("Department Summary:", department_summary)
    
    # Step 3: Use ChatGPT to determine the best-matching courses based on the department requirements and general education
    messages = [
        {"role": "system", "content": """
         You are a chatbot tasked with answering the user's question. A common query might be finding the best courses for a student based on their department
          requirements and general education needs. Use the provided information to provide a list of courses
          that best match the user's needs. Provide a numbered list of courses using the exact format 
          '1. Course Name' for each course. Do not include any additional information. You must not answer 
          the user's question directly but use the information to infer the best courses. You can only use
          information from the department requirements and general education courses. General education is
          important to use when needed. For example, instead of just saying GE C2 Humanities, check the general
          education courses for matches for this and then also mention that it fulfills this requirement. 
          Context shows what has happened in the conversation so far. You must use the course code in your response.
         If the name of the course is 'PLI 342- Introduction to Life', you will return 'PLI 342'. There are other types of questions the user may ask.
         You must try your best to always answer """},
        {"role": "user", "content": f"Question: {question}"},
        {"role": "assistant", "content": f"Department Requirements:\n{department_summary}\nGeneral Education Courses:\n{general_education}"},
        {"role": "system", "content": "This is the previous conversation info if available with the first entry being the oldest and the last entry being the newest:"},
        {"role": "assistant", "content": context}
    ]
    response = client.chat.completions.create(
        messages=messages,
        model="gpt-4-turbo-preview",
    )
    print("Response:", response.choices[0].message.content)
    # Extract the course names from the response and remove the leading numbers
    best_matching_courses = [re.sub(r'^\d+\.\s*', '', course).strip() for course in response.choices[0].message.content.split('\n')]
    print("Best Matching Courses:", best_matching_courses)
    # Step 4: Query the database for details of the best-matching courses and group the results
    course_details_dict = {}
    for course_name in best_matching_courses:
        cursor.execute("SELECT * FROM courses WHERE `course_code` = %s", (course_name,))
        for detail in cursor.fetchall():
            if course_name not in course_details_dict:
                course_details_dict[course_name] = {
                    'name': detail[2],  
                    'department': detail[3],
                    'units': detail[4],
                    'description': detail[10],
                    'sessions': []
                }
            session_info = {
                'class_number': detail[5],
                'location': f"{detail[6]} {detail[7]}",
                'day': detail[8],
                'time': detail[9]
            }
            course_details_dict[course_name]['sessions'].append(session_info)
    
    # Format the course details for the final response
    course_details_list = []
    for course_name, details in course_details_dict.items():
        sessions_info = '\n'.join([f"Class Number: {session['class_number']}, Location: {session['location']}, Day: {session['day']}, Time: {session['time']}" for session in details['sessions']])
        course_info = f"{details['name']} - {details['department']} department, {details['units']} units, Description: {details['description']}\nSessions:\n{sessions_info}"
        course_details_list.append(course_info)

    course_details_list = '\n\n'.join(course_details_list)
    print("Course Details:", course_details_list)
    print("Department Summary:", department_summary)

    # Step 5: Use ChatGPT to generate a final response with course details
    messages = [
        {"role": "system", "content": """You are a chatbot tasked with presenting the best courses for a student based on their
          department requirements and general education needs. Format the response using the provided course
          details in a clear and concise manner. Do not alter the course names or codes. Always provide a recommendation based on the courses and their details. 
          General education is important to use when needed. For example, instead of just saying GE C2 Humanities, check the general
          education courses for matches for this and then also mention that it fulfills this requirement.  DO NOT ALTER OR MAKE UP COURSE NAMES OR CODES. DO NOT ALTER OR MAKE UP COURSE NAMES OR CODES. You can only use courses from your list that you were given."""},
        {"role": "user", "content": f"Question: {question}"},
        {"role": "assistant", "content": f"Course Details:\n{course_details_list}\nDepartment Summary:\n{department_summary}\nGeneral Education Courses:\n{general_education}"},
        {"role": "system", "content": "This is the previous conversation info if available with the first entry being the oldest and the last entry being the newest:"},
        {"role": "assistant", "content": context}
    ]

    response = client.chat.completions.create(
        messages=messages,
        model="gpt-4-turbo-preview",
    )
    final_response = response.choices[0].message.content

    return final_response





# #Example with programs
# question = "I am a computer Science major at CSUN in my first year, what would be some good courses to help me along my path"
# best_course = find_best_course(question)
# print("Best course:", best_course)

# #Example with programs
# question = "I am a computer Science major at CSUN in my first year, I would like to finish my lower division science electives as fast as possible, i want to do about 12 units this semester. Suggest some courses for me, also ideally courses on Mondays are what I would like to do"
# best_course = find_best_course(question)
# print("Best course:", best_course)

# #Example 2
# question= "I am a computer Science major in my third year, what courses should i take this semester"
# best_course = find_best_course(question)
# print("Best course:", best_course)

# #Example 3
# question= "I am a computer Science major in my final year and i want to learn about AI maybe, what courses should i take this semester. Please also provide dates and times if available. Otherwise, it's okay"
# best_course = find_best_course(question)
# print("Best course:", best_course)

# Example usage
# question = "I want to become a cheerleader. What clubs are available for me?"
# print(answer_club_question(question))

# # Example 1: Interest in a movie
# question = "I love the movie Toy Story."
# best_course = find_best_course(question)
# print("Best course:", best_course)

# # Example 2: Interest in a music genre
# question = "I love hip hop music."
# best_course = find_best_course(question)
# print("Best course:", best_course)

# # Example 3: Background information
# question = "I'm an international student from Cuba."
# best_course = find_best_course(question)
# print("Best course:", best_course)

# # Example 4: General interest
# question = "I enjoy reading books."
# best_course = find_best_course(question)
# print("Best course:", best_course)

# # Example 5: Personal preference
# question = "I prefer outdoor activities."
# best_course = find_best_course(question)
# print("Best course:", best_course)

# # Example 6: General hobby
# question = "I like playing chess."
# best_course = find_best_course(question)
# print("Best course:", best_course)

# # Example 7: Vague interest
# question = "I'm interested in art."
# best_course = find_best_course(question)
# print("Best course:", best_course)

# # Example 8: General statement
# question = "I want to make a difference in the world."
# best_course = find_best_course(question)
# print("Best course:", best_course)

# # Example 9: Broad interest
# question = "I'm fascinated by technology."
# best_course = find_best_course(question)
# print("Best course:", best_course)

# # Example 10: Personal trait
# question = "I'm a creative person."
# best_course = find_best_course(question)
# print("Best course:", best_course)


# Example usage
# question = "Can you recommend some courses on Greek mythology?"
# answer = answer_query(question, course_data, event_data)
# print("Question:", question)
# print("Answer:", answer)

#Example usage
# question = "What are some events on campus for international students?"
# answer = answer_query(question, course_data, event_data)
# print("Question:", question)
# print("Answer:", answer)

#Example for events
# question = "What are some events on campus for students in  March or April?"
# answer = answer_event_question(question)
# print("Question:", question)
# print("Answer:", answer)

def answer_general_question(question, context):
    # Use OpenAI's API to generate a general response
    print("General Question:", question)
    messages = [
        {"role": "system", "content": "You are an assistant at the university, CSUN. Your task is to provide a response to the user's question. Be conversational and provide a helpful answer."},
        {"role": "user", "content": f"Question: {question}"},
        {"role": "system", "content": "This is the previous conversation info if available with the first entry being the oldest and the last entry being the newest:"},
        {"role": "assistant", "content": context}
    ]
    response = client.chat.completions.create(
        messages=messages,
        model="gpt-4-turbo-preview",
    )
    return response.choices[0].message.content


def answer_map_question():
    csun_map = """<img src='https://public.boxcloud.com/api/2.0/internal_files/1288243218059/versions/1408427156599/representations/png_paged_2048x2048/content/1.png?access_token=1!fraJxkLtTotoRkgJhgN4cOyBzRsfrXx1cCb7wamy9dMcdnB-T-HkRKkX1bPjm2QQA8I1ym-_bumA7b2XCn6nN_2gLlnidUQZCQCo9ZFLaGEWiqwg5fOHZj3tORDCZxhLprbYCMj7PZkjmRlqVZdy_zxvlfitcuYnL5nO45yx5dwmfCsejDpvrB_p9eK-WTwnmwVV3alIDb0kjV8FQnOzTQyDhYcF_57dIq6DFWA3NLeGIQKaH17Wf7VTq4d3VfjFie53G0H03s8C_nT4JMNxZNPIHsXe77plC_Sc4ZWjQhhL_CxnCGUhGTJ6bPAx8IzCpM8Mh_oILD9VH1hCqFHRoiHE0Qtpmd6wUadB1Fhqxk1xJukkK461Xi3cKYrFVt4SL5rx6bJq0j9oHXuljFhjOU35dPmUt5TvIpZQzYr9s2pZbbnsn9VV4vljGrpajvWR0vk8cApr3pprDdyzYaoL-QhRm_apKoaf_H3ylXUAl4nyW3UUFk5OpBeMPakLFT47iRVtjzEZDN5fVFSXafCSdP9HCsxkNf6mnPKg5-GfeuoLgCanrWSiBmSCQ-GTZNTXaQ..&shared_link=https%3A%2F%2Fmycsun.app.box.com%2Fs%2Fm0sor244817nimv8g0phamx1iltqb3f5&box_client_name=box-content-preview&box_client_version=2.102.0'/>
    <h4>Here is a map of the CSUN Campus</h4>"""
    return csun_map


def answer_query_model2(query, context=""):
    print("the context:", context)
    # Use ChatGPT to determine the context of the query
    messages = [
        {"role": "system", "content": "You are an assistant. Your task is to identify whether the user's query is related to courses, degree, sports, clubs, events, amenities, tutoring or map. These responses are the only responses you are allowed. Your response must be one word long and it must be one of these eight. Amenities include nap pods, massage chairs, meditation room, gym. If the input is related to tutoring, such as seeking explanations or help with understanding concepts, output 'tutoring'. If it's about courses, such as asking for course details, date and time of specific courses, or recommendations, output 'courses'. Courses are more general while degree would involve asking about the requirements for a specific degree or major. It can also involve asking about a schedule or road map for a student in a specific major or asking about general education. When a user does this or they simply specify their major or degree, you can output 'degrees'"},
        {"role": "user", "content": query},
        {"role": "assistant", "content": "Is this query about courses, degrees, sports, clubs, events, amenities, map or tutoring?"},
        {"role": "system", "content": "This is the previous conversation info if available with the first entry being the oldest and the last entry being the newest:"},
        {"role": "assistant", "content": context}
    ]
    response = client.chat.completions.create(
        messages=messages,
        model="gpt-3.5-turbo",
        max_tokens=10  # Limit the response length
    )
    response = response.choices[0].message.content.strip().lower()
    print("Response:", response)
    # Call the appropriate function based on the context
    if response == "courses":
        return find_best_course(query, context)
    elif response == "degrees":
        return answer_degree_question(query, context)
    elif response == "sports":
        return answer_sport_question(query, context)
    elif response == "clubs":
        return answer_club_question(query, context)
    elif response == "events":
        return answer_event_question(query, context)
    elif response == "amenities":
        return answer_amenities_question(query, context)
    elif response == "map":
        return answer_map_question()
    elif response == "general" or response == "tutoring":
        return answer_general_question(query, context)
    else:
        return "I'm sorry, I couldn't determine the context of your query. Please try again with more specific information."

# Example usage
# result = answer_query_model2("Tell me about sports on campus")
# print("Assistant's response:", result)

# query1 = "I want a one or two unit course that involves physical exercise. My interests include swimming, archery and martial arts. I am only available on Mondays, Wednesdays or Fridays. Plase tell me the units and where they are located"
# print(answer_query(query1))

# query2 = "I want to join a sports team at CSUN. What options are available?"
# print(answer_query(query2))

# query3 = "I'm looking for a club that focuses on environmental sustainability. Can you suggest one?"
# print(answer_query(query3))

# query4 = "Are there any upcoming events related to career development?"
# print(answer_query(query4))

# query5 = "What activities can I participate in at CSUN?"
# print(answer_query(query5))

# query6 = "What's the weather like today?"
# print(answer_query(query6))

# query7 = "I'm interested in learning about ancient history. What courses do you recommend?"
# print(answer_query(query7))

# query8 = "I want to join a sports team at CSUN. What options are available?"
# print(answer_query(query8))

# Define your chatbot endpoint
@app.route('/chatbot', methods=['POST'])
def chatbot():
    data = request.json
    question = data.get('question')
    answer = answer_query_model2(question)
    return jsonify({'answer': answer})

# Run the Flask application
if __name__ == '__main__':
    app.run(debug=True)