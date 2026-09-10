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
st.title("🚀 Anas Technology - Lead Generation Tool")
st.markdown("Search UK businesses, filter by size, and pitch appropriate IT/Tech solutions.")

# Sidebar for inputs
with st.sidebar:
    st.header("🎯 Target Settings")
    industry = st.selectbox("Select Industry (Niche):", sorted(INDUSTRIES))
    location = st.selectbox("Select UK City/Area:", sorted(UK_CITIES))
    
    st.markdown("---")
    st.header("📊 Filter Leads")
    
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
    
    search_button = st.button("🔍 Search Real-Time Data", use_container_width=True)

# Main area for results
if search_button:
    st.info(f"Fetching real-time data for **{industry}** in **{location}** via Google Maps API... Please wait.")
    
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    status_text.text("Connecting to Google Maps API...")
    raw_query = f"{industry} in {location}, UK"
    safe_query = urllib.parse.quote(raw_query)
    search_url = f"https://maps.googleapis.com/maps/api/place/textsearch/json?query={safe_query}&key={GOOGLE_API_KEY}"
    
    try:
        response_data = requests.get(search_url).json()
        api_status = response_data.get("status")
        
        if api_status != "OK" and api_status != "ZERO_RESULTS":
            error_msg = response_data.get("error_message", "Unknown API error")
            st.error(f"Google API Error ({api_status}): {error_msg}")
            st.info("Pehle yeh 'Dummy Data' par chal raha tha. Asli API lagane ke baad Google apko error de raha hai. Yeh error Google Cloud Console se API ko theek karne se solve hoga.")
            results = []
        else:
            results = response_data.get("results", [])
        
        all_data = []
        total_places = min(len(results), 20) # We process up to 20 results per search to avoid massive API costs
        
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
                
                # Determine Size (Enterprise vs Small based on reviews count)
                if reviews_count >= 100:
                    size = "Enterprise"
                else:
                    size = "Small"
                
                # Fetch deeper details (Phone, Website, Link)
                details_url = f"https://maps.googleapis.com/maps/api/place/details/json?place_id={place_id}&fields=name,formatted_phone_number,website,url&key={GOOGLE_API_KEY}"
                det_resp = requests.get(details_url).json().get("result", {})
                
                phone = det_resp.get("formatted_phone_number", "Not Found")
                website = det_resp.get("website", "Not Found")
                map_link = det_resp.get("url", f"https://maps.google.com/?q={name.replace(' ', '+')}")
                
                # Determine Pitch based on real data
                if website == "Not Found":
                    pitch = "Website Development"
                elif size == "Enterprise":
                    pitch = "Custom ERP, Omnichannel CRM, AI"
                else:
                    pitch = "SEO & Social Media Marketing"

                # Filter Logic based on selected Target Pitch
                if "Needs Website" in target_pitch and website != "Not Found":
                    continue
                if "SEO & Social Media" in target_pitch and (website == "Not Found" or size == "Enterprise"):
                    continue
                if "Enterprise Grade" in target_pitch and size != "Enterprise":
                    continue
                
                # Generate Smart Social Media Search Links
                safe_name = urllib.parse.quote(name)
                linkedin_link = f"https://www.linkedin.com/search/results/companies/?keywords={safe_name}"
                facebook_link = f"https://www.facebook.com/search/pages/?q={safe_name}"
                
                # Fetch Email (if they have a website)
                if website != "Not Found":
                    status_text.text(f"Scanning {website} for email addresses...")
                    email_address = extract_email_from_website(website)
                else:
                    email_address = "No Website"
                
                # WhatsApp Logic
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
                # Prepare columns to show
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
                
                # Save to session state
                safe_industry = industry.replace('&', 'and')
                st.session_state['search_results'] = df_filtered
                
                # Make safe target pitch string for filename
                safe_target = target_pitch.split('(')[0].strip().replace(' ', '_').replace('&', 'and')
                st.session_state['file_name'] = f"{safe_industry}_{location}_{safe_target}_leads.csv"
            else:
                st.warning("No companies matched your specific filter criteria in this area.")
                
    except Exception as e:
        st.error(f"Error fetching data from Google Maps API: {e}")

# Show data and download button if we have results in session state
if 'search_results' in st.session_state:
    df_filtered = st.session_state['search_results']
    file_name = st.session_state['file_name']
    
    st.success(f"Found {len(df_filtered)} real businesses from Google Maps matching your criteria!")
    
    # Display dataframe
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
    
    # Export to CSV feature
    csv = df_filtered.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 Download Data as CSV/Excel",
        data=csv,
        file_name=file_name,
        mime='text/csv',
    )

    st.markdown("---")
    st.header("💬 Smart Communication Scripts")
    st.markdown("Select a company to generate tailored Email, Phone, and WhatsApp scripts.")
    
    # Create a list of company names from the filtered dataframe
    company_names = df_filtered["Name"].tolist()
    
    if company_names:
        selected_company = st.selectbox("Select Company:", company_names)
        
        # Get the row for the selected company
        company_data = df_filtered[df_filtered["Name"] == selected_company].iloc[0]
        
        pitch = company_data.get("Pitch", "")
        size = company_data.get("Size", "Small")
        
        # --- Logic for Content Generation ---
        
        # Email Logic
        email_subject = ""
        email_body = ""
        
        # Phone Logic
        phone_script = ""
        
        # WhatsApp Logic
        whatsapp_message = ""
        
        if "Website" in pitch:
            email_subject = f"Digital Growth Opportunity for {selected_company}"
            email_body = f"Hi Team at {selected_company},\n\nHope you are having a great day.\n\nWhile searching for top services in {location}, I came across your business profile. You have a great reputation locally, but I noticed that you currently don't have a professional website.\n\nIn today's digital age, many potential customers in {location} are searching online, and without a website, they might be going to your competitors.\n\nAt Anas Technology UK, we specialize in building highly converting, professional websites for businesses like yours. A website will act as your 24/7 digital storefront, bringing in more direct calls and customers.\n\nWould you be open to a quick 5-minute chat this week to see how we can help {selected_company} grow?\n\nBest regards,\nBusiness Development Team\nAnas Technology UK\nhttps://anastechnology.co.uk"
            
            phone_script = f"""[Introduction]
"Hi, is this the owner or manager at {selected_company}? 
My name is [Your Name], calling from Anas Technology UK."

[The Hook / Problem]
"I'll be very brief. I was searching for services in {location} today and your business came up. You have a great local reputation, but I noticed you don't have a live website right now."

[The Value / Solution]
"A lot of customers are searching online right now, and without a website, they are likely going straight to your competitors. We help local businesses like yours build professional, affordable websites that actually generate calls and leads."

[Call to Action]
"Would you have 5 minutes this week to discuss how we can get {selected_company} set up online and bring in more customers?"""

            whatsapp_message = f"Hi {selected_company} team! 👋 This is [Your Name] from Anas Technology UK. I noticed you do great work in {location}, but you don't have a website yet. We help local businesses build professional websites to get more direct customers. Are you open to a quick chat about getting your business online? 🚀"

        elif "SEO" in pitch or "Social Media" in pitch:
            email_subject = f"Unlocking more local customers for {selected_company}"
            email_body = f"Hi Team at {selected_company},\n\nI was impressed by the services you offer across {location}.\n\nHowever, during a quick digital audit, I noticed that your online visibility (SEO/Social Media) isn't reflecting the true quality of your business. Your competitors are currently taking up the top spots on Google Maps and search results.\n\nAt Anas Technology UK, we help businesses like {selected_company} dominate local search and social media, ensuring that when customers look for your services, they find YOU first.\n\nCan we schedule a brief call next Tuesday to share a few free tips on how you can improve your digital presence?\n\nBest regards,\nBusiness Development Team\nAnas Technology UK\nhttps://anastechnology.co.uk"
            
            phone_script = f"""[Introduction]
"Hi, is this the decision maker at {selected_company}? 
My name is [Your Name], calling from Anas Technology UK."

[The Hook / Problem]
"I was looking at your online profile in {location}. You guys do great work, but I noticed you're not showing up at the top of Google searches, and your social media could be doing a lot more for you."

[The Value / Solution]
"Right now, when people search, they are finding your competitors first. We specialize in Local SEO and Social Media Marketing. We can push {selected_company} to the top of Google Maps so you get those phone calls instead of the other guys."

[Call to Action]
"I'd love to share a couple of free tips on how you can fix this. Do you have 5 minutes tomorrow for a quick chat?"""

            whatsapp_message = f"Hi {selected_company} team! 🌟 [Your Name] here from Anas Technology UK. I was checking out your business in {location}. You have great potential, but you're missing out on customers because competitors are ranking higher on Google Maps. We can help you fix your SEO and dominate local searches. Can we schedule a quick 5-min call? 📈"

        else:
            email_subject = f"Enterprise Tech Solutions & Automation for {selected_company}"
            email_body = f"Hi Team at {selected_company},\n\nAs a leading player in {location}, scaling your operations efficiently must be a top priority.\n\nI am reaching out from Anas Technology UK, an enterprise-grade consultancy. We help established companies like yours reduce operational bottlenecks, improve data flow, and automate redundant tasks.\n\nBased on your scale, we believe our Custom ERP, AI automation, and Omnichannel CRM solutions could significantly streamline your processes and increase your bottom-line revenue.\n\nI would love to arrange a brief introductory call with our technical director to discuss how our custom software solutions align with {selected_company}'s growth goals for this year.\n\nAre you available for a brief meeting next week?\n\nBest regards,\nBusiness Development Team\nAnas Technology UK\nhttps://anastechnology.co.uk"
            
            phone_script = f"""[Introduction - Ask for Specific Role]
"Hi, could you please connect me with the Operations Director or IT Manager? ... 
Hi, my name is [Your Name] from Anas Technology UK. We are an enterprise software consultancy."

[The Hook / Problem]
"I'm calling because we work with growing companies in {location} to help them automate their daily operations. I see {selected_company} has been expanding."

[The Value / Solution]
"When companies reach your size, using basic software or multiple disconnected systems causes bottlenecks. We build Custom ERPs, Omnichannel CRMs, and AI tools that centralize your data, save hundreds of admin hours, and increase revenue."

[Call to Action]
"I’m not looking to sell you anything today, but I’d love to set up a 10-minute discovery call with our Technical Director to see if our tech solutions align with your growth plans. How does next Tuesday look for you?"""

            whatsapp_message = f"Hello {selected_company} Management, this is [Your Name] from Anas Technology UK. We are an enterprise consultancy helping companies automate operations and scale faster using Custom ERPs and AI solutions. I'd love to arrange a brief call to discuss how our tech can streamline your operations in {location}. Let me know a good time to connect. 🤝"

        # --- UI Display using Tabs ---
        tab1, tab2, tab3 = st.tabs(["📧 Email", "📞 Phone Script", "📱 WhatsApp"])
        
        with tab1:
            st.text_input("Email Subject:", value=email_subject)
            st.text_area("Email Body (Copy this):", value=email_body, height=300)
            
        with tab2:
            st.info("💡 Tip: Read this naturally, don't sound like a robot. Pause and wait for their answers.")
            st.text_area("Live Calling Script:", value=phone_script, height=350)
            
        with tab3:
            st.success("💡 Tip: WhatsApp messages should be short and friendly. Use emojis!")
            st.text_area("WhatsApp Message:", value=whatsapp_message, height=150)
        
    else:
        st.warning("No companies found to generate scripts for.")
