# Prompt Template Advanced Features

## Template inheritance

```
base = {"system": "You are a {role}.", "format": "Return {format}."}
child = {**base, "task": "Task: {task}"}
```

## Variable validation

```
schema = {
  "length": {"type": int, "min": 10, "max": 500},
  "tone": {"type": str, "choices": ["formal", "casual"]}
}
```

## Caching rendered prompts

```
cache = {}
key = hash(frozenset(kwargs.items()))
cache[key] = template.format(**kwargs)
```

## Multi-turn templates

```
messages = [
  {"role": "system", "content": system_prompt},
  {"role": "user", "content": user_message}
]
```

## Stateful templates

```
states = {
  "init": "Ask for {first_input}",
  "process": "Process {first_input}"
}
```
