# Lumina Study Pulse

> AI-powered study assistant for answering questions from study materials.

Lumina Study Pulse is a study assistant that allows students to upload their study materials as PDFs and ask questions about them.

Instead of giving a general AI answer, the system searches the uploaded PDF, finds the relevant information, and uses it to generate a short and simple answer. It also shows the page or section from which the answer was taken.

## Problem Statement

Students usually have lecture notes, textbooks, and other study materials in PDF format. Finding a particular topic or answer from a large PDF can take a lot of time.

Normal AI chatbots can answer questions quickly, but their answers may not always be based on the student's actual study material.

Lumina Study Pulse tries to solve this by making the uploaded study material the main source for answering questions.

## How It Works

The basic process is:

1. Student uploads a PDF.
2. The text is extracted from the PDF.
3. The extracted text is divided into smaller chunks.
4. The chunks are converted into embeddings.
5. The embeddings are stored in FAISS.
6. The student asks a question.
7. FAISS searches for the most relevant chunks.
8. The relevant content is sent to Gemini.
9. Gemini generates a short answer using the retrieved content.
10. The source page/chunk is shown along with the answer.

## Features

### PDF Upload

Students can upload their study material in PDF format.

The application extracts the text from the uploaded file and prepares it for searching.

### Question and Answer

Students can ask questions about the uploaded study material through a chat interface.

For example:

> What is the Pumping Lemma?

The system searches the PDF and finds the relevant content before generating the answer.

### Source-Based Answers

The answer is generated using the content retrieved from the uploaded PDF.

The application also shows the source used for the answer.

Example:

> Source: Formal Languages Notes.pdf - Page 25

This makes it easier for students to check the answer from their original notes.

### Answer Not Found

If the requested information cannot be found in the uploaded PDF, the system should not generate an unrelated answer.

Instead, it will show:

> I couldn't find this information in the study material.

## System Flow

```text
Upload PDF
    |
    v
Extract PDF Text
    |
    v
Split Text into Chunks
    |
    v
Create Embeddings
    |
    v
Store Embeddings in FAISS
    |
    v
Student Asks Question
    |
    v
Search Relevant Chunks
    |
    v
Send Question + Context to Gemini
    |
    v
Generate Answer
    |
    v
Display Answer + Source
