#!/bin/bash
# Script to check if the current project is using the latest template version

# Default repository URL
REPO_URL="https://github.com/tailored-intelligence/ti-templates.git"

# Override with user-provided repo URL
if [ "$#" -eq 1 ]; then
    REPO_URL=$1
fi

# Check if .ti-templates file exists in the current directory
if [ ! -f ".ti-templates" ]; then
    echo "Error: No .ti-templates file found. This project may not have been initialized with ti-templates."
    exit 1
fi

# Read current project version
PROJECT_VERSION=$(grep "^version=" .ti-templates | cut -d'=' -f2)
if [ -z "$PROJECT_VERSION" ]; then
    echo "Error: Could not determine project template version from .ti-templates file."
    exit 1
fi

echo "Current project template version: $PROJECT_VERSION"

# Create temporary directory for fetching latest version
TEMP_DIR=$(mktemp -d)
trap 'rm -rf "$TEMP_DIR"' EXIT

# Fetch latest version from repository
echo "Fetching latest template version information..."
git clone --quiet --depth 1 "$REPO_URL" "$TEMP_DIR" > /dev/null 2>&1
if [ $? -ne 0 ]; then
    echo "Error: Failed to fetch latest template information."
    exit 1
fi

# Read latest version
LATEST_VERSION=$(cat "$TEMP_DIR/version.txt")
if [ -z "$LATEST_VERSION" ]; then
    echo "Error: Could not determine latest template version."
    exit 1
fi

echo "Latest template version: $LATEST_VERSION"

# Compare versions (simple semantic version comparison)
PROJECT_MAJOR=$(echo $PROJECT_VERSION | cut -d. -f1)
PROJECT_MINOR=$(echo $PROJECT_VERSION | cut -d. -f2)
PROJECT_PATCH=$(echo $PROJECT_VERSION | cut -d. -f3)

LATEST_MAJOR=$(echo $LATEST_VERSION | cut -d. -f1)
LATEST_MINOR=$(echo $LATEST_VERSION | cut -d. -f2)
LATEST_PATCH=$(echo $LATEST_VERSION | cut -d. -f3)

OUTDATED=false

if [ $PROJECT_MAJOR -lt $LATEST_MAJOR ]; then
    OUTDATED=true
elif [ $PROJECT_MAJOR -eq $LATEST_MAJOR ] && [ $PROJECT_MINOR -lt $LATEST_MINOR ]; then
    OUTDATED=true
elif [ $PROJECT_MAJOR -eq $LATEST_MAJOR ] && [ $PROJECT_MINOR -eq $LATEST_MINOR ] && [ $PROJECT_PATCH -lt $LATEST_PATCH ]; then
    OUTDATED=true
fi

if [ "$OUTDATED" = true ]; then
    echo "Your project is using an outdated template version."
    echo "Consider updating to the latest version using the update-templates.sh script:"
    echo "  ./scripts/update-templates.sh"
    
    # If changelog is available, show recent changes
    if [ -f "$TEMP_DIR/CHANGELOG.md" ]; then
        echo
        echo "Recent changes in newer versions:"
        echo "--------------------------------"
        current_version_found=false
        in_unreleased=false
        
        while IFS= read -r line; do
            if [[ $line == "## [Unreleased]"* ]]; then
                in_unreleased=true
                echo "$line"
                continue
            fi
            
            if [[ $line == "## [$PROJECT_VERSION]"* ]]; then
                current_version_found=true
                break
            fi
            
            if [[ $line == "## ["* ]] && [ "$in_unreleased" = true ]; then
                in_unreleased=false
                echo "$line"
                continue
            fi
            
            if [ "$in_unreleased" = true ] || [[ $line == "### "* ]] || [[ $line == "- "* ]]; then
                echo "$line"
            fi
        done < "$TEMP_DIR/CHANGELOG.md"
    fi
    
    exit 2
else
    echo "Your project is using the latest template version. No update needed."
    exit 0
fi

chmod +x "$(dirname "$0")/check-template-version.sh" 