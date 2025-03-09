#!/bin/bash

# Test Cursor IDE Setup Script
# Validates that the Cursor IDE configuration meets project requirements

set -e
echo "🔍 Testing Cursor IDE Setup..."

# Check if .cursor directory exists
if [ ! -d ".cursor" ]; then
  echo "❌ .cursor directory not found!"
  exit 1
else
  echo "✅ .cursor directory found"
fi

# Check if settings.json exists and is valid JSON
if [ ! -f ".cursor/settings.json" ]; then
  echo "❌ .cursor/settings.json not found!"
  exit 1
else
  if ! jq -e . ".cursor/settings.json" > /dev/null 2>&1; then
    echo "❌ .cursor/settings.json is not valid JSON!"
    exit 1
  else
    echo "✅ .cursor/settings.json exists and is valid JSON"
  fi
fi

# Check if rules directory exists and has required files
if [ ! -d ".cursor/rules" ]; then
  echo "❌ .cursor/rules directory not found!"
  exit 1
else
  echo "✅ .cursor/rules directory found"
  
  # Check for required rule files
  REQUIRED_FILES=(
    "01-core-system.md"
    "02-architecture.md"
    "03-cursor-optimization.md"
    "04-code-quality.md"
    "05-language-specific.md"
    "06-python-specific.md"
    "07-docker-guidelines.md"
    "08-testing-guidelines.md"
  )
  
  for file in "${REQUIRED_FILES[@]}"; do
    if [ ! -f ".cursor/rules/$file" ]; then
      echo "❌ Required rule file .cursor/rules/$file not found!"
      exit 1
    else
      echo "✅ Found rule file: $file"
    fi
  done
fi

# Check if .cursorignore exists
if [ ! -f ".cursorignore" ]; then
  echo "❌ .cursorignore file not found!"
  exit 1
else
  echo "✅ .cursorignore file found"
fi

# Verify tailoredIntelligence section in settings.json
if ! jq -e '.cursor.tailoredIntelligence.projectType != "[TYPE]"' ".cursor/settings.json" > /dev/null 2>&1; then
  echo "❌ tailoredIntelligence section not properly configured in settings.json!"
  exit 1
else
  echo "✅ tailoredIntelligence section is properly configured"
fi

# Verify that Python is specified as the technology
if ! jq -e '.cursor.tailoredIntelligence.technology == "Python"' ".cursor/settings.json" > /dev/null 2>&1; then
  echo "❌ Python not specified as technology in settings.json!"
  exit 1
else
  echo "✅ Python is specified as the technology"
fi

# Verify that rulesEnabled is set to true
if ! jq -e '.cursor.ai.rulesEnabled == true' ".cursor/settings.json" > /dev/null 2>&1; then
  echo "❌ Rules are not enabled in settings.json!"
  exit 1
else
  echo "✅ Rules are enabled in settings.json"
fi

# Verify that rulesDirectory is set correctly
if ! jq -e '.cursor.ai.rulesDirectory == ".cursor/rules"' ".cursor/settings.json" > /dev/null 2>&1; then
  echo "❌ Rules directory not correctly configured in settings.json!"
  exit 1
else
  echo "✅ Rules directory is correctly configured"
fi

echo "✨ All checks passed! Cursor IDE is properly configured for development." 