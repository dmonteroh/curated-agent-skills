# Prompt Template Patterns

## Classification template

```
Classify the {content_type} into one of: {categories}

{content_type}: {input}
Category:
```

## Extraction template

```
Extract the following fields:
{fields}

Input:
{input}

Return JSON:
```

## Generation template

```
Generate {output_type} based on {input_type}.

Requirements:
{requirements}

{input_type}: {input}
{output_type}:
```

## Transformation template

```
Transform {source_format} to {target_format}.

Rules:
{rules}

Input ({source_format}):
{input}

Output ({target_format}):
```
