# Seabottle

**Seabottle** is a modern, API-first alternative to traditional journaling. It allows users to capture thoughts, lock them away for a specific duration ("bury" them), and only revisit them once they have "released." It facilitates a conversation with your past self by allowing replies to released capsules.

This project is built with **FastAPI** for high performance and **PostgreSQL** for robust data storage, with a strong focus on privacy and security through encryption.

Check it out at [here!](journal.edisonwang.dev)

## Features

* **Time-Locked Entries ("Capsules")**:
    * Create capsules that are inaccessible until a specific duration has passed.
    * Content is **encrypted at rest** using Fernet symmetric encryption; even the database admin cannot read your thoughts without the key.


* **Conversational Journaling**:
    * Once a capsule is released, you can "reply" to it.
    * Build threads of conversation with your past self to track personal growth and changes in perspective.

* **Email Notifications**: An automated system to notify users via email when a capsule has been released and is ready to be read.

* **Secure Authentication**:
    * Custom API Key authentication system.
    * Keys are hashed and salted (SHA-256) for security.
    * User passwords are secured using Bcrypt.

* **User Management**:
    * Register, update profile, change passwords, and delete accounts.
    * Regenerate API keys securely.

## 🚀 Upcoming Features (Roadmap)

## Tech Stack

* **Framework**: [FastAPI](https://fastapi.tiangolo.com/) (Python 3.12)
* **Database**: PostgreSQL (Async via `asyncpg`)
* **ORM**: SQLModel / SQLAlchemy
* **Migrations**: Alembic
* **Security**: `cryptography` (Fernet), `passlib` (Bcrypt), `hashlib` (sha256)
* **Deployment**: Docker

## Installation & Setup

### Prerequisites

* Python 3.12+
* PostgreSQL
* Docker (Optional, for containerized deployment)

### Local Development

1. **Clone the repository**
```bash
git clone https://github.com/Syzygicality/seabottle.git
cd seabottle

```


2. **Create a Virtual Environment**
```bash
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

```


3. **Install Dependencies**
```bash
pip install -r requirements.txt

```


4. **Environment Configuration**
Create a `.env` file in the root directory (refer to `template.env`). You will need to generate a Fernet key for encryption.
```env
DB_USER=postgres
DB_PASSWORD=password
DB_LOCATION=localhost
DB_PORT=5432
DB_NAME=time_capsule_db
# Generate a key using: python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
FERNET_KEY=your_fernet_key_here

```


5. **Run Migrations**
Initialize the database schema using Alembic.
```bash
alembic upgrade head

```


6. **Start the Server**
```bash
uvicorn app.main:app --reload

```


The API will be available at `http://127.0.0.1:8000`.

### Docker Setup

1. **Build the Image**
```bash
docker build -t seabottle .

```


2. **Run the Container**
Ensure you pass the required environment variables or use a `.env` file.
```bash
docker run -p 8000:8000 --env-file .env seabottle

```



## API Documentation

Once the server is running, you can access the interactive API documentation (Swagger UI) at:

* **URL**: `http://127.0.0.1:8000/docs`

### Key Endpoints

* **Users**:
* `POST /users/me`: Register a new user.
* `POST /users/api-key/create`: Generate your first API Key.


* **Capsules**:
* `POST /capsules/post`: Bury a new capsule (requires `time_held` delta).
* `GET /capsules`: List all *released* capsules.
* `GET /capsules/conversations`: View threaded conversations.



## License

Distributed under the MIT License. See `LICENSE` for more information.