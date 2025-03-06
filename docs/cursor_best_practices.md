# Tailored Intelligence Templates Documentation

## Overview

The `ti-templates` repository provides standardized templates, configuration files, and development guidelines for all Tailored Intelligence (TI) components. This centralized approach ensures consistent development patterns, architectural alignment, quality standards, and integration approaches across the entire TI ecosystem.

## Purpose

The purpose of this repository is to:

1. **Standardize Development**: Ensure all TI components follow the same patterns and practices
2. **Accelerate Setup**: Reduce the time required to initialize new components
3. **Enforce Quality**: Maintain consistent quality standards across all projects
4. **Facilitate Integration**: Ensure components can interact seamlessly
5. **Guide Development**: Provide clear direction through Cursor AI rules and templates

## Repository Structure

```
ti-templates/
├── .cursor/                   # Cursor AI configuration
│   └── rules/                 # Cursor AI development guidelines
├── templates/                 # Project file templates
│   ├── README.md.template     # Project README template
│   ├── plan.md.template       # Development planning template
│   ├── progress.md.template   # Progress tracking template
│   ├── documentation.md.template  # Documentation template
│   ├── testing.md.template    # Testing documentation template
│   └── step_completion_checklist.md.template  # Task completion checklist
├── docker/                    # Docker configuration templates
│   ├── python.Dockerfile      # Python Dockerfile template
│   ├── node.Dockerfile        # Node.js Dockerfile template
│   ├── generic.Dockerfile     # Generic Dockerfile template
│   ├── docker-compose.yml     # Docker Compose template
│   └── .dockerignore          # Docker ignore template
├── github-workflows/          # GitHub Actions workflow templates
│   └── ci.yml                 # CI pipeline workflow
└── scripts/                   # Utility scripts
    ├── docker-utils.sh        # Docker utility functions
    └── ti-init.sh             # Project initialization script
```

## Template Components in Detail

### Cursor Rules

Cursor rules provide guidance to Cursor AI for code generation and project development. These rules are organized into categories:

1. **General Rules (general.mdc)**
   - Architecture alignment with TI's two-pillar system
   - Step-based implementation approach
   - Documentation standards
   - Source control practices

2. **Code Quality Rules (code_quality.mdc)**
   - Code structure and organization
   - Naming conventions
   - Documentation requirements
   - Error handling practices
   - Performance considerations
   - Security best practices

3. **Testing Rules (testing.mdc)**
   - Test coverage requirements
   - Test types and implementation
   - Test-driven development guidelines
   - Test structure
   - Testing edge cases

4. **Docker Rules (docker.mdc)**
   - Dockerfile structure guidelines
   - Base image selection guidance
   - Security practices
   - Environment variable handling
   - Build optimization techniques
   - Testing in Docker environments

5. **Language-Specific Rules**
   - Technology-specific best practices
   - Framework and library recommendations
   - Common patterns and approaches
   - Performance considerations
   - Error handling techniques

### Project Templates

The templates directory contains standardized files for all TI projects:

1. **plan.md.template**
   - Structured development plan with phases
   - Task breakdown with test requirements
   - Acceptance criteria
   - Dependency mapping
   - Risk assessment

2. **progress.md.template**
   - Current status tracking
   - Completed tasks documentation
   - In-progress task monitoring
   - Challenge tracking
   - Testing result documentation

3. **README.md.template**
   - Project overview
   - Architecture description
   - Feature listing
   - Installation instructions
   - Usage examples
   - API reference
   - Development workflow

4. **documentation.md.template**
   - Comprehensive component documentation
   - Interface definitions
   - Integration points
   - Design patterns
   - Docker configuration
   - Performance and security considerations
   - Troubleshooting guidelines

5. **testing.md.template**
   - Test framework documentation
   - Test categories and organization
   - Test fixtures and data
   - Test-to-task mapping
   - Coverage reporting
   - Continuous integration
   - Test design guidelines

6. **step_completion_checklist.md.template**
   - Implementation verification checklist
   - Testing verification checklist
   - Documentation verification checklist
   - Integration verification checklist
   - Docker verification checklist
   - Performance verification checklist
   - Security verification checklist

### Docker Configuration

Docker files ensure consistent containerization:

1. **Dockerfiles**
   - Multi-stage builds for efficiency
   - Security best practices
   - Environment configuration
   - User permissions
   - Optimized layer caching

2. **docker-compose.yml**
   - Service definitions
   - Volume mounting
   - Environment configuration
   - Network setup
   - Testing configuration

3. **.dockerignore**
   - Exclusion patterns for Docker context
   - Security-focused exclusions
   - Performance-optimizing exclusions

### GitHub Workflows

CI/CD configuration for automated testing and deployment:

1. **ci.yml**
   - Linting steps
   - Testing process
   - Build validation
   - Coverage reporting
   - Docker image building and testing

### Utility Scripts

Helper scripts for common operations:

1. **docker-utils.sh**
   - Docker build functionality
   - Test execution in containers
   - Development environment management
   - Production deployment helpers
   - Cleanup utilities

2. **ti-init.sh**
   - Project initialization automation
   - Template application with customization
   - Git repository setup
   - Directory structure creation

## Template Variables

Templates use placeholders that get replaced during project initialization:

| Variable | Description | Example |
|----------|-------------|---------|
| `[COMPONENT_NAME]` | The specific TI component | voice, pic, research |
| `[TYPE]` | The component type | agent, pipeline, server |
| `[TECHNOLOGY]` | Primary technology stack | python, node |
| `[DATE]` | Current date | YYYY-MM-DD format |

## Using the Templates

### Automated Initialization

The recommended approach to start a new TI project is using the initialization script:

```bash
./scripts/ti-init.sh
```

The script will:
1. Prompt for component details
2. Create the directory structure
3. Apply templates with customized values
4. Initialize a Git repository
5. Set up Cursor rules for development guidance

### Manual Template Application

For more customized setups or adding templates to existing projects:

```bash
# Copy template
cp templates/plan.md.template my-project/plan.md

# Replace variables
sed -i "s/\[COMPONENT_NAME\]/voice/g" my-project/plan.md
sed -i "s/\[TYPE\]/agent/g" my-project/plan.md
sed -i "s/\[TECHNOLOGY\]/python/g" my-project/plan.md
sed -i "s/\[DATE\]/$(date +%Y-%m-%d)/g" my-project/plan.md
```

## Extending the Templates

This section provides guidelines for expanding the template system with new components or modifications.

### Adding New Language Support

To add support for a new programming language:

1. **Create a language-specific rules file**:
   ```bash
   # Use the template to create a new language-specific rule file
   cp templates/cursor-technology-guidelines.md.template .cursor/rules/06-[language]-specific.md
   # Edit the file to customize for the specific language
   sed -i "s/\[TECHNOLOGY\]/[Language Name]/g" .cursor/rules/06-[language]-specific.md
   ```

2. **Create a language-specific Dockerfile**:
   ```bash
   cp docker/generic.Dockerfile docker/[language].Dockerfile
   ```

3. **Update the initialization script** to recognize the new language:
   - Modify `ti-init.sh` to handle the new language option
   - Add any language-specific setup steps

4. **Create language-specific templates** if needed:
   - Special configuration files (e.g., `tsconfig.json` for TypeScript)
   - Build tool configurations
   - Testing framework setups

### Adding New Template Types

To add a new template type:

1. **Create the template file** with appropriate placeholders:
   ```bash
   touch templates/[new_template_name].template
   ```

2. **Update the initialization script** to copy and configure the new template:
   - Add the template to the list of files processed in `ti-init.sh`

3. **Update documentation** to reflect the new template type

### Modifying Existing Templates

When modifying existing templates:

1. **Maintain backward compatibility** when possible
2. **Document breaking changes** clearly
3. **Version the templates** to allow tracking of changes
4. **Update all relevant files** to maintain consistency:
   - If changing architecture patterns in one file, update related templates
   - Ensure Cursor rules align with template changes

### Version Control for Templates

Consider implementing a versioning system for templates:

1. **Add version metadata** to templates:
   ```markdown
   <!-- Template version: 1.2.0 -->
   ```

2. **Create an update script** to help existing projects adopt changes:
   ```bash
   ./scripts/ti-update-templates.sh [new-version]
   ```

3. **Maintain a changelog** for template modifications:
   ```markdown
   # Template Changelog
   
   ## Version 1.2.0
   - Added security checklist to step_completion_checklist.md
   - Updated Docker best practices in docker.mdc
   - Enhanced test requirements in testing.mdc
   ```

## Template Guidelines

When creating or modifying templates, follow these guidelines:

1. **Clarity**: Templates should be clear and well-documented
2. **Flexibility**: Allow for customization where appropriate
3. **Consistency**: Maintain consistent patterns across all templates
4. **Completeness**: Include all necessary components
5. **Focus**: Each template should have a single responsibility
6. **Architecture Alignment**: Ensure all templates align with TI architecture

## Cursor Prompt Usage

The repository includes a comprehensive Cursor prompt for initializing projects:

1. **Open a new directory** in Cursor
2. **Paste the project initialization prompt**
3. **Fill in the placeholders** for component details
4. **Let Cursor guide** the creation of all necessary files
5. **Review and customize** the generated files

## Advanced Template Customization

For projects requiring advanced customization:

### Template Extensions

Create specialized extensions of base templates:

```bash
mkdir -p templates/extensions/ml-agent/
cp templates/plan.md.template templates/extensions/ml-agent/plan.md.template
# Add ML-specific tasks and requirements
```

### Component-Specific Templates

Develop templates tailored to specific TI components:

```bash
mkdir -p templates/voice-agent/
# Create voice-agent specialized templates
```

### Template Composition

Implement a system for composing templates:

```bash
# Script to combine multiple template fragments
./scripts/compose-template.sh base_template.md extension1.md extension2.md > combined_template.md
```

## Testing Templates

Ensure templates work correctly by:

1. **Creating test initialization processes**:
   ```bash
   ./scripts/test-templates.sh --component voice --type agent --technology python
   ```

2. **Validating generated files**:
   ```bash
   ./scripts/validate-project.sh ./test-projects/ti-voice-agent/
   ```

3. **Checking for template consistency**:
   ```bash
   ./scripts/check-template-consistency.sh
   ```

## GitHub Actions for Templates

Consider implementing GitHub Actions workflows for the template repository:

1. **Template Validation**: Verify templates are well-formed
2. **Test Template Application**: Test applying templates to sample projects
3. **Documentation Generation**: Automatically update documentation
4. **Version Tracking**: Tag releases when templates change significantly

## Template Update Process

When updating templates, follow this process:

1. **Draft changes** in a feature branch
2. **Test changes** by initializing test projects
3. **Update documentation** to reflect changes
4. **Update version numbers** in affected templates
5. **Submit a pull request** with detailed description
6. **Merge after approval** and testing

## Conclusion

The `ti-templates` repository provides a robust foundation for consistent development across the Tailored Intelligence architecture. By following the guidelines in this documentation, you can effectively use, maintain, and extend the template system to support the evolving needs of the TI ecosystem.

This centralized approach to templates ensures that all TI components benefit from shared best practices, consistent structures, and seamless integration capabilities, enabling faster development without sacrificing quality or architectural integrity.
