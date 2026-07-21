# toggle

## Recognise
A heart, a star or a switch — an element with two visual states.

## Apply
const [active, setActive] = useState(false);

<FavoriteIcon active={active} onToggle={() => setActive(!active)} />

If a matching collection entity exists (Favorite, Wishlist):
const handleToggle = async () => {
  try {
    active ? await deleteFavorite(item.id) : await createFavorite({ item_id: item.id });
    setActive(!active);
  } catch { /* keep previous state */ }
};

## Condition
Without a matching entity in api/client, stay local-only.