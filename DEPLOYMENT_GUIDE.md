# 🚀 Deployment Guide: Streamlit + Neon PostgreSQL

This guide will help you deploy your Streamlit app with persistent PostgreSQL storage using Neon.

## Step 1: Create a Neon Database (Free)

1. Go to [neon.tech](https://neon.tech) and sign up for a free account
2. Click **"Create Project"**
3. Choose a project name (e.g., "apogea-merchants")
4. Select a region closest to you
5. Click **"Create Project"**

## Step 2: Get Your Database Connection String

1. After creating the project, you'll see your connection details
2. Copy the **Connection String** (it looks like this):
   ```
   postgresql://username:password@ep-xxx-xxx.region.aws.neon.tech/neondb?sslmode=require
   ```
3. Save this securely - you'll need it in the next steps

## Step 3: Test Locally (Optional but Recommended)

1. Create a file `.streamlit/secrets.toml` in your project:
   ```bash
   mkdir .streamlit
   # On Windows: md .streamlit
   ```

2. Add your database URL to `.streamlit/secrets.toml`:
   ```toml
   DATABASE_URL = "postgresql://your-connection-string-here"
   ```

3. **IMPORTANT**: Add `.streamlit/secrets.toml` to your `.gitignore`:
   ```
   .streamlit/secrets.toml
   ```

4. Install dependencies and run locally:
   ```bash
   pip install -r requirements.txt
   streamlit run apogea.py
   ```

## Step 4: Deploy to Streamlit Cloud

1. Push your code to GitHub (make sure `.streamlit/secrets.toml` is in `.gitignore`!)

2. Go to [share.streamlit.io](https://share.streamlit.io)

3. Click **"New app"** and connect your GitHub repository

4. Configure your app:
   - **Repository**: Your GitHub repo
   - **Branch**: main (or your branch name)
   - **Main file path**: apogea.py

5. **Add your database secret**:
   - Click **"Advanced settings"**
   - In the **"Secrets"** section, add:
     ```toml
     DATABASE_URL = "postgresql://your-connection-string-here"
     ```
   - Click **"Save"**

6. Click **"Deploy"**!

## Step 5: Verify Everything Works

1. Wait for deployment to complete (usually 2-3 minutes)
2. Your app will open automatically
3. Try adding a merchant or item
4. Refresh the page - your data should persist! ✅

## Troubleshooting

### "DATABASE_URL not found in secrets"
- Make sure you added the DATABASE_URL in Streamlit Cloud's secrets section
- Check that the secret name is exactly `DATABASE_URL` (case-sensitive)

### "connection refused" or "could not connect"
- Verify your Neon database is active (Neon free tier may pause after inactivity)
- Check that your connection string includes `?sslmode=require`
- Make sure there are no extra spaces in your DATABASE_URL

### "relation does not exist"
- The database tables will be created automatically on first run
- Try restarting the app in Streamlit Cloud

## Free Tier Limits

**Neon Free Tier includes:**
- 512 MB storage
- 1 project
- Auto-suspension after 5 minutes of inactivity (automatically wakes up when accessed)

This is more than enough for your merchant database app!

## Security Notes

✅ **DO**: 
- Keep your database URL secret
- Use Streamlit's secrets management
- Add `.streamlit/secrets.toml` to `.gitignore`

❌ **DON'T**: 
- Commit secrets.toml to git
- Share your database URL publicly
- Hardcode credentials in your code

---

Need help? Check:
- [Neon Documentation](https://neon.tech/docs)
- [Streamlit Secrets Management](https://docs.streamlit.io/streamlit-community-cloud/deploy-your-app/secrets-management)
