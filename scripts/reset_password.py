import argparse
import logging
import secrets
import string
import sys

from dotenv import load_dotenv

# We need to add the project root to the python path to allow imports from src
sys.path.append(".")

from src.api.auth.infrastructure.repositories import SQLAlchemyUserRepository
from src.api.auth.infrastructure.security import PasswordService
from src.core.infrastructure.database import SessionLocal

# Configure basic logging
logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger(__name__)


def generate_temp_password(length: int = 12) -> str:
    """Generates a secure, random password."""
    alphabet = string.ascii_letters + string.digits + "!@#$%^&*"
    while True:
        password = "".join(secrets.choice(alphabet) for i in range(length))
        # Ensure the password has a mix of character types for robustness
        if (
            any(c.islower() for c in password)
            and any(c.isupper() for c in password)
            and any(c.isdigit() for c in password)
            and any(c in "!@#$%^&*" for c in password)
        ):
            return password


def main() -> None:
    """
    Main function to parse arguments and reset a user's password.
    """
    parser = argparse.ArgumentParser(description="ProVAI User Password Reset CLI.")
    parser.add_argument(
        "--email", type=str, required=True, help="Email address of the user to modify."
    )
    args = parser.parse_args()

    # Load environment variables to connect to the database
    load_dotenv()
    logger.info("Connecting to the database...")

    db = SessionLocal()
    try:
        user_repo = SQLAlchemyUserRepository(db)
        user = user_repo.get_by_email(args.email)

        if not user:
            logger.error(f"❌ User with email '{args.email}' not found.")
            sys.exit(1)

        logger.info(
            f"Found user '{user.name}' (ID: {user.id}). Generating new password..."
        )

        # Generate a new secure password
        new_password = generate_temp_password()

        # Hash the new password using our existing service
        password_service = PasswordService()
        hashed_password = password_service.get_password_hash(new_password)

        # Update the user's hashed password in the database
        user.hashed_password = hashed_password
        db.commit()

        logger.info("\n" + "=" * 40)
        logger.info("✅ Password successfully reset!")
        logger.info(f"   User: {user.email}")
        logger.info(f"   TEMPORARY PASSWORD: {new_password}")
        logger.info("=" * 40 + "\n")
        logger.info(
            "Please provide this password to the user and advise them to change it."
        )

    except Exception as e:
        logger.error(f"An unexpected error occurred: {e}")
        db.rollback()
        sys.exit(1)
    finally:
        db.close()


if __name__ == "__main__":
    main()
