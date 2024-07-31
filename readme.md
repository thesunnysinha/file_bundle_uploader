### Prerequisites

1. **Create `.env` File inside backend Folder:**

    Create a `.env` file in your project directory using `envExample` as a template.

2. **Install Redis:**

    ### For Linux
    ```
    sudo apt update
    sudo apt install redis-server
    sudo systemctl start redis-server
    sudo systemctl enable redis-server
    sudo systemctl status redis-server
    ```

3. **Create and Activate Virtual Environment:**

   Open Command Prompt (cmd) and navigate to your project directory.

   Create a virtual environment named `venv`:

   ```
   python -m venv venv
   ```

   Activate the virtual environment:
   
   ```
   venv\Scripts\activate
   ```


4. **Install Dependencies:**

 While inside the activated virtual environment, install dependencies from `requirements.txt`:

 ```
 cd backend
 pip install -r requirements.txt
 ```

### Using Script

1. **Run `runserver.sh` Script:**

 Make the script executable:

 ```
 chmod +x runserver.sh
 ```

 Execute the script:

 ```
 ./runserver.sh
 ```