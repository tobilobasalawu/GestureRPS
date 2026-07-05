# How AI & LLMs Actually Work — My Notes

A plain-English map of everything, built from first principles. Starts at the webcam
game, ends at how ChatGPT predicts a word.

---

## 1. The tools (and who does what)

| Tool | What it is | Its job |
|------|-----------|---------|
| **OpenCV** | computer-vision library | **grabs** raw frames from the webcam + draws on screen. Just pixels — it detects nothing. "The eyes." |
| **MediaPipe** | Google's ready-made AI models | **detects** the hand and returns 21 points. "The brain that recognises." |
| **TensorFlow** | engine to *build & train* AI | trains neural networks. MediaPipe's model was made with it. "The factory." |
| **PyTorch** | rival of TensorFlow (by Meta) | same job as TensorFlow; favoured for research + LLMs. |
| **Our code** | plain if-statements | counts fingers → decides the move. |

**Key line:** OpenCV *grabs* pixels → MediaPipe *detects* the hand → our code *decides* the gesture.

- **MediaPipe = a ready meal** (already cooked, just use it — only does hands/face/pose).
- **TensorFlow = the kitchen** (build any dish, but you must cook).
- MediaPipe uses **21 landmarks** (points 0–20): 0 = wrist, then 4 points per finger × 5 fingers.

---

## 2. The family tree of AI

```
NEURAL NETWORK        ← the family: numbers in → numbers out, learns patterns
   └── TRANSFORMER    ← one architecture, built on "attention"
         └── LLM      ← a huge transformer trained on text
               └── GPT ← one brand (Generative Pre-trained Transformer)
```

- **Neural network** = the foundation. Empty at birth; learns by adjusting internal numbers.
- **Transformer** = the specific design that made LLMs work.
- **LLM** = transformer + massive scale + petabytes of text.
- Frameworks (**TensorFlow / PyTorch**) can train *any* type: vision, language, audio — the
  type depends on the **data**, not the framework.

---

## 3. Tokens vs Embeddings

- **Token** = a unique **ID** for a word. Like a barcode. Says *which* word, not what it means.
  ("cat" → #2543)
- **Embedding** = a long **list of numbers** that holds the word's **meaning**. Places words in
  a "meaning space" where similar words sit close together.
  (Famous: `king − man + woman ≈ queen` — meaning becomes math.)

**Token = the name tag. Embedding = the personality behind it.**

---

## 4. Attention (the heart of the transformer)

**Old problem:** models read word-by-word and forgot the start by the end.
**Fix:** *attention* — read all words at once; each word puts **heavy emphasis** on the words
that matter to it, **light emphasis** on the rest.

**What emphasis actually DOES:** it lets each word **rewrite its own embedding** using context.
- "a **cat** is an animal" → cat leans on "animal" → becomes *the creature*.
- "my name is **Cat**" → cat leans on "name" → becomes *a person's name*.

This repeats across **many layers** — early layers catch grammar, deep layers catch meaning.

**Bonus:** attention looks at all words *simultaneously* → massively parallel → trainable across
**thousands of GPUs**. That parallelism is *why* LLMs could scale.

---

## 5. How it predicts the next word

The transformer never "knows" the answer — it **scores every word** and picks.

1. After the layers, take the final context-rich embedding.
2. Score all ~50,000 possible next words.
3. **Softmax** turns scores into probabilities that add to 100%
   ("The sky is ___" → blue 71%, grey 12%, clear 6% …).
4. **Pick one** — with a bit of randomness set by **temperature**
   (high = creative/risky, low = safe/predictable).
5. Append it → feed everything back in → predict again → fluent text, one token at a time.

This is why it can be creative, why the same prompt varies, and why it "hallucinates"
(it picks *plausible*, not *true*).

---

## 6. Two phases people confuse: Generation vs Training

| | Generation (using it) | Training (before release) |
|--|----------------------|---------------------------|
| Who appends the word? | the AI, automatically | slides along the **real text** |
| Uses its own guess? | yes (creating new text) | no — walks the real text; guess only measures error |
| Humans review each word? | no | no (real text = answer key) |
| What changes? | nothing (model is frozen) | the model's **weights** (internal numbers) |

**Temperature = a generation dial only. It has nothing to do with training.**

---

## 7. How training actually works (the fill-in-the-blank game)

Take real text: *"The sky is blue."*
1. Hide the next word: "The sky is ___".
2. Model guesses (maybe "green" 40%, "blue" 30%).
3. Reveal the real word — "blue". Measure **how wrong** and **in which direction** (the "error").
4. Give the weights **one tiny nudge** to make that mistake less likely.
5. **Move on to the next word — even if it was wrong.** It does NOT retry until correct.

- No humans write answers — **the real text is its own answer key** (self-supervised learning).
- **Being wrong is the fuel**, not failure. Wrong guesses tell it which way to nudge.
  If it were always right, there'd be nothing to learn.
- **Basketball analogy:** each miss nudges your aim. You don't fix one shot — you take
  millions, drifting toward good.
- Each nudge barely changes anything; **billions of tiny nudges** across billions of contexts
  add up. There's no single "gets smart" moment — fluency **emerges** from scale.

---

## 8. The full training pipeline

1. **Pretraining → base model.** Petabytes of internet text, fill-in-the-blank billions of
   times. Thousands of GPUs, huge cost. Output: smart but raw.
2. **Fine-tuning.** Train on cleaner, task-shaped examples so it answers *usefully*.
3. **RLHF (Reinforcement Learning from Human Feedback).** Humans rate **whole answers**
   (never single words); the model learns to prefer the good ones. Makes it helpful + aligned.

Built with **Python + PyTorch**, running on thousands of **GPUs**.

---

## The one-sentence version

> Turn text into tokens (IDs) → embeddings (meaning) → run through a transformer where
> **attention** rewrites each word's meaning in context → score every possible next word →
> pick one → repeat. It **learns** by playing fill-in-the-blank on real text billions of times,
> nudging itself a hair each time it's wrong. Same core idea as the webcam game's vision model —
> just language instead of pixels.
