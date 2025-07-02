import streamlit as st
import requests
import pandas as pd
import time
import pyperclip
import matplotlib.pyplot as plt
from datetime import datetime

# Configuration
BACKEND_URL = "http://localhost:8000"

# Page setup
st.set_page_config(
    page_title="Advanced Password Creator",
    page_icon="🔒",
    layout="wide"
)

# Session state initialization
if 'password_history' not in st.session_state:
    st.session_state.password_history = []
if 'api_response_time' not in st.session_state:
    st.session_state.api_response_time = []
if 'api_errors' not in st.session_state:
    st.session_state.api_errors = 0

def call_api(endpoint, payload=None):
    try:
        start_time = time.time()
        if payload:
            response = requests.post(f"{BACKEND_URL}{endpoint}", json=payload)
        else:
            response = requests.get(f"{BACKEND_URL}{endpoint}")
        
        response_time = time.time() - start_time
        st.session_state.api_response_time.append(response_time)
        
        if response.status_code == 200:
            return response.json()
        else:
            st.session_state.api_errors += 1
            st.error(f"API Error: {response.json().get('detail', 'Unknown error')}")
            return None
    except requests.exceptions.RequestException as e:
        st.session_state.api_errors += 1
        st.error(f"Connection error: {str(e)}")
        return None

def add_to_history(password_data, password_type="Password"):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    password_value = password_data.get("password") or password_data.get("passphrase") or password_data.get("pin")
    st.session_state.password_history.insert(0, {
        "timestamp": timestamp,
        "type": password_type,
        "value": password_value,
        "strength": password_data.get("strength", {}).get("score", 0),
        "crack_time": password_data.get("strength", {}).get("crack_time", "N/A")
    })

def display_strength_meter(score):
    colors = ["#ff0000", "#ff4000", "#ff8000", "#ffbf00", "#ffff00", "#bfff00", "#80ff00", "#40ff00", "#00ff00"]
    width = (score + 1) * 10 if score is not None else 0
    
    st.markdown(f"""
    <div style="background-color: #f0f0f0; border-radius: 5px; height: 20px; margin: 10px 0;">
        <div style="background: linear-gradient(to right, {colors[0]}, {colors[-1]}); 
                    width: {width}%; height: 100%; border-radius: 5px; 
                    transition: width 0.5s ease;"></div>
    </div>
    <div style="text-align: center; margin-top: -20px;">
        {["Very Weak", "Weak", "Fair", "Good", "Strong"][min(score, 4)] if score is not None else "N/A"}
    </div>
    """, unsafe_allow_html=True)

def name_input_fields(prefix=""):
    col1, col2 = st.columns(2)
    with col1:
        name_part1 = st.text_input("First name part (e.g., name, nickname)", key=f"{prefix}name_part1")
    with col2:
        name_part2 = st.text_input("Second name part (e.g., surname, pet name)", key=f"{prefix}name_part2")
    return name_part1, name_part2

def name_based_password_section():
    st.subheader("Name-Based Password Options")
    
    col1, col2 = st.columns(2)
    with col1:
        name_part1 = st.text_input("Primary Name (required)", key="nb_name1")
        complexity = st.select_slider(
            "Transformation Complexity",
            options=[1, 2, 3],
            value=2,
            format_func=lambda x: ["Simple", "Moderate", "Complex"][x-1],
            key="nb_complexity"
        )
    with col2:
        name_part2 = st.text_input("Secondary Name (optional)", key="nb_name2")
        include_random = st.checkbox(
            "Include Random Characters", 
            True,
            help="Adds random characters to increase security",
            key="nb_random"
        )
    
    length = st.slider("Password Length", 8, 32, 14, key="nb_length")
    
    if st.button("Generate Name-Based Password", key="nb_generate"):
        if not name_part1:
            st.error("Please enter at least a primary name")
            return
        
        payload = {
            "name_part1": name_part1,
            "name_part2": name_part2,
            "length": length,
            "complexity": complexity,
            "include_random": include_random
        }
        
        with st.spinner("Creating name-based password..."):
            result = call_api("/generate/name-based", payload)
            if result:
                st.code(result["password"], language="text")
                add_to_history(result, "Name-Based")
                
                st.markdown(f"**Strength:** {result['strength']['score']}/4")
                display_strength_meter(result['strength']['score'])
                st.markdown(f"**Estimated crack time:** {result['strength']['crack_time']}")
                
                if st.button("Copy to Clipboard", key="nb_copy"):
                    pyperclip.copy(result["password"])
                    st.success("Copied to clipboard!")
                st.write("---")

# Sidebar for navigation
st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to", ["Password Generator", "Password Strength Checker", "Password Validator", "Performance Metrics", "About"])

if page == "Password Generator":
    st.title("🔒 Advanced Password Generator")
    
    tab1, tab2, tab3, tab4 = st.tabs([
        "Random Password", 
        "Passphrase", 
        "Numeric PIN",
        "Name-Based Password"
    ])
    
    with tab1:
        st.subheader("Random Password Generator")
        
        col1, col2 = st.columns(2)
        
        with col1:
            length = st.slider("Password Length", 8, 64, 16, key="pass_length")
            include_upper = st.checkbox("Include Uppercase Letters", True, key="pass_upper")
            include_lower = st.checkbox("Include Lowercase Letters", True, key="pass_lower")
            include_digits = st.checkbox("Include Digits", True, key="pass_digits")
            include_special = st.checkbox("Include Special Characters", True, key="pass_special")
        
        with col2:
            exclude_similar = st.checkbox("Exclude Similar Characters (l,1,I,o,0,O)", True, key="pass_similar")
            exclude_ambiguous = st.checkbox("Exclude Ambiguous Characters ({ } [ ] ( ) etc.)", True, key="pass_ambiguous")
            num_passwords = st.slider("Number of Passwords to Generate", 1, 10, 3, key="pass_num")
        
        st.markdown("**Optional: Include name parts**")
        name_part1, name_part2 = name_input_fields("pass_")
        
        if st.button("Generate Password(s)", key="pass_generate"):
            payload = {
                "length": length,
                "include_uppercase": include_upper,
                "include_lowercase": include_lower,
                "include_digits": include_digits,
                "include_special": include_special,
                "exclude_similar": exclude_similar,
                "exclude_ambiguous": exclude_ambiguous,
                "name_part1": name_part1 if name_part1 else None,
                "name_part2": name_part2 if name_part2 else None
            }
            
            with st.spinner("Generating secure passwords..."):
                for i in range(num_passwords):
                    result = call_api("/generate/password", payload)
                    if result:
                        st.code(result["password"], language="text")
                        add_to_history(result)
                        
                        st.markdown(f"**Strength:** {result['strength']['score']}/4")
                        display_strength_meter(result['strength']['score'])
                        st.markdown(f"**Estimated crack time:** {result['strength']['crack_time']}")
                        
                        if st.button("Copy to Clipboard", key=f"copy_pass_{i}"):
                            pyperclip.copy(result["password"])
                            st.success("Copied to clipboard!")
                        st.write("---")
    
    with tab2:
        st.subheader("Passphrase Generator")
        
        col1, col2 = st.columns(2)
        
        with col1:
            word_count = st.slider("Number of Words", 3, 10, 4, key="phrase_words")
            separator = st.selectbox("Word Separator", ["-", "_", ".", " ", ""], key="phrase_sep")
            capitalize = st.checkbox("Capitalize Words", True, key="phrase_cap")
            add_number = st.checkbox("Add Random Number", True, key="phrase_num")
            num_passphrases = st.slider("Number of Passphrases to Generate", 1, 5, 2, key="phrase_count")
        
        st.markdown("**Optional: Include name parts**")
        name_part1, name_part2 = name_input_fields("phrase_")
        
        if st.button("Generate Passphrase(s)", key="phrase_generate"):
            payload = {
                "word_count": word_count,
                "separator": separator,
                "capitalize": capitalize,
                "add_number": add_number,
                "name_part1": name_part1 if name_part1 else None,
                "name_part2": name_part2 if name_part2 else None
            }
            
            with st.spinner("Generating memorable passphrases..."):
                for i in range(num_passphrases):
                    result = call_api("/generate/passphrase", payload)
                    if result:
                        st.code(result["passphrase"], language="text")
                        add_to_history(result, "Passphrase")
                        
                        st.markdown(f"**Strength:** {result['strength']['score']}/4")
                        display_strength_meter(result['strength']['score'])
                        st.markdown(f"**Estimated crack time:** {result['strength']['crack_time']}")
                        
                        if st.button("Copy to Clipboard", key=f"copy_phrase_{i}"):
                            pyperclip.copy(result["passphrase"])
                            st.success("Copied to clipboard!")
                        st.write("---")
    
    with tab3:
        st.subheader("Numeric PIN Generator")
        
        length = st.slider("PIN Length", 4, 12, 6, key="pin_length")
        num_pins = st.slider("Number of PINs to Generate", 1, 10, 3, key="pin_count")
        
        if st.button("Generate PIN(s)", key="pin_generate"):
            payload = {"length": length}
            
            with st.spinner("Generating secure PINs..."):
                for i in range(num_pins):
                    result = call_api("/generate/pin", payload)
                    if result:
                        st.code(result["pin"], language="text")
                        add_to_history({"pin": result["pin"]}, "PIN")
                        
                        if st.button("Copy to Clipboard", key=f"copy_pin_{i}"):
                            pyperclip.copy(result["pin"])
                            st.success("Copied to clipboard!")
                        st.write("---")
    
    with tab4:
        name_based_password_section()

elif page == "Password Strength Checker":
    st.title("🔍 Password Strength Checker")
    
    password = st.text_input("Enter a password to check its strength", type="password", key="strength_check")
    
    if password:
        with st.spinner("Analyzing password strength..."):
            result = call_api("/check-strength", {"password": password})
            if result:
                st.subheader("Strength Analysis")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.metric("Strength Score", f"{result['score']}/4")
                    display_strength_meter(result['score'])
                    st.metric("Estimated Crack Time", result['crack_time'])
                    st.metric("Guess Attempts", f"{result['guesses']:,}")
                
                with col2:
                    if result['feedback']['warning']:
                        st.warning(f"⚠️ {result['feedback']['warning']}")
                    
                    if result['feedback']['suggestions']:
                        st.info("**Suggestions:**")
                        for suggestion in result['feedback']['suggestions']:
                            st.write(f"- {suggestion}")

elif page == "Password Validator":
    st.title("✅ Password Validator")
    
    password = st.text_input("Enter a password to validate", type="password", key="validate_pass")
    
    st.subheader("Validation Rules")
    col1, col2 = st.columns(2)
    
    with col1:
        min_length = st.number_input("Minimum Length", 1, 100, 8, key="val_min_len")
        require_upper = st.checkbox("Require Uppercase Letters", True, key="val_upper")
        require_lower = st.checkbox("Require Lowercase Letters", True, key="val_lower")
    
    with col2:
        require_digit = st.checkbox("Require Digits", True, key="val_digit")
        require_special = st.checkbox("Require Special Characters", True, key="val_special")
    
    if password:
        payload = {
            "password": password,
            "rules": {
                "min_length": min_length,
                "require_upper": require_upper,
                "require_lower": require_lower,
                "require_digit": require_digit,
                "require_special": require_special
            }
        }
        
        with st.spinner("Validating password..."):
            result = call_api("/validate", payload)
            if result:
                if result['is_valid']:
                    st.success("✅ Password meets all requirements!")
                else:
                    st.error("❌ Password doesn't meet all requirements:")
                    for error in result['errors']:
                        st.write(f"- {error}")

elif page == "Performance Metrics":
    st.title("📊 Performance Metrics")
    
    if st.session_state.api_response_time:
        avg_response_time = sum(st.session_state.api_response_time) / len(st.session_state.api_response_time)
        st.metric("Average API Response Time", f"{avg_response_time:.3f} seconds")
        
        fig, ax = plt.subplots()
        ax.plot(st.session_state.api_response_time, marker='o')
        ax.set_title("API Response Times")
        ax.set_xlabel("Request Number")
        ax.set_ylabel("Response Time (seconds)")
        st.pyplot(fig)
    else:
        st.warning("No API response data available yet.")
    
    st.metric("Total API Errors", st.session_state.api_errors)
    
    st.subheader("Password History")
    if st.session_state.password_history:
        history_df = pd.DataFrame(st.session_state.password_history)
        st.dataframe(history_df)
        
        if not history_df.empty and 'strength' in history_df.columns:
            strength_counts = history_df['strength'].value_counts().sort_index()
            fig, ax = plt.subplots()
            strength_counts.plot(kind='bar', ax=ax)
            ax.set_title("Password Strength Distribution")
            ax.set_xlabel("Strength Score")
            ax.set_ylabel("Count")
            st.pyplot(fig)
    else:
        st.info("No password generation history yet.")

elif page == "About":
    st.title("ℹ️ About Password Creator")
    
    st.markdown("""
    ### Advanced Password Creator (v1.2)
    This application provides secure password generation and analysis tools with name-based options.
    
    **New in v1.2:**
    - Name-based password generation with customizable complexity
    - Three levels of name transformation (Simple, Moderate, Complex)
    - Option to combine names with random characters
    - Enhanced security for all password types
    
    **Features:**
    - Generate random passwords with customizable parameters
    - Create memorable passphrases
    - Generate numeric PINs
    - Create name-based passwords
    - Check password strength with detailed analysis
    - Validate passwords against custom rules
    - Performance metrics tracking
    
    **Security Notes:**
    - Name parts are transformed and never stored
    - All generation uses cryptographically secure methods
    - Passwords are never logged or stored permanently
    - Uses zxcvbn for realistic strength estimation
    """)
    
    st.markdown("---")
    st.markdown("Created with ❤️ for better security practices")

# Footer
st.markdown("---")
st.markdown("""
<style>
.footer {
    font-size: 0.8em;
    color: #666;
    text-align: center;
    margin-top: 2em;
}
</style>
<div class="footer">
    🔒 Always use strong, unique passwords for each account. Consider using a password manager.
</div>
""", unsafe_allow_html=True)