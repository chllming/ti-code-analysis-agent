# Setting Up Cursor for TI Template Development

## Installation and Configuration

### 1. Install Cursor

Download and install Cursor from the official website: [https://cursor.so](https://cursor.so)

Cursor is available for:
- macOS
- Windows
- Linux

### 2. Open the TI Templates Repository

Once installed, open the TI Templates repository in Cursor:

```bash
# Clone the repository if you haven't already
git clone https://github.com/your-org/ti-templates.git

# Open with Cursor
cursor ti-templates/
```

### 3. Verify AI Rules Configuration

The repository includes pre-configured AI rules in the `.cursor/rules/` directory. These rules guide Cursor's AI to follow TI development standards.

Verify that the rules are properly loaded by:
1. Opening Cursor Composer (⌘+I on macOS, Ctrl+I on Windows/Linux)
2. Typing a test prompt like: "What are the TI architecture principles?"
3. Cursor should reference the architecture guidelines from the rules

### 4. Configure Cursor Settings (Optional)

For optimal performance with TI templates, consider these recommended settings:

1. Open Cursor Settings (⌘+, on macOS, Ctrl+, on Windows/Linux)
2. Configure the following:
   - **Model**: Set to "Claude 3.5 Sonnet" or "GPT-4" for best results
   - **Context**: Enable "Use full codebase as context"
   - **Tools**: Ensure terminal access is enabled for running scripts
   - **YOLO Mode**: Disable by default (enable only when needed)

## Codebase Indexing

For Cursor to provide the best assistance, it needs to index your codebase:

1. When you first open the project, Cursor should automatically start indexing
2. If needed, manually trigger indexing:
   - Command Palette (⌘+Shift+P on macOS, Ctrl+Shift+P on Windows/Linux)
   - Type "Cursor: Index Codebase" and select the command

## Setting Up AI API Keys (Optional)

For production use or increased quota, you may want to use your own API keys:

1. Open Cursor Settings
2. Navigate to "Model Providers"
3. Add your API keys for:
   - OpenAI (for GPT models)
   - Anthropic (for Claude models)

## Integration with TI Workflow

The TI templates repository includes several scripts that work with Cursor:

1. **Project initialization**:
   ```bash
   ./scripts/ti-init.sh
   ```
   Use Cursor to customize the generated project structure

2. **Version management**:
   ```bash
   ./scripts/check-template-version.sh
   ```
   Cursor can help analyze version differences

3. **Template updates**:
   ```bash
   ./scripts/update-templates.sh
   ```
   Cursor can assist with resolving conflicts during updates

## Documentation

For detailed usage instructions, see:

1. [cursor_ai_workflow.md](./cursor_ai_workflow.md) - Complete guide for using Cursor with TI templates
2. [cursor_best_practices.md](./cursor_best_practices.md) - Best practices for Cursor AI
3. [documentation.md](./documentation.md) - General TI templates documentation

## Troubleshooting

Common issues and solutions:

1. **Indexing problems**:
   - Delete the `.cursor` directory and restart indexing
   - Ensure `.gitignore` patterns aren't excluding important files

2. **AI not following TI standards**:
   - Verify rules are properly loaded in `.cursor/rules/`
   - Reference specific rules in your prompts
   - Provide explicit instructions about TI architecture

3. **Performance issues**:
   - Try a different model in settings
   - Break large requests into smaller chunks
   - Use more specific file references with @ syntax

For more help, consult the [Cursor documentation](https://docs.cursor.com/) or reach out to the TI development team.

## Understanding the Rule Structure

The TI Templates repository uses a structured approach to Cursor AI rules:

1. **Core Rules**: Located in `.cursor/rules/` directory
   - `01-core-system.md`: Core system guidance
   - `02-architecture.md`: Architecture standards
   - `03-cursor-optimization.md`: Cursor-specific optimization
   - `04-code-quality.md`: Code quality standards
   - `05-language-specific.md`: Language-specific guidelines
   - `06-[technology]-specific.md`: Technology-specific guidelines (e.g., Python, Node.js)
   - `07-docker-guidelines.md`: Docker and containerization best practices
   - `08-testing-guidelines.md`: Comprehensive testing standards

2. **Rule Hierarchy**: Rules are processed in numerical order, with later rules building on earlier ones

3. **Technology-Specific Rules**: Custom rules for each supported technology stack
   - Created from the `cursor-technology-guidelines.md.template`
   - Customized for specific languages and frameworks

When developing new templates or modifying existing ones, ensure your changes align with these rules. 