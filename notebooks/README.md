# Team Collaboration & Workflow

This repo is set to Public so the tutor can quickly review our work, but only our team members can push changes.

## 1. How we collaborate
We use GitHub as the main hub. Before you start coding, always get the latest work from others.

*   **Step 1: Get latest changes**
    `git pull origin main`
*   **Step 2: Save your work**
    ```bash
    git add .
    git commit -m "Update logic for [component]"
    git push origin main
    ```

## 2. Setting up SageMaker / CLI (Authentication)
Since only team members can push, you'll need to prove it's you. Use a **Personal Access Token (PAT)** instead of your password.

1.  **Get a Token**: GitHub > Settings > Developer Settings > Personal Access Tokens > Tokens (classic). Create one with `repo` access.
2.  **Save it once**: In your SageMaker terminal, run:
    `git config --global credential.helper store`
3.  **Login**: The first time you push, it will ask for a password. **Paste your PAT card here.** It will remember it forever.

## 3. Running in Google Colab (For us or Tutors)
*   Open the [sprint1_poc.ipynb](https://github.com/studiobuilders/ism-cyberrag/blob/main/notebooks/sprint1_poc.ipynb) notebook.
*   Click the **Open in Colab** button.
*   Run the first cell to clone the repo and install dependencies.

## 4. Repo Structure
*   `src/`: All our modular Python code (PDF parsing, etc.) goes here.
*   `notebooks/`: Use this for testing and demos.
*   `.env.example`: Use this to see what keys we need (never push the real `.env`).
