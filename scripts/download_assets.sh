#!/usr/bin/env bash
# This script reads the `assets` config to download all required assets.
# It uses the robust `curl` command to check the HTTP Content-Length header
# and provides a colorful, user-friendly output.

set -e # Exit immediately if any command fails

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
BOLD='\033[1m'
NC='\033[0m' # No Color (reset)

human_readable_size() {
	local BYTES=$1
	if ! [[ "$BYTES" =~ ^[0-9]+$ ]] || [[ "$BYTES" -eq 0 ]]; then
		echo "N/A"
		return
	fi

	if (($(echo "$BYTES >= 1024*1024*1024" | bc -l))); then
		echo "$(echo "scale=2; $BYTES/(1024*1024*1024)" | bc)GB"
	elif (($(echo "$BYTES >= 1024*1024" | bc -l))); then
		echo "$(echo "scale=2; $BYTES/(1024*1024)" | bc)MB"
	elif (($(echo "$BYTES >= 1024" | bc -l))); then
		echo "$(echo "scale=1; $BYTES/1024" | bc)KB"
	else
		echo "${BYTES}B"
	fi
}

download_file() {
	local DIR=$1
	local NAME=$2
	local URL=$3
	local FILE_PATH="${DIR}/${NAME}"

	mkdir -p "$DIR"

	if [ -f "$FILE_PATH" ]; then
		printf "${GREEN}✅ Asset '${BOLD}${NAME}${NC}${GREEN}' already exists in '${DIR}/'. Skipping.${NC}\n"
	else
		printf "${YELLOW}⏳ Asset '${BOLD}${NAME}${NC}${YELLOW}' not found. Checking remote file size...${NC}\n"

		FILE_SIZE_BYTES=$(curl -sIL "$URL" | grep -i "Content-Length" | tail -n 1 | awk '{print $2}' | tr -d '\r' || true)

		local HUMAN_SIZE=$(human_readable_size "$FILE_SIZE_BYTES")
		printf "   File size is ~${BOLD}${BLUE}${HUMAN_SIZE}${NC}.\n"
		printf "   Downloading from URL...\n"

		# Perform the actual download with wget for its progress bar
		wget -q --show-progress -O "$FILE_PATH" "$URL"

		if [ $? -eq 0 ]; then
			printf "${GREEN}✅ Asset '${NAME}' downloaded successfully.${NC}\n"
		else
			printf "${RED}❌ ERROR: Download for '${NAME}' failed.${NC}\n"
			rm -f "$FILE_PATH"
			exit 1
		fi
	fi
}

printf "\n${BLUE}${BOLD}--- ProVAI Asset Setup (Reading from assets/*.yml) ---${NC}\n"

read -r MODEL_NAME MODEL_URL <<<"$(python -m scripts.helpers.asset_reader llm default)"
download_file "models" "$MODEL_NAME" "$MODEL_URL"

read -r DOC_NAME DOC_URL <<<"$(python -m scripts.helpers.asset_reader doc default)"
download_file "sample_data" "$DOC_NAME" "$DOC_URL"

printf "${GREEN}${BOLD}--- Asset Setup Complete ---${NC}\n\n"
