# Google Cloud Run Deployment Guide

This guide will help you deploy your Telegram Image Generation Bot to Google Cloud Run using the Google Cloud Console (no terminal commands needed!).

## Prerequisites

Before you start, make sure you have:
- A Google Cloud account with billing enabled
- A GitHub account
- Your Telegram bot token (from @BotFather on Telegram)
- Your Gradio API URL (from your Google Colab notebook)

---

## Part 1: Prepare Your GitHub Repository

### Step 1: Create a New GitHub Repository
1. Go to [GitHub](https://github.com) and sign in
2. Click the "+" icon in the top right corner
3. Select "New repository"
4. Name it something like "telegram-image-bot"
5. Make it **Public** (required for Cloud Run to access it)
6. **Do NOT** initialize with README, .gitignore, or license
7. Click "Create repository"

### Step 2: Upload Your Code to GitHub
1. On your new repository page, click "uploading an existing file"
2. Drag and drop ALL these files from your project:
   - `bot.py`
   - `config.py`
   - `gradio_connector.py`
   - `keyboards.py`
   - `user_sessions.py`
   - `Dockerfile`
   - `requirements.txt`
   - `.dockerignore`
3. Scroll down and click "Commit changes"

Your code is now ready on GitHub! ✅

---

## Part 2: Deploy to Google Cloud Run

### Step 1: Open Google Cloud Console
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Sign in with your Google account
3. If you don't have a project, create one:
   - Click the project dropdown at the top
   - Click "New Project"
   - Name it (e.g., "telegram-bot")
   - Click "Create"

### Step 2: Enable Required APIs
1. In the search bar at the top, type "Cloud Run API"
2. Click on "Cloud Run API" and click "Enable"
3. Do the same for "Cloud Build API" - search, click, and enable

### Step 3: Go to Cloud Run
1. Click the hamburger menu (≡) in the top left
2. Scroll down to "Cloud Run"
3. Click on "Cloud Run"

### Step 4: Create a New Service
1. Click the blue "**CREATE SERVICE**" button
2. Select "**Continuously deploy from a repository (source or function)**"
3. Click "**SET UP WITH CLOUD BUILD**"

### Step 5: Connect Your GitHub Repository
1. Under "Repository Provider", select "**GitHub**"
2. Click "**Authenticate**" (if not already connected)
3. A popup will appear - sign in to GitHub and authorize Google Cloud Build
4. After authorization, you'll see your GitHub repositories
5. Find and select your repository (e.g., "telegram-image-bot")
6. Click "**Next**"

### Step 6: Configure Build Settings
1. **Branch**: Select "^main$" (or whatever your default branch is)
2. **Build Type**: Select "**Dockerfile**"
3. **Source location**: Type `/Dockerfile` (this points to your Dockerfile)
4. Click "**Save**"

### Step 7: Configure Service Settings

**Service Settings:**
- **Service name**: Give it a name (e.g., "telegram-image-bot")
- **Region**: Choose a region close to you (e.g., "us-central1" or "europe-west1")

**Authentication:**
- Select "**Allow unauthenticated invocations**" (so Telegram can send messages to your bot)

**Container Settings** (expand "Container, Networking, Security"):
1. Click "**Container**" tab
2. **Container port**: Enter `8080`
3. **CPU allocation**: Select "CPU is always allocated"
4. **Memory**: Select at least "512 MiB" (image generation needs memory)
5. **Maximum requests per container**: Leave as default (80)

**Environment Variables** (still in Container settings):
1. Scroll down to "Environment variables"
2. Click "**ADD VARIABLE**" and add:
   - Name: `TELEGRAM_BOT_TOKEN`
   - Value: Your bot token (from @BotFather)
3. Click "**ADD VARIABLE**" again:
   - Name: `GRADIO_API_URL`
   - Value: Your Gradio URL (from Colab, e.g., `https://xxxxx.gradio.live/`)
4. Click "**ADD VARIABLE**" one more time:
   - Name: `WEBHOOK_URL`
   - Value: Leave this EMPTY for now (we'll set it after deployment)

### Step 8: Deploy!
1. Scroll down and click the blue "**CREATE**" button
2. Wait for the deployment (this takes 2-5 minutes)
3. You'll see a progress indicator - wait until it shows "✓ Service deployed successfully"

---

## Part 3: Set Up the Webhook

### Step 1: Get Your Service URL
1. After deployment completes, you'll see your service URL
2. It looks like: `https://telegram-image-bot-xxxxx-uc.a.run.app`
3. **Copy this URL** - you'll need it!

### Step 2: Update WEBHOOK_URL Environment Variable
1. On your Cloud Run service page, click "**EDIT & DEPLOY NEW REVISION**"
2. Scroll down to "Environment variables"
3. Find the `WEBHOOK_URL` variable
4. Update its value to your service URL (the one you just copied)
5. Make sure it's the full URL, like: `https://telegram-image-bot-xxxxx-uc.a.run.app`
6. Click "**DEPLOY**"
7. Wait for the new revision to deploy (about 1-2 minutes)

### Step 3: Verify Your Bot is Running
1. Open Telegram and find your bot
2. Send `/start` to your bot
3. You should get a welcome message! 🎉
4. Try sending a prompt like "sunset over mountains, 4k, detailed"
5. Your bot should respond and let you generate images!

---

## Troubleshooting

### Bot doesn't respond
- Check that your `TELEGRAM_BOT_TOKEN` is correct
- Make sure `WEBHOOK_URL` is set to your Cloud Run service URL
- Check the logs: In Cloud Run service page, click "LOGS" tab

### "Generation failed" error
- Make sure your Google Colab notebook is running
- Check that `GRADIO_API_URL` is correct and accessible
- Colab sessions expire after inactivity - restart your Colab notebook

### Build failed
- Check that all files were uploaded to GitHub correctly
- Make sure the Dockerfile path is correct (`/Dockerfile`)
- Look at Cloud Build logs for specific errors

---

## Cost Information

Google Cloud Run pricing:
- **Free tier**: 2 million requests per month, 360,000 GB-seconds of memory
- Your bot will likely stay in the free tier unless you have thousands of users
- Only charges when your bot is actively processing requests
- You can set up billing alerts in Google Cloud Console

---

## Updating Your Bot

When you want to make changes:
1. Update your code on GitHub (upload new files or edit existing ones)
2. Cloud Build will automatically detect the change
3. It will rebuild and redeploy your bot automatically
4. Wait 2-5 minutes for the new version to be live

---

## Important Notes

- Your Google Colab must be running for image generation to work
- Colab sessions expire after ~12 hours of inactivity - you'll need to restart it
- Each time you restart Colab, you'll get a new Gradio URL - update the `GRADIO_API_URL` environment variable in Cloud Run when this happens
- Consider using a persistent API service instead of Colab for 24/7 operation

---

**Congratulations! Your bot is now running 24/7 on Google Cloud Run!** 🚀

If you have any issues, check the Cloud Run logs for error messages. The logs will show what's happening when your bot receives messages.
