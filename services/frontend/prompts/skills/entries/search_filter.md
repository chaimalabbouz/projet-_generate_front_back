# search_filter

## Recognise
A search input placed above a list.

## Apply — LOCAL filtering only, never server-side
const [search, setSearch] = useState('');

const filtered = items.filter(i =>
  (i.name ?? i.title ?? '').toLowerCase().includes(search.toLowerCase())
);

On the input : value={search} onChange={e => setSearch(e.target.value)}
On the list  : filtered.map(...)   instead of   items.map(...)

## Forbidden
Calling the API on every keystroke. No search endpoint exists.