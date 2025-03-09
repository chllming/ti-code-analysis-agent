#!/bin/bash
# Test CI/CD Pipeline Script
# This script makes a small change to trigger the CI/CD pipeline

# Colors for better readability
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Function to print colored messages
print_message() {
  echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
  echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
  echo -e "${RED}[ERROR]${NC} $1"
}

# Check if git is available
if ! command -v git &> /dev/null; then
  print_error "Git is not installed. Please install git to continue."
  exit 1
fi

# Check if we're in a git repository
if ! git rev-parse --is-inside-work-tree &> /dev/null; then
  print_error "Not in a git repository. Please run this script from within the repository."
  exit 1
fi

# Check for uncommitted changes
if ! git diff-index --quiet HEAD --; then
  print_warning "You have uncommitted changes. Commit or stash them before running this script."
  git status
  read -p "Do you want to continue anyway? (y/n): " CONTINUE
  if [[ ${CONTINUE,,} != "y" ]]; then
    print_message "Exiting without making changes."
    exit 0
  fi
fi

# Get current branch
CURRENT_BRANCH=$(git symbolic-ref --short HEAD)
print_message "Current branch: ${CURRENT_BRANCH}"

# Check if we're on main branch
if [[ "$CURRENT_BRANCH" != "main" ]]; then
  print_warning "You are not on the main branch. The CI/CD pipeline is configured to run on pushes to main."
  read -p "Do you want to switch to main branch? (y/n): " SWITCH_BRANCH
  if [[ ${SWITCH_BRANCH,,} == "y" ]]; then
    git checkout main
    if [ $? -ne 0 ]; then
      print_error "Failed to switch to main branch."
      exit 1
    fi
  else
    print_warning "Continuing on ${CURRENT_BRANCH}. Note that the automatic CI/CD may not trigger."
  fi
fi

# Make a small change to trigger the CI/CD pipeline
TIMESTAMP=$(date "+%Y-%m-%d %H:%M:%S")
echo "# CI/CD Test: ${TIMESTAMP}" >> ci_cd_test.md
git add ci_cd_test.md

# Commit the change
git commit -m "test: Trigger CI/CD pipeline - ${TIMESTAMP}"

# Ask to push
read -p "Do you want to push this commit to trigger the CI/CD pipeline? (y/n): " PUSH
if [[ ${PUSH,,} == "y" ]]; then
  print_message "Pushing to ${CURRENT_BRANCH}..."
  git push origin ${CURRENT_BRANCH}
  if [ $? -eq 0 ]; then
    print_message "Push successful. Check the GitHub Actions tab to see the workflow run."
    print_message "GitHub Actions URL: https://github.com/your-username/ti-code-analysis-agent/actions"
  else
    print_error "Push failed."
    exit 1
  fi
else
  print_message "Changes committed but not pushed. Push manually when ready:"
  print_message "git push origin ${CURRENT_BRANCH}"
fi

print_message "Done!"
exit 0 