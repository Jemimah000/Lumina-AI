# 📚 Lumina Study Pulse

> **AI-Powered Study Assistant for Source-Grounded Learning**

Lumina Study Pulse is an AI-powered study assistant that helps students understand their study materials faster.

Students can upload a **PDF containing lecture notes, textbooks, or solved examples**, ask questions about the content, and receive **short, simple, and source-grounded answers** generated using only the uploaded study material.

---

## 🎯 Problem Statement

Students often have large study PDFs, lecture transcripts, textbooks, and notes. Finding a specific answer inside these documents can be time-consuming.

At the same time, generic AI assistants may provide answers that are:

- ❌ Not based on the student's study material
- ❌ Difficult to verify
- ❌ Sometimes incorrect or hallucinated
- ❌ Too long or complicated

**Lumina Study Pulse** solves this problem by searching the student's uploaded study material and generating answers based only on the relevant content.

---

## 💡 Solution

Lumina Study Pulse provides a simple AI-powered chat interface where students can:

1. **Upload a study PDF**
2. **Ask questions about the PDF**
3. **Search the relevant content**
4. **Generate a concise AI answer**
5. **View the source page/chunk used**
6. **Get a clear message when the answer isn't available**

The goal is to make studying **faster, simpler, and more trustworthy**.

---

## 👥 Target Users

Lumina Study Pulse is designed for:

- 🎓 **College Students**
- 🏫 **School Students**
- 💻 **Online Learners**
- 📖 **Self-Learners**

---

# ✨ Features

## 📄 1. Upload PDF

Students can upload their study material in PDF format.

The system:

- Reads the PDF
- Extracts the text
- Identifies individual pages
- Prepares the content for searching

---

## 💬 2. Ask Questions

Students can ask questions through a simple chatbot interface.

Example:

> **What is the Pumping Lemma?**

The system searches the uploaded study material for relevant information.

---

## 🔎 3. Find Relevant Information

The extracted PDF content is divided into smaller chunks.

These chunks are converted into **embeddings** and stored in a **FAISS vector database**.

When a student asks a question, the system searches for the most relevant chunks.

---

## 🤖 4. AI-Generated Answer

The relevant content is sent to **Google Gemini** along with the student's question.

Gemini generates a:

- **Short**
- **Simple**
- **Clear**
- **Source-based**

answer using the retrieved study material.

---

## 📌 5. Show Source

Every answer should display where the information came from.

Example:

> **Source:** Formal Languages Notes.pdf — Page 25

This allows students to verify the answer directly from their study material.

---

## 🚫 6. Answer Not Found

If the requested information cannot be found in the uploaded PDF, the system will not generate a random answer.

Instead, it will display:

> **"I couldn't find this information in the study material."**

This helps reduce AI hallucinations and keeps answers grounded in the student's materials.

---

# 🔄 System Flow

```text
                    ┌───────────────┐
                    │   Upload PDF  │
                    └───────┬───────┘
                            │
                            ▼
                    ┌───────────────┐
                    │  Extract Text │
                    │    (pypdf)    │
                    └───────┬───────┘
                            │
                            ▼
                    ┌───────────────┐
                    │ Split into    │
                    │    Chunks     │
                    └───────┬───────┘
                            │
                            ▼
                    ┌───────────────┐
                    │   Generate    │
                    │   Embeddings  │
                    └───────┬───────┘
                            │
                            ▼
                    ┌───────────────┐
                    │     FAISS     │
                    │ Vector Store  │
                    └───────┬───────┘
                            │
                            │
                 Student asks question
                            │
                            ▼
                    ┌───────────────┐
                    │    Search     │
                    │  Relevant     │
                    │    Chunks     │
                    └───────┬───────┘
                            │
                            ▼
                    ┌───────────────┐
                    │ Gemini AI API │
                    └───────┬───────┘
                            │
                            ▼
                 ┌─────────────────────┐
                 │ Answer + Source     │
                 └─────────────────────┘
