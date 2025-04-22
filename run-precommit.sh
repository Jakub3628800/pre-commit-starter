#!/bin/bash

# Set the maximum number of attempts
MAX_ATTEMPTS=5
ATTEMPT=1

echo "Running formatting tools until they stabilize..."

# Define formatter hooks
FORMATTERS=("trailing-whitespace" "end-of-file-fixer" "ruff-format" "black" "isort")

# Loop until formatting is stable or we reach maximum attempts
while [ $ATTEMPT -le $MAX_ATTEMPTS ]; do
  echo "🔄 Attempt $ATTEMPT of $MAX_ATTEMPTS"

  # Run each formatting hook separately
  for HOOK in "${FORMATTERS[@]}"; do
    echo "Running $HOOK..."
    pre-commit run "$HOOK" --all-files || true
  done

  # Add all changes
  git add .

  # Check if running the formatters again would make changes
  CHANGES_DETECTED=false
  for HOOK in "${FORMATTERS[@]}"; do
    if pre-commit run "$HOOK" --all-files | grep -q "Failed"; then
      CHANGES_DETECTED=true
      break
    fi
  done

  if [ "$CHANGES_DETECTED" = true ]; then
    ATTEMPT=$((ATTEMPT + 1))
    git add .
  else
    echo "✅ Formatting stabilized!"
    break
  fi
done

if [ $ATTEMPT -gt $MAX_ATTEMPTS ]; then
  echo "⚠️ Warning: Could not stabilize formatting after $MAX_ATTEMPTS attempts."
fi

# Now run all pre-commit hooks
echo "Running all pre-commit checks..."
pre-commit run --all-files

# Print success message if everything passes
if pre-commit run --all-files; then
  echo "✅ All pre-commit checks passed!"
  exit 0
else
  echo "❌ Some pre-commit checks still failed."
  exit 1
fi
