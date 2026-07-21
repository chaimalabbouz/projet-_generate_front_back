# form_submit

## Recognise
A group of input fields followed by a submit button.

## Apply
const [form, setForm] = useState({ field1: '', field2: '' });
const [sending, setSending] = useState(false);
const [feedback, setFeedback] = useState<string | null>(null);

const handleChange = (e: React.ChangeEvent<HTMLInputElement>) =>
  setForm({ ...form, [e.target.name]: e.target.value });

const handleSubmit = async () => {
  setSending(true);
  setFeedback(null);
  try {
    await createEntity(form);
    setFeedback("Votre demande a bien été envoyée.");
    setForm({ field1: '', field2: '' });
  } catch {
    setFeedback("Une erreur est survenue. Réessayez.");
  } finally {
    setSending(false);
  }
};

On each field : name={...} value={form.x} onChange={handleChange}
On the button  : onClick={handleSubmit} disabled={sending}
Below it       : {feedback && <p>{feedback}</p>}

## Forbidden
Using <form onSubmit>. Changing any className.