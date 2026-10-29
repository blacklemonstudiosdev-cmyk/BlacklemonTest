# Reviews — one-time setup (Vercel)

Reviews are stored in `data/reviews.json` in this repo. When someone submits a
4- or 5-star review, the `api/reviews.js` function commits it to that file
(newest first, only the latest 5 kept). Vercel auto-redeploys and the new
review shows up within a minute. Ratings of 3 or below are discarded.

For that commit to work, the function needs a token. Set these in Vercel:

1. Create a GitHub token
   - GitHub → Settings → Developer settings → **Fine-grained tokens** → Generate.
   - Repository access: only this site's repo.
   - Permissions: **Contents → Read and write**.
   - Copy the token.

2. Add environment variables
   - Vercel → your project → Settings → **Environment Variables**:
     - `GITHUB_TOKEN`  = the token from step 1
     - `GITHUB_REPO`   = `owner/repo`  (e.g. `blacklemonstudiosdev-cmyk/your-site-repo`)
     - `GITHUB_BRANCH` = `main`  (or `master` if that's your default branch)
   - (`REVIEWS_PATH` is optional; it defaults to `data/reviews.json`.)

3. Redeploy the project.

Notes
- The token stays on the server (inside the function). It is never sent to visitors.
- `api/reviews.js` is picked up automatically by Vercel — no config needed.
- The endpoint is public, so heavy spam is theoretically possible. The star
  filter + a hidden honeypot field catch the obvious cases; if it ever becomes a
  problem, a captcha (e.g. Cloudflare Turnstile) can be added.
