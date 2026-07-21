# counter

## Recognise
A block containing a "-", a number and a "+".

## Apply
const [quantity, setQuantity] = useState(1);

<QuantitySelector
  value={quantity}
  onIncrement={() => setQuantity(quantity + 1)}
  onDecrement={() => setQuantity(Math.max(1, quantity - 1))}
/>

The value is then used by the associated action button.

## Condition
The component must expose value / onIncrement / onDecrement.
If it does not, leave it untouched.