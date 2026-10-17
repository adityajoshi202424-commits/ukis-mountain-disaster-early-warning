# UKIS 2026 P-011 Workspace Guidelines

## Mandatory Continuous Dual-Sync Protocol
After every turn or code update:
1. Stage all changes: `git add .`
2. Commit changes: `git commit -m "..."`
3. Push to GitHub: `git push origin main`
   - Repo: https://github.com/adityajoshi202424-commits/ukis-mountain-disaster-early-warning
4. Deploy to Vercel production:
   - In `frontend/`: `npx vercel --prod --yes`
   - Live URL: https://frontend-rosy-phi-23.vercel.app
5. Keep all data 100% authentic with zero hardcoding or fabrication.
