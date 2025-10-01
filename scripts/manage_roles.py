import argparse
import logging
import sys

from dotenv import load_dotenv

# To allow imports from src
sys.path.append(".")

from src.api.auth.infrastructure.repositories import SQLAlchemyUserRepository
from src.core.infrastructure.database import SessionLocal
from src.core.infrastructure.settings import settings

# Configure basic logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

VALID_ROLES = ["student", "teacher"]


def main() -> None:
    """
    Main function to parse arguments and manage user roles.
    """
    parser = argparse.ArgumentParser(description="ProVAI User Role Management CLI.")
    parser.add_argument(
        "--email", type=str, required=True, help="Email address of the user to modify."
    )
    parser.add_argument(
        "--role",
        type=str,
        required=True,
        choices=VALID_ROLES,
        help=f"The new role to assign. Must be one of: {', '.join(VALID_ROLES)}.",
    )
    args = parser.parse_args()

    # Load environment variables to get the database URL
    load_dotenv()
    logger.info(
        f"Connecting to database specified in ENV_STATE='{settings.ENV_STATE}'..."
    )

    db = SessionLocal()
    try:
        user_repo = SQLAlchemyUserRepository(db)
        user = user_repo.get_by_email(args.email)

        if not user:
            logger.error(f"❌ User with email '{args.email}' not found.")
            sys.exit(1)

        logger.info(
            f"Found user '{user.name}' (ID: {user.id}) with current role '{user.role}'."
        )

        if user.role == args.role:
            logger.warning(
                f"⚠️ User already has the role '{args.role}'. No changes made."
            )
            sys.exit(0)

        # Update the user's role
        user.role = args.role
        db.commit()

        logger.info(
            f"✅ Successfully updated user '{args.email}' to role '{args.role}'."
        )

    except Exception as e:
        logger.error(f"An unexpected error occurred: {e}")
        db.rollback()
        sys.exit(1)
    finally:
        db.close()


if __name__ == "__main__":
    main()
