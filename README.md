# Customer Service Chatbot for Tech Support 
## Still a Work in Progress - don't stress lemme finish it first :)

For all software-related issues, troubleshooting needs, and general programming guidance (forked data from StackOverflow & GitHub Issues)

## Overview

The chatbot utilizes Natural Language Processing (NLP) to understand user queries and fetch relevant information from multiple platforms.

This project integrates data sources like GitHub Issues and StackOverflow to provide info on tech-related problems experienced by beginners and experts alike.

![images](https://github.com/user-attachments/assets/891009b0-6fed-483d-95af-9e2272bcf573)

P.S: This is my final year CS project - I'm tryna get all 12 credits for this. 

Only the backend works for now, but A LOT of debugging is needed expeditiously.

## Table of Contents

- [Features](#features)
- [Technologies Used](#technologies-used)
- [Installation](#installation)
- [Usage](#usage)
- [File Structure](#file-structure)
- [Contributing](#contributing)
- [License](#license)

## Features

- **Data Integration**: Fetches data from GitHub issues and StackOverflow questions.
- **Natural Language Processing**: Uses NLP to understand user queries and provide relevant responses.
- **Documentation Fetching**: Retrieves relevant documentation based on user queries.
- **Troubleshooting Steps**: Provides troubleshooting steps for common issues.
- **General Information**: Offers general information based on user queries.

## Technologies Used

### Backend

- Python 3.8.5
- FastAPI
- GitHub REST API (access to GitHub Issues)
- StackExchange API (access to StackOverflow)
- Pydantic
- Pytest (for unit & integration testing)
- Docker (for containerization)

### Frontend (yet to decide)

- React.js, or
- Streamlit, or
- Flask

## Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/Odushhh/ts-chatbot-v2.git
   cd ts-chatbot-v2
   ```

2. Create a virtual environment:

   ```bash
   python -m venv venv
   ```

3. Activate the virtual environment:

   - On Windows:

     ```bash
     venv\Scripts\activate
     ```

   - On macOS/Linux:

     ```bash
     source venv/bin/activate
     ```

4. Install the required packages:

   ```bash
   pip install -r requirements.txt
   ```

5. Set up environment variables. Create a `.env` file in the root directory and add your API keys:

   ```plaintext
   GITHUB_API_TOKEN=your_github_api_token
   STACKOVERFLOW_API_KEY=your_stackoverflow_api_key
   ```

## Usage

To run the application, use the following command:

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

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
