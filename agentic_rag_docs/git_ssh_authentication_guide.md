# Resolving Git 403 Error: Switching from HTTPS to SSH

This guide details the steps to bypass corporate network HTTPS blocking or credential caching issues (which result in a 403 error) by setting up SSH authentication for GitHub.

## 1. Generate a New SSH Key
Open your terminal (preferably Git Bash) and generate a new SSH key using the Ed25519 algorithm.

```bash
ssh-keygen -t ed25519 -C "your_email@example.com"
```
*Note: When prompted for a file to save the key, press **Enter** to accept the default location (`~/.ssh/id_ed25519`). This ensures the SSH agent can find it automatically.*

## 2. Start the SSH Agent and Add Your Key
Ensure the SSH agent is running in the background and add your newly generated private key to it.

```bash
eval "$(ssh-agent -s)"
ssh-add ~/.ssh/id_ed25519
```
*You should see output like `Agent pid 1234` followed by `Identity added`.*

## 3. Copy Your Public Key
Display your public key in the terminal so you can copy it.

```bash
cat ~/.ssh/id_ed25519.pub
```
*Highlight and copy the entire output string (e.g., `ssh-ed25519 AAA... your_email@example.com`).*

## 4. Add the Key to GitHub
1. Log into your GitHub account in a web browser.
2. Navigate to **Settings** > **SSH and GPG keys**.
3. Click the **New SSH key** button.
4. Give it a recognizable title (e.g., "Work Laptop").
5. Paste the entire copied string into the **Key** field.
6. Click **Add SSH key**.

## 5. Switch Your Local Repository to Use SSH
In your local project folder, update the Git remote URL from HTTPS to SSH. Replace `YOUR_GITHUB_USERNAME` and `YOUR_REPOSITORY_NAME` with your actual details.

```bash
git remote set-url origin git@github.com:YOUR_GITHUB_USERNAME/YOUR_REPOSITORY_NAME.git
```
*You can verify the change by running `git remote -v`. Both `fetch` and `push` URLs should now start with `git@github.com:`.*

## 6. Push Your Code
Finally, push your changes to the remote repository.

```bash
git push -u origin main
```
*Note: The first time you do this, you will be asked if you are sure you want to continue connecting. Type `yes` and press Enter to add GitHub to your known hosts list.*