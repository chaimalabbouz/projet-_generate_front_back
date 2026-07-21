# form_validation

## Recognise
A form where some labels contain * (required fields).

## Apply
Build a validity flag from the *Create schema of the entity:

const isValid =
  form.name.trim() !== '' &&
  /\S+@\S+\.\S+/.test(form.email) &&
  form.message.trim() !== '';

On the button : disabled={!isValid || sending}

TYPES — for every number field in the Create schema:
  <Input type="number" ... />
  and convert before sending: Number(form.quantity)

## Forbidden
Making an optional field required. Changing any className.
Blocking the button for a field that is not marked *.