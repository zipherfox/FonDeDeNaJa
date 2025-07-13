FonDeDeNaJa
===================
This program is built for validating scores from image input or zip file.

## Configuration: `resources/developers.csv`

**Variables:**

1. **access**: User access level
    - `1`: Student
    - `2`: Teacher
    - `3`: Administrator
    - `4`: Developer
    - `5`: Administrator and developer (Superadmin)
2. **email**: Your email address
3. **name**: Your name
4. **role**: Your role (e.g., Website Developer)
5. **welcome_message** (optional): Custom welcome message
    - If left empty, a default message will be used: `Welcome Back, {name}!`

**How to use:**

1. Add a new developer by appending a new line with the format:
   ```csv
   access,email,name,role,welcome_message
   ```
   - ⚠️ **If any field contains whitespace, enclose the value in double quotes.**
     For example: `2,dev@example.com,"Jane Doe","Lead Developer","Welcome, Jane!"`
2. Ensure the email is unique to avoid conflicts.
3. The `welcome_message` can be customized for each developer.
4. The CSV file will be read by the application to display developer information.

## Configuration: `config.toml`

This file will be used for application-wide settings.

**Example:**
```toml
[app]
default_welcome = "Welcome Back Developer! {name} ({role})\nYou are logged in as: {email}"
# Add more configuration variables as needed
```

- Edit `config.toml` to customize default messages and other settings.

---

For more details, see the code or contact the project maintainer.