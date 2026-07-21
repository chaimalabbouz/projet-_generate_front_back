# delete_action

## Recognise
A Delete / Remove / Supprimer button inside a repeated block (.map).

## Apply
const handleDelete = async (id: number) => {
  if (!window.confirm("Confirmer la suppression ?")) return;
  try {
    await deleteEntity(id);
    setItems(items.filter(i => i.id !== id));
  } catch {
    alert("Suppression impossible");
  }
};

On the button : onClick={() => handleDelete(item.id)}

## Condition
Apply ONLY if deleteEntity exists in api/client.
Otherwise leave the button untouched.

## Forbidden
Deleting without confirmation. Re-fetching the whole list afterwards.