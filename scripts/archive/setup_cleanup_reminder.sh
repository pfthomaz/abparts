#!/bin/bash

echo "========================================="
echo "Setup Cleanup Reminder"
echo "========================================="
echo ""
echo "This will create a git hook that reminds you"
echo "to run cleanup every 3 days."
echo ""

read -p "Install git hook? (y/n) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Cancelled."
    exit 1
fi

# Create the git hook
cat > .git/hooks/post-commit << 'EOF'
#!/bin/bash

# Check if cleanup is needed (every 3 days)
if [ -f .last_cleanup ]; then
    LAST_CLEANUP=$(cat .last_cleanup)
    DAYS_SINCE=$(( ($(date +%s) - $(date -d "$LAST_CLEANUP" +%s 2>/dev/null || date -j -f "%a %b %d %T %Z %Y" "$LAST_CLEANUP" +%s)) / 86400 ))
    
    if [ $DAYS_SINCE -gt 3 ]; then
        echo ""
        echo "╔════════════════════════════════════════╗"
        echo "║  🧹 Time for Project Cleanup!          ║"
        echo "╚════════════════════════════════════════╝"
        echo ""
        echo "It's been $DAYS_SINCE days since last cleanup."
        echo ""
        echo "Run: ./weekly_cleanup.sh"
        echo ""
    fi
else
    # First time - create the file
    date > .last_cleanup
fi
EOF

# Make it executable
chmod +x .git/hooks/post-commit

# Initialize the last cleanup file
date > .last_cleanup

echo ""
echo "✓ Git hook installed!"
echo ""
echo "Now, every time you commit, you'll get a reminder"
echo "if it's been more than 3 days since cleanup."
echo ""
echo "Test it now:"
echo "  ./weekly_cleanup.sh"
echo ""
