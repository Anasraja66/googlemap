import streamlit as st
import pandas as pd
import time
import requests
import urllib.parse
import re

# Set page config for a better UI
st.set_page_config(page_title="Anas Technology Lead Gen Tool", page_icon="🏢", layout="wide")

def extract_email_from_website(url):
    if not url or url == "Not Found":
        return "No Website"
    
    try:
        # Act like a normal browser to avoid blocks
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
        # Use timeout to prevent the script from hanging on slow websites
        response = requests.get(url, headers=headers, timeout=5)
        
        # Regex to find standard email patterns
        emails = re.findall(r'[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}', response.text)
        
        # Remove duplicates and false positives (e.g., image filenames that look like emails)
        valid_emails = list(set([e for e in emails if not e.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.webp', 'sentry.io'))]))
        
        if valid_emails:
            # Prioritize 'info@', 'contact@', or 'hello@' emails if they exist
            priority_emails = [e for e in valid_emails if e.lower().startswith(('info@', 'contact@', 'hello@', 'admin@', 'sales@'))]
            if priority_emails:
                return priority_emails[0]
            return valid_emails[0]
            
    except Exception:
        return "Could Not Read Website"
        
    return "Not Found on Website"

def generate_whatsapp_link(phone):
    if phone == "Not Found" or not phone:
        return "No Number"
    
    # Clean phone: remove spaces, hyphens, brackets
    clean_phone = re.sub(r'[^\d+]', '', phone)
    
    # Check if it's a UK Mobile Number (Starts with 07 or +447)
    if clean_phone.startswith('07'):
        wa_number = '44' + clean_phone[1:]
        return f"https://wa.me/{wa_number}"
    elif clean_phone.startswith('+447'):
        wa_number = clean_phone.replace('+', '')
        return f"https://wa.me/{wa_number}"
    elif clean_phone.startswith('447'):
        return f"https://wa.me/{clean_phone}"
    else:
        # It's a landline (01, 02, 03, 08 etc.)
        return "Landline (Call Only)"

# Fetch API KEY securely from Streamlit Secrets
try:
    GOOGLE_API_KEY = st.secrets["GOOGLE_API_KEY"]
except FileNotFoundError:
    st.error("Secrets file not found. Please setup .streamlit/secrets.toml locally.")
    st.stop()
except KeyError:
    st.error("API Key not found! Please set GOOGLE_API_KEY in Streamlit Secrets.")
    st.stop()

# Lists for Dropdowns
INDUSTRIES = [
    # A
    "Accounting Firms", "Acupuncture Clinics", "Advertising Agencies", "Air Conditioning Services", 
    "Alternative Medicine Clinics", "Antique Stores", "Apparel Stores", "Appliance Repair Services", 
    "Architectural Firms", "Art Galleries", "Attorneys", "Auto Body Shops", "Auto Dealerships", 
    "Auto Repair Shops", "Aviation Services",
    # B
    "Bakeries", "Banks", "Barbershops", "Bars", "Beauty Salons", "Bed and Breakfasts", 
    "Bookkeeping Services", "Bookstores", "Boutique Clothing", "Breweries", "Builders", 
    "Business Consultants", "Butcher Shops",
    # C
    "Cafes", "Car Detailing Services", "Car Rental Agencies", "Car Wash", "Cardiology Clinics", 
    "Carpentry Services", "Catering Services", "Charter Flights", "Childcare Centers", 
    "Chiropractic Clinics", "Cleaning Services", "Clothing Stores", "Coffee Shops", 
    "Commercial Real Estate", "Computer Repair Services", "Construction Companies", 
    "Consulting Firms", "Contractors", "Convenience Stores", "Cosmetic Surgery Clinics", 
    "Courier Services", "Credit Unions",
    # D
    "Dance Studios", "Day Care Centers", "Decorating Services", "Dental Clinics", 
    "Dermatology Clinics", "Design Agencies", "Double Glazing Installers", "Driving Schools", 
    "Dry Cleaners",
    # E
    "E-Learning Companies", "Electrical Contractors", "Electronics Stores", "Energy Companies", 
    "Engineering Firms", "Event Management Companies", "Event Venues", "Eye Care Clinics",
    # F
    "Farming", "Fencing Services", "Financial Advisors", "Fine Dining", "Fitness Centers", 
    "Florists", "Food Packaging Companies", "Food Processing Companies", "Freight Forwarding", 
    "Furniture Stores",
    # G
    "Gardening Centers", "Gas Stations", "Graphic Design Studios", "Grocery Stores", 
    "Guttering Services", "Gyms",
    # H
    "Hair Salons", "Hardware Stores", "Health Food Stores", "Heating Contractors", 
    "Home Inspectors", "Hospitals", "Hotels", "HVAC Services",
    # I
    "Insurance Agencies", "Insurance Brokers", "Interior Designers", "Investment Firms", 
    "IT Support Companies",
    # J
    "Janitorial Services", "Jewelry Stores",
    # K
    "Kennels", "Kitchen Fitting Services",
    # L
    "Landscaping Services", "Laundromats", "Law Firms", "Lighting Stores", "Locksmiths", 
    "Logistics Companies",
    # M
    "Manufacturing Companies", "Maritime Companies", "Marketing Agencies", "Massage Therapy", 
    "Mechanics", "Medical Supply Stores", "Mental Health Therapists", "Mortgage Brokers", 
    "Moving Companies", "MSPs", "Music Schools",
    # N
    "Nail Salons", "Non-Profit Organizations", "Nurseries", "Nursing Homes",
    # O
    "Oil and Gas Companies", "Optometrists", "Orthodontists",
    # P
    "Packaging Companies", "Painting Contractors", "Paving Contractors", "Pest Control Services", 
    "Pet Grooming", "Pet Shops", "Pharmacies", "Photography Studios", "Physiotherapy Clinics", 
    "Pilates Studios", "Plumbing Services", "PR Agencies", "Printing Companies", 
    "Private Medical Clinics", "Private Tutors", "Production Facilities", "Property Management Companies", 
    "Pubs",
    # Q & R
    "Real Estate Agencies", "Recruitment Agencies", "Restaurants", "Roofing Contractors",
    # S
    "Security Services", "Shipping Companies", "Shoe Stores", "Skip Hire", "Software Companies", 
    "Solar Panel Installers", "Solicitors", "Spas", "Sporting Goods Stores", "Staffing Agencies", 
    "Storage Facilities", "Supermarkets", "Surveyors",
    # T
    "Tailors", "Tattoo Parlors", "Taxi Services", "Telecommunications Companies", "Towing Services", 
    "Travel Agencies", "Tree Services",
    # U & V
    "Upholstery Services", "Veterinary Clinics", "Videography Services",
    # W
    "Warehousing Facilities", "Waste Removal Services", "Web Design Agencies", "Wedding Planners", 
    "Wedding Venues", "Window Installers",
    # X, Y, Z
    "Yoga Studios"
]

UK_CITIES = [
    "All UK (Entire Country)",
    "Aberdeen", "Armagh", "Bangor", "Bath", "Belfast", "Birmingham", "Bradford", 
    "Brighton & Hove", "Bristol", "Cambridge", "Canterbury", "Cardiff", "Carlisle", 
    "Chelmsford", "Chester", "Chichester", "Colchester", "Coventry", "Derby", "Derry", 
    "Doncaster", "Dundee", "Dunfermline", "Durham", "Edinburgh", "Ely", "Exeter", 
    "Glasgow", "Gloucester", "Hereford", "Inverness", "Kingston upon Hull", "Lancaster", 
    "Leeds", "Leicester", "Lichfield", "Lincoln", "Lisburn", "Liverpool", "London", 
    "Manchester", "Milton Keynes", "Newcastle upon Tyne", "Newport", "Newry", "Norwich", 
    "Nottingham", "Oxford", "Perth", "Peterborough", "Plymouth", "Portsmouth", "Preston", 
    "Ripon", "Salford", "Salisbury", "Sheffield", "Southampton", "Southend-on-Sea", 
    "St Albans", "St Asaph", "St Davids", "Stirling", "Stoke-on-Trent", "Sunderland", 
    "Swansea", "Truro", "Wakefield", "Wells", "Westminster", "Winchester", "Wolverhampton", 
    "Worcester", "Wrexham", "York",
    "Reading", "Luton", "Bolton", "Bournemouth", "Middlesbrough", "Teesside", 
    "Swindon", "Slough", "Blackpool", "Dudley", "Walsall", "Telford", "Warrington", 
    "Rotherham", "Stockport", "Oldham", "Blackburn", "Poole",
    "High Wycombe", "Basingstoke", "Cheltenham", "Crawley", "Eastbourne", "Farnborough", 
    "Gillingham", "Halifax", "Harrogate", "Hastings", "Huddersfield", "Ipswich", 
    "Keighley", "Kettering", "Kidderminster", "Mansfield", "Northampton", "Nuneaton", 
    "Rochdale", "Rugby", "Scunthorpe", "Shrewsbury", "Southport", "Stafford",
    "Stockton-on-Tees", "Stourbridge", "Sutton Coldfield", "Tamworth", "Taunton", 
    "Torbay", "Wallasey", "Watford", "West Bromwich", "Weston-super-Mare", "Weymouth", 
    "Wigan", "Woking", "Worthing"
]

# Main Title
import datetime
from datetime import timedelta

st.title("?? Anas Technology - Lead Generation Tool")
st.markdown("Search UK businesses, filter by size, and pitch appropriate IT/Tech solutions.")

try:
    CH_API_KEY = st.secrets.get("CH_API_KEY", "")
except Exception:
    CH_API_KEY = ""

# Sidebar Mode Selection
with st.sidebar:
    st.header("?? Select Mode")
    app_mode = st.radio("Choose Tool:", ["??? Google Maps Area Scanner", "?? Daily New Business Radar"])
    st.markdown("---")

if app_mode == "??? Google Maps Area Scanner":
    with st.sidebar:
        st.header("?? Target Settings")
        industry = st.selectbox("Select Industry (Niche):", sorted(INDUSTRIES))
        location = st.selectbox("Select UK City/Area:", sorted(UK_CITIES))
        
        st.markdown("---")
        st.header("?? Filter Leads")
        
        target_pitch = st.radio(
            "Target Pitch / Lead Type:",
            [
                "All Leads", 
                "Needs Website (No Website Found)", 
                "Needs SEO & Social Media (Small/Medium with Website)", 
                "Enterprise Grade (Large Businesses for ERP/AI)"
            ]
        )
        
        st.markdown("### Data Columns to Fetch")
        col1, col2 = st.columns(2)
        with col1:
            fetch_phone = st.checkbox("Phone", value=True)
            fetch_email = st.checkbox("Email", value=True)
            fetch_map_link = st.checkbox("Google Maps Link", value=True)
        with col2:
            fetch_website = st.checkbox("Website URL", value=True)
            fetch_socials = st.checkbox("Social Media", value=True)
        
        search_button = st.button("?? Search Real-Time Data", use_container_width=True)

    if search_button:
        st.info(f"Fetching real-time data for **{industry}** in **{location}** via Google Maps API... Please wait.")
        
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        status_text.text("Connecting to Google Maps API...")
        
        if location == "All UK (Entire Country)":
            raw_query = f"{industry} in United Kingdom"
        else:
            raw_query = f"{industry} in {location}, UK"
            
        safe_query = urllib.parse.quote(raw_query)
        search_url = f"https://maps.googleapis.com/maps/api/place/textsearch/json?query={safe_query}&key={GOOGLE_API_KEY}"
        
        try:
            response_data = requests.get(search_url).json()
            api_status = response_data.get("status")
            
            if api_status != "OK" and api_status != "ZERO_RESULTS":
                error_msg = response_data.get("error_message", "Unknown API error")
                st.error(f"Google API Error ({api_status}): {error_msg}")
                results = []
            else:
                results = response_data.get("results", [])
            
            all_data = []
            total_places = min(len(results), 20)
            
            if total_places == 0 and api_status == "OK":
                st.error("No businesses found for this location and industry.")
            elif total_places == 0 and api_status == "ZERO_RESULTS":
                 st.warning("Google Maps returned 0 results for this specific search. Try a different city or a broader industry.")
            elif total_places > 0:
                for idx, place in enumerate(results[:total_places]):
                    progress_bar.progress(int((idx / total_places) * 100))
                    status_text.text(f"Extracting details for: {place.get('name')}...")
                    
                    place_id = place.get("place_id")
                    name = place.get("name")
                    reviews_count = place.get("user_ratings_total", 0)
                    
                    if reviews_count >= 100:
                        size = "Enterprise"
                    else:
                        size = "Small"
                    
                    details_url = f"https://maps.googleapis.com/maps/api/place/details/json?place_id={place_id}&fields=name,formatted_phone_number,website,url&key={GOOGLE_API_KEY}"
                    det_resp = requests.get(details_url).json().get("result", {})
                    
                    phone = det_resp.get("formatted_phone_number", "Not Found")
                    website = det_resp.get("website", "Not Found")
                    map_link = det_resp.get("url", f"https://maps.google.com/?q={name.replace(' ', '+')}")
                    
                    if website == "Not Found":
                        pitch = "Website Development"
                    elif size == "Enterprise":
                        pitch = "Custom ERP, Omnichannel CRM, AI"
                    else:
                        pitch = "SEO & Social Media Marketing"

                    if "Needs Website" in target_pitch and website != "Not Found":
                        continue
                    if "SEO & Social Media" in target_pitch and (website == "Not Found" or size == "Enterprise"):
                        continue
                    if "Enterprise Grade" in target_pitch and size != "Enterprise":
                        continue
                    
                    safe_name = urllib.parse.quote(name)
                    linkedin_link = f"https://www.linkedin.com/search/results/companies/?keywords={safe_name}"
                    facebook_link = f"https://www.facebook.com/search/pages/?q={safe_name}"
                    
                    if website != "Not Found":
                        status_text.text(f"Scanning {website} for email addresses...")
                        email_address = extract_email_from_website(website)
                    else:
                        email_address = "No Website"
                    
                    whatsapp_link = generate_whatsapp_link(phone)
                    
                    all_data.append({
                        "Name": name,
                        "Phone (Call)": phone,
                        "WhatsApp": whatsapp_link,
                        "Email": email_address,
                        "Website": website,
                        "LinkedIn": linkedin_link,
                        "Facebook": facebook_link,
                        "Size": size,
                        "Pitch": pitch,
                        "Map Link": map_link
                    })
                    
                progress_bar.progress(100)
                status_text.text("Data fetching complete!")
                
                df = pd.DataFrame(all_data)
                
                if len(df) > 0:
                    columns_to_show = ["Name"]
                    if fetch_phone: 
                        columns_to_show.append("Phone (Call)")
                        columns_to_show.append("WhatsApp")
                    if fetch_email: columns_to_show.append("Email")
                    if fetch_website: columns_to_show.append("Website")
                    if fetch_socials: 
                        columns_to_show.append("LinkedIn")
                        columns_to_show.append("Facebook")
                    if fetch_map_link: columns_to_show.append("Map Link")
                    
                    columns_to_show.append("Size")
                    columns_to_show.append("Pitch")
                    
                    df_filtered = df[columns_to_show]
                    
                    safe_industry = industry.replace('&', 'and')
                    st.session_state['search_results'] = df_filtered
                    
                    safe_target = target_pitch.split('(')[0].strip().replace(' ', '_').replace('&', 'and')
                    st.session_state['file_name'] = f"{safe_industry}_{location}_{safe_target}_leads.csv"
                else:
                    st.warning("No companies matched your specific filter criteria in this area.")
                    
        except Exception as e:
            st.error(f"Error fetching data from Google Maps API: {e}")

    if 'search_results' in st.session_state:
        df_filtered = st.session_state['search_results']
        file_name = st.session_state['file_name']
        
        st.success(f"Found {len(df_filtered)} real businesses from Google Maps matching your criteria!")
        
        st.dataframe(
            df_filtered, 
            use_container_width=True,
            column_config={
                "Map Link": st.column_config.LinkColumn("Google Maps Link"),
                "LinkedIn": st.column_config.LinkColumn("LinkedIn Search"),
                "Facebook": st.column_config.LinkColumn("Facebook Search"),
                "Website": st.column_config.LinkColumn("Website"),
                "WhatsApp": st.column_config.LinkColumn("WhatsApp Link")
            }
        )
        
        csv = df_filtered.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="?? Download Data (CSV Format for Excel)",
            data=csv,
            file_name=file_name,
            mime='text/csv',
            key='download_csv_button'
        )

elif app_mode == "?? Daily New Business Radar":
    with st.sidebar:
        st.header("?? Radar Settings")
        date_option = st.selectbox("Registered Date:", ["Yesterday (Brand New)", "Last 7 Days"])
        fetch_limit = st.slider("Companies to fetch (Max 50):", 5, 50, 20)
        search_radar_btn = st.button("?? Scan UK Companies House", use_container_width=True)
        
    st.info("This mode pulls officially registered UK companies straight from the government registry (Companies House). It automatically generates smart search links so your BD can instantly find their LinkedIn, Facebook, or Website.")
    
    if search_radar_btn:
        if not CH_API_KEY:
            st.error("Companies House API Key is missing! Please add it to Streamlit Secrets.")
            st.stop()
            
        progress_bar = st.progress(0)
        status_text = st.empty()
        status_text.text("Connecting to UK Companies House API...")
        
        today = datetime.date.today()
        if date_option == "Yesterday (Brand New)":
            from_date = today - timedelta(days=1)
        else:
            from_date = today - timedelta(days=7)
            
        url = f"https://api.company-information.service.gov.uk/advanced-search/companies?incorporated_from={from_date}&incorporated_to={today}&size={fetch_limit}"
        
        try:
            response = requests.get(url, auth=(CH_API_KEY, ''))
            if response.status_code == 200:
                data = response.json()
                items = data.get("items", [])
                
                if not items:
                    st.warning("No new companies found for this date range.")
                else:
                    all_ch_data = []
                    total = len(items)
                    for idx, company in enumerate(items):
                        progress_bar.progress(int((idx / total) * 100))
                        
                        c_name = company.get("company_name", "").title()
                        c_date = company.get("date_of_creation", "")
                        
                        address_dict = company.get("registered_office_address", {})
                        locality = address_dict.get("locality", "Unknown")
                        postal_code = address_dict.get("postal_code", "")
                        address = f"{locality}, {postal_code}"
                        
                        status_text.text(f"Processing: {c_name}...")
                        
                        # Generate Smart Links
                        safe_name = urllib.parse.quote(c_name)
                        google_search = f"https://www.google.com/search?q={safe_name}+{locality}+UK"
                        linkedin_search = f"https://www.linkedin.com/search/results/companies/?keywords={safe_name}"
                        fb_search = f"https://www.facebook.com/search/pages/?q={safe_name}"
                        
                        all_ch_data.append({
                            "Company Name": c_name,
                            "Date Created": c_date,
                            "City / Postal": address,
                            "Google Search": google_search,
                            "LinkedIn Search": linkedin_search,
                            "Facebook Search": fb_search
                        })
                        
                    progress_bar.progress(100)
                    status_text.text("Companies House data fetching complete!")
                    
                    df_ch = pd.DataFrame(all_ch_data)
                    st.success(f"Found {len(df_ch)} newly registered businesses in the UK!")
                    
                    st.dataframe(
                        df_ch,
                        use_container_width=True,
                        column_config={
                            "Google Search": st.column_config.LinkColumn("Find Website/Phone"),
                            "LinkedIn Search": st.column_config.LinkColumn("Find Founder on LinkedIn"),
                            "Facebook Search": st.column_config.LinkColumn("Find Facebook Page")
                        }
                    )
                    
                    csv = df_ch.to_csv(index=False).encode('utf-8')
                    st.download_button(
                        label="?? Download Data (CSV Format for Excel)",
                        data=csv,
                        file_name=f"New_UK_Businesses_{today}.csv",
                        mime='text/csv',
                        key='download_ch_csv'
                    )
            else:
                st.error(f"Companies House API Error {response.status_code}: {response.text}")
        except Exception as e:
            st.error(f"Failed to fetch data from Companies House: {e}")
