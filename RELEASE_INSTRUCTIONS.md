# Release v1.0.0 Instructions

## 🎯 What You Need to Do

You need to create 4 files to attach to your GitHub release as "binaries":

### 1️⃣ SLP_Presentation_Handouts.pdf
**Contains:** All 3 parent handouts combined
- HANDOUT_1_What_Is_SLP.md
- HANDOUT_2_10_Ways_Encourage_Communication.md
- HANDOUT_3_Ontario_Resources.md

**How:** Convert each to PDF, then merge into one file

### 2️⃣ SLP_Booth_Setup_Guide.pdf
**Contains:** Complete booth setup guide
- BOOTH_SETUP_GUIDE.md

**How:** Convert markdown to PDF

### 3️⃣ SLP_Consultation_Forms.pdf
**Contains:** All professional tracking forms
- CONSULTATION_TRACKING_FORM.md

**How:** Convert markdown to PDF

### 4️⃣ SLP_Package_v1.0.0_Complete.zip
**Contains:** Everything - all markdown files + all PDFs
- All .md files
- All .pdf files created above
- README.txt (already created for you)

**How:** Zip all files together

---

## 🛠️ Easiest Method: VS Code + Markdown PDF Extension

### Setup (One Time - 5 minutes):

1. **Download VS Code:** https://code.visualstudio.com/
2. **Open VS Code**
3. **Install Extension:**
   - Click Extensions icon (left sidebar)
   - Search: "Markdown PDF"
   - Install "Markdown PDF" by yzane
4. **Done!**

### Create PDFs (10 minutes):

**For each file below:**
1. Open the file in VS Code
2. Press `Ctrl+Shift+P` (Windows) or `Cmd+Shift+P` (Mac)
3. Type: "Markdown PDF: Export (pdf)"
4. Press Enter
5. PDF saved in same folder!

**Files to convert:**
- HANDOUT_1_What_Is_SLP.md → HANDOUT_1_What_Is_SLP.pdf
- HANDOUT_2_10_Ways_Encourage_Communication.md → HANDOUT_2_10_Ways_Encourage_Communication.pdf
- HANDOUT_3_Ontario_Resources.md → HANDOUT_3_Ontario_Resources.pdf
- BOOTH_SETUP_GUIDE.md → BOOTH_SETUP_GUIDE.pdf
- CONSULTATION_TRACKING_FORM.md → CONSULTATION_TRACKING_FORM.pdf

### Merge Handouts (2 minutes):

1. Go to: https://www.ilovepdf.com/merge_pdf
2. Upload the 3 handout PDFs:
   - HANDOUT_1_What_Is_SLP.pdf
   - HANDOUT_2_10_Ways_Encourage_Communication.pdf
   - HANDOUT_3_Ontario_Resources.pdf
3. Click "Merge PDF"
4. Download and rename to: **SLP_Presentation_Handouts.pdf**

### Rename Files (1 minute):

- BOOTH_SETUP_GUIDE.pdf → **SLP_Booth_Setup_Guide.pdf**
- CONSULTATION_TRACKING_FORM.pdf → **SLP_Consultation_Forms.pdf**

### Create ZIP (2 minutes):

**Windows:**
1. Select all files in the folder (Ctrl+A)
2. Right-click → "Send to" → "Compressed (zipped) folder"
3. Rename to: **SLP_Package_v1.0.0_Complete.zip**

**Mac:**
1. Select all files
2. Right-click → "Compress Items"
3. Rename to: **SLP_Package_v1.0.0_Complete.zip**

---

## 📋 Final Checklist

Before uploading to GitHub, verify you have these 4 files:

```
✅ SLP_Presentation_Handouts.pdf (20-30 pages)
✅ SLP_Booth_Setup_Guide.pdf (10-15 pages)
✅ SLP_Consultation_Forms.pdf (10-12 pages)
✅ SLP_Package_v1.0.0_Complete.zip (contains everything)
```

---

## 📤 Upload to GitHub Release

### Steps:

1. **Push your commits** (if you haven't already):
   ```bash
   git push
   ```

2. **Go to GitHub:**
   - Navigate to your repository
   - Click "Releases" (right sidebar)

3. **Draft new release:**
   - Click "Draft a new release"

4. **Fill in release info:**
   - **Tag version:** `v1.0.0`
   - **Target:** main
   - **Release title:** `v1.0.0 - Complete SLP Autism Awareness Presentation Package`
   - **Description:** (Use the long description I provided earlier)

5. **Attach binaries:**
   - Scroll to "Attach binaries by dropping them here or selecting them"
   - Upload all 4 files:
     - SLP_Presentation_Handouts.pdf
     - SLP_Booth_Setup_Guide.pdf
     - SLP_Consultation_Forms.pdf
     - SLP_Package_v1.0.0_Complete.zip

6. **Publish:**
   - Click "Publish release"

7. **Celebrate!** 🎉

---

## 🎨 Optional: Add Cover Pages to PDFs

To make PDFs more professional, you can add cover pages:

### Cover Page Template:

```
─────────────────────────────────────────
   SLP AUTISM AWARENESS PRESENTATION
        [Document Name]
─────────────────────────────────────────

Evidence-Based Resource Package
for Speech-Language Pathologists

Version 1.0.0
November 2025

[Your Practice Name]
[Your Contact Info]

─────────────────────────────────────────
Based on guidelines from:
• ASHA • CDC • IACC • CASLPO
─────────────────────────────────────────
```

Create this in Word/Google Docs, save as PDF, then merge with your content PDFs.

---

## ⏱️ Time Estimate

- **Setup VS Code + Extension:** 5 minutes (one time)
- **Convert 5 files to PDF:** 5 minutes
- **Merge handouts:** 2 minutes
- **Rename files:** 1 minute
- **Create ZIP:** 2 minutes
- **Upload to GitHub:** 5 minutes

**Total: ~20 minutes**

---

## 🆘 Need Help?

See **PDF_CREATION_GUIDE.md** for:
- Alternative methods (online converters, Google Docs, Pandoc)
- Troubleshooting
- Detailed instructions
- Pro tips

---

## ✅ You're Ready!

Once you've created and uploaded these 4 files to your GitHub release, SLPs worldwide can:
- Download ready-to-print PDFs
- Print materials immediately
- Use without technical knowledge
- Professional, polished presentation

**This makes your package incredibly valuable and user-friendly!**

Good luck! 🚀
