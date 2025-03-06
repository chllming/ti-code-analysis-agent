#!/bin/bash
# Script to update project templates to the latest version

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

# Read project metadata
PROJECT_VERSION=$(grep "^version=" .ti-templates | cut -d'=' -f2)
COMPONENT=$(grep "^component=" .ti-templates | cut -d'=' -f2)
TYPE=$(grep "^type=" .ti-templates | cut -d'=' -f2)
TECH=$(grep "^technology=" .ti-templates | cut -d'=' -f2)
DATE_CREATED=$(grep "^date_created=" .ti-templates | cut -d'=' -f2)

if [ -z "$PROJECT_VERSION" ] || [ -z "$COMPONENT" ] || [ -z "$TYPE" ] || [ -z "$TECH" ]; then
    echo "Error: Could not read all required metadata from .ti-templates file."
    exit 1
fi

echo "Current project template version: $PROJECT_VERSION"
echo "Project details: ${COMPONENT} ${TYPE} (${TECH})"

# Create temporary directory for fetching latest templates
TEMP_DIR=$(mktemp -d)
trap 'rm -rf "$TEMP_DIR"' EXIT

# Fetch latest templates
echo "Fetching latest templates..."
git clone --quiet --depth 1 "$REPO_URL" "$TEMP_DIR" > /dev/null 2>&1
if [ $? -ne 0 ]; then
    echo "Error: Failed to fetch latest templates."
    exit 1
fi

# Read latest version
LATEST_VERSION=$(cat "$TEMP_DIR/version.txt")
if [ -z "$LATEST_VERSION" ]; then
    echo "Error: Could not determine latest template version."
    exit 1
fi

echo "Latest template version: $LATEST_VERSION"

# Create backup directory
BACKUP_DIR="./template_update_backup_$(date +%Y%m%d_%H%M%S)"
mkdir -p "$BACKUP_DIR"
echo "Creating backup of existing files in $BACKUP_DIR"

# Update .cursor rules
if [ -d ".cursor/rules" ]; then
    echo "Updating Cursor rules..."
    # Backup existing rules
    mkdir -p "$BACKUP_DIR/.cursor/rules"
    cp -a .cursor/rules/. "$BACKUP_DIR/.cursor/rules/"
    
    # Copy new rules
    cp -a "$TEMP_DIR/.cursor/rules"/*.md .cursor/rules/
    
    # Handle technology-specific rules
    if [ -n "$TECH" ]; then
        # Check if there's a technology-specific rule in the old cursor-rules format
        if [ -f "$TEMP_DIR/cursor-rules-old/${TECH}_specific.mdc" ]; then
            echo "Found ${TECH}-specific rules in old format, converting to new format..."
            # Convert the old format rule file to the new format
            echo "# ${TECH^} Specific Guidelines" > .cursor/rules/06-${TECH}-specific.md
            echo "" >> .cursor/rules/06-${TECH}-specific.md
            cat "$TEMP_DIR/cursor-rules-old/${TECH}_specific.mdc" | sed 's/^#/##/g' >> .cursor/rules/06-${TECH}-specific.md
        elif [ ! -f ".cursor/rules/06-${TECH}-specific.md" ]; then
            # Create a new technology-specific rule file if one doesn't exist
            echo "Creating new ${TECH}-specific rules..."
            echo "# ${TECH^} Specific Guidelines" > .cursor/rules/06-${TECH}-specific.md
            echo "" >> .cursor/rules/06-${TECH}-specific.md
            echo "## Best Practices" >> .cursor/rules/06-${TECH}-specific.md
            echo "- Follow standard ${TECH} conventions" >> .cursor/rules/06-${TECH}-specific.md
            echo "- Ensure proper error handling in all ${TECH} code" >> .cursor/rules/06-${TECH}-specific.md
            echo "- Write comprehensive tests for ${TECH} components" >> .cursor/rules/06-${TECH}-specific.md
        fi
    fi
    
    # Update Cursor documentation
    echo "Updating Cursor documentation..."
    mkdir -p docs
    cp "$TEMP_DIR/cursor_setup.md" CURSOR.md 2>/dev/null || true
    cp "$TEMP_DIR/cursor_best_practices.md" docs/cursor_best_practices.md 2>/dev/null || true
    if [ -f "$TEMP_DIR/cursor_ai_workflow.md" ]; then
        cp "$TEMP_DIR/cursor_ai_workflow.md" docs/cursor_ai_workflow.md 2>/dev/null || true
    fi
fi

# Update GitHub workflows
if [ -d ".github/workflows" ]; then
    echo "Updating GitHub workflows..."
    # Backup existing workflows
    mkdir -p "$BACKUP_DIR/.github/workflows"
    cp -a .github/workflows/. "$BACKUP_DIR/.github/workflows/"
    
    # Copy new workflows
    cp -a "$TEMP_DIR/github-workflows"/* .github/workflows/
fi

# Update utility scripts
if [ -d "scripts" ]; then
    echo "Updating utility scripts..."
    # Backup existing scripts
    mkdir -p "$BACKUP_DIR/scripts"
    cp -a scripts/. "$BACKUP_DIR/scripts/"
    
    # Copy new scripts (excluding this update script itself)
    for script in "$TEMP_DIR/scripts"/*; do
        base_name=$(basename "$script")
        if [[ "$base_name" != "update-templates.sh" && "$base_name" != "check-template-version.sh" ]]; then
            cp "$script" "scripts/"
            chmod +x "scripts/$base_name"
        fi
    done
    
    # Copy these versioning scripts if they don't already exist
    if [ ! -f "scripts/check-template-version.sh" ]; then
        cp "$TEMP_DIR/scripts/check-template-version.sh" "scripts/"
        chmod +x "scripts/check-template-version.sh"
    fi
    cp "$TEMP_DIR/scripts/update-templates.sh" "scripts/update-templates.sh.new"
fi

# Update Docker configuration
if [ -f "Dockerfile" ] && [ -f "$TEMP_DIR/docker/${TECH}.Dockerfile" ]; then
    echo "Updating Docker configuration..."
    # Backup existing Docker files
    mkdir -p "$BACKUP_DIR/docker"
    [ -f "Dockerfile" ] && cp "Dockerfile" "$BACKUP_DIR/docker/"
    [ -f "docker-compose.yml" ] && cp "docker-compose.yml" "$BACKUP_DIR/docker/"
    [ -f ".dockerignore" ] && cp ".dockerignore" "$BACKUP_DIR/docker/"
    
    # Offer to update Docker files
    read -p "Update Dockerfile? This may overwrite customizations. (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        cp "$TEMP_DIR/docker/${TECH}.Dockerfile" "Dockerfile"
    fi
    
    read -p "Update docker-compose.yml? This may overwrite customizations. (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        cp "$TEMP_DIR/docker/docker-compose.yml" "docker-compose.yml"
    fi
    
    read -p "Update .dockerignore? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        cp "$TEMP_DIR/docker/.dockerignore" ".dockerignore"
    fi
fi

# Update .ti-templates file
echo "Updating .ti-templates metadata file..."
cat > .ti-templates << EOF
# Tailored Intelligence Templates Metadata
version=$LATEST_VERSION
component=$COMPONENT
type=$TYPE
technology=$TECH
date_created=$DATE_CREATED
date_updated=$(date +%Y-%m-%d)
EOF

echo
echo "Template update completed."
echo "Original files backed up to: $BACKUP_DIR"
echo

# Notify about the update script itself
if [ -f "scripts/update-templates.sh.new" ]; then
    echo "A new version of the update-templates.sh script is available."
    echo "To update this script (recommended), run:"
    echo "  mv scripts/update-templates.sh.new scripts/update-templates.sh"
    echo "  chmod +x scripts/update-templates.sh"
    echo
fi

echo "To verify the update, run your tests and ensure everything still works."
echo "If you encounter issues, you can restore the backup files or manually merge changes."

chmod +x "$(dirname "$0")/update-templates.sh" 