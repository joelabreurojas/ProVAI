#!/usr/bin/env bash
# This script downloads all required external assets for ProVAI,
# including the LLM model and the sample PDF document.

set -e # Exit immediately if any command fails

MODEL_DIR="models"
MODEL_NAME="phi-2.Q4_K_M.gguf"
MODEL_URL="https://huggingface.co/TheBloke/phi-2-GGUF/resolve/main/phi-2.Q4_K_M.gguf"
MODEL_SIZE_GB="~2.9GB"

DOC_DIR="sample_data"
DOC_NAME="scipy-lectures.pdf"
DOC_URL="https://scipy-lectures.org/_downloads/ScipyLectures-simple.pdf"
DOC_SIZE_MB="~15MB"

download_file() {
	local DIR=$1
	local NAME=$2
	local URL=$3
	local SIZE=$4
	local FILE_PATH="${DIR}/${NAME}"

	mkdir -p "$DIR"

	if [ -f "$FILE_PATH" ]; then
		echo "✅ Asset '$NAME' already exists in '$DIR/'. Skipping download."
	else
		echo "⏳ Asset '$NAME' not found."
		echo "   Downloading from URL (size: ${SIZE})..."

		wget -q --show-progress -O "$FILE_PATH" "$URL"

		if [ $? -eq 0 ]; then
			echo "✅ Asset '$NAME' downloaded successfully."
		else
			echo "❌ ERROR: Download for '$NAME' failed. Please check the URL and your connection."
			rm -f "$FILE_PATH"
			exit 1
		fi
	fi
}

echo "--- ProVAI Asset Setup ---"

download_file "$MODEL_DIR" "$MODEL_NAME" "$MODEL_URL" "$MODEL_SIZE_GB"
download_file "$DOC_DIR" "$DOC_NAME" "$DOC_URL" "$DOC_SIZE_MB"

echo "--- Asset Setup Complete ---"
