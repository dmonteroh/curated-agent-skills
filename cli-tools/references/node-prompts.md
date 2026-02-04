# Node.js Interactive Prompts

## Inquirer

```javascript
import inquirer from 'inquirer';

// Text input
const { name } = await inquirer.prompt([
  {
    type: 'input',
    name: 'name',
    message: 'Project name:',
    default: 'my-project',
    validate: (input) => input.length > 0 || 'Name required',
  },
]);

// Select from list
const { environment } = await inquirer.prompt([
  {
    type: 'list',
    name: 'environment',
    message: 'Select environment:',
    choices: ['development', 'staging', 'production'],
    default: 'development',
  },
]);

// Checkbox (multi-select)
const { features } = await inquirer.prompt([
  {
    type: 'checkbox',
    name: 'features',
    message: 'Select features:',
    choices: [
      { name: 'TypeScript', checked: true },
      { name: 'ESLint', checked: true },
      { name: 'Prettier', checked: true },
      { name: 'Jest', checked: false },
    ],
  },
]);

// Confirmation
const { confirmed } = await inquirer.prompt([
  {
    type: 'confirm',
    name: 'confirmed',
    message: 'Deploy to production?',
    default: false,
  },
]);

// Password
const { password } = await inquirer.prompt([
  {
    type: 'password',
    name: 'password',
    message: 'Enter password:',
    mask: '*',
  },
]);
```
