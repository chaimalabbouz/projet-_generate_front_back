# add_to_cart

## Recognise
An "Add to cart" / "Ajouter au panier" button on a product.

## Apply — never create the same product twice
const [cartItems, setCartItems] = useState<CartItem[]>([]);

useEffect(() => { listCartItems().then(setCartItems); }, []);

const handleAddToCart = async () => {
  const existing = cartItems.find(i => i.product_id === product.id);
  try {
    if (existing) {
      await updateCartItem(existing.id, {
        product_id: product.id,
        quantity: existing.quantity + quantity,
        unit_price: product.price,
      });
    } else {
      await createCartItem({
        product_id: product.id,
        quantity,
        unit_price: product.price,
      });
    }
    const fresh = await listCartItems();
    setCartItems(fresh);
  } catch {
    alert("Impossible d'ajouter au panier");
  }
};

CART TOTAL — computed locally, never stored:
const total = cartItems.reduce((s, i) => s + i.unit_price * i.quantity, 0);

## Condition
Apply ONLY if createCartItem, updateCartItem and listCartItems exist
in api/client. Otherwise leave the button untouched.