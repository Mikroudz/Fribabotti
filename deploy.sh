#!/bin/bash
set -e


PROJECT_DIR="/home/gh-action-runner-user/fribabotti"
RELEASES_DIR="$PROJECT_DIR/releases"
SHARED_DIR="$PROJECT_DIR/shared"
VENV_PATH="$SHARED_DIR/venv"
# A timestamp-based directory for the new release
RELEASE_DIR="$RELEASES_DIR/$(date +%Y%m%d%H%M%S)"

echo "Starting deployment..."

# --- 1. Create New Release Directory ---
echo "--> Creating new release directory: $RELEASE_DIR"
mkdir -p "$RELEASE_DIR"
# Copy the application code from the runner's workspace to the release directory
# The GITHUB_WORKSPACE variable is provided by the runner
cp -R "$GITHUB_WORKSPACE"/* "$RELEASE_DIR"
cd "$RELEASE_DIR"

if [ ! -e "$VENV_PATH/pyvenv.cfg" ]; then
	python3 -m venv $VENV_PATH
fi

# --- 2. Create .env file from GitHub Secrets ---
# The secrets are passed as environment variables by the workflow file
echo "--> Creating .env file from secrets"

echo "DB_TYPE=${DB_TYPE}" >> .env
echo "DB_HOST=${DB_HOST}" >> .env
echo "DB_USER=${DB_USER}" >> .env
echo "DB_PASSWORD=${DB_PASSWORD}" >> .env
echo "DB_DATABASE=${DB_DATABASE}" >> .env
echo "DEV_MODE=${DEV_MODE}" >> .env
echo "BOT_SECRET=${BOT_SECRET}" >> .env

echo ".env file created successfully."

echo "--> Activating virtual environment and installing/updating dependencies"
source "$VENV_PATH/bin/activate"
pip install -r requirements.txt
deactivate

# --- 4. Run Alembic Migrations (if any) ---
echo "--> Running database migrations"
source "$VENV_PATH/bin/activate"
alembic upgrade head
deactivate

# --- 5. Atomically Switch Symlink ---
echo "--> Activating new release by updating the 'current' symlink"
rm -f "$PROJECT_DIR/current"
ln -s "$RELEASE_DIR" "$PROJECT_DIR/current"
echo "--> Symlink switched to $RELEASE_DIR"

# --- 6. Restart the Application Service ---
echo "--> Restarting the application service"
sudo systemctl restart tg-fribabotti.service
echo "--> Service restarted successfully."

# --- 7. (Optional) Cleanup Old Releases ---
echo "--> Cleaning up old releases (keeping last 5)"
# List all release directories, sort them, keep the last 5, and delete the rest
ls -1dr "$RELEASES_DIR"/* | tail -n +6 | xargs -r rm -rf

echo "Deployment finished successfully!"