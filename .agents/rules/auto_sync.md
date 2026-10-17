# Mandatory Continuous Dual-Sync Protocol (GitHub & Vercel)

## Rule Requirement
For every user message and code modification in this workspace:
1. **Zero Uncommitted Code**: Every created, modified, or regenerated file must be immediately staged (`git add .`) and committed (`git commit -m "..."`).
2. **Push to Remote GitHub**: Push immediately to remote `origin` on branch `main` (`git push origin main`).
   - Repository: `https://github.com/adityajoshi202424-commits/ukis-mountain-disaster-early-warning`
3. **Deploy Directly to Vercel Production**: Run `npx vercel --prod --yes` in `frontend/` so that the live Vercel application at `https://frontend-rosy-phi-23.vercel.app` reflects the latest changes in real time.
4. **Zero Data Fabrication**: Never hardcode values. Keep all telemetry grounded in real external APIs (Open-Meteo, Copernicus GloFAS, USGS).
5. **Always Report Status**: Provide the latest commit hash, GitHub link, and live production Vercel URL in every response.
