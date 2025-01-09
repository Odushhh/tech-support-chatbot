# Customer Service Chatbot for Tech Support 

For all software-related issues, troubleshooting needs, and general programming guidance (forked data from StackOverflow & GitHub Issues)

[Tech Support Chatbot LIVE!] (https://techsupportchatbot.vercel.app/)

## Overview

This chatbot utilizes a few NLP techniques to understand user queries and fetch relevant information from multiple platforms.

Data is 'forked' from sources like GitHub Issues and StackOverflow to provide answers to tech-related problems.

All types of devs experience such issues - check image.

![images](https://github.com/user-attachments/assets/891009b0-6fed-483d-95af-9e2272bcf573)

P.S: This is my final year CS project btw
Only the backend works for now, but A LOT of debugging is needed expeditiously.

## Table of Contents

- [Features](#features)
- [Technologies Used](#technologies-used)
- [Installation](#installation)
- [Usage](#usage)
- [File Structure](#file-structure)
- [Contributing](#contributing)
- [License](#license)

## Capabilities

- **Data Integration**: Fetches data from GitHub issues and StackOverflow questions.
- **Natural Language Processing**: Uses NLP to understand user queries and provide relevant responses.
- **Documentation Fetching**: Retrieves relevant documentation based on user queries.
- **Troubleshooting Steps**: Provides troubleshooting steps for common issues.
- **General Information**: Offers general information based on user queries.
  
## Features
- **Smart Search**: Instantly searches developer forums and tech documentation for accurate solutions.
- **Code-Aware**: Understands code snippets and errors to provide contextual debugging assistance.
- **Vast Knowledge**: Leverages data from StackOverflow, GitHub, and the broader internet for comprehensive tech support.
- **Pricing Tiers**: Offers a clear breakdown of pricing options for users.
- **Waitlist Form**: Users can join the waitlist to gain early access to the chatbot.

## Technologies Used

### Backend (check *master* branch)

- Python 3.8.5
- FastAPI
- GitHub REST API (access to GitHub Issues)
- StackExchange API (access to StackOverflow)
- Pydantic
- Pytest (for unit & integration testing)
- Docker (for containerization)

### Frontend (check *main* branch)

- React.js, or
- Streamlit, or
- Flask

## Installation

1. Clone repo:

   ```bash
   git clone https://github.com/Odushhh/ts-chatbot-v2.git
   cd ts-chatbot-v2
   ```

2. Create and activate the virtualenv:

   ```bash
   python -m venv venv
   
   - On Windows:
     venv\Scripts\activate
   

   - On macOS/Linux:

     source venv/bin/activate
     
   ```



   

3. Install dependancies:

   ```bash
   pip install -r requirements.txt
   ```

4. Check `.env` file for all keys, tokens, etc.:

   ```plaintext
   GITHUB_API_TOKEN=your_github_api_token
   STACKOVERFLOW_API_KEY=your_stackoverflow_api_key
   ```

## Usage

Run the application:

```bash
uvicorn backend.app.main:app --reload
```


## File Structure

```plaintext
backend/
│
├── app/
│   ├── api/
│   ├── core/
│   ├── data/
│   ├── nlp/
│   ├── tests/
│   └── utils/
│
├── .env
├── .gitignore
├── docker-compose.yml
├── Dockerfile
└── requirements.txt
```

## Contributing

Contributions are welcome! Please follow these steps to contribute:

1. Fork the repository.
2. Create a new branch (`git checkout -b feature-branch`).
3. Make your changes and commit them (`git commit -m 'Add new feature'`).
4. Push to the branch (`git push origin feature-branch`).
5. Create a pull request.

## Contact me! (please?)

[LinkedIn](https://www.linkedin.com/in/adrian-oduma-4374a4252/)

[Email][mailto:adrianoduma8@gmail.com]

