# Django Web3 Wallet Engine

A secure Django-based platform integrated with a self-hosted Thirdweb Engine to provide automated custodial blockchain wallets for users.

## 🚀 Features

- **User Authentication:** Email/password registration with JWT (JSON Web Token) security.
- **Custodial Wallets:** Automatic on-chain wallet generation for every new user.
- **Web3 Infrastructure:** Self-hosted Thirdweb Engine running via Docker (Postgres & Redis).
- **Financial Operations:** Support for Deposits, Withdrawals, and Token Swaps.
- **Administrative CMS:** Backend management system for user accounts and system health.

## 🛠 Tech Stack

- **Backend:** Django, Django REST Framework
- **Blockchain:** Thirdweb Engine (Self-Hosted)
- **Database:** PostgreSQL
- **DevOps:** Docker, Docker-Compose
- **Cache:** Redis

## 📋 Infrastructure

The project runs a synchronized Docker stack:

1. **Engine:** Primary blockchain gateway (Port 3005).
2. **DB:** Dedicated PostgreSQL instance for transaction metadata.
3. **Redis:** High-speed queue for managing concurrent transactions.

## ⚙️ Setup

1. **Launch Engine:**
   ```bash
   docker-compose up -d
   ```

Configure Django:
Add your THIRDWEB_API_SECRET_KEY and ADMIN_WALLET_ADDRESS to the environment settings.

Run Migrations:

python manage.py migrate
python manage.py runserver

Milestones
[x] Milestone 1: User Identity & JWT Authentication.

[x] Milestone 2: Local Docker Engine Deployment & Validation.

[ ] Milestone 3: Access Token integration and Automated Wallet creation.

🔐 Security
Private keys are never stored in the Django database; they are managed securely within the encrypted Thirdweb Engine vault.
