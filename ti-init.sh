#!/bin/bash
# TI Project Initialization Script (Standalone Version)
# This script runs in the root of an empty project to set up a TI project

# Function to handle errors
handle_error() {
  echo "❌ Error: $1"
  echo "Initialization failed. Please check the error message and try again."
  
  # Clean up any temporary files before exiting
  if [ -d "$TEMP_DIR" ]; then
    rm -rf "$TEMP_DIR"
  fi
  
  exit 1
}

# Ensure GitHub credentials are available
if [ -z "$(git config --global user.name)" ]; then
  handle_error "Git credentials not configured. Please run:
  git config --global user.name \"Your Name\"
  git config --global user.email \"your.email@example.com\""
fi

echo "🚀 Tailored Intelligence Project Initializer"
echo "============================================"
echo "This script will set up a new TI project in the current directory."
echo

# Get current directory name as default component name
DEFAULT_COMPONENT=$(basename $(pwd) | sed 's/^ti-//g' | sed 's/-.*//g')

# Get project details
if [ -n "$DEFAULT_COMPONENT" ] && [ "$DEFAULT_COMPONENT" != "$(basename $(pwd))" ]; then
  read -p "Component name [${DEFAULT_COMPONENT}]: " COMPONENT
  COMPONENT=${COMPONENT:-${DEFAULT_COMPONENT}}
else
  read -p "Component name (e.g., voice, pic): " COMPONENT
fi

read -p "Type (e.g., agent, pipeline): " TYPE
read -p "Technology stack (python, node, etc.): " TECH

# Create a temp directory for cloning the repository
TEMP_DIR=$(mktemp -d)
echo "📥 Downloading templates from GitHub..."

# Clone templates repository
git clone https://github.com/chllming/ti-templates.git "$TEMP_DIR" > /dev/null 2>&1 || 
  handle_error "Failed to clone templates repository. Check your internet connection and GitHub access."

# Get template version
VERSION=$(cat "$TEMP_DIR/version.txt")
if [ -z "$VERSION" ]; then
  VERSION="1.0.0" # Default version if not found
fi

echo "✅ Templates downloaded successfully (version: $VERSION)"

# Get the current date in YYYY-MM-DD format
TODAY=$(date +%Y-%m-%d)

# Create directory structure
echo "📁 Creating project directory structure..."
mkdir -p src tests docs scripts config .cursor/rules .github/workflows

# Copy and configure templates
echo "📝 Configuring project templates..."
for template in $(find "$TEMP_DIR/templates" -name "*.template"); do
  dest_file="$(basename ${template%.template})"
  cp "$template" "$dest_file"
  
  # Add version header to template files
  echo "<!-- Generated from ti-templates version $VERSION on $TODAY -->" > "$dest_file.tmp"
  cat "$dest_file" >> "$dest_file.tmp"
  mv "$dest_file.tmp" "$dest_file"
  
  # Replace variables
  sed -i.bak "s/\[COMPONENT_NAME\]/${COMPONENT}/g" "$dest_file" && rm -f "$dest_file.bak"
  sed -i.bak "s/\[TYPE\]/${TYPE}/g" "$dest_file" && rm -f "$dest_file.bak"
  sed -i.bak "s/\[TECHNOLOGY\]/${TECH}/g" "$dest_file" && rm -f "$dest_file.bak"
  sed -i.bak "s/\[DATE\]/$TODAY/g" "$dest_file" && rm -f "$dest_file.bak"
  sed -i.bak "s/\[VERSION\]/$VERSION/g" "$dest_file" && rm -f "$dest_file.bak"
done

# Move project documentation to appropriate directories
if [ -f "README.md" ]; then
  mv README.md docs/
fi

if [ -f "documentation.md" ]; then
  mv documentation.md docs/
fi

# Set up Cursor rules
echo "🖱️ Setting up Cursor configuration..."
mkdir -p .cursor/rules
cp -r "$TEMP_DIR/.cursor/rules/"* .cursor/rules/

# Copy cursor config template if it exists
if [ -f "$TEMP_DIR/templates/cursor-config-template.json" ]; then
  cp "$TEMP_DIR/templates/cursor-config-template.json" .cursor/settings.json
fi

# Copy technology-specific rules if available
if [ -n "$TECH" ]; then
  # Check if we have a template for this technology
  if [ -f "$TEMP_DIR/templates/cursor-technology-guidelines.md.template" ]; then
    # Create technology-specific rule file from template
    cp "$TEMP_DIR/templates/cursor-technology-guidelines.md.template" ".cursor/rules/06-${TECH}-specific.md"
    
    # Replace placeholders
    sed -i.bak "s/\[TECHNOLOGY\]/${TECH^}/g" ".cursor/rules/06-${TECH}-specific.md" && rm -f ".cursor/rules/06-${TECH}-specific.md.bak"
    echo "✅ Created ${TECH}-specific cursor rules from template"
  else
    echo "⚠️ No ${TECH}-specific template found. Creating generic rules."
    # Create minimal placeholder
    echo "# ${TECH^} Specific Guidelines" > ".cursor/rules/06-${TECH}-specific.md"
    echo "" >> ".cursor/rules/06-${TECH}-specific.md"
    echo "## Best Practices" >> ".cursor/rules/06-${TECH}-specific.md"
    echo "- Follow standard ${TECH} conventions" >> ".cursor/rules/06-${TECH}-specific.md"
    echo "- Ensure proper error handling in all ${TECH} code" >> ".cursor/rules/06-${TECH}-specific.md"
    echo "- Write comprehensive tests for ${TECH} components" >> ".cursor/rules/06-${TECH}-specific.md"
  fi
fi

# Create local Cursor setup guide
cp "$TEMP_DIR/CURSOR.md" ./CURSOR.md 2>/dev/null || 
  echo "⚠️ Warning: CURSOR.md not found in template repository"

mkdir -p docs
cp "$TEMP_DIR/DOCUMENTATION.md" ./docs/cursor_best_practices.md 2>/dev/null || 
  echo "⚠️ Warning: DOCUMENTATION.md not found in template repository"

# Set up Docker files
echo "🐳 Setting up Docker configuration..."
if [ -f "$TEMP_DIR/docker/${TECH}.Dockerfile" ]; then
  cp "$TEMP_DIR/docker/${TECH}.Dockerfile" ./Dockerfile
else
  cp "$TEMP_DIR/docker/generic.Dockerfile" ./Dockerfile 2>/dev/null || 
    echo "⚠️ Warning: No suitable Dockerfile found in template repository"
fi

cp "$TEMP_DIR/docker/docker-compose.yml" ./ 2>/dev/null
cp "$TEMP_DIR/docker/.dockerignore" ./ 2>/dev/null

# Copy GitHub workflows
echo "🔄 Setting up CI/CD workflows..."
mkdir -p .github/workflows
cp "$TEMP_DIR/github-workflows/ci.yml" ./.github/workflows/ 2>/dev/null

# Copy utility scripts
echo "📜 Copying utility scripts..."
mkdir -p ./scripts
cp "$TEMP_DIR/scripts/docker-utils.sh" ./scripts/ 2>/dev/null
chmod +x ./scripts/docker-utils.sh 2>/dev/null || true

# Copy versioning and maintenance scripts
echo "📜 Copying maintenance scripts..."
cp "$TEMP_DIR/scripts/check-template-version.sh" ./scripts/ 2>/dev/null
chmod +x ./scripts/check-template-version.sh 2>/dev/null || true

cp "$TEMP_DIR/scripts/update-templates.sh" ./scripts/ 2>/dev/null
chmod +x ./scripts/update-templates.sh 2>/dev/null || true

# Copy the new ti-update.sh script if it exists
cp "$TEMP_DIR/scripts/ti-update.sh" ./scripts/ 2>/dev/null
chmod +x ./scripts/ti-update.sh 2>/dev/null || true

# Copy the GitHub push script if it exists
cp "$TEMP_DIR/scripts/push-to-github.sh" ./scripts/ 2>/dev/null
chmod +x ./scripts/push-to-github.sh 2>/dev/null || true

# Create .env.example file
echo "📄 Creating environment configuration..."
cat > .env.example << EOF
# Environment Configuration for ti-${COMPONENT}-${TYPE}

# Application settings
DEBUG=false
LOG_LEVEL=INFO

# Service settings
PORT=8000

# Add other configuration variables here
EOF

# Create .cursorignore file
cat > .cursorignore << EOL
# Cursor ignore file - prevents indexing of specified patterns

# Dependencies
node_modules/
venv/
.venv/
__pycache__/
*.pyc

# Build artifacts
dist/
build/
*.min.js
*.min.css
*.map

# Large data files
*.csv
*.parquet
*.sqlite
*.db

# Logs and temporary files
logs/
*.log
.DS_Store
.cache/
tmp/

# Sensitive information
.env
.env.*
credentials/
*_key.*
*_token.*
EOL

# Create .ti-templates metadata file
cat > .ti-templates << EOF
# Tailored Intelligence Templates Metadata
version=$VERSION
component=$COMPONENT
type=$TYPE
technology=$TECH
date_created=$TODAY
repository_url=https://github.com/chllming/ti-templates.git
EOF

# Initialize git repository
if [ ! -d ".git" ]; then
  echo "🔄 Initializing Git repository..."
  git init > /dev/null
  git add .
  git commit -m "Initial project setup from ti-templates version $VERSION" > /dev/null
  echo "✅ Git repository initialized"
else
  echo "⚠️ Git repository already exists. Not initializing."
fi

# Clean up temporary directory
rm -rf "$TEMP_DIR"
# Remove the initialization script itself
echo "🧹 Cleaning up..."

echo
echo "✅ Project initialization complete!"
echo "Template version: $VERSION"
echo
echo "Next steps:"
echo "1. Review and update the generated files"
echo "2. Create remote repository on GitHub:"
echo "   https://github.com/new?name=ti-${COMPONENT}-${TYPE}"
echo "3. Connect your local repository:"
echo "   git remote add origin https://github.com/chllming/ti-${COMPONENT}-${TYPE}.git"
echo "   git push -u origin main"
echo
echo "To check for template updates in the future, run:"
echo "   ./scripts/check-template-version.sh"
echo
echo "🚀 Happy coding!"

# Finally, remove this script so it doesn't remain in the project
# When this script is run directly, the removal is scheduled to happen after script exit
if [ "$0" = "./ti-init-standalone.sh" ]; then
  trap "rm -f ./ti-init-standalone.sh" EXIT
fi 