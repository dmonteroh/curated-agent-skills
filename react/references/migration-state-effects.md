# Migration Patterns: State and Effects

## Pattern: Constructor + State → `useState`

### Class Component

```tsx
interface Props {
  initialCount: number;
}

interface State {
  count: number;
}

class Counter extends React.Component<Props, State> {
  constructor(props: Props) {
    super(props);
    this.state = { count: props.initialCount };
  }

  increment = () => {
    this.setState({ count: this.state.count + 1 });
  };

  render() {
    return (
      <button onClick={this.increment}>Count: {this.state.count}</button>
    );
  }
}
```

### Modern React

```tsx
function Counter({ initialCount }: Props) {
  const [count, setCount] = useState(initialCount);

  const increment = () => setCount(prev => prev + 1);

  return <button onClick={increment}>Count: {count}</button>;
}
```

**Notes:**
- No constructor needed.
- Prefer functional updates for derived state.

---

## Pattern: Lifecycle Methods → `useEffect`

### Class Component

```tsx
class UserProfile extends React.Component<{ userId: string }, State> {
  state = { user: null as User | null };

  componentDidMount() {
    this.fetchUser();
  }

  componentDidUpdate(prevProps: Props) {
    if (prevProps.userId !== this.props.userId) {
      this.fetchUser();
    }
  }

  componentWillUnmount() {
    window.removeEventListener('resize', this.handleResize);
  }
}
```

### Modern React

```tsx
function UserProfile({ userId }: Props) {
  const [user, setUser] = useState<User | null>(null);

  useEffect(() => {
    let cancelled = false;

    async function fetchUser() {
      const userData = await api.getUser(userId);
      if (!cancelled) setUser(userData);
    }

    fetchUser();

    return () => {
      cancelled = true;
    };
  }, [userId]);

  useEffect(() => {
    function handleResize() {
      // Handle resize
    }

    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, []);

  return <div>{user?.name}</div>;
}
```

**Notes:**
- Split effects by concern.
- Always clean up subscriptions.
- Include all dependencies.

---

## Pattern: Complex State → `useReducer`

```tsx
type Action =
  | { type: 'ADD_TODO'; text: string }
  | { type: 'TOGGLE_TODO'; id: string };

function todoReducer(state: State, action: Action): State {
  switch (action.type) {
    case 'ADD_TODO':
      return {
        ...state,
        todos: [
          ...state.todos,
          { id: crypto.randomUUID(), text: action.text, completed: false },
        ],
      };
    case 'TOGGLE_TODO':
      return {
        ...state,
        todos: state.todos.map(todo =>
          todo.id === action.id
            ? { ...todo, completed: !todo.completed }
            : todo
        ),
      };
    default:
      return state;
  }
}

function TodoManager() {
  const [state, dispatch] = useReducer(todoReducer, {
    todos: [],
    filter: 'all',
  });

  return (
    <div>
      {state.todos.map(todo => (
        <TodoItem
          key={todo.id}
          todo={todo}
          onToggle={() => dispatch({ type: 'TOGGLE_TODO', id: todo.id })}
        />
      ))}
    </div>
  );
}
```

**Notes:**
- Use when state transitions are complex.
- Reducers keep state logic testable.
