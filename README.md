# Facial Access System

This is a web app for a facial recognition access system. **The main idea is to run this on a Raspberry Pi connected to a door, so it can automatically unlock when it recognizes a known face.** You can add members, upload their pictures, and see them recognized on a live camera feed.

## The Goal: Raspberry Pi Door Control

The ultimate goal for this project is to make a real-world, DIY smart lock. It's designed to be lightweight enough to run on a **Raspberry Pi**.

**How it would work:**
1.  The Python code runs on a Raspberry Pi with a camera module (or webcam) attached.
2.  When a known face is detected, the script can be modified to trigger a GPIO pin on the Rasberry Pi.
3.  That GPIO pin would be connected to a relay or a motor driver to control an electronic door lock.

**What's Missing:**
**The electronics part!** I haven't implemented the connection from the Raspberry Pi's GPIO pins to an actual door lock. This would require knowledge of relays, solenoids, or electronic strikes. If you know how to do this, your contribution would be awesome!

## Features

* **Live Camera Feed:** See who the camera is seeing in real-time.
* **Login Page:** A simple login page to keep the dashboard private and secure.
* **Member Management:** You can add new people and delete old ones from the system.
* **Photo Uploads:** Upload pictures for each person to train the recognition model.
* **Logging:** The system saves a log of every face it detects in daily text files.

## Tech Stack

* **Backend:** Python, FastAPI
* **Frontend:** HTML, CSS, JavaScript
* **Face Recognition:** dlib, face-recognition, OpenCV
* **Deployment:** Docker

## How to Run it

### Running with Docker

1.  **Build the Docker image:**
    ```bash
    docker build -t facial-access-system .
    ```

2.  **Run the container:**
    This command connects your webcam and saves your data outside the container.
    ```bash
    docker run -p 8000:8000 facial-access-system
    ```
    ***Note:*** *This Docker image is built for standard (x86) computers. To run on a Raspberry Pi, you would need to build the image for an ARM architecture.*
    *The port is set to 8000, however you can change and set it to whatever port number you want.*

3.  **Check it out:**
    Open your web browser and go to `http://localhost:8000` (or `https://ip-address:8000`).

### Running Locally (Without Docker)

1.  **Create a virtual environment:**
    ```bash
    python3 -m venv venv
    source venv/bin/activate
    # On Windows, use: venv\Scripts\activate
    ```

2.  **Install the requirements:**
    *(Note: `dlib` can take a very long time to install.)*
    ```bash
    pip install -r requirements.txt
    ```

3.  **change the `.env` file:**
    Create or change the file named `.env` and add your login details.
    ```env
    LOGIN_USERNAME=admin
    LOGIN_PASSWORD=1234
    SECRET_KEY=change_this_key_or_be_hacked
    ```

4.  **Run the app:**
    From the `src/web/` directory, run:
    ```bash
    uvicorn app:app --host 0.0.0.0 --port 8000
    ```

## How to Use the App

1.  Go to `http://localhost:8000` (or `https://ip-address:8000`) and log in.
2.  In the sidebar, click `+ Add Member` and type in a name.
3.  A new button with that person's name will appear. Click it.
4.  Upload a few clear photos of their face and click 'Upload Photo'.
5.  Click the `Live` button to see the camera feed and check if it recognizes them!

## License

MIT License