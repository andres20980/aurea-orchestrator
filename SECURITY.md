# Security Policy

## Supported Versions

| Version | Supported          |
| ------- | ------------------ |
| 0.1.x   | :white_check_mark: |

## Security Considerations

### Template Rendering

The Aurea Orchestrator Prompt Registry uses Jinja2 for template rendering. This is an intentional design choice to enable dynamic prompt generation with variable substitution.

**Key Security Points:**

1. **Trusted Users Only**: The template creation and management endpoints should only be accessible to trusted users. Templates can execute Jinja2 expressions, so only authorized personnel should be allowed to create or modify templates.

2. **Input Validation**: The system validates:
   - YAML syntax correctness
   - Jinja2 template syntax
   - Variable rendering with StrictUndefined mode to catch undefined variables

3. **No Code Execution**: Templates do not have access to Python code execution capabilities by default. However, Jinja2 templates can access object attributes and methods.

4. **Recommended Security Measures**:
   - Implement authentication and authorization for all API endpoints
   - Use role-based access control (RBAC) to restrict template creation to trusted users
   - Log all template creation, modification, and deletion operations
   - Implement rate limiting on API endpoints
   - Consider implementing a template approval workflow for production environments
   - Use HTTPS in production deployments
   - Regularly audit stored templates for suspicious content

### Database Security

- The default configuration uses SQLite with local file storage
- For production deployments:
  - Use a proper database server (PostgreSQL, MySQL)
  - Implement database encryption at rest
  - Use connection pooling with appropriate limits
  - Apply least-privilege principles for database access

### API Security

**Production Deployment Recommendations:**

1. **Authentication**: Implement JWT or OAuth2 authentication
2. **Authorization**: Add role-based or attribute-based access control
3. **Rate Limiting**: Prevent abuse with rate limiting
4. **CORS**: Configure CORS policies appropriately for your use case
5. **HTTPS**: Always use HTTPS in production
6. **Input Sanitization**: Additional input sanitization layers for untrusted environments

### Reporting a Vulnerability

If you discover a security vulnerability, please email the maintainers directly rather than opening a public issue. Include:

- Description of the vulnerability
- Steps to reproduce
- Potential impact
- Suggested fix (if any)

We will respond to security reports within 48 hours and work with you to address the issue.

## Safe Usage Guidelines

### For Template Creators

- Only create templates with content from trusted sources
- Avoid including sensitive data directly in templates
- Use variables for any dynamic or sensitive content
- Review templates before setting them as active
- Test templates in a development environment first

### For System Administrators

- Implement authentication on all API endpoints
- Monitor template creation and usage patterns
- Regularly audit templates for compliance
- Implement backup and recovery procedures
- Keep dependencies updated
- Use environment variables for sensitive configuration

### For Developers

- Always validate user input beyond the provided validations
- Implement additional sandboxing if accepting templates from untrusted sources
- Consider using a template approval workflow
- Log all template operations for audit trails
- Implement comprehensive error handling
- Never expose internal error details to end users

## Known Limitations

1. **Template Injection**: By design, the system allows Jinja2 template expressions. This is intentional but requires trusted template creators.

2. **No Built-in Authentication**: The current version does not include authentication. This must be added for production use.

3. **SQLite Default**: The default SQLite database is suitable for development but should be replaced with a production-grade database for production deployments.

## Dependencies

All dependencies are listed in `requirements.txt`. Keep them updated and monitor for security advisories:

- FastAPI: Web framework
- SQLAlchemy: ORM layer
- Pydantic: Data validation
- Jinja2: Template rendering
- PyYAML: YAML parsing

Run `pip install --upgrade -r requirements.txt` regularly to get security updates.

## Compliance

This software is provided as-is without warranty. Organizations using this software are responsible for:

- Implementing appropriate security controls
- Conducting security assessments
- Ensuring compliance with applicable regulations
- Maintaining audit logs
- Implementing data protection measures

## Updates

This security policy will be updated as the project evolves. Check back regularly for updates.

Last Updated: 2025-11-11
