# Deploying to Streamlit Cloud - Step-by-Step Guide

**Make your Force Plate Report Generator accessible from anywhere**

This guide shows you how to deploy your Streamlit app to the cloud so coaches can access it from any device with a web browser - no installation needed!

---

## 🎯 What You'll Get

After following this guide, you'll have:
- ✅ A public URL (e.g., `https://your-app.streamlit.app`)
- ✅ Accessible from any device with internet
- ✅ No installation required for users
- ✅ Automatic updates when you push to GitHub
- ✅ Free hosting (no credit card needed)

**Time needed:** 15-20 minutes for first-time setup

---

## ⚠️ Before You Start

### What You Need:

1. **GitHub Account** (free)
   - If you don't have one: https://github.com/signup
   - You'll need to verify your email

2. **Streamlit Cloud Account** (free)
   - You'll create this during setup
   - Uses your GitHub account to sign in

3. **Your Code on GitHub**
   - Your B_Ellis repository should already be on GitHub
   - If not, see "Uploading to GitHub" section below

### Important Notes:

⚠️ **Data Privacy:** Your app will be PUBLIC by default
- Anyone with the URL can access it
- Don't include sensitive athlete data in the repository
- Data files uploaded by users stay private (not stored)
- Consider password protection (see Advanced section)

✅ **What's Safe:**
- The code is safe to share (it's just the analysis tool)
- Reports are only visible to the person who generated them
- Uploaded data is temporary and not saved

---

## 📋 Step-by-Step Deployment

### Step 1: Prepare Your GitHub Repository

**1.1 - Make sure your repository is pushed to GitHub:**

```bash
cd B_Ellis
git status  # Check current status
git push origin main  # Or your branch name
```

**1.2 - Verify files are on GitHub:**
- Go to https://github.com/YOUR_USERNAME/B_Ellis
- You should see:
  - `generate_report_app.py`
  - `requirements.txt`
  - `README.md`
  - Other documentation files

**1.3 - Check requirements.txt:**

Make sure it contains:
```
streamlit>=1.28.0
pandas>=2.1.0
numpy>=1.24.3
plotly>=5.17.0
openpyxl>=3.1.2
```

---

### Step 2: Create Streamlit Cloud Account

**2.1 - Go to Streamlit Cloud:**
- Open your browser
- Navigate to: https://share.streamlit.io

**2.2 - Sign up with GitHub:**
- Click **"Sign up"** or **"Continue with GitHub"**
- You'll be redirected to GitHub
- Click **"Authorize Streamlit"**
- Enter your GitHub password if prompted

**2.3 - Verify your email:**
- Check your email for verification link
- Click the link to verify
- Return to Streamlit Cloud

---

### Step 3: Deploy Your App

**3.1 - Click "New app":**
- Look for the **"New app"** button (top right)
- Click it to start deployment

**3.2 - Configure deployment settings:**

You'll see a form with these fields:

**Repository:**
- Click the dropdown
- Find and select: `YOUR_USERNAME/B_Ellis`
- If you don't see it, click "Connect another repo" and authorize access

**Branch:**
- Select: `main` (or your branch name like `claude/training-report...`)

**Main file path:**
- Type: `generate_report_app.py`
- This tells Streamlit which file to run

**App URL (optional):**
- This will be auto-filled like: `b-ellis-RANDOM.streamlit.app`
- You can customize it: `baylor-force-plate.streamlit.app`
- Must be unique across all Streamlit apps
- Use lowercase letters, numbers, and hyphens only

**3.3 - Click "Deploy!":**
- The blue **"Deploy!"** button at the bottom
- Wait for deployment (takes 2-5 minutes first time)
- You'll see a loading screen with logs

**3.4 - Watch the deployment logs:**

You'll see messages like:
```
Cloning repository...
Installing dependencies...
Starting app...
```

**Success looks like:**
```
✓ Your app is live!
```

---

### Step 4: Test Your App

**4.1 - Your app is now live!**
- The URL will be displayed at the top
- Example: `https://baylor-force-plate.streamlit.app`
- Click the URL to open your app

**4.2 - Test the functionality:**
1. Try uploading the three CSV files
2. Click "Generate Report"
3. Verify the report displays correctly
4. Test downloading HTML and Text versions

**4.3 - Common first-time issues:**

**Issue: "ModuleNotFoundError"**
- Check your `requirements.txt` includes all dependencies
- Make sure file is in the root of your repository

**Issue: "File not found"**
- Verify `generate_report_app.py` is in the root directory
- Check the "Main file path" setting in Streamlit Cloud

**Issue: App keeps restarting**
- Check the logs for error messages
- Look for Python syntax errors in your code

---

### Step 5: Share Your App

**5.1 - Get your shareable URL:**
- Copy the URL from your browser address bar
- Example: `https://baylor-force-plate.streamlit.app`

**5.2 - Share with your team:**

**Via Email:**
```
Subject: New Force Plate Report Generator

Hi Team,

Our new force plate report generator is now live!

Access it here: https://baylor-force-plate.streamlit.app

How to use:
1. Open the link
2. Upload your three CSV files (CMJ, IMTP, Roster)
3. Click "Generate Report"
4. Download the report

No installation needed - works in any web browser.

Questions? Let me know!
```

**Via Slack/Teams:**
```
🎉 Force Plate Report Generator is live!
📊 https://baylor-force-plate.streamlit.app

Upload your data files and get instant reports. No software installation needed!
```

**5.3 - Bookmark the URL:**
- Add to browser bookmarks
- Add to staff shared resources
- Pin in communication channels

---

## 🔄 Updating Your App

### Automatic Updates

**Great news:** Your app updates automatically when you push to GitHub!

**Workflow:**
1. Make changes to your code locally
2. Test locally: `streamlit run generate_report_app.py`
3. Commit changes: `git commit -am "Your update message"`
4. Push to GitHub: `git push origin main`
5. Wait 30-60 seconds
6. Streamlit Cloud automatically redeploys! ✨

**No need to manually redeploy** - it happens automatically!

### Manual Reboot

**If something goes wrong:**

1. Go to https://share.streamlit.io
2. Click on your app name
3. Click the **"⋮"** menu (three dots)
4. Select **"Reboot app"**
5. Wait for restart (30 seconds)

---

## ⚙️ App Settings & Management

### Accessing App Settings

1. Go to https://share.streamlit.io
2. Click on your app
3. Click **"Settings"** in the top menu

### Important Settings:

**General:**
- **App URL** - Change your custom URL
- **Main file path** - Update if you rename files
- **Branch** - Switch to different branch

**Secrets (see Security section):**
- Store passwords or API keys
- Never commit secrets to GitHub
- Access via `st.secrets` in code

**Analytics:**
- View app usage statistics
- See number of visitors
- Monitor performance

---

## 🔐 Security & Privacy

### Making Your App Private

**Option 1: Email Restriction (Recommended)**

1. Go to App Settings → **"Sharing"**
2. Select **"Restrict to email domain"**
3. Enter: `@baylor.edu`
4. Only Baylor email addresses can access

**Option 2: Password Protection**

Add this to the top of `generate_report_app.py`:

```python
import streamlit as st

def check_password():
    """Returns `True` if user enters correct password."""
    def password_entered():
        if st.session_state["password"] == "YOUR_PASSWORD_HERE":
            st.session_state["password_correct"] = True
            del st.session_state["password"]
        else:
            st.session_state["password_correct"] = False

    if "password_correct" not in st.session_state:
        st.text_input(
            "Password",
            type="password",
            on_change=password_entered,
            key="password"
        )
        st.info("Enter password to access the app")
        return False
    elif not st.session_state["password_correct"]:
        st.text_input(
            "Password",
            type="password",
            on_change=password_entered,
            key="password"
        )
        st.error("😕 Password incorrect")
        return False
    else:
        return True

if not check_password():
    st.stop()

# Rest of your app code here...
```

**Better: Use Streamlit Secrets**

1. In Streamlit Cloud → Settings → **"Secrets"**
2. Add:
   ```toml
   password = "YourSecurePassword123"
   ```
3. In your code:
   ```python
   if st.session_state["password"] == st.secrets["password"]:
   ```

**Option 3: Deploy on Baylor Internal Network**
- Contact Baylor IT
- Host on internal server instead
- Only accessible from Baylor network

---

## 📊 Monitoring Your App

### View App Analytics

1. Go to https://share.streamlit.io
2. Click your app name
3. Click **"Analytics"** tab

**You can see:**
- Number of visitors per day
- Most active times
- Average session duration
- Resource usage (RAM, CPU)

### App Logs

**View real-time logs:**
1. Open your app in browser
2. Click **"☰"** menu (top right)
3. Select **"Manage app"**
4. View logs in real-time

**Useful for:**
- Debugging errors
- Seeing what users are doing
- Monitoring performance

---

## 🆘 Troubleshooting

### App Won't Deploy

**Error: "Requirements installation failed"**
- Check `requirements.txt` syntax
- Verify package names are correct
- Try pinning versions: `pandas==2.1.0`

**Error: "Module not found"**
- Add missing package to `requirements.txt`
- Push changes to GitHub
- Wait for automatic redeploy

**Error: "File not found: generate_report_app.py"**
- Verify file is in repository root
- Check spelling exactly matches
- Update "Main file path" in settings

### App Runs but Crashes

**Check the logs:**
1. Open app
2. Click ☰ → "Manage app"
3. Look for error messages in logs

**Common issues:**
- Missing data file references
- Syntax errors in code
- Memory limits exceeded (upgrade to paid plan)

### App is Slow

**Tips for performance:**
- Use `@st.cache_data` decorator on data loading
- Optimize pandas operations
- Reduce data processing in main loop
- Consider upgrading to paid plan for more resources

### Can't Find App on Streamlit Cloud

**Solution:**
1. Go to https://share.streamlit.io
2. Sign in with GitHub
3. Check "All apps" dropdown
4. Your app should be listed

---

## 💰 Pricing & Limits

### Free Tier (Community Plan)

**Included:**
- ✅ Unlimited public apps
- ✅ 1 GB RAM per app
- ✅ 1 CPU core per app
- ✅ Community support
- ✅ Automatic HTTPS
- ✅ Custom domain support

**Limits:**
- Apps sleep after 7 days of inactivity
- Limited to 3 private apps
- Resource limits (RAM/CPU)

### Paid Plans (If Needed)

**Starter Plan ($20/month):**
- More private apps
- No sleep mode
- More resources

**Team Plan ($250/month):**
- Team collaboration
- Priority support
- Higher resource limits
- Custom domains

**For most use cases, FREE TIER is sufficient!**

---

## 🎓 Advanced Tips

### Custom Domain

**Instead of:** `your-app.streamlit.app`
**Use:** `forceplate.baylor.edu`

1. Contact Baylor IT for DNS setup
2. In Streamlit Settings → Custom domain
3. Add your domain
4. Follow DNS instructions

### Multiple Environments

**Deploy different versions:**
- Production: Deploy from `main` branch
- Testing: Deploy from `dev` branch
- Each gets its own URL

### Scheduled Updates

**Auto-update data:**
- Use Streamlit's scheduling (paid plans)
- Or set up GitHub Actions to trigger updates
- Or use external cron jobs

---

## 📚 Additional Resources

### Official Documentation

- **Streamlit Docs:** https://docs.streamlit.io
- **Deployment Guide:** https://docs.streamlit.io/streamlit-community-cloud
- **Troubleshooting:** https://docs.streamlit.io/knowledge-base

### Community Support

- **Forum:** https://discuss.streamlit.io
- **Discord:** https://discord.gg/streamlit
- **GitHub Issues:** https://github.com/streamlit/streamlit/issues

### Video Tutorials

- Search YouTube: "Deploy Streamlit app"
- Streamlit's official channel has great tutorials

---

## ✅ Quick Reference Checklist

**Initial Deployment:**
- [ ] Code is on GitHub
- [ ] `requirements.txt` is correct
- [ ] Created Streamlit Cloud account
- [ ] Connected GitHub repository
- [ ] Configured app settings
- [ ] Clicked "Deploy"
- [ ] Tested app functionality
- [ ] Shared URL with team

**Regular Maintenance:**
- [ ] Monitor app analytics weekly
- [ ] Check logs for errors
- [ ] Update code as needed (auto-deploys)
- [ ] Archive old reports
- [ ] Review user feedback

**Security:**
- [ ] Consider email restrictions
- [ ] Add password if needed
- [ ] Don't commit sensitive data
- [ ] Use secrets for passwords
- [ ] Regular security reviews

---

## 🎉 You're Done!

Your Force Plate Report Generator is now live and accessible to your entire coaching staff!

**Next Steps:**
1. Share the URL with your team
2. Train staff on how to use it (show them STREAMLIT_QUICK_START.md)
3. Monitor usage and gather feedback
4. Make improvements based on feedback
5. Update the app as needed (auto-deploys!)

**Questions?**
- Check the troubleshooting section
- Visit Streamlit's documentation
- Contact Baylor IT for institutional support

---

**Baylor University Athletics - B.A.I.R. Initiative**
**Deployment Guide v1.0 | December 2024**
