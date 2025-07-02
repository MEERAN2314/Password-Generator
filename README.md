# Password-Generator

This project provides a password generation tool with a Streamlit frontend and a FastAPI backend.

## Features

- Secure password generation
- Password strength estimation using zxcvbn
- User-friendly interface via Streamlit

## Technologies Used

**Backend:**

- FastAPI
- Uvicorn
- Python-multipart
- Passlib
- zxcvbn

**Frontend:**

- Streamlit
- Requests
- Pandas
- Matplotlib
- Pyperclip
- zxcvbn

## Setup

1. Clone the repository.
2. Navigate to the `backend` directory and run `pip install -r requirements.txt`.
3. Navigate to the `frontend` directory and run `pip install -r requirements.txt`.
4. Run the backend using `uvicorn main:app --reload`.
5. Run the frontend using `streamlit run app.py`.
