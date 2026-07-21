# loading_empty

## Recognise
A page rendering a list (.map) with no loading, error or empty state.

## Apply
const [items, setItems] = useState<Entity[]>([]);
const [loading, setLoading] = useState(true);
const [error, setError] = useState<string | null>(null);

useEffect(() => {
  listEntities()
    .then(setItems)
    .catch(() => setError("Impossible de charger les données"))
    .finally(() => setLoading(false));
}, []);

Inside the list container, BEFORE the .map:
{loading && <p>Chargement…</p>}
{error && <p>{error}</p>}
{!loading && !error && items.length === 0 && <p>Aucun résultat</p>}
{items.map(...)}

## Forbidden
Changing any className. Replacing the container structure.