# Prompt Template Architecture

## Basic template

```
class PromptTemplate:
    def __init__(self, template, variables):
        self.template = template
        self.variables = variables

    def render(self, **kwargs):
        missing = set(self.variables) - set(kwargs.keys())
        if missing:
            raise ValueError(f"Missing variables: {missing}")
        return self.template.format(**kwargs)
```

## Conditional blocks

```
Template:
"""
{task}

{{#if examples}}
Examples:
{examples}
{{/if}}
"""
```

## Modular composition

```
components = {
  "system": "You are a {role}.",
  "task": "Task: {task}",
  "format": "Output: {format}"
}

prompt = join([components[name] for name in ["system", "task", "format"]])
```
