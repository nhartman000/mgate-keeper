# mgate-keeper

## Table of Contents
1. [Quick Start](#quick-start)
2. [Project Structure Overview](#project-structure-overview)
3. [API Key Setup](#api-key-setup)
4. [Usage Example](#usage-example)
5. [Development](#development)
6. [Security Best Practices](#security-best-practices)
7. [Troubleshooting](#troubleshooting)
8. [Contributing](#contributing)
9. [Support](#support)

## Quick Start
1. Clone the repository:
    ```bash
    git clone https://github.com/nhartman000/mgate-keeper.git
    cd mgate-keeper
    ```
2. Create a virtual environment:
    ```bash
    python3 -m venv venv
    source venv/bin/activate  # On Windows use `venv\Scripts\activate`
    ```
3. Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```
4. Configure the `.env` file:
    - Copy the example:
    ```bash
    cp .env.example .env
    ```
    - Fill in the necessary configuration details.
5. Run demos:
    ```bash
    python demo.py
    ```

## Project Structure Overview
- `src/`: Contains the source code.
- `tests/`: Contains unit tests.
- `demos/`: Contains example demo files.
- `requirements.txt`: Lists dependencies.
- `.env.example`: Example environment variable file.

## API Key Setup
1. **OpenAI**:  
   - Sign up at [OpenAI](https://openai.com/).
   - Fetch your API key from the dashboard and set it as `OPENAI_API_KEY` in your `.env`.

2. **Google**:  
   - Create a project in the [Google Cloud Console](https://console.cloud.google.com/).
   - Enable the APIs you need and create service credentials.
   - Set your API credentials in the `.env`.

## Usage Example
Here is an example of how to use the mgate-keeper package:
```python
from mgate_keeper import MGateKeeper

# Instantiate the class
mgate_keeper = MGateKeeper(api_key='YOUR_API_KEY')

# Running a sample method
response = mgate_keeper.run_demo()
print(response)
```

## Development
- To run tests:
    ```bash
    pytest tests/
    ```
- To build the package:
    ```bash
    python setup.py sdist bdist_wheel
    ```

## Security Best Practices
- Keep your API keys confidential and do not expose them in client-side code.
- Regularly rotate your API keys.
- Use `.env` files to manage sensitive data.

## Troubleshooting
- If you encounter issues:  
  - Check the API key and its configuration.  
  - Look into logs for error details.  
  - Verify dependencies match those in `requirements.txt`.

## Contributing
- Fork the repository.
- Create a new branch for your feature:
    ```bash
    git checkout -b my-feature
    ```
- Push your changes:
    ```bash
    git push origin my-feature
    ```
- Create a pull request.

## Support
- For support, issues, and feature requests, please open an issue in this repository.