#!/bin/bash

# Fix git configuration and push to GitHub
echo "Setting up git configuration..."

# Kill any hanging git processes
pkill -f git 2>/dev/null || true
sleep 2

# Configure git
git config --global user.name "ICGNU3"
git config --global user.email "icgnu3@example.com"
git config --global init.defaultBranch main

# Add files and commit
echo "Adding files to git..."
git add . 2>/dev/null || {
    echo "Removing git locks..."
    rm -f .git/index.lock .git/config.lock 2>/dev/null || true
    sleep 1
    git add .
}

# Commit changes
git commit -m "OuRhizome contact intelligence CRM platform - Initial commit" 2>/dev/null || echo "Already committed or no changes"

# Add remote (if not exists)
git remote add origin https://github.com/ICGNU3/ourhizome-protocol.git 2>/dev/null || git remote set-url origin https://github.com/ICGNU3/ourhizome-protocol.git

# Push to GitHub
echo "Pushing to GitHub..."
if [ ! -z "$GITHUB_TOKEN" ]; then
    git push -u https://$GITHUB_TOKEN@github.com/ICGNU3/ourhizome-protocol.git main
else
    echo "Please set GITHUB_TOKEN environment variable"
    echo "export GITHUB_TOKEN=your_token_here"
    echo "Then run: bash push_to_github.sh"
fi