# Cursor-Optimized Development Guidelines

## Cursor Composer Usage
- When using Cursor Composer for complex tasks, break them into logical steps
- Provide clear, specific instructions with detailed requirements
- Reference existing files and documentation using @ syntax
- Specify constraints and architectural requirements up front
- Verify generated code with tests before accepting

## Contextual References
- Use @ syntax to reference files rather than copying code into prompts
- Attach relevant documentation when referencing external libraries
- Define clear boundaries for code generation
- Reference architecture diagrams or documents for context when applicable

## Rules for AI-Generated Code
- All AI-generated code must follow our style guides and conventions
- Generated code must include appropriate error handling
- Add proper documentation comments for all public interfaces
- Ensure proper test coverage for all new functionality
- Follow security best practices and avoid common vulnerabilities

## Composer Agent Mode
- Leverage Agent mode for complex multi-file changes
- Use Edit mode for simple, targeted modifications
- For debugging, provide clear error messages and expected behavior
- When refactoring, specify the patterns to follow and constraints to maintain

## Code Review Process
- Use Cursor to help review code by asking it to analyze changes
- Leverage Composer to suggest improvements to existing code
- Ask the AI to explain complex code sections when necessary
- Use Cursor for generating test cases based on implementation

## Continuous Improvement
- Use Cursor to help document code and architecture decisions
- Ask Cursor to suggest optimizations for existing code
- Utilize the AI for exploring alternative implementation approaches
- Incorporate Cursor feedback into planning and architecture decisions 