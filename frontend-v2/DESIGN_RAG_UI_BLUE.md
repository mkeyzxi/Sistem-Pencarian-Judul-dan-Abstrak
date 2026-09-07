# DESIGN RAG UI — Chat-First Interface
## Design System & UI Specification untuk Chatbot RAG

> **Tujuan:** mendefinisikan desain antarmuka chatbot RAG yang modern, akademik, bersih, responsif, dan berfokus pada percakapan serta bukti retrieval.
>
> Dokumen ini menggantikan pendekatan dashboard/sidebar pada desain sebelumnya. **UI utama hanya berfokus pada Chat, Retrieval Evidence, Source Document, dan Message Composer.**
>
> **Primary:** `#1B2CC1`  
> **Deep Navy:** `#091540`  
> **Secondary Blue:** `#7692FF`  
> **Soft Blue:** `#ABD2FA`

---

# 1. Design Direction

## 1.1 Konsep Utama

Antarmuka menggunakan prinsip:

- **Chat-first** — pertanyaan dan jawaban menjadi pusat pengalaman.
- **RAG-first** — sumber dokumen dan bukti retrieval merupakan bagian penting dari jawaban.
- **Academic** — cocok untuk pencarian skripsi, jurnal, dokumen penelitian, dan knowledge base.
- **Clean** — tidak ada sidebar permanen, dashboard, kartu statistik, atau navigasi yang tidak diperlukan.
- **Trustworthy** — jawaban yang bersumber dari dokumen harus mudah ditelusuri.
- **Responsive** — desktop, tablet, dan mobile menggunakan pola interaksi yang sama.
- **Subtle interaction** — animasi digunakan secukupnya dan tidak bergaya neon/cyberpunk.

## 1.2 Visual Personality

Target visual:

```text
Modern
  +
Academic
  +
Research-oriented
  +
AI / RAG
  +
Clean
```

Hindari:

```text
Dashboard admin
Gaming UI
Cyberpunk
Neon AI
Gradient berlebihan
Glow berlebihan
Card overload
```

---

# 2. Scope UI

Dokumen ini hanya mencakup:

```text
┌────────────────────────────────────────────────────┐
│                  RAG CHAT INTERFACE                │
├────────────────────────────────────────────────────┤
│                                                    │
│                  Empty / Welcome                  │
│                                                    │
│ User Message                                       │
│                                                    │
│ Assistant Answer                                   │
│   ├── Markdown content                              │
│   ├── Retrieval sources                             │
│   └── Source details                                │
│                                                    │
│ User Message                                       │
│                                                    │
│ Assistant Answer                                   │
│                                                    │
├────────────────────────────────────────────────────┤
│                MESSAGE COMPOSER                    │
└────────────────────────────────────────────────────┘
```

Tidak termasuk:

- sidebar;
- chat history panel;
- dashboard analytics;
- admin panel;
- profile panel;
- settings dashboard;
- halaman statistik;
- panel navigasi kompleks.

---

# 3. Core Color System

## 3.1 Brand Palette

| Token | Hex | Fungsi |
|---|---|---|
| `primary` | `#1B2CC1` | CTA, send button, active state, AI identity |
| `primary-dark` | `#15219A` | hover / pressed |
| `navy` | `#091540` | heading kuat, dark surface, code block |
| `blue-secondary` | `#7692FF` | secondary emphasis |
| `blue-soft` | `#ABD2FA` | highlight lembut, source accents |
| `background` | `#F8FAFF` | halaman utama |
| `surface` | `#FFFFFF` | card dan composer |
| `surface-soft` | `#F2F5FF` | panel sekunder |
| `border` | `#DCE3F7` | border default |
| `border-strong` | `#BBC8EE` | border aktif |

## 3.2 Semantic Colors

Warna semantic digunakan seperlunya.

| Token | Value | Fungsi |
|---|---|---|
| `success` | `#18794E` | sukses / source tersedia |
| `warning` | `#A15C00` | warning |
| `danger` | `#B42318` | error |
| `info` | `#1B2CC1` | informasi |

## 3.3 Color Hierarchy

Gunakan rasio visual:

```text
#091540   → heading / strong text / dark area
#1B2CC1   → action / brand / AI
#7692FF   → supporting emphasis
#ABD2FA   → soft highlight
#F8FAFF   → page background
#FFFFFF   → content surface
```

Jangan menjadikan semua elemen biru.

Prioritas visual:

```text
Content
  >
Primary Action
  >
Source Evidence
  >
Metadata
```

---

# 4. CSS Variables

Gunakan design token terpusat.

```css
:root {
  --color-primary: #1B2CC1;
  --color-primary-hover: #15219A;
  --color-primary-active: #101A75;

  --color-navy: #091540;

  --color-blue-secondary: #7692FF;
  --color-blue-soft: #ABD2FA;

  --color-background: #F8FAFF;
  --color-surface: #FFFFFF;
  --color-surface-soft: #F2F5FF;

  --color-text-primary: #091540;
  --color-text-secondary: #53617F;
  --color-text-muted: #8995B0;

  --color-border: #DCE3F7;
  --color-border-strong: #BBC8EE;

  --color-success: #18794E;
  --color-warning: #A15C00;
  --color-danger: #B42318;
  --color-info: #1B2CC1;

  --radius-sm: 8px;
  --radius-md: 12px;
  --radius-lg: 16px;
  --radius-xl: 20px;
  --radius-2xl: 24px;
  --radius-pill: 999px;

  --shadow-sm: 0 1px 3px rgba(9, 21, 64, 0.06);
  --shadow-md: 0 8px 28px rgba(9, 21, 64, 0.08);
  --shadow-lg: 0 16px 48px rgba(9, 21, 64, 0.10);

  --content-max-width: 900px;
  --composer-max-width: 900px;
  --header-height: 64px;
}
```

---

# 5. Typography

## 5.1 Font Stack

```css
body {
  font-family:
    Inter,
    ui-sans-serif,
    system-ui,
    -apple-system,
    BlinkMacSystemFont,
    "Segoe UI",
    sans-serif;
}
```

## 5.2 Hierarchy

| Element | Size | Weight | Line Height |
|---|---:|---:|---:|
| Hero title | 32–40px | 700 | 1.15 |
| Chat title | 18–20px | 650 | 1.3 |
| Message | 15–16px | 400 | 1.7–1.8 |
| Source title | 14–15px | 650 | 1.4 |
| Metadata | 12–13px | 400 | 1.4 |
| Badge | 11–12px | 650 | 1 |
| Composer text | 15–16px | 400 | 1.5 |

## 5.3 Reading Rules

Untuk jawaban RAG:

- gunakan line-height yang longgar;
- jangan membuat paragraf terlalu lebar;
- judul jawaban harus memiliki hierarchy;
- metadata harus lebih kecil daripada isi;
- similarity score tidak boleh lebih dominan daripada judul dokumen.

---

# 6. Application Layout

## 6.1 Desktop

```text
┌─────────────────────────────────────────────────────────────┐
│                     RAG ASSISTANT                           │
│           Knowledge Retrieval & Chat                        │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│                     EMPTY STATE                             │
│                                                             │
│              Temukan informasi dari dokumen                 │
│                                                             │
│              [ Suggested Question ]                         │
│                                                             │
│                                                             │
│ User                                                        │
│ ┌───────────────────────────────────────────────────────┐   │
│ │ Cari penelitian tentang RAG untuk skripsi             │   │
│ └───────────────────────────────────────────────────────┘   │
│                                                             │
│ AI                                                          │
│ ┌───────────────────────────────────────────────────────┐   │
│ │ Berdasarkan dokumen yang ditemukan, ...               │   │
│ │                                                       │   │
│ │ Sources                                               │   │
│ │ ┌───────────────────────────────────────────────┐     │   │
│ │ │ 01  Skripsi_RAG.pdf                  0.92     │     │   │
│ │ │     Excerpt ...                               │     │   │
│ │ └───────────────────────────────────────────────┘     │   │
│ └───────────────────────────────────────────────────────┘   │
│                                                             │
├─────────────────────────────────────────────────────────────┤
│  [ Tanyakan sesuatu tentang dokumen...              ] [↑]   │
│       Jawaban dihasilkan berdasarkan retrieval              │
└─────────────────────────────────────────────────────────────┘
```

## 6.2 Mobile

```text
┌───────────────────────────────┐
│       RAG Assistant            │
├───────────────────────────────┤
│                               │
│  User                         │
│  ┌─────────────────────────┐  │
│  │ Cari penelitian tentang  │  │
│  │ RAG                     │  │
│  └─────────────────────────┘  │
│                               │
│  AI                           │
│  Jawaban ...                  │
│                               │
│  Sources                      │
│  ┌─────────────────────────┐  │
│  │ Skripsi_RAG.pdf         │  │
│  │ Relevance 0.92          │  │
│  └─────────────────────────┘  │
│                               │
├───────────────────────────────┤
│ [ Tulis pertanyaan...     ] ↑ │
└───────────────────────────────┘
```

---

# 7. Global Structure

```html
<div class="rag-app">
  <header class="rag-header">
    ...
  </header>

  <main class="chat-shell">
    <section class="chat-content">
      ...
    </section>

    <footer class="composer-area">
      ...
    </footer>
  </main>
</div>
```

CSS:

```css
.rag-app {
  min-height: 100dvh;
  display: flex;
  flex-direction: column;

  background: var(--color-background);
  color: var(--color-text-primary);
}

.chat-shell {
  flex: 1;
  min-height: 0;

  display: flex;
  flex-direction: column;
}
```

---

# 8. Header

Header harus minimal.

```text
┌─────────────────────────────────────────────────────┐
│  [AI] RAG Assistant                         ● Ready │
└─────────────────────────────────────────────────────┘
```

## 8.1 Header Components

```text
AI Avatar
   +
Application Name
   +
Small system status
```

Contoh:

```text
[AI]  RAG Assistant
      Knowledge Search • Ready
```

## 8.2 CSS

```css
.rag-header {
  height: var(--header-height);
  padding: 0 24px;

  display: flex;
  align-items: center;
  justify-content: space-between;

  background: rgba(248, 250, 255, 0.92);
  border-bottom: 1px solid var(--color-border);

  position: sticky;
  top: 0;
  z-index: 20;

  backdrop-filter: blur(14px);
}
```

## 8.3 Status

Gunakan indikator kecil.

```text
● Ready
● Searching
● Generating
● Error
```

Tidak perlu animasi berlebihan.

---

# 9. AI Identity

Avatar AI:

```css
.ai-avatar {
  width: 36px;
  height: 36px;

  display: grid;
  place-items: center;

  background: var(--color-primary);
  color: #FFFFFF;

  border-radius: 11px;
}
```

Alternatif:

```text
[ R ]
[ AI ]
[ ✦ ]
```

Gunakan satu bentuk yang konsisten pada seluruh aplikasi.

---

# 10. Main Chat Content

## 10.1 Content Width

```css
.chat-content {
  flex: 1;
  overflow-y: auto;
}

.chat-content-inner {
  width: min(100%, var(--content-max-width));
  margin-inline: auto;

  padding:
    32px 24px
    140px;
}
```

Tujuan:

```text
Readable width
      +
Generous whitespace
      +
Focused conversation
```

## 10.2 Desktop

Maksimal:

```text
900px
```

Tidak perlu full-width.

## 10.3 Mobile

```css
@media (max-width: 640px) {
  .chat-content-inner {
    padding:
      24px 16px
      120px;
  }
}
```

---

# 11. Empty State

Empty state menjadi wajah utama aplikasi.

```text
                     [AI]

              RAG Assistant

       Temukan informasi dari dokumen
          dengan pertanyaan alami.

 [ Cari penelitian tentang RAG ]

 [ Jelaskan isi dokumen ]

 [ Temukan metode penelitian tertentu ]
```

## 11.1 Empty State Title

```css
.empty-state-title {
  margin: 0;

  color: var(--color-navy);

  font-size: clamp(28px, 4vw, 38px);
  line-height: 1.12;
  font-weight: 700;
  letter-spacing: -0.03em;
}
```

## 11.2 Empty State Description

```css
.empty-state-description {
  max-width: 620px;
  margin-top: 14px;

  color: var(--color-text-secondary);

  font-size: 15px;
  line-height: 1.7;
}
```

---

# 12. Suggested Questions

Suggested questions bukan fitur navigasi. Ia adalah shortcut ke chat.

```text
┌─────────────────────────────────────┐
│ Cari skripsi tentang Retrieval      │
└─────────────────────────────────────┘

┌─────────────────────────────────────┐
│ Apa penelitian yang menggunakan RAG?│
└─────────────────────────────────────┘

┌─────────────────────────────────────┐
│ Jelaskan dokumen yang relevan       │
└─────────────────────────────────────┘
```

CSS:

```css
.suggestion-chip {
  min-height: 42px;

  padding: 10px 14px;

  background: var(--color-surface);
  border: 1px solid var(--color-border);

  border-radius: var(--radius-pill);

  color: var(--color-text-primary);

  cursor: pointer;

  transition:
    background 160ms ease,
    border-color 160ms ease,
    transform 160ms ease;
}

.suggestion-chip:hover {
  background: var(--color-blue-soft);
  border-color: var(--color-border-strong);
}

.suggestion-chip:active {
  transform: translateY(1px);
}
```

---

# 13. Message System

Struktur umum:

```text
Message
├── Role
├── Content
├── Metadata
├── Actions
└── Sources
```

---

# 14. User Message

User message tidak perlu bubble terlalu gelap.

```text
                          ┌─────────────────────────┐
                          │ Cari dokumen tentang RAG│
                          └─────────────────────────┘
```

CSS:

```css
.message.user {
  display: flex;
  justify-content: flex-end;
}

.message.user .message-bubble {
  max-width: min(78%, 680px);

  padding: 12px 16px;

  background: var(--color-primary);
  color: #FFFFFF;

  border-radius:
    18px
    18px
    6px
    18px;
}
```

Catatan:

- jangan membuat bubble terlalu besar;
- jangan gunakan shadow berat;
- teks harus tetap terbaca;
- pesan pendek harus tetap terlihat compact.

---

# 15. Assistant Message

Assistant message adalah area paling penting.

```text
[AI]  Berdasarkan dokumen yang ditemukan,
      terdapat beberapa penelitian yang relevan...

      ## Hasil

      Penelitian pertama membahas ...

      Sources
      ┌────────────────────────────────────────┐
      │ Skripsi_RAG.pdf                    0.92│
      │ "...relevant excerpt..."               │
      └────────────────────────────────────────┘
```

CSS:

```css
.message.assistant {
  display: flex;
  gap: 12px;

  justify-content: flex-start;
}

.message.assistant .message-body {
  flex: 1;
  min-width: 0;
  max-width: 780px;
}
```

Assistant tidak menggunakan bubble biru.

Tujuannya:

```text
User
→ compact colored bubble

Assistant
→ clean document-like response
```

---

# 16. Assistant Markdown Renderer

Karena RAG menghasilkan jawaban Markdown, renderer harus menjadi komponen utama.

## 16.1 Paragraph

```css
.prose p {
  margin: 0 0 14px;
  line-height: 1.78;
}
```

## 16.2 Heading

```css
.prose h2 {
  margin:
    28px 0
    12px;

  color: var(--color-navy);

  font-size: 20px;
  line-height: 1.3;
}

.prose h3 {
  margin:
    22px 0
    10px;

  color: var(--color-navy);

  font-size: 17px;
}
```

## 16.3 List

```css
.prose ul,
.prose ol {
  margin: 14px 0;
  padding-left: 22px;
}

.prose li {
  margin-bottom: 7px;
  line-height: 1.7;
}
```

## 16.4 Blockquote

```css
.prose blockquote {
  margin: 18px 0;
  padding: 12px 16px;

  border-left:
    3px solid
    var(--color-blue-secondary);

  background: var(--color-surface-soft);
  color: var(--color-text-secondary);
}
```

---

# 17. Inline Code

```css
.prose code:not(pre code) {
  padding: 2px 6px;

  border-radius: 6px;

  background: var(--color-surface-soft);

  color: var(--color-primary);

  font-size: 0.9em;
}
```

---

# 18. Code Block

Code block menjadi dark surface.

```text
┌──────────────────────────────────────────────┐
│ Python                              Copy     │
├──────────────────────────────────────────────┤
│ docs = retriever.invoke(query)               │
│ answer = llm.generate(context)               │
└──────────────────────────────────────────────┘
```

```css
.code-block {
  overflow: hidden;

  background: var(--color-navy);
  color: #FFFFFF;

  border:
    1px solid
    rgba(171, 210, 250, 0.24);

  border-radius: var(--radius-lg);

  box-shadow: var(--shadow-sm);
}
```

Header code:

```css
.code-block-header {
  height: 38px;
  padding: 0 12px;

  display: flex;
  align-items: center;
  justify-content: space-between;

  border-bottom:
    1px solid
    rgba(171, 210, 250, 0.16);
}
```

---

# 19. RAG Evidence Architecture

RAG UI harus membedakan:

```text
USER QUERY
      ↓
QUERY UNDERSTANDING
      ↓
RETRIEVAL
      ↓
RELEVANT DOCUMENTS
      ↓
CONTEXT
      ↓
GENERATED ANSWER
```

Namun jangan selalu menampilkan pipeline teknis secara penuh.

Default:

```text
Generated Answer
      ↓
Sources
```

Detail pipeline:

```text
▸ Retrieval details
```

---

# 20. Source Evidence

Source evidence adalah salah satu pembeda utama antara chatbot biasa dan RAG.

Contoh:

```text
Sources

┌─────────────────────────────────────────────────┐
│ 01  Skripsi_RAG_2024.pdf                  0.92 │
│                                                 │
│ Penelitian membahas penerapan Retrieval...     │
│                                                 │
│ [ View source ]                     [ Expand ] │
└─────────────────────────────────────────────────┘
```

## 20.1 Source Card

```css
.source-card {
  display: block;

  padding: 14px 16px;

  background: var(--color-surface);

  border:
    1px solid
    var(--color-border);

  border-radius: var(--radius-lg);

  transition:
    border-color 160ms ease,
    box-shadow 160ms ease,
    transform 160ms ease;
}

.source-card:hover {
  border-color: var(--color-blue-secondary);
  box-shadow: var(--shadow-sm);
}
```

---

# 21. Source Card Anatomy

```text
Source Card
│
├── Index
├── Document icon
├── Document title
├── Metadata
│
├── Relevance score
│
├── Excerpt
│
└── Actions
     ├── View
     └── Expand
```

Contoh visual:

```text
┌──────────────────────────────────────────────┐
│ 01  📄  Penelitian_RAG.pdf          0.92     │
│                                              │
│     Teknik Informatika • 2024               │
│                                              │
│     "Penelitian ini membahas penggunaan     │
│      retrieval augmented generation..."     │
│                                              │
│     [Lihat sumber]       [Detail retrieval] │
└──────────────────────────────────────────────┘
```

---

# 22. Relevance Badge

```css
.relevance-badge {
  display: inline-flex;
  align-items: center;

  min-height: 24px;
  padding: 4px 8px;

  background: var(--color-blue-soft);
  color: var(--color-primary);

  border-radius: var(--radius-pill);

  font-size: 12px;
  font-weight: 700;
}
```

Contoh:

```text
Relevance 0.92
Similarity 0.89
Score 0.87
```

Jangan:

```text
0.92
```

sebagai headline terbesar.

---

# 23. Relevance Visualization

Alternatif badge:

```text
Relevance

██████████████████░░  0.92
```

CSS concept:

```css
.relevance-bar {
  height: 6px;
  overflow: hidden;

  background: #E8EDFA;

  border-radius: var(--radius-pill);
}

.relevance-bar-fill {
  height: 100%;
  width: var(--score);

  background: var(--color-primary);

  border-radius: inherit;
}
```

Gunakan progress bar hanya jika score benar-benar berguna untuk pengguna.

---

# 24. Source Metadata

Metadata dapat berupa:

```text
Document
Title
Year
Author
Category
Page
Chunk
Similarity
Retriever
```

Jangan tampilkan semuanya secara default.

Default:

```text
Title
Year
Similarity
```

Detail:

```text
▸ Metadata
```

---

# 25. Excerpt / Retrieved Context

Source card dapat menampilkan potongan text.

```text
"Penelitian ini menggunakan arsitektur
Retrieval-Augmented Generation untuk
meningkatkan relevansi pencarian..."
```

CSS:

```css
.source-excerpt {
  margin-top: 10px;

  color: var(--color-text-secondary);

  font-size: 13px;
  line-height: 1.65;

  display: -webkit-box;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
```

---

# 26. Source Expansion

Default collapsed:

```text
Sources

[ Source 01 ]
[ Source 02 ]
[ Source 03 ]
```

Expanded:

```text
Source 01

Document
Skripsi_RAG.pdf

Metadata
Year: 2024
Chunk: 12
Score: 0.92

Retrieved excerpt
"..."

[ View document ]
```

CSS:

```css
.source-details {
  overflow: hidden;

  display: grid;
  grid-template-rows: 0fr;

  transition:
    grid-template-rows 180ms ease;
}

.source-details.open {
  grid-template-rows: 1fr;
}
```

---

# 27. Retrieval Transparency

Transparansi harus dijaga tanpa membebani pengguna.

Default:

```text
Answer
↓
Sources
```

Advanced:

```text
▸ Retrieval details
```

Isi:

```text
Retrieval Strategy
Top-K
Embedding
Similarity
Retrieved chunks
Context size
```

Contoh:

```text
▸ Retrieval details

Strategy      Semantic Search
Top-K         5
Similarity    Cosine
Chunks        5
```

Nilai konfigurasi aktual harus mengikuti backend yang digunakan. Jangan menampilkan konfigurasi yang tidak benar.

---

# 28. Retrieval Debug Mode

Mode debug hanya untuk developer/researcher.

```text
┌────────────────────────────────────────────────┐
│ Retrieval Debug                                │
├────────────────────────────────────────────────┤
│                                                │
│ Original Query                                 │
│ "Apa penelitian tentang RAG?"                  │
│                                                │
│ Retrieved Documents                            │
│                                                │
│ 01  score 0.92                                 │
│ 02  score 0.89                                 │
│ 03  score 0.87                                 │
│                                                │
│ Context Chunks                                 │
│                                                │
│ chunk_01                                       │
│ chunk_02                                       │
│ chunk_03                                       │
└────────────────────────────────────────────────┘
```

Mode debug:

```text
User
  → normal UI
Developer / Researcher
  → expanded technical UI
```

Jangan membuat debug information tampil otomatis.

---

# 29. RAG Answer Structure

Jawaban RAG idealnya:

```text
Answer
│
├── Direct answer
│
├── Supporting explanation
│
├── Optional list/table
│
└── Sources
```

Bukan:

```text
Answer
↓
Large technical logs
↓
Retrieval dump
↓
Huge metadata
```

---

# 30. Source-Aware Answer

Ketika jawaban menggunakan sumber:

```text
Berdasarkan dokumen yang ditemukan,
RAG digunakan untuk menggabungkan retrieval
dengan proses generasi jawaban.

[Sumber 1] [Sumber 2]
```

Citation dapat berupa:

```text
[1]
[2]
```

atau:

```text
Source 1
Source 2
```

Citation visual harus dapat diklik.

---

# 31. Inline Citation

Contoh:

```text
RAG menggabungkan retrieval dengan generation [1].
```

Citation:

```css
.inline-citation {
  display: inline-flex;
  align-items: center;

  min-width: 20px;
  height: 20px;

  justify-content: center;

  border-radius: 6px;

  background: var(--color-blue-soft);
  color: var(--color-primary);

  font-size: 11px;
  font-weight: 700;

  cursor: pointer;
}
```

Interaction:

```text
click [1]
   ↓
scroll / focus
   ↓
Source 1 highlighted
```

---

# 32. Highlighted Source

Saat citation dipilih:

```css
.source-card.highlighted {
  border-color: var(--color-primary);

  box-shadow:
    0 0 0 3px
    rgba(27, 44, 193, 0.10);
}
```

Jangan menggunakan glow besar.

---

# 33. Answer Actions

Setiap assistant message dapat memiliki:

```text
Copy
Regenerate
Good
Bad
```

Contoh:

```text
[ Copy ] [ Regenerate ] [ 👍 ] [ 👎 ]
```

CSS:

```css
.message-action {
  width: 32px;
  height: 32px;

  display: grid;
  place-items: center;

  border: 0;
  background: transparent;

  color: var(--color-text-muted);

  border-radius: var(--radius-sm);

  cursor: pointer;
}

.message-action:hover {
  color: var(--color-primary);
  background: var(--color-surface-soft);
}
```

---

# 34. Copy Interaction

Default:

```text
Copy
```

Setelah berhasil:

```text
✓ Copied
```

Durasi:

```text
1–2 detik
```

Tidak perlu toast besar untuk tindakan sederhana.

---

# 35. Message Composer

Composer adalah komponen permanen.

```text
┌───────────────────────────────────────────────────┐
│ Tanyakan sesuatu tentang dokumen...           [↑]│
└───────────────────────────────────────────────────┘
```

CSS:

```css
.composer-area {
  position: sticky;
  bottom: 0;

  padding:
    12px 20px
    calc(16px + env(safe-area-inset-bottom));

  background:
    linear-gradient(
      to bottom,
      transparent,
      var(--color-background) 28%
    );

  z-index: 30;
}

.composer-wrapper {
  width: min(100%, var(--composer-max-width));
  margin-inline: auto;
}

.composer {
  display: flex;
  align-items: flex-end;
  gap: 10px;

  min-height: 58px;
  padding: 8px;

  background: var(--color-surface);

  border:
    1px solid
    var(--color-border-strong);

  border-radius: var(--radius-xl);

  box-shadow: var(--shadow-md);
}
```

---

# 36. Textarea

```css
.composer textarea {
  flex: 1;

  min-height: 42px;
  max-height: 220px;

  padding: 10px 12px;

  resize: none;

  border: 0;
  outline: 0;

  background: transparent;

  color: var(--color-text-primary);

  font: inherit;
  line-height: 1.5;
}

.composer textarea::placeholder {
  color: var(--color-text-muted);
}
```

Behavior:

```text
1 line
↓
2 lines
↓
3 lines
↓
maximum 220px
↓
internal scroll
```

---

# 37. Send Button

```css
.send-button {
  width: 42px;
  height: 42px;

  display: grid;
  place-items: center;

  flex: 0 0 42px;

  border: 0;
  border-radius: 13px;

  background: var(--color-primary);
  color: #FFFFFF;

  cursor: pointer;

  transition:
    background 160ms ease,
    transform 160ms ease;
}

.send-button:hover {
  background: var(--color-primary-hover);
}

.send-button:active {
  transform: translateY(1px);
}

.send-button:disabled {
  opacity: 0.45;
  cursor: not-allowed;
}
```

---

# 38. Composer States

## Empty

```text
[ Tanyakan sesuatu...                         ] [↑]
```

## Typing

```text
[ Cari penelitian tentang Retrieval-Augmented ] [↑]
```

## Loading

```text
[ Sedang mencari dokumen...                   ] [■]
```

## Error

```text
[ Gagal memproses pertanyaan                  ] [↻]
```

---

# 39. Loading State

Untuk RAG, loading sebaiknya mencerminkan proses secara sederhana.

```text
AI

Mencari dokumen…
```

atau:

```text
AI

Menganalisis hasil retrieval…
```

atau:

```text
AI

Menyusun jawaban…
```

Jangan:

```text
████████████████████
LOADING AI ENGINE...
```

Jangan memakai spinner besar memenuhi layar.

---

# 40. Typing Indicator

```text
● ● ●
```

CSS:

```css
.typing-dot {
  animation:
    typing 1.1s infinite ease-in-out;
}

@keyframes typing {
  0%,
  60%,
  100% {
    opacity: 0.25;
    transform: translateY(0);
  }

  30% {
    opacity: 1;
    transform: translateY(-2px);
  }
}
```

---

# 41. Streaming Response

Saat LLM streaming:

```text
User submits
      ↓
User message appears
      ↓
AI placeholder
      ↓
"Retrieving..."
      ↓
Answer starts streaming
      ↓
Sources appear
      ↓
Actions appear
```

Jangan mengunci seluruh interface selama streaming.

User tetap dapat membaca konten sebelumnya.

---

# 42. Scroll Behavior

```css
.chat-content {
  overflow-y: auto;
  scroll-behavior: smooth;
}
```

Rules:

1. scroll ke jawaban terbaru ketika user berada di bagian bawah;
2. jangan memaksa scroll jika user sedang membaca pesan lama;
3. saat user kembali ke bawah, resume auto-scroll;
4. source expansion tidak boleh menyebabkan jump besar.

---

# 43. New Answer Behavior

```text
Submit
  ↓
Append user message
  ↓
Scroll to latest
  ↓
Show retrieval state
  ↓
Show assistant response
  ↓
Stream tokens
  ↓
Attach sources
  ↓
Enable actions
```

---

# 44. Error UX

Error message:

```text
Tidak dapat memproses pertanyaan.

Silakan coba kembali atau gunakan pertanyaan
yang lebih spesifik.

[ Coba lagi ]
```

Error hanya mewarnai:

- icon;
- text;
- retry action.

Jangan membuat seluruh background merah.

---

# 45. No Retrieval Result

Khusus RAG:

```text
Tidak ditemukan dokumen yang cukup relevan.

Coba gunakan kata kunci yang lebih spesifik
atau ajukan pertanyaan dengan konteks tambahan.
```

Visual:

```text
[AI]

No relevant sources found
```

Jangan menghasilkan daftar sumber kosong.

---

# 46. Low-Relevance Retrieval

Jika source tersedia tetapi relevansinya rendah:

```text
Saya menemukan beberapa dokumen yang mungkin
berkaitan, tetapi relevansinya terbatas.

Sources
...
```

UI dapat memberi indikator:

```text
Low relevance
```

Gunakan warna warning secara halus.

---

# 47. Source Count

Contoh:

```text
Sources · 5
```

atau:

```text
5 sources used
```

Tidak perlu menjadikan jumlah source sebagai headline.

---

# 48. Source Grid vs List

Gunakan **list** sebagai default.

```text
Source 01
Source 02
Source 03
```

Gunakan grid hanya jika sumber berisi metadata yang sangat ringkas.

Untuk penelitian/dokumen akademik:

```text
LIST > GRID
```

Karena judul dan excerpt membutuhkan ruang horizontal.

---

# 49. Source Sorting

UI dapat menyusun source berdasarkan:

```text
relevance descending
```

Contoh:

```text
0.93
0.91
0.88
0.84
0.81
```

Score harus berasal dari backend/retriever.

Jangan menghitung ulang score di layer UI.

---

# 50. RAG Result Card

Untuk pencarian beberapa dokumen:

```text
Hasil yang relevan

┌─────────────────────────────────────────────────┐
│ #1                                              │
│ Evaluasi Retrieval-Augmented Generation...     │
│                                                 │
│ Relevance 0.93                                  │
│                                                 │
│ Penelitian ini mengevaluasi ...                 │
│                                                 │
│ [Buka dokumen]                                  │
└─────────────────────────────────────────────────┘
```

Prioritas:

```text
Title
↓
Excerpt
↓
Metadata
↓
Score
```

---

# 51. Search Result vs Source Evidence

Jangan mencampur dua konsep.

## Search Result

Digunakan ketika user meminta daftar dokumen.

```text
1. Judul A
2. Judul B
3. Judul C
```

## Source Evidence

Digunakan untuk menunjukkan sumber yang mendukung jawaban.

```text
Answer
↓
Sources used
```

Keduanya dapat menggunakan visual yang sama, tetapi konteksnya berbeda.

---

# 52. Document Preview

Source dapat membuka preview.

Konsep:

```text
[Source Card]
       ↓
[View Source]
       ↓
Document Preview
```

Preview tidak perlu menjadi halaman baru jika tidak dibutuhkan.

Desktop:

```text
Chat
                Document Preview
```

Mobile:

```text
Chat
 ↓
Source
 ↓
Full-screen preview
```

---

# 53. Source Selection

Saat source diklik:

```text
Source Card
    ↓
selected
    ↓
visual emphasis
```

CSS:

```css
.source-card.selected {
  border-color: var(--color-primary);

  background: #F7F8FF;
}
```

---

# 54. Technical Details Accordion

```text
▸ Retrieval details
```

Expanded:

```text
▾ Retrieval details

Query
...

Strategy
...

Top-K
...

Similarity
...

Retrieved chunks
...
```

Animation:

```css
transition: 180ms ease;
```

Jangan menggunakan modal besar untuk informasi kecil.

---

# 55. RAG Trust Layer

UI RAG harus memberi kesan:

```text
"Jawaban ini tidak berdiri sendiri."
```

Visual hierarchy:

```text
Answer
      ↓
Evidence
      ↓
Source
      ↓
Document
```

Jangan membuat:

```text
AI Answer
      ↓
No indication of source
```

---

# 56. Empty Source Handling

Jika backend tidak mengirim source:

```text
Answer
↓
No source section
```

Jangan membuat card:

```text
Sources: 0
```

kecuali memang dibutuhkan untuk debugging.

---

# 57. Message Separation

Gunakan whitespace.

```css
.message-list {
  display: flex;
  flex-direction: column;
  gap: 28px;
}
```

Jangan membuat border di setiap message.

Target:

```text
User

      Assistant

User

      Assistant
```

bukan:

```text
┌───────────────────────┐
│ User                  │
├───────────────────────┤
│ Assistant             │
├───────────────────────┤
```

---

# 58. Background

Background utama:

```css
body {
  background: var(--color-background);
}
```

Jangan menggunakan:

```text
full page gradient
large blobs
animated background
grid cyberpunk
```

Blue palette lebih kuat bila background tetap tenang.

---

# 59. Surface System

Gunakan 3 level:

```text
Level 0
Background
#F8FAFF

Level 1
Surface
#FFFFFF

Level 2
Surface Soft
#F2F5FF
```

Contoh:

```text
Page
 └── Message
      └── Source Card
           └── Metadata
```

Gunakan surface, bukan shadow berat.

---

# 60. Border System

Default:

```css
border: 1px solid var(--color-border);
```

Active:

```css
border-color: var(--color-primary);
```

Tidak perlu border tebal.

Prioritas visual:

```text
spacing
  >
border
  >
shadow
```

---

# 61. Shadow System

Gunakan:

```css
--shadow-sm:
  0 1px 3px rgba(9, 21, 64, 0.06);

--shadow-md:
  0 8px 28px rgba(9, 21, 64, 0.08);

--shadow-lg:
  0 16px 48px rgba(9, 21, 64, 0.10);
```

Penggunaan:

```text
Composer → shadow-md
Source card → shadow-sm
Modal/preview → shadow-lg
```

Jangan memberi shadow ke semua elemen.

---

# 62. Border Radius

```text
8px
→ small controls

12px
→ button / small cards

16px
→ source card

20px
→ composer

24px
→ featured area

999px
→ chip / badge
```

Jangan semua komponen menggunakan rounded-full.

---

# 63. Spacing System

Gunakan kelipatan 4.

```text
4px
8px
12px
16px
20px
24px
28px
32px
40px
48px
64px
```

Rules:

| Context | Spacing |
|---|---:|
| Icon ↔ text | 8px |
| Message gap | 24–28px |
| Source internal | 12–16px |
| Section | 24–40px |
| Page | 16px mobile / 24px desktop |
| Composer | 8px internal |

---

# 64. Responsive Design

## 64.1 Breakpoints

```css
/* Mobile */
@media (max-width: 640px) {}

/* Tablet */
@media (min-width: 641px) and (max-width: 1024px) {}

/* Desktop */
@media (min-width: 1025px) {}
```

---

# 65. Mobile Rules

Pada mobile:

- horizontal padding 16px;
- source card full width;
- user bubble maksimum 90%;
- composer tetap mudah dijangkau;
- send button minimal 40px;
- technical details tetap collapsed;
- excerpt maksimal 3 baris;
- answer tetap memiliki line-height tinggi.

CSS:

```css
@media (max-width: 640px) {
  .rag-header {
    padding: 0 14px;
  }

  .message.user .message-bubble {
    max-width: 90%;
  }

  .composer-area {
    padding:
      10px
      10px
      calc(10px + env(safe-area-inset-bottom));
  }

  .source-card {
    width: 100%;
  }
}
```

---

# 66. Tablet Rules

Tablet:

```text
Main content
≈ 90% width
```

Tidak perlu membuat layout dua kolom.

Chat tetap satu kolom.

---

# 67. Accessibility

## 67.1 Focus State

```css
:focus-visible {
  outline:
    3px solid
    rgba(118, 146, 255, 0.42);

  outline-offset: 2px;
}
```

## 67.2 Button Requirements

Semua button harus memiliki:

- accessible label;
- keyboard support;
- visible focus state;
- disabled state;
- target touch yang cukup besar.

Contoh:

```html
<button
  type="button"
  aria-label="Kirim pesan"
>
  ↑
</button>
```

---

# 68. Contrast Guidance

Gunakan:

```text
#091540
```

untuk teks utama.

Gunakan:

```text
#1B2CC1
```

untuk action dan identity.

`#ABD2FA` digunakan sebagai surface/accent ringan dan jangan menjadi warna teks utama pada background terang.

---

# 69. Reduced Motion

Untuk pengguna yang memilih reduced motion:

```css
@media (prefers-reduced-motion: reduce) {
  *,
  *::before,
  *::after {
    animation-duration: 0.01ms !important;
    animation-iteration-count: 1 !important;
    scroll-behavior: auto !important;
    transition-duration: 0.01ms !important;
  }
}
```

---

# 70. Interaction Philosophy

Gunakan animasi hanya untuk:

```text
Message appearance
Source expansion
Button state
Loading
Mobile preview
```

Durasi:

```text
120–180ms
```

Panel:

```text
180–260ms
```

Hindari:

```text
large scale
bouncing
floating glow
continuous pulse
parallax
excessive blur
```

---

# 71. Message Entrance

```css
.message-enter {
  animation:
    message-enter 180ms ease-out;
}

@keyframes message-enter {
  from {
    opacity: 0;
    transform: translateY(4px);
  }

  to {
    opacity: 1;
    transform: translateY(0);
  }
}
```

---

# 72. Iconography

Gunakan satu icon library.

Rekomendasi:

```text
Lucide
Heroicons
Phosphor
```

Target:

```text
Action     → 18–20px
Metadata   → 16px
Small icon → 14px
```

Jangan mencampur terlalu banyak style icon.

---

# 73. Core Components

Struktur komponen:

```text
components/
│
├── rag/
│   ├── RagApp
│   ├── RagHeader
│   ├── ChatShell
│   ├── ChatContent
│   ├── EmptyState
│   ├── SuggestedQuestions
│   │
│   ├── MessageList
│   ├── UserMessage
│   ├── AssistantMessage
│   ├── MessageActions
│   │
│   ├── MarkdownRenderer
│   ├── CodeBlock
│   ├── InlineCitation
│   │
│   ├── SourceList
│   ├── SourceCard
│   ├── SourceExcerpt
│   ├── SourceMetadata
│   ├── RelevanceBadge
│   ├── RetrievalDetails
│   └── RetrievalDebug
│
├── composer/
│   ├── MessageComposer
│   ├── SendButton
│   ├── TypingIndicator
│   └── ComposerStatus
│
└── ui/
    ├── Button
    ├── IconButton
    ├── Badge
    ├── Accordion
    └── Tooltip
```

---

# 74. Minimal Component Architecture

Jika project kecil:

```text
RagApp
├── Header
├── Chat
│   ├── EmptyState
│   ├── MessageList
│   │   ├── UserMessage
│   │   └── AssistantMessage
│   │       ├── Markdown
│   │       └── Sources
│   └── Composer
```

Jangan membuat component terlalu banyak hanya untuk styling kecil.

---

# 75. Data Contract

Frontend sebaiknya menerima bentuk data semacam berikut:

```ts
type ChatSource = {
  id: string;
  title: string;
  excerpt?: string;
  score?: number;
  metadata?: Record<string, unknown>;
};

type ChatMessage = {
  id: string;
  role: "user" | "assistant";
  content: string;
  sources?: ChatSource[];
  createdAt?: string;
  loading?: boolean;
  error?: string;
};
```

Jika backend sudah memiliki bentuk berbeda, gunakan adapter:

```text
Backend response
      ↓
Mapper / Adapter
      ↓
UI data model
```

Jangan mengubah backend hanya karena kebutuhan visual.

---

# 76. Conversation State

Minimal:

```text
messages
input
isLoading
isStreaming
error
expandedSources
selectedSource
retrievalDetailsOpen
```

Contoh React:

```tsx
const [messages, setMessages] =
  useState<ChatMessage[]>([]);

const [input, setInput] =
  useState("");

const [isLoading, setIsLoading] =
  useState(false);

const [isStreaming, setIsStreaming] =
  useState(false);

const [selectedSource, setSelectedSource] =
  useState<string | null>(null);
```

---

# 77. Message Lifecycle

```text
User types
   ↓
Submit
   ↓
Append user message
   ↓
Set loading
   ↓
Call RAG API
   ↓
Retrieval
   ↓
LLM generation
   ↓
Stream / receive answer
   ↓
Attach sources
   ↓
Render source cards
   ↓
Enable message actions
   ↓
Loading false
```

UI harus merepresentasikan lifecycle backend, bukan menggantikannya.

---

# 78. RAG-Specific UI States

Minimal state:

```text
Idle
Retrieving
Generating
Complete
No Sources
Low Relevance
Error
```

Visual mapping:

| State | Visual |
|---|---|
| Idle | composer normal |
| Retrieving | small status |
| Generating | typing indicator |
| Complete | answer + sources |
| No Sources | info message |
| Low Relevance | warning |
| Error | danger + retry |

---

# 79. State Copy

## Idle

```text
Tanyakan sesuatu tentang dokumen...
```

## Retrieving

```text
Mencari dokumen yang relevan...
```

## Generating

```text
Menyusun jawaban...
```

## No Sources

```text
Tidak ditemukan dokumen yang cukup relevan.
```

## Error

```text
Terjadi kesalahan saat memproses pertanyaan.
```

---

# 80. Tailwind Design Tokens

Jika project menggunakan Tailwind:

```ts
theme: {
  extend: {
    colors: {
      primary: "#1B2CC1",
      "primary-dark": "#15219A",
      navy: "#091540",
      secondary: "#7692FF",
      "blue-soft": "#ABD2FA",
      background: "#F8FAFF",
      surface: "#FFFFFF",
      "surface-soft": "#F2F5FF",
      border: "#DCE3F7",

      text: {
        primary: "#091540",
        secondary: "#53617F",
        muted: "#8995B0",
      },
    },
  },
}
```

Contoh:

```tsx
<div className="min-h-dvh bg-background text-text-primary">
```

```tsx
<button className="bg-primary text-white">
```

```tsx
<div className="border border-border bg-surface">
```

---

# 81. Example Tailwind Layout

```tsx
<div className="flex min-h-dvh flex-col bg-background">

  <header className="
    sticky top-0 z-20
    h-16
    border-b border-border
    bg-background/90
    backdrop-blur
  ">
    {/* RAG Header */}
  </header>

  <main className="flex min-h-0 flex-1 flex-col">

    <section className="flex-1 overflow-y-auto">
      <div className="
        mx-auto w-full max-w-[900px]
        px-4 py-8 pb-36
        md:px-6
      ">
        {/* Messages */}
      </div>
    </section>

    <footer className="
      sticky bottom-0 z-30
      bg-background/90
      backdrop-blur
    ">
      {/* Composer */}
    </footer>

  </main>

</div>
```

---

# 82. Suggested Desktop Widths

| Area | Width |
|---|---:|
| Header | Full width |
| Chat content | 900px |
| Message content | 780px |
| Composer | 900px |
| User bubble | max 680px |
| Source card | 100% of assistant content |

---

# 83. Suggested Mobile Dimensions

| Element | Recommendation |
|---|---:|
| Page padding | 16px |
| Header horizontal | 14px |
| Send button | ≥ 40px |
| Composer radius | 18–20px |
| User bubble | ≤ 90% |
| Source card | 100% |
| Assistant avatar | 32–36px |

---

# 84. RAG UX Rules

## Rule 1 — Answer first

User harus menemukan inti jawaban sebelum metadata teknis.

## Rule 2 — Evidence visible

Source jangan disembunyikan terlalu dalam.

## Rule 3 — Technical detail optional

Retrieval detail collapsed secara default.

## Rule 4 — Score is metadata

Similarity bukan headline.

## Rule 5 — No fake certainty

UI tidak boleh menyiratkan bahwa source selalu benar hanya karena score tinggi.

## Rule 6 — Source title matters

Judul dokumen adalah identitas utama source.

## Rule 7 — One-column by default

Chat akademik lebih mudah dibaca dengan satu kolom utama.

---

# 85. RAG Source Priority

Visual hierarchy:

```text
1. Document title
2. Excerpt
3. Source metadata
4. Relevance score
5. Technical retrieval info
```

Jangan:

```text
1. Score
2. Score
3. Score
4. Title
```

---

# 86. UX untuk Pertanyaan Pencarian

Contoh:

```text
User:
"Cari skripsi tentang RAG"
```

UI:

```text
AI:

Saya menemukan beberapa dokumen yang relevan.

1. Evaluasi Retrieval-Augmented Generation...
2. Implementasi RAG...
3. Optimasi Semantic Retrieval...

Sources
[3 sources]
```

Source muncul setelah jawaban atau hasil pencarian, bukan sebagai tabel teknis panjang.

---

# 87. UX untuk Pertanyaan Penjelasan

Contoh:

```text
User:
"Apa inti penelitian ini?"
```

UI:

```text
AI:

Inti penelitian membahas ...

Poin utama:
• ...
• ...
• ...

Sources
[ Document 01 ]
```

---

# 88. UX untuk Perbandingan

Contoh:

```text
User:
"Bandingkan dua penelitian ini."
```

Assistant:

```text
## Perbandingan

| Aspek | Penelitian A | Penelitian B |
|---|---|---|
| Metode | ... | ... |
| Dataset | ... | ... |
| Tujuan | ... | ... |

Sources
...
```

Table harus mengikuti Markdown renderer dan tetap responsive.

---

# 89. Responsive Table

Pada mobile:

```css
.table-wrapper {
  overflow-x: auto;
  -webkit-overflow-scrolling: touch;
}
```

Jangan mengecilkan font sampai sulit dibaca hanya agar tabel muat.

---

# 90. Markdown Link

Link:

```css
.prose a {
  color: var(--color-primary);
  text-decoration: underline;
  text-underline-offset: 3px;
}

.prose a:hover {
  color: var(--color-primary-hover);
}
```

---

# 91. Empty Search Results

Untuk retrieval kosong:

```text
Tidak ditemukan hasil yang cukup relevan.

Coba:
• gunakan istilah yang lebih spesifik;
• tambahkan konteks;
• gunakan kata kunci lain.
```

Suggested refinement dapat menjadi chip:

```text
[ Coba "retrieval augmented generation" ]
```

---

# 92. Query Refinement UX

Jangan membuat user harus kembali mengetik dari nol.

Setelah no result:

```text
Tidak ditemukan hasil relevan.

Coba pertanyaan yang lebih spesifik:

[ RAG untuk pencarian skripsi ]
[ Semantic search pada skripsi ]
[ Hybrid retrieval ]
```

---

# 93. Conversation Continuity

User dapat mengirim:

```text
User:
Cari penelitian RAG.

Assistant:
...

User:
Yang menggunakan metode tertentu?

Assistant:
...
```

UI tidak perlu menampilkan panel history terpisah.

Context conversation menjadi bagian dari chat.

---

# 94. Long Conversation

Saat percakapan panjang:

- content tetap satu kolom;
- source card tetap compact;
- header tetap sticky;
- composer selalu accessible;
- auto-scroll tetap terkontrol.

Jangan memampatkan semua message terlalu kecil.

---

# 95. Long Source List

Jika source lebih dari 5:

```text
Sources · 8

[Source 1]
[Source 2]
[Source 3]

[ Show more ]
```

Default jumlah source yang ditampilkan mengikuti kebutuhan aplikasi.

UI tidak boleh mengarang nilai Top-K.

---

# 96. Source Collapse

Contoh:

```text
Sources · 5

▾ Source 01
▾ Source 02
▾ Source 03

[Show all sources]
```

Untuk source sederhana:

```text
Source 01
```

dapat collapsed.

Untuk source yang sangat penting:

```text
Source 01
[Expanded]
```

---

# 97. Source Card Accessibility

Contoh:

```html
<article
  class="source-card"
  aria-label="Sumber 1: Skripsi RAG 2024"
>
  ...
</article>
```

Button:

```html
<button
  type="button"
  aria-label="Buka sumber Skripsi RAG 2024"
>
  Lihat sumber
</button>
```

---

# 98. Keyboard Interaction

Recommended:

```text
Enter
→ submit

Shift + Enter
→ new line

Tab
→ navigate controls

Escape
→ close source preview / accordion
```

Jangan mengorbankan Shift + Enter.

---

# 99. Composer Keyboard Behavior

```text
Enter
→ send

Shift + Enter
→ newline

Ctrl/Cmd + Enter
→ optional alternative submit
```

Implementasi harus konsisten di seluruh aplikasi.

---

# 100. Mobile Composer Safe Area

```css
.composer-area {
  padding-bottom:
    max(
      12px,
      env(safe-area-inset-bottom)
    );
}
```

Tujuan:

```text
iPhone / mobile navigation
+
chat composer
```

tidak saling bertabrakan.

---

# 101. Error Recovery

Error harus menyediakan:

```text
Problem
↓
Explanation
↓
Action
```

Contoh:

```text
Tidak dapat mengambil dokumen.

Periksa koneksi atau coba lagi.

[ Coba lagi ]
```

Jangan hanya:

```text
Error 500
```

untuk pengguna umum.

---

# 102. Empty State Visual Balance

Jangan membuat empty state terlalu tinggi.

Target:

```text
Header
↓
40–100px whitespace
↓
AI identity
↓
Title
↓
Description
↓
Suggested questions
```

---

# 103. Visual Balance

Warna:

```text
60%  light background
25%  white surfaces
10%  navy / dark text
5%   primary blue accents
```

Proporsi ini bukan aturan matematis mutlak, tetapi menjadi panduan agar biru tidak memenuhi seluruh interface.

---

# 104. Gradient Policy

Gradient boleh digunakan sangat ringan untuk area dekoratif tertentu.

Contoh:

```css
background:
  linear-gradient(
    180deg,
    rgba(171, 210, 250, 0.15),
    transparent
  );
```

Jangan menggunakan:

```text
full-screen blue gradient
rainbow gradient
animated gradient
neon glow
```

---

# 105. Dark Surface Usage

Dark navy hanya untuk:

```text
Code block
Technical panel
Optional document preview header
```

Jangan mengubah seluruh aplikasi menjadi dark theme kecuali memang dibuat sebagai tema terpisah.

---

# 106. Design Tokens — Complete

```css
:root {
  --color-primary: #1B2CC1;
  --color-primary-hover: #15219A;
  --color-primary-active: #101A75;

  --color-navy: #091540;

  --color-secondary: #7692FF;
  --color-blue-soft: #ABD2FA;

  --color-background: #F8FAFF;
  --color-surface: #FFFFFF;
  --color-surface-soft: #F2F5FF;

  --color-text-primary: #091540;
  --color-text-secondary: #53617F;
  --color-text-muted: #8995B0;

  --color-border: #DCE3F7;
  --color-border-strong: #BBC8EE;

  --color-success: #18794E;
  --color-warning: #A15C00;
  --color-danger: #B42318;
  --color-info: #1B2CC1;

  --radius-sm: 8px;
  --radius-md: 12px;
  --radius-lg: 16px;
  --radius-xl: 20px;
  --radius-2xl: 24px;
  --radius-pill: 999px;

  --shadow-sm: 0 1px 3px rgba(9, 21, 64, 0.06);
  --shadow-md: 0 8px 28px rgba(9, 21, 64, 0.08);
  --shadow-lg: 0 16px 48px rgba(9, 21, 64, 0.10);

  --content-max-width: 900px;
  --composer-max-width: 900px;
  --header-height: 64px;
}
```

---

# 107. Complete Layout HTML

```html
<div class="rag-app">

  <header class="rag-header">
    <div class="rag-brand">
      <div class="ai-avatar">AI</div>

      <div>
        <div class="rag-title">
          RAG Assistant
        </div>

        <div class="rag-status">
          Knowledge Search
        </div>
      </div>
    </div>
  </header>


  <main class="chat-shell">

    <section class="chat-content">
      <div class="chat-content-inner">

        <div class="message-list">

          <!-- EmptyState -->

          <!-- UserMessage -->

          <!-- AssistantMessage -->
          <!-- Markdown -->
          <!-- Sources -->

        </div>

      </div>
    </section>


    <footer class="composer-area">

      <div class="composer-wrapper">

        <div class="composer">

          <textarea
            placeholder="Tanyakan sesuatu tentang dokumen..."
            aria-label="Pertanyaan"
          ></textarea>

          <button
            type="button"
            class="send-button"
            aria-label="Kirim pesan"
          >
            ↑
          </button>

        </div>

      </div>

    </footer>

  </main>

</div>
```

---

# 108. Full Interaction Flow

```text
OPEN APP
   ↓
EMPTY STATE
   ↓
User asks question
   ↓
USER MESSAGE
   ↓
RETRIEVING
   ↓
RETRIEVAL COMPLETE
   ↓
ASSISTANT RESPONSE
   ↓
SOURCES
   ↓
USER FOLLOW-UP
   ↓
RETRIEVING
   ↓
ASSISTANT RESPONSE
```

---

# 109. RAG Transparency Flow

```text
Question
   │
   ▼
┌──────────────────────┐
│ Query                │
└──────────────────────┘
   │
   ▼
┌──────────────────────┐
│ Retrieval            │
└──────────────────────┘
   │
   ▼
┌──────────────────────┐
│ Relevant Sources     │
└──────────────────────┘
   │
   ▼
┌──────────────────────┐
│ Generated Answer     │
└──────────────────────┘
   │
   ▼
┌──────────────────────┐
│ Evidence / Sources   │
└──────────────────────┘
```

---

# 110. Design Priority

Implementasi mengikuti urutan:

## Priority 1 — Readability

User harus langsung memahami:

```text
Question
Answer
Sources
Input
```

## Priority 2 — RAG Evidence

User dapat memahami:

```text
"Jawaban ini berasal dari dokumen mana?"
```

## Priority 3 — Interaction

User dapat:

```text
Ask
Copy
Regenerate
Open source
Expand details
```

## Priority 4 — Visual Polish

Baru kemudian:

```text
Hover
Transitions
Shadow
Micro animation
```

---

# 111. Do / Don't

## DO

- gunakan `#1B2CC1` sebagai primary;
- gunakan `#091540` untuk heading dan dark surface;
- gunakan `#7692FF` sebagai secondary accent;
- gunakan `#ABD2FA` sebagai soft highlight;
- buat chat sebagai pusat aplikasi;
- tampilkan source evidence;
- gunakan whitespace;
- gunakan source card yang compact;
- gunakan technical retrieval details secara collapsed;
- gunakan responsive one-column layout;
- jaga answer readability.

## DON'T

- jangan membuat sidebar permanen;
- jangan membuat dashboard statistik;
- jangan menggunakan neon glow;
- jangan menggunakan gradient berlebihan;
- jangan membuat semua elemen berwarna biru;
- jangan membuat similarity score sebagai headline;
- jangan menampilkan retrieval logs secara default;
- jangan menggunakan card terlalu banyak;
- jangan membuat seluruh UI dark;
- jangan memaksa auto-scroll;
- jangan menyembunyikan source penting.

---

# 112. Visual Target

```text
                    #091540
                       │
                       ▼
              ┌─────────────────┐
              │   RAG Assistant │
              │ Knowledge Search│
              └─────────────────┘

                       ↓

              ┌─────────────────┐
              │       AI        │
              │                 │
              │ Find knowledge  │
              │ from documents  │
              │                 │
              │ [Suggested]     │
              └─────────────────┘

                       ↓

      User
      ┌──────────────────────────────────┐
      │ Cari skripsi tentang RAG         │
      └──────────────────────────────────┘

                       ↓

      AI
      ┌──────────────────────────────────┐
      │ Berdasarkan dokumen yang         │
      │ ditemukan, ...                   │
      │                                  │
      │ Sources                          │
      │ ┌──────────────────────────────┐ │
      │ │ 📄 Skripsi_RAG.pdf      0.92 │ │
      │ │ Excerpt ...                  │ │
      │ └──────────────────────────────┘ │
      └──────────────────────────────────┘

                       ↓

      ┌──────────────────────────────────┐
      │ Tanyakan sesuatu...          [↑] │
      └──────────────────────────────────┘
```

---

# 113. Implementation Checklist

## Global

- [ ] Background `#F8FAFF`
- [ ] Primary `#1B2CC1`
- [ ] Deep navy `#091540`
- [ ] Secondary `#7692FF`
- [ ] Soft blue `#ABD2FA`
- [ ] Design token terpusat
- [ ] Typography konsisten
- [ ] Responsive
- [ ] Accessibility
- [ ] Reduced motion

## Chat

- [ ] Header
- [ ] Empty state
- [ ] Suggested questions
- [ ] User message
- [ ] Assistant message
- [ ] Markdown renderer
- [ ] Code block
- [ ] Inline citation
- [ ] Message actions
- [ ] Loading
- [ ] Error
- [ ] No-result state

## RAG

- [ ] Source evidence
- [ ] Source card
- [ ] Source title
- [ ] Excerpt
- [ ] Metadata
- [ ] Relevance badge
- [ ] Optional relevance bar
- [ ] Source expansion
- [ ] Citation linking
- [ ] Retrieval details
- [ ] Retrieval debug mode
- [ ] Low relevance state
- [ ] No source state

## Composer

- [ ] Auto resize textarea
- [ ] Enter submit
- [ ] Shift + Enter newline
- [ ] Send disabled state
- [ ] Loading state
- [ ] Error state
- [ ] Mobile safe area
- [ ] Accessible label

## Responsive

- [ ] Mobile ≤ 640px
- [ ] Tablet 641–1024px
- [ ] Desktop ≥ 1025px
- [ ] Source full width on mobile
- [ ] User bubble ≤ 90%
- [ ] Composer accessible
- [ ] No horizontal overflow

---

# 114. Definition of Done

Desain dianggap selesai ketika:

1. Tidak ada sidebar permanen.
2. Chat menjadi pusat seluruh aplikasi.
3. User dapat langsung memahami cara bertanya.
4. Assistant answer mudah dibaca.
5. Source retrieval terlihat jelas.
6. Source dapat diekspansi.
7. Citation dapat dikaitkan dengan source.
8. Similarity/relevance hanya menjadi metadata.
9. Technical retrieval information collapsed secara default.
10. Loading state tidak mengganggu halaman.
11. Error state dapat ditindaklanjuti.
12. Empty-result state tersedia.
13. Composer selalu mudah dijangkau.
14. Desktop dan mobile memiliki UX konsisten.
15. Warna menggunakan:
    - `#1B2CC1`
    - `#091540`
    - `#7692FF`
    - `#ABD2FA`
16. UI tidak terlihat seperti dashboard admin.
17. UI tidak menggunakan neon/cyberpunk.
18. UI terasa profesional untuk konteks akademik/penelitian.
19. Layer presentasi tidak mengubah logic RAG tanpa kebutuhan.
20. Konfigurasi teknis yang ditampilkan UI harus berasal dari data/backend yang benar.

---

# 115. Prinsip Integrasi

Desain ini harus diperlakukan sebagai **presentation layer untuk sistem RAG yang sudah ada**.

```text
EXISTING RAG
   │
   ├── Query
   ├── Retrieval
   ├── Vector Search
   ├── Context
   ├── LLM
   └── Response
          │
          ▼
      UI ADAPTER
          │
          ▼
     RAG CHAT UI
          │
          ├── Answer
          ├── Citations
          ├── Sources
          ├── Metadata
          └── Composer
```

Yang idealnya tidak dirombak hanya karena perubahan UI:

```text
Retrieval logic
Embedding pipeline
Vector database
LLM integration
API contract
Evaluation logic
```

Jika struktur data backend berbeda, gunakan mapper/adapter pada frontend.

---

# 116. Final Design Statement

> **RAG Assistant harus terasa seperti tempat bertanya dan menelusuri pengetahuan, bukan seperti dashboard.**
>
> Pengguna datang untuk bertanya, menerima jawaban, melihat bukti dokumen, dan melanjutkan percakapan.
>
> Karena itu, seluruh desain harus memprioritaskan:
>
> **Conversation → Answer → Evidence → Source → Follow-up**

Visual identity dibangun dari empat warna utama:

```text
PRIMARY       #1B2CC1
DEEP NAVY     #091540
SECONDARY     #7692FF
SOFT BLUE     #ABD2FA
```

Target akhir:

```text
Clean
+
Academic
+
Modern
+
Trustworthy
+
RAG-focused
```
